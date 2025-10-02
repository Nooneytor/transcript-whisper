#!/usr/bin/env python3
"""
Aplicación Streamlit para transcribir archivos de audio usando OpenAI Whisper.
Permite subir audios, elegir modelo/idioma, transcribir y descargar en TXT/DOCX.
"""

import os
import tempfile
import streamlit as st
import whisper
from docx import Document
from io import BytesIO
import time
import subprocess
import sys

def export_docx(text: str, segments=None) -> bytes:
    """
    Exporta la transcripción a formato DOCX con timestamps opcionales.
    
    Args:
        text (str): Texto de la transcripción
        segments (list): Lista de segmentos con timestamps (opcional)
    
    Returns:
        bytes: Contenido del archivo DOCX
    """
    doc = Document()
    doc.add_heading('Transcripción de Audio', 0)
    
    # Añadir información general
    doc.add_heading('Información', level=1)
    doc.add_paragraph(f'Fecha de transcripción: {time.strftime("%Y-%m-%d %H:%M:%S")}')
    if segments:
        doc.add_paragraph(f'Número de segmentos: {len(segments)}')
    
    # Añadir transcripción completa
    doc.add_heading('Transcripción Completa', level=1)
    doc.add_paragraph(text)
    
    # Añadir segmentos con timestamps si están disponibles
    if segments:
        doc.add_heading('Segmentos con Timestamps', level=1)
        for i, segmento in enumerate(segments):
            inicio = int(segmento['start'])
            fin = int(segmento['end'])
            texto_seg = segmento['text']
            
            # Formatear tiempo
            inicio_min = inicio // 60
            inicio_sec = inicio % 60
            fin_min = fin // 60
            fin_sec = fin % 60
            
            doc.add_paragraph(f'[{inicio_min:02d}:{inicio_sec:02d} - {fin_min:02d}:{fin_sec:02d}] {texto_seg}')
    
    # Guardar en BytesIO
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio.read()

