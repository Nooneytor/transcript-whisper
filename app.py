#!/usr/bin/env python3
"""
Aplicación Streamlit para transcribir archivos de audio usando OpenAI Whisper.
Permite subir audios, elegir modelo/idioma, transcribir y descargar en TXT/DOCX.
"""

import os
import tempfile
import streamlit as st
import time
import threading

# Importar módulos propios
from src.config import APP_TITLE, APP_ICON, MAX_FILE_SIZE_MB, MODELOS_DISPONIBLES
from src.utils import format_time, setup_ffmpeg, calcular_tiempo_estimado
from src.export import export_txt, export_docx
from src.transcription import load_whisper_model, transcribe_audio, ProgressCapture
from src.ui_components import render_sidebar, render_file_uploader, render_file_info, render_info_panel

# Configuración de la página
st.set_page_config(
    page_title='Transcriptor Whisper',
    page_icon=APP_ICON,
    layout='wide',
    initial_sidebar_state='expanded'
)

# Verificar y configurar ffmpeg
@st.cache_resource
def init_ffmpeg():
    """Inicializa ffmpeg y retorna si está disponible"""
    return setup_ffmpeg()

ffmpeg_available = init_ffmpeg()
if not ffmpeg_available:
    st.warning("⚠️ FFmpeg no está disponible. La transcripción puede fallar.")

# Título principal
st.title(APP_TITLE)
st.markdown('---')

# Inicializar estado de sesión
if 'procesando' not in st.session_state:
    st.session_state.procesando = False
if 'resultado' not in st.session_state:
    st.session_state.resultado = None

# Layout principal
col1, col2 = st.columns([2, 1])

