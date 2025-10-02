"""
Configuración de la aplicación.
"""

# Modelos disponibles
MODELOS_DISPONIBLES = {
    'tiny': {
        'nombre': 'Tiny',
        'tamaño': '~39 MB',
        'velocidad': 'Muy rápido',
        'precision': 'Básica',
        'tiempo_por_mb': 0.5,  # minutos por MB
        'disponible': True
    },
    'base': {
        'nombre': 'Base',
        'tamaño': '~74 MB',
        'velocidad': 'Rápido',
        'precision': 'Buena',
        'tiempo_por_mb': 1.2,
        'disponible': True
    },
    'small': {
        'nombre': 'Small',
        'tamaño': '~244 MB',
        'velocidad': 'Lento',
        'precision': 'Muy buena',
        'tiempo_por_mb': 2.5,
        'disponible': False,  # No disponible en CPU gratuita
        'razon_deshabilitado': 'Requiere demasiados recursos para CPU gratuita'
    }
}

# Idiomas soportados
IDIOMAS = {
    'auto': 'Detección automática',
    'es': 'Español',
    'en': 'English',
    'fr': 'Français',
    'pt': 'Português',
    'it': 'Italiano',
    'de': 'Deutsch'
}

# Formatos de audio soportados
FORMATOS_AUDIO = ['mp3', 'wav', 'm4a', 'flac', 'ogg', 'mp4', 'webm', 'mkv']

# Límites
MAX_FILE_SIZE_MB = 200
RECOMMENDED_FILE_SIZE_MB = 50

# UI
APP_TITLE = '🎙️ Transcriptor de Audio con Whisper'
APP_ICON = '🎙️'

