"""
Funciones para la transcripción de audio con Whisper.
"""
import whisper
import streamlit as st
import sys
import re


class ProgressCapture:
    """Captura los logs de progreso de Whisper"""
    def __init__(self):
        self.logs = []
        self.porcentaje = 0
        self.ultimo_log = ''
        
    def write(self, text):
        if text.strip():
            self.logs.append(text)
            # Buscar porcentajes en los logs (formato: XX%)
            match = re.search(r'(\d+)%', text)
            if match:
                self.porcentaje = int(match.group(1))
                self.ultimo_log = text.strip()
    
    def flush(self):
        pass


@st.cache_resource
def load_whisper_model(model_name):
    """Carga el modelo de Whisper y lo mantiene en caché"""
    try:
        return whisper.load_model(model_name)
    except Exception as e:
        st.error(f"Error al cargar el modelo: {e}")
        return None


def transcribe_audio(model, audio_path, language=None, progress_capture=None):
    """
    Transcribe un archivo de audio usando Whisper.
    
    Args:
        model: Modelo de Whisper cargado
        audio_path (str): Ruta al archivo de audio
        language (str): Idioma (None para auto-detección)
        progress_capture: Objeto para capturar progreso
    
    Returns:
        dict: Resultado de la transcripción
    """
    transcribe_kwargs = {
        'fp16': False,  # Forzar FP32 en CPU
        'verbose': True,  # Activar para capturar progreso
    }
    
    if language and language != 'auto':
        transcribe_kwargs['language'] = language
    
    # Redirigir stderr si se proporciona progress_capture
    if progress_capture:
        old_stderr = sys.stderr
        sys.stderr = progress_capture
        try:
            resultado = model.transcribe(audio_path, **transcribe_kwargs)
            sys.stderr = old_stderr
            return resultado
        except Exception as e:
            sys.stderr = old_stderr
            raise e
    else:
        return model.transcribe(audio_path, **transcribe_kwargs)

