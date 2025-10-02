"""
Funciones para la transcripción de audio con Whisper.
"""
import whisper
import streamlit as st
import sys
import re
import io


class ProgressTracker:
    """Rastrea el progreso de la transcripción en tiempo real capturando logs de Whisper"""
    def __init__(self, duracion_total):
        self.duracion_total = duracion_total
        self.ultimo_timestamp = 0
        self.porcentaje = 0
        self.tiempo_procesado_formateado = "0:00"
        self.buffer = []
    
    def write(self, text):
        """Captura salida de stderr/stdout de Whisper"""
        if text.strip():
            self.buffer.append(text)
            
            # Buscar porcentajes en el formato de Whisper: "XX%"
            match_percent = re.search(r'(\d+)%', text)
            if match_percent:
                self.porcentaje = int(match_percent.group(1))
                
                # Si tenemos duración total, calcular timestamp procesado
                if self.duracion_total > 0:
                    timestamp_segundos = (self.porcentaje / 100) * self.duracion_total
                    self.ultimo_timestamp = timestamp_segundos
                    minutos = int(timestamp_segundos // 60)
                    segundos = int(timestamp_segundos % 60)
                    self.tiempo_procesado_formateado = f"{minutos}:{segundos:02d}"
    
    def flush(self):
        """Requerido por la interfaz de streams"""
        pass
    
    def update_from_timestamp(self, timestamp_segundos):
        """Actualiza el progreso basándose en el timestamp procesado"""
        self.ultimo_timestamp = timestamp_segundos
        
        # Calcular porcentaje
        if self.duracion_total > 0:
            self.porcentaje = min(100, int((timestamp_segundos / self.duracion_total) * 100))
        
        # Formatear tiempo procesado
        minutos = int(timestamp_segundos // 60)
        segundos = int(timestamp_segundos % 60)
        self.tiempo_procesado_formateado = f"{minutos}:{segundos:02d}"


@st.cache_resource
def load_whisper_model(model_name):
    """Carga el modelo de Whisper y lo mantiene en caché"""
    try:
        return whisper.load_model(model_name)
    except Exception as e:
        st.error(f"Error al cargar el modelo: {e}")
        return None


def transcribe_audio(model, audio_path, language=None, progress_tracker=None):
    """
    Transcribe un archivo de audio usando Whisper.
    
    Args:
        model: Modelo de Whisper cargado
        audio_path (str): Ruta al archivo de audio
        language (str): Idioma (None para auto-detección)
        progress_tracker: Objeto ProgressTracker para actualizar progreso (opcional)
    
    Returns:
        dict: Resultado de la transcripción
    """
    transcribe_kwargs = {
        'fp16': False,  # Forzar FP32 en CPU
        'verbose': True,  # ACTIVAR para capturar porcentajes
    }
    
    if language and language != 'auto':
        transcribe_kwargs['language'] = language
    
    # Si hay progress_tracker, redirigir stderr para capturar progreso
    if progress_tracker:
        # Guardar stderr original
        old_stderr = sys.stderr
        
        try:
            # Redirigir stderr al progress_tracker
            sys.stderr = progress_tracker
            
            # Transcribir (los logs de progreso irán a progress_tracker)
            result = model.transcribe(audio_path, **transcribe_kwargs)
            
            # Restaurar stderr
            sys.stderr = old_stderr
            
            return result
        except Exception as e:
            # Asegurar que stderr se restaura incluso si hay error
            sys.stderr = old_stderr
            raise e
    else:
        # Transcripción simple sin seguimiento
        return model.transcribe(audio_path, **transcribe_kwargs)

