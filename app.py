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
from src.utils import format_time, setup_ffmpeg, get_audio_duration
from src.export import export_txt, export_docx
from src.transcription import load_whisper_model, transcribe_audio, ProgressTracker
from src.ui_components import render_sidebar, render_file_uploader, render_file_info, render_info_panel

# Configuración de la página
st.set_page_config(
    page_title='Transcriptor Whisper',
    page_icon='🎙️',
    layout='wide',
    initial_sidebar_state='expanded'
)

# Verificar FFmpeg
ffmpeg_available = setup_ffmpeg()

# Inicializar estado de procesamiento
if 'procesando' not in st.session_state:
    st.session_state.procesando = False

# Título principal
st.title(f'{APP_ICON} {APP_TITLE}')
st.markdown('### Convierte audio a texto con OpenAI Whisper')

# Renderizar sidebar y obtener configuración
modelo_real, idioma, modelo_disabled = render_sidebar(st.session_state.procesando)

# Área principal
col1, col2 = st.columns([2, 1])

with col1:
    archivo = render_file_uploader(st.session_state.procesando)
    
    if archivo:
        render_file_info(archivo)
        
        # Calcular tamaño para validaciones posteriores
        tamano_mb = archivo.size / (1024 * 1024)
        
        iniciar_transcripcion = st.button(
            '🚀 Transcribir Audio',
            type='primary',
            use_container_width=True,
            disabled=modelo_disabled or st.session_state.procesando
        )
        
        if iniciar_transcripcion:
            if tamano_mb > MAX_FILE_SIZE_MB:
                st.error(f'❌ El archivo es demasiado grande. Máximo {MAX_FILE_SIZE_MB}MB.')
            elif not ffmpeg_available:
                st.error('❌ FFmpeg no está disponible. No se puede procesar el audio.')
                st.info('💡 Intenta recargar la página o contacta al administrador.')
            elif modelo_disabled:
                st.error('❌ El modelo seleccionado no está disponible. Por favor, elige "tiny" o "base".')
            else:
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
                
                # Contenedores de progreso
                progress_bar = st.progress(0)
                status_text = st.empty()
                status_detail = st.empty()
                
                # Paso 1: Cargar modelo
                status_text.info('🔄 Paso 1/3: Cargando modelo Whisper...')
                progress_bar.progress(10)
                
                tiempo_inicio = time.time()
                model = load_whisper_model(modelo_real)
                
                if model is None:
                    st.session_state.procesando = False
                    st.error('❌ No se pudo cargar el modelo.')
                    st.stop()
                
                progress_bar.progress(20)
                status_text.info('📊 Analizando audio...')
                
                # Obtener duración del audio
                duracion_audio = get_audio_duration(ruta_temp)
                
                if duracion_audio:
                    duracion_min = int(duracion_audio // 60)
                    duracion_seg = int(duracion_audio % 60)
                    
                    # Mostrar información
                    st.warning('⚠️ **Importante**: No cierres esta ventana ni recargues la página.')
                    st.info(
                        f'📊 **Duración del audio**: {duracion_min}:{duracion_seg:02d} | '
                        f'**Modelo**: {modelo_real} | '
                        f'**Tamaño**: {tamano_mb:.1f} MB'
                    )
                    
                    # Crear tracker de progreso
                    progress_tracker = ProgressTracker(duracion_audio)
                else:
                    st.warning('⚠️ **Importante**: No cierres esta ventana ni recargues la página.')
                    st.info(f'📊 **Modelo**: {modelo_real} | **Tamaño**: {tamano_mb:.1f} MB')
                    progress_tracker = None
                
                progress_bar.progress(30)
                status_text.info('🎵 Paso 2/3: Transcribiendo audio...')
                
                # Contenedor fijo para logs de Whisper
                st.markdown('##### 📋 Logs de Whisper')
                logs_container = st.empty()
                
                # Configurar transcripción en background
                resultado_container = {'resultado': None, 'error': None, 'completado': False}
                
                def transcribe_thread():
                    try:
                        resultado_container['resultado'] = transcribe_audio(
                            model, ruta_temp, idioma, progress_tracker
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
                
                while not resultado_container['completado']:
                    tiempo_transcurrido = time.time() - tiempo_transcripcion_inicio
                    
                    # Usar progreso real si está disponible
                    if progress_tracker and progress_tracker.porcentaje > 0:
                        progreso_porcentaje = progress_tracker.porcentaje
                        progreso_barra = 30 + int(progreso_porcentaje * 0.6)
                        progress_bar.progress(min(progreso_barra, 90))
                        
                        # Calcular tiempo restante basado en velocidad real
                        if progreso_porcentaje > 5:
                            tiempo_por_porcentaje = tiempo_transcurrido / progreso_porcentaje
                            tiempo_restante_est = tiempo_por_porcentaje * (100 - progreso_porcentaje)
                        else:
                            tiempo_restante_est = 0
                        
                        minutos_trans = int(tiempo_transcurrido // 60)
                        segundos_trans = int(tiempo_transcurrido % 60)
                        minutos_rest = int(tiempo_restante_est // 60)
                        segundos_rest = int(tiempo_restante_est % 60)
                        
                        # Formatear duración total
                        duracion_min = int(duracion_audio // 60)
                        duracion_seg = int(duracion_audio % 60)
                        
                        status_detail.success(
                            f'🎵 **Progreso: {progreso_porcentaje}%** | '
                            f'Procesado: {progress_tracker.tiempo_procesado_formateado} / {duracion_min}:{duracion_seg:02d}\n\n'
                            f'⏱️ Tiempo transcurrido: {minutos_trans}:{segundos_trans:02d} | '
                            f'Restante: ~{minutos_rest}:{segundos_rest:02d}'
                        )
                        
                        # Mostrar los últimos logs de Whisper (últimos 8)
                        if progress_tracker.buffer:
                            recent_logs = progress_tracker.buffer[-8:]
                            logs_text = '\n'.join(recent_logs)
                            logs_container.code(logs_text, language=None)
                    else:
                        # Aún no hay progreso real, solo mostrar tiempo transcurrido
                        minutos_trans = int(tiempo_transcurrido // 60)
                        segundos_trans = int(tiempo_transcurrido % 60)
                        
                        progress_bar.progress(35)
                        status_detail.info(
                            f'⏱️ Iniciando transcripción... Tiempo transcurrido: {minutos_trans}:{segundos_trans:02d}'
                        )
                        
                        # Mostrar logs iniciales si hay
                        if progress_tracker and progress_tracker.buffer:
                            logs_text = '\n'.join(progress_tracker.buffer[-5:])
                            logs_container.code(logs_text, language=None)
                    
                    time.sleep(1)  # Actualizar cada segundo
                
                thread.join()
                
                # Verificar si hubo error
                if resultado_container['error']:
                    st.session_state.procesando = False
                    st.error(f'❌ Error durante la transcripción: {resultado_container["error"]}')
                    st.stop()
                
                resultado = resultado_container['resultado']
                
                # Paso 3: Preparar resultado
                progress_bar.progress(95)
                status_text.info('📝 Paso 3/3: Preparando resultados...')
                
                texto_completo = resultado.get('text', '')
                segmentos = resultado.get('segments', [])
                idioma_detectado = resultado.get('language', 'desconocido')
                
                # Generar archivos para descargar
                txt_content = export_txt(texto_completo, segmentos)
                docx_bytes = export_docx(texto_completo, segmentos)
                
                progress_bar.progress(100)
                status_text.success('✅ ¡Transcripción completada!')
                status_detail.empty()
                
                tiempo_total = time.time() - tiempo_inicio
                st.success(f'🎉 Completado en {tiempo_total/60:.1f} minutos')
                
                # Mostrar resultados
                st.markdown('---')
                st.subheader('📄 Resultado')
                st.info(f'**Idioma detectado**: {idioma_detectado}')
                
                with st.expander('📝 Ver transcripción completa', expanded=True):
                    st.text_area(
                        'Texto transcrito',
                        texto_completo,
                        height=300,
                        label_visibility='collapsed'
                    )
                
                # Botones de descarga
                col_down1, col_down2 = st.columns(2)
                with col_down1:
                    st.download_button(
                        label='📥 Descargar TXT',
                        data=txt_content,
                        file_name=f'transcripcion_{archivo.name}.txt',
                        mime='text/plain',
                        use_container_width=True
                    )
                with col_down2:
                    st.download_button(
                        label='📥 Descargar DOCX',
                        data=docx_bytes,
                        file_name=f'transcripcion_{archivo.name}.docx',
                        mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                        use_container_width=True
                    )
                
                # Resetear estado
                st.session_state.procesando = False
                
            except Exception as e:
                st.session_state.procesando = False
                st.error(f'❌ Error: {str(e)}')
            finally:
                # Limpiar archivo temporal
                try:
                    os.unlink(ruta_temp)
                except:
                    pass

with col2:
    render_info_panel()

# Footer
st.markdown('---')
st.markdown(
    '<div style="text-align: center; color: #666;">'
    'Desarrollado con ❤️ usando OpenAI Whisper y Streamlit'
    '</div>',
    unsafe_allow_html=True
)
