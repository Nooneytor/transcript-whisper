"""
Componentes de interfaz de usuario reutilizables.
"""
import streamlit as st
from src.config import MODELOS_DISPONIBLES, IDIOMAS


def render_sidebar(estado_procesando=False):
    """Renderiza la barra lateral con configuración"""
    st.sidebar.header('⚙️ Configuración')
    
    # Mostrar advertencia si está procesando
    if estado_procesando:
        st.sidebar.warning('⚠️ Transcripción en proceso... Por favor espera.')
    
    # Selector de modelo
    modelos_lista = []
    modelo_default_idx = 0
    
    for idx, (key, info) in enumerate(MODELOS_DISPONIBLES.items()):
        if info['disponible']:
            modelos_lista.append(key)
            if key == 'base':
                modelo_default_idx = len(modelos_lista) - 1
        else:
            modelos_lista.append(f"🚫 {key} (no disponible)")
    
    modelo_seleccionado = st.sidebar.selectbox(
        '🤖 Modelo de Whisper',
        modelos_lista,
        index=modelo_default_idx,
        help='Modelos más grandes = mejor precisión pero más lento',
        disabled=estado_procesando
    )
    
    # Determinar el modelo real
    if modelo_seleccionado.startswith('🚫'):
        st.sidebar.error('⚠️ Este modelo no está disponible en CPU gratuita. Por favor, selecciona "tiny" o "base".')
        modelo_real = 'base'
        modelo_disabled = True
    else:
        modelo_real = modelo_seleccionado
        modelo_disabled = False
    
    # Selector de idioma
    idioma = st.sidebar.selectbox(
        '🌍 Idioma',
        list(IDIOMAS.keys()),
        format_func=lambda x: IDIOMAS[x],
        index=1,  # 'es' por defecto
        help='Dejar en "auto" para detección automática',
        disabled=estado_procesando
    )
    
    # Información sobre el modelo seleccionado
    if modelo_real in MODELOS_DISPONIBLES:
        info = MODELOS_DISPONIBLES[modelo_real]
        st.sidebar.markdown('### 📊 Información del Modelo')
        st.sidebar.info(f"**{info['nombre']}**: {info['tamaño']} - {info['velocidad']}, precisión {info['precision'].lower()}")
    
    # Advertencia de rendimiento
    st.sidebar.markdown('### ⚡ Rendimiento en CPU')
    st.sidebar.warning(f"⏱️ Tiempo estimado para 200MB: **10-25 min con base**")
    st.sidebar.info("💡 **Consejo**: Usa archivos < 50MB o modelo 'tiny' para pruebas rápidas.")
    
    return modelo_real, idioma, modelo_disabled


def render_file_uploader(estado_procesando=False):
    """Renderiza el componente de subida de archivos"""
    from src.config import FORMATOS_AUDIO
    
    st.header('📁 Subir Archivo de Audio')
    
    archivo = st.file_uploader(
        'Selecciona un archivo de audio',
        type=FORMATOS_AUDIO,
        help='Recomendado: < 50MB para mejor rendimiento en CPU. Máximo: 200MB',
        disabled=estado_procesando
    )
    
    return archivo


def render_file_info(archivo):
    """Muestra información sobre el archivo subido"""
    from src.config import MAX_FILE_SIZE_MB, RECOMMENDED_FILE_SIZE_MB
    
    tamano_mb = archivo.size / (1024*1024)
    st.success(f'✅ Archivo cargado: {archivo.name}')
    
    # Advertencia por tamaño
    if tamano_mb > 100:
        st.warning(f'⚠️ Tamaño: {tamano_mb:.1f} MB - La transcripción puede tardar mucho en CPU')
    elif tamano_mb > RECOMMENDED_FILE_SIZE_MB:
        st.info(f'📏 Tamaño: {tamano_mb:.1f} MB - Tiempo de transcripción moderado')
    else:
        st.info(f'📏 Tamaño: {tamano_mb:.1f} MB - Tamaño óptimo para CPU')
    
    return tamano_mb


def render_info_panel():
    """Renderiza el panel de información"""
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
    - **small**: ⚠️ No disponible en CPU gratuita
    
    ### 📁 Formatos soportados:
    MP3, WAV, M4A, FLAC, OGG, MP4, WEBM, MKV
    
    ### 🌐 Despliegue:
    Esta app está optimizada para Hugging Face Spaces con CPU gratuita.
    Para procesamiento más rápido, considera activar GPU.
    """)