with col1:
    # Renderizar sidebar y obtener configuración
    modelo_real, idioma, modelo_disabled = render_sidebar(st.session_state.procesando)
    
    # Subir archivo
    archivo = render_file_uploader(st.session_state.procesando)
    
    if archivo:
        # Mostrar información del archivo
        tamano_mb = render_file_info(archivo)
        
        # Botón de transcripción
        iniciar_transcripcion = st.button(
            '🚀 Transcribir Audio',
            type='primary',
            use_container_width=True,
            disabled=modelo_disabled or st.session_state.procesando
        )
        
        if iniciar_transcripcion and not st.session_state.procesando:
            # Validaciones
            if archivo.size > MAX_FILE_SIZE_MB * 1024 * 1024:
                st.error(f'❌ El archivo es demasiado grande. Máximo {MAX_FILE_SIZE_MB}MB.')
            elif not ffmpeg_available:
                st.error('❌ FFmpeg no está disponible. No se puede procesar el audio.')
            elif modelo_disabled:
                st.error('❌ El modelo seleccionado no está disponible. Por favor, elige "tiny" o "base".')
            else:
                # Marcar como procesando
                st.session_state.procesando = True
                st.rerun()
        
        # Procesar si está en estado de procesamiento
        if st.session_state.procesando:
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'_{archivo.name}') as tmp:
                tmp.write(archivo.read())
                ruta_temp = tmp.name
            
            try:
                # UI de progreso
                st.markdown('---')
                st.subheader('🔄 Proceso de Transcripción')
                
                # Calcular tiempo estimado
                tiempo_est = calcular_tiempo_estimado(tamano_mb, modelo_real, MODELOS_DISPONIBLES)
                
                # Advertencias
                st.warning('⚠️ **Importante**: No cierres esta ventana ni recargues la página.')
                st.info(f'📊 **Modelo**: {modelo_real} | **Tamaño**: {tamano_mb:.1f} MB | **Tiempo estimado**: ~{tiempo_est:.1f} min')
                
                # Contenedores de progreso
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Contenedor de logs fijo (no empty)
                st.markdown('##### 📋 Logs de Whisper')
                whisper_logs_placeholder = st.empty()
                
                transcription_progress = st.empty()
                detail_progress = st.empty()
                
                # Paso 1: Cargar modelo
                status_text.info('🔄 Paso 1/3: Cargando modelo Whisper...')
                progress_bar.progress(10)
                
                tiempo_inicio = time.time()
                model = load_whisper_model(modelo_real)
                
                if model is None:
                    st.session_state.procesando = False
                    st.error('❌ No se pudo cargar el modelo.')
                    st.stop()
                
                progress_bar.progress(30)
                status_text.info('🎵 Paso 2/3: Transcribiendo audio...')
                
                # Configurar captura de progreso
                progress_capture = ProgressCapture()
                resultado_container = {'resultado': None, 'error': None, 'completado': False}
                
                def transcribe_thread():
                    try:
                        resultado_container['resultado'] = transcribe_audio(
                            model, ruta_temp, idioma, progress_capture
                        )
                        resultado_container['completado'] = True
                    except Exception as e:
                        resultado_container['error'] = str(e)
                        resultado_container['completado'] = True
                
                # Iniciar transcripción en background
                thread = threading.Thread(target=transcribe_thread)
                thread.start()
                
                # Actualizar progreso en tiempo real
                tiempo_transcripcion_inicio = time.time()
                logs_whisper = []
                
                while not resultado_container['completado']:
                    tiempo_transcurrido = time.time() - tiempo_transcripcion_inicio
                    porcentaje_whisper = progress_capture.porcentaje
                    
                    if porcentaje_whisper > 0:
                        # Progreso real
                        progreso_real = 30 + int((porcentaje_whisper / 100) * 60)
                        progress_bar.progress(min(progreso_real, 90))
                        
                        transcription_progress.info(f'🎵 Transcribiendo... **{porcentaje_whisper}%** completado')
                        
                        # Calcular tiempo restante
                        if porcentaje_whisper > 5:
                            tiempo_por_porcentaje = tiempo_transcurrido / porcentaje_whisper
                            tiempo_restante = tiempo_por_porcentaje * (100 - porcentaje_whisper)
                            minutos = int(tiempo_restante // 60)
                            segundos = int(tiempo_restante % 60)
                            detail_progress.success(
                                f'⏱️ Transcurrido: {int(tiempo_transcurrido)}s | '
                                f'Restante: **~{minutos}m {segundos}s**'
                            )
                        else:
                            detail_progress.info(f'⏱️ Transcurrido: {int(tiempo_transcurrido)}s')
                        
                        # Actualizar logs
                        if progress_capture.ultimo_log and (not logs_whisper or logs_whisper[-1] != progress_capture.ultimo_log):
                            logs_whisper.append(progress_capture.ultimo_log)
                            if len(logs_whisper) > 10:
                                logs_whisper.pop(0)
                        
                        # Mostrar logs siempre
                        if logs_whisper:
                            logs_text = '\n'.join([f'• {log}' for log in logs_whisper[-5:]])
                            whisper_logs_placeholder.code(logs_text, language=None)
                        else:
                            whisper_logs_placeholder.code('• Esperando logs de Whisper...', language=None)
                    else:
                        # Inicializando
                        progress_bar.progress(30)
                        transcription_progress.info('🎵 Inicializando...')
                        whisper_logs_placeholder.code('• Inicializando Whisper...', language=None)
                    
                    time.sleep(0.5)
                
                # Esperar a que termine
                thread.join()
                
                # Limpiar UI de progreso
                transcription_progress.empty()
                detail_progress.empty()
                whisper_logs_placeholder.empty()
                
                # Verificar errores
                if resultado_container['error']:
                    st.session_state.procesando = False
                    st.error(f'❌ Error: {resultado_container["error"]}')
                    st.stop()
                
                # Guardar resultado
                st.session_state.resultado = resultado_container['resultado']
                st.session_state.procesando = False
                
                progress_bar.progress(100)
                status_text.success('✅ ¡Transcripción completada!')
                
                tiempo_total = time.time() - tiempo_inicio
                st.success(f'🎉 Completado en {tiempo_total/60:.1f} minutos')
                
            except Exception as e:
                st.session_state.procesando = False
                st.error(f'❌ Error: {str(e)}')
            finally:
                # Limpiar archivo temporal
                try:
                    os.unlink(ruta_temp)
                except:
                    pass
                st.rerun()
    
    # Mostrar resultados si existen
    if st.session_state.resultado and not st.session_state.procesando:
        resultado = st.session_state.resultado
        st.markdown('---')
        st.header('📝 Resultado de la Transcripción')
        
        # Métricas
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric('Idioma detectado', resultado.get('language', 'N/A'))
        with col_m2:
            st.metric('Segmentos', len(resultado.get('segments', [])))
        with col_m3:
            duracion = resultado.get('segments', [{}])[-1].get('end', 0) if resultado.get('segments') else 0
            st.metric('Duración', format_time(duracion))
        
        # Transcripción completa
        texto_completo = resultado['text']
        st.text_area('Transcripción completa', texto_completo, height=300)
        
        # Botones de descarga
        st.subheader('💾 Descargar Resultados')
        col_d1, col_d2 = st.columns(2)
        
        with col_d1:
            txt_content = export_txt(texto_completo, resultado.get('segments'))
            st.download_button(
                '📄 Descargar TXT',
                txt_content,
                file_name=f'transcripcion_{archivo.name.split(".")[0]}.txt',
                mime='text/plain',
                use_container_width=True
            )
        
        with col_d2:
            docx_content = export_docx(texto_completo, resultado.get('segments'))
            st.download_button(
                '📝 Descargar DOCX',
                docx_content,
                file_name=f'transcripcion_{archivo.name.split(".")[0]}.docx',
                mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                use_container_width=True
            )
        
        # Botón para nueva transcripción
        if st.button('🔄 Nueva Transcripción', use_container_width=True):
            st.session_state.resultado = None
            st.rerun()

with col2:
    render_info_panel()

# Footer
st.markdown('---')
st.markdown('Desarrollado con ❤️ usando [Streamlit](https://streamlit.io) y [OpenAI Whisper](https://github.com/openai/whisper)')