def format_time(seconds):
    """Formatea segundos a formato MM:SS"""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def setup_ffmpeg():
    """Configura ffmpeg para que esté disponible en el PATH"""
    try:
        # Verificar si ffmpeg está disponible
        result = subprocess.run(['ffmpeg', '-version'], 
                             capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    # Si no está disponible, intentar usar los ejecutables locales
    try:
        local_ffmpeg = os.path.join(os.getcwd(), 'ffmpeg', 'ffmpeg.exe')
        if os.path.exists(local_ffmpeg):
            # Añadir al PATH temporalmente
            ffmpeg_dir = os.path.join(os.getcwd(), 'ffmpeg')
            os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ['PATH']
            
            # Verificar que funciona
            result = subprocess.run([local_ffmpeg, '-version'], 
                                 capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    return False

# Configuración de la página
st.set_page_config(
    page_title='Transcriptor Whisper',
    page_icon='🎙️',
    layout='wide',
    initial_sidebar_state='expanded'
)

# Verificar y configurar ffmpeg
@st.cache_resource
def init_ffmpeg():
    """Inicializa ffmpeg y retorna si está disponible"""
    return setup_ffmpeg()

# Verificar ffmpeg al cargar la página
ffmpeg_available = init_ffmpeg()
if not ffmpeg_available:
    st.error("⚠️ FFmpeg no está disponible. La transcripción puede fallar.")
    st.info("💡 Si estás en Streamlit Cloud, esto debería resolverse automáticamente.")

# Título principal
st.title('🎙️ Transcriptor de Audio con Whisper')
st.markdown('---')

# Sidebar con opciones
st.sidebar.header('⚙️ Configuración')

# Selector de modelo
modelo = st.sidebar.selectbox(
    '🤖 Modelo de Whisper',
    ['tiny', 'base', 'small'],
    index=1,
    help='Modelos más grandes = mejor precisión pero más lento'
)

# Selector de idioma
idioma = st.sidebar.selectbox(
    '🌍 Idioma',
    ['auto', 'es', 'en', 'fr', 'pt', 'it', 'de'],
    index=1,
    help='Dejar en "auto" para detección automática'
)

# Información sobre modelos
st.sidebar.markdown('### 📊 Información de Modelos')
model_info = {
    'tiny': '~39 MB - Muy rápido, precisión básica',
    'base': '~74 MB - Equilibrio velocidad/precisión (recomendado)',
    'small': '~244 MB - Mejor precisión, más lento'
}
st.sidebar.info(f"**{modelo}**: {model_info[modelo]}")

# Área principal
col1, col2 = st.columns([2, 1])

with col1:
    st.header('📁 Subir Archivo de Audio')
    
    # File uploader
    archivo = st.file_uploader(
        'Selecciona un archivo de audio',
        type=['mp3', 'wav', 'm4a', 'flac', 'ogg', 'mp4', 'webm', 'mkv'],
        help='Máximo 200MB. Formatos soportados: MP3, WAV, M4A, FLAC, OGG, MP4, WEBM'
    )
    
    if archivo:
        st.success(f'✅ Archivo cargado: {archivo.name}')
        st.info(f'📏 Tamaño: {archivo.size / (1024*1024):.1f} MB')
        
        # Botón de transcripción
        if st.button('🚀 Transcribir Audio', type='primary', use_container_width=True):
            if archivo.size > 200 * 1024 * 1024:  # 200MB
                st.error('❌ El archivo es demasiado grande. Máximo 200MB.')
            elif not ffmpeg_available:
                st.error('❌ FFmpeg no está disponible. No se puede procesar el audio.')
                st.info('💡 Intenta recargar la página o contacta al administrador.')
            else:
                # Crear archivo temporal
                with tempfile.NamedTemporaryFile(delete=False, suffix=f'_{archivo.name}') as tmp:
                    tmp.write(archivo.read())
                    ruta_temp = tmp.name
                
                try:
                    # Mostrar progreso
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Cargar modelo
                    status_text.text('🔄 Cargando modelo Whisper...')
                    progress_bar.progress(20)
                    
                    with st.spinner('Cargando modelo...'):
                        model = whisper.load_model(modelo)
                    
                    progress_bar.progress(40)
                    status_text.text('🎵 Transcribiendo audio...')
                    
                    # Configurar parámetros de transcripción
                    transcribe_kwargs = {}
                    if idioma != 'auto':
                        transcribe_kwargs['language'] = idioma
                    
                    # Transcribir
                    with st.spinner('Transcribiendo... esto puede tardar varios minutos'):
                        resultado = model.transcribe(ruta_temp, **transcribe_kwargs)
                    
                    progress_bar.progress(100)
                    status_text.text('✅ Transcripción completada!')
                    
                    # Mostrar resultados
                    st.success('🎉 ¡Transcripción completada exitosamente!')
                    
                    # Información del resultado
                    col_info1, col_info2, col_info3 = st.columns(3)
                    with col_info1:
                        st.metric('Idioma detectado', resultado.get('language', 'No detectado'))
                    with col_info2:
                        st.metric('Segmentos', len(resultado.get('segments', [])))
                    with col_info3:
                        duracion = resultado.get('segments', [{}])[-1].get('end', 0) if resultado.get('segments') else 0
                        st.metric('Duración', format_time(duracion))
                    
                    # Mostrar transcripción
                    st.header('📝 Resultado de la Transcripción')
                    texto_completo = resultado['text']
                    st.text_area(
                        'Transcripción completa',
                        texto_completo,
                        height=300,
                        help='Puedes copiar este texto directamente'
                    )
                    
                    # Mostrar segmentos con timestamps
                    if resultado.get('segments'):
                        st.header('⏱️ Segmentos con Timestamps')
                        
                        # Mostrar solo los primeros 10 segmentos para no sobrecargar
                        segmentos_mostrar = resultado['segments'][:10]
                        
                        for i, segmento in enumerate(segmentos_mostrar):
                            inicio = segmento['start']
                            fin = segmento['end']
                            texto_seg = segmento['text']
                            
                            st.markdown(f"**{format_time(inicio)} - {format_time(fin)}**: {texto_seg}")
                        
                        if len(resultado['segments']) > 10:
                            st.info(f'... y {len(resultado["segments"]) - 10} segmentos más')
                    
                    # Botones de descarga
                    st.header('💾 Descargar Resultados')
                    
                    col_download1, col_download2 = st.columns(2)
                    
                    with col_download1:
                        st.download_button(
                            '📄 Descargar TXT',
                            texto_completo,
                            file_name=f'transcripcion_{archivo.name.split(".")[0]}.txt',
                            mime='text/plain',
                            use_container_width=True
                        )
                    
                    with col_download2:
                        docx_content = export_docx(texto_completo, resultado.get('segments'))
                        st.download_button(
                            '📝 Descargar DOCX',
                            docx_content,
                            file_name=f'transcripcion_{archivo.name.split(".")[0]}.docx',
                            mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                            use_container_width=True
                        )
                    
                except Exception as e:
                    st.error(f'❌ Error durante la transcripción: {str(e)}')
                    st.info('💡 Sugerencias: Verifica que el archivo no esté corrupto y que sea un formato de audio válido.')
                
                finally:
                    # Limpiar archivo temporal
                    try:
                        os.unlink(ruta_temp)
                    except:
                        pass

with col2:
    st.header('ℹ️ Información')
    
    st.markdown("""
    ### 🎯 Cómo usar:
    1. **Selecciona** el modelo y idioma en la barra lateral
    2. **Sube** tu archivo de audio
    3. **Haz clic** en "Transcribir Audio"
    4. **Espera** a que se complete (puede tardar varios minutos)
    5. **Descarga** el resultado en TXT o DOCX
    
    ### ⚡ Consejos de rendimiento:
    - **tiny**: Más rápido, menos preciso
    - **base**: Equilibrio perfecto (recomendado)
    - **small**: Más preciso, más lento
    
    ### 📁 Formatos soportados:
    MP3, WAV, M4A, FLAC, OGG, MP4, WEBM, MKV
    """)
    
    st.markdown('---')
    
    st.markdown("""
    ### 🚀 Despliegue
    Esta app está optimizada para:
    - **Streamlit Cloud** (CPU)
    - **Hugging Face Spaces** (GPU opcional)
    """)

# Footer
st.markdown('---')
st.markdown(
    'Desarrollado con ❤️ usando [Streamlit](https://streamlit.io) y [OpenAI Whisper](https://github.com/openai/whisper)'
)
