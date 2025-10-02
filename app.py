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
    st.warning("⚠️ FFmpeg no está disponible. La transcripción puede fallar.")

# Cache del modelo para evitar recargas
@st.cache_resource
def load_whisper_model(model_name):
    """Carga el modelo de Whisper y lo mantiene en caché"""
    try:
        return whisper.load_model(model_name)
    except Exception as e:
        st.error(f"Error al cargar el modelo: {e}")
        return None

# Título principal
st.title('🎙️ Transcriptor de Audio con Whisper')
st.markdown('---')

# Sidebar con opciones
st.sidebar.header('⚙️ Configuración')

# Selector de modelo
modelo_options = ['tiny', 'base', '🚫 small (no disponible en CPU gratuita)']
modelo = st.sidebar.selectbox(
    '🤖 Modelo de Whisper',
    modelo_options,
    index=1,
    help='Modelos más grandes = mejor precisión pero más lento'
)

# Convertir la selección a nombre real del modelo
if modelo.startswith('🚫'):
    st.sidebar.error('⚠️ El modelo "small" requiere demasiados recursos y no funciona bien en CPU gratuita. Por favor, selecciona "tiny" o "base".')
    modelo_real = 'base'  # Fallback
    modelo_disabled = True
else:
    modelo_real = modelo
    modelo_disabled = False

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
}
if modelo_real in model_info:
    st.sidebar.info(f"**{modelo_real}**: {model_info[modelo_real]}")

# Advertencia de rendimiento en CPU
st.sidebar.markdown('### ⚡ Rendimiento en CPU')
tiempo_estimado = {
    'tiny': '3-8 min',
    'base': '10-25 min',
}
if modelo_real in tiempo_estimado:
    st.sidebar.warning(f"⏱️ Tiempo estimado para audio de 200MB: **{tiempo_estimado[modelo_real]}**")
st.sidebar.info("💡 **Consejo**: Usa archivos más pequeños o modelo 'tiny' para pruebas rápidas.")

# Área principal
col1, col2 = st.columns([2, 1])

with col1:
    st.header('📁 Subir Archivo de Audio')
    
    # File uploader
    archivo = st.file_uploader(
        'Selecciona un archivo de audio',
        type=['mp3', 'wav', 'm4a', 'flac', 'ogg', 'mp4', 'webm', 'mkv'],
        help='Recomendado: < 50MB para mejor rendimiento en CPU. Máximo: 200MB'
    )
    
    if archivo:
        tamano_mb = archivo.size / (1024*1024)
        st.success(f'✅ Archivo cargado: {archivo.name}')
        
        # Advertencia por tamaño
        if tamano_mb > 100:
            st.warning(f'⚠️ Tamaño: {tamano_mb:.1f} MB - La transcripción puede tardar mucho en CPU')
        elif tamano_mb > 50:
            st.info(f'📏 Tamaño: {tamano_mb:.1f} MB - Tiempo de transcripción moderado')
        else:
            st.info(f'📏 Tamaño: {tamano_mb:.1f} MB - Tamaño óptimo para CPU')
        
        # Botón de transcripción
        col_btn1, col_btn2 = st.columns([3, 1])
        with col_btn1:
            iniciar_transcripcion = st.button('🚀 Transcribir Audio', type='primary', use_container_width=True, disabled=modelo_disabled)
        
        if iniciar_transcripcion:
            if archivo.size > 200 * 1024 * 1024:  # 200MB
                st.error('❌ El archivo es demasiado grande. Máximo 200MB.')
            elif not ffmpeg_available:
                st.error('❌ FFmpeg no está disponible. No se puede procesar el audio.')
                st.info('💡 Intenta recargar la página o contacta al administrador.')
            elif modelo_disabled:
                st.error('❌ El modelo seleccionado no está disponible. Por favor, elige "tiny" o "base".')
            else:
                # Crear archivo temporal
                with tempfile.NamedTemporaryFile(delete=False, suffix=f'_{archivo.name}') as tmp:
                    tmp.write(archivo.read())
                    ruta_temp = tmp.name
                
                try:
                    # Contenedores para progreso y logs
                    st.markdown('---')
                    st.subheader('🔄 Proceso de Transcripción')
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    log_container = st.expander('📋 Ver logs detallados', expanded=True)
                    
                    import datetime
                    
                    def log_message(message, emoji='ℹ️'):
                        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
                        with log_container:
                            st.text(f"{emoji} [{timestamp}] {message}")
                    
                    # Calcular tiempo estimado
                    duracion_estimada_min = {
                        'tiny': tamano_mb * 0.5,  # ~30 seg por MB
                        'base': tamano_mb * 1.2,  # ~1.2 min por MB
                    }
                    tiempo_est = duracion_estimada_min.get(modelo_real, tamano_mb * 1.0)
                    
                    # Advertencia sobre cancelación
                    st.warning('⚠️ **Importante**: Una vez iniciado, el proceso no se puede cancelar. Si necesitas detenerlo, recarga la página (perderás el progreso).')
                    
                    log_message(f'Iniciando transcripción con modelo "{modelo_real}"', '🚀')
                    log_message(f'Tamaño del archivo: {tamano_mb:.1f} MB', '📏')
                    log_message(f'Tiempo estimado: {tiempo_est:.1f} minutos', '⏱️')
                    log_message('Por favor, mantén esta ventana abierta...', '⚠️')
                    
                    # Cargar modelo (cacheado)
                    status_text.info('🔄 Paso 1/3: Cargando modelo Whisper...')
                    progress_bar.progress(10)
                    log_message('Cargando modelo desde caché...', '🔄')
                    
                    tiempo_inicio = time.time()
                    model = load_whisper_model(modelo_real)
                    if model is None:
                        log_message('Error al cargar el modelo', '❌')
                        st.error('❌ No se pudo cargar el modelo.')
                        st.stop()
                    
                    tiempo_carga = time.time() - tiempo_inicio
                    log_message(f'Modelo cargado correctamente ({tiempo_carga:.1f}s)', '✅')
                    
                    progress_bar.progress(30)
                    status_text.info('🎵 Paso 2/3: Transcribiendo audio... (Esto puede tardar varios minutos)')
                    log_message('Procesando audio con Whisper...', '🎵')
                    log_message('Detectando idioma y segmentando...', '🔍')
                    
                    # Configurar parámetros de transcripción optimizados para CPU
                    transcribe_kwargs = {
                        'fp16': False,  # Forzar FP32 en CPU
                        'verbose': False,  # Reducir output
                    }
                    if idioma != 'auto':
                        transcribe_kwargs['language'] = idioma
                        log_message(f'Idioma configurado: {idioma}', '🌍')
                    else:
                        log_message('Detección automática de idioma activada', '🌍')
                    
                    # Transcribir
                    tiempo_transcripcion_inicio = time.time()
                    progress_bar.progress(40)
                    
                    resultado = model.transcribe(ruta_temp, **transcribe_kwargs)
                    
                    tiempo_transcripcion = time.time() - tiempo_transcripcion_inicio
                    progress_bar.progress(90)
                    log_message(f'Transcripción completada ({tiempo_transcripcion:.1f}s = {tiempo_transcripcion/60:.1f} min)', '✅')
                    
                    status_text.info('📝 Paso 3/3: Generando resultados...')
                    log_message('Generando archivos de descarga...', '📝')
                    
                    progress_bar.progress(100)
                    status_text.success('✅ ¡Transcripción completada exitosamente!')
                    
                    tiempo_total = time.time() - tiempo_inicio
                    log_message(f'Proceso completado en {tiempo_total:.1f}s ({tiempo_total/60:.1f} min)', '🎉')
                    
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
