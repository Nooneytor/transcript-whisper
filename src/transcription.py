"""
Funciones para la transcripción de audio con Whisper.
"""
import whisper
import streamlit as st
import sys
import re


class ProgressCapture:
    """Captura los logs de progreso de Whisper desde stdout y stderr"""
    def __init__(self):
        self.logs = []
        self.todos_los_logs = []  # Guardar TODOS los logs
        self.porcentaje = 0
        self.ultimo_log = ''
        self.ultimo_timestamp = ''
        
    def write(self, text):
        if text.strip():
            text_clean = text.strip()
            
            # Guardar TODO
            self.todos_los_logs.append(text_clean)
            
            # Detectar timestamp de Whisper [HH:MM:SS.mmm --> HH:MM:SS.mmm]
            match_timestamp = re.search(r'\[(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})\]', text_clean)
            
            if match_timestamp:
                # Es un segmento con timestamp - guardarlo siempre
                self.ultimo_timestamp = match_timestamp.group(1)
                self.ultimo_log = text_clean
                self.logs.append(text_clean)
                
                # Estimar progreso basado en timestamps
                # Extraer el tiempo final del segmento
                try:
                    end_time = match_timestamp.group(2)
                    # Convertir a segundos
                    h, m, s = end_time.split(':')
                    seconds = int(h) * 3600 + int(m) * 60 + float(s)
                    # Asumir que el audio es el tamaño aproximado y calcular %
                    # (esto es una estimación, se refinará con el tiempo total)
                    self.porcentaje = min(95, int(seconds / 10))  # Estimación temporal
                except:
                    pass
            else:
                # Buscar otros patrones
                # Patrón 1: XX% o XX%|
                match_percent = re.search(r'(\d+)%', text_clean)
                # Patrón 2: [XX/YY] (segmentos)
                match_segments = re.search(r'\[(\d+)/(\d+)\]', text_clean)
                # Patrón 3: Palabras clave
                keywords = ['Detecting language', 'Processing', 'segment', 'transcrib', 'decoding', 'loaded', 'model']
                
                if match_percent:
                    self.porcentaje = int(match_percent.group(1))
                    self.ultimo_log = text_clean
                    self.logs.append(text_clean)
                elif match_segments:
                    current = int(match_segments.group(1))
                    total = int(match_segments.group(2))
                    self.porcentaje = int((current / total) * 100)
                    self.ultimo_log = text_clean
                    self.logs.append(text_clean)
                elif any(keyword.lower() in text_clean.lower() for keyword in keywords):
                    # Log importante
                    self.ultimo_log = text_clean
                    self.logs.append(text_clean)
    
    def flush(self):
        pass
    
    def get_recent_logs(self, n=5):
        """Obtiene los últimos N logs"""
        return self.logs[-n:] if self.logs else []


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
    
    # Redirigir STDOUT Y STDERR si se proporciona progress_capture
    if progress_capture:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        # Redirigir ambos a progress_capture
        sys.stdout = progress_capture
        sys.stderr = progress_capture
        
        try:
            resultado = model.transcribe(audio_path, **transcribe_kwargs)
            # Restaurar streams
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            return resultado
        except Exception as e:
            # Asegurar restauración en caso de error
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            raise e
    else:
        return model.transcribe(audio_path, **transcribe_kwargs)

