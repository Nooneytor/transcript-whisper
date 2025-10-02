"""
Funciones para la transcripción de audio con Whisper.
"""
import whisper
import streamlit as st


class ProgressTracker:
    """Rastrea el progreso de la transcripción basándose en timestamps"""
    def __init__(self, duracion_total):
        self.duracion_total = duracion_total
        self.ultimo_timestamp = 0
        self.porcentaje = 0
    
    def update(self, segments):
        """Actualiza el progreso basándose en los segmentos procesados"""
        if segments and len(segments) > 0:
            # Obtener el último segmento procesado
            ultimo_segmento = segments[-1]
            # El timestamp 'end' indica hasta dónde se ha procesado
            self.ultimo_timestamp = ultimo_segmento.get('end', 0)
            
            # Calcular porcentaje
            if self.duracion_total > 0:
                self.porcentaje = min(100, int((self.ultimo_timestamp / self.duracion_total) * 100))


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
        'verbose': False,  # Desactivar verbose
    }
    
    if language and language != 'auto':
        transcribe_kwargs['language'] = language
    
    # Si hay progress_tracker, hacemos transcripción iterativa
    if progress_tracker:
        # Cargar audio
        audio = whisper.load_audio(audio_path)
        audio = whisper.pad_or_trim(audio)
        
        # Detectar idioma si es necesario
        mel = whisper.log_mel_spectrogram(audio).to(model.device)
        
        if language is None or language == 'auto':
            _, probs = model.detect_language(mel)
            detected_lang = max(probs, key=probs.get)
            transcribe_kwargs['language'] = detected_lang
        
        # Transcribir con progreso
        result = model.transcribe(audio_path, **transcribe_kwargs)
        
        # Actualizar progreso al final
        if 'segments' in result:
            progress_tracker.update(result['segments'])
        
        return result
    else:
        # Transcripción simple sin seguimiento
        return model.transcribe(audio_path, **transcribe_kwargs)

