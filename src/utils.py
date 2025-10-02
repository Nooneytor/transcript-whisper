"""
Utilidades generales para la aplicación.
"""
import os
import subprocess
import sys
import json


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


def calcular_tiempo_estimado(duracion_audio_segundos, modelo, config):
    """
    Calcula el tiempo estimado de transcripción basándose en la duración del audio.
    
    Args:
        duracion_audio_segundos: Duración del audio en segundos
        modelo: Nombre del modelo ('tiny', 'base', 'small')
        config: Diccionario de configuración de modelos
    
    Returns:
        float: Tiempo estimado en minutos
    """
    if duracion_audio_segundos is None:
        # Fallback: asumir 10 minutos si no se puede obtener duración
        return 10.0
    
    # Convertir a minutos
    duracion_minutos = duracion_audio_segundos / 60
    
    # Obtener factor de velocidad del modelo
    if modelo in config and 'factor_velocidad' in config[modelo]:
        factor = config[modelo]['factor_velocidad']
    else:
        factor = 1.5  # Factor por defecto
    
    # Tiempo estimado = duración del audio × factor del modelo
    tiempo_estimado = duracion_minutos * factor
    
    return max(1.0, tiempo_estimado)  # Mínimo 1 minuto


def get_audio_duration(audio_path):
    """
    Obtiene la duración de un archivo de audio en segundos usando FFprobe.
    
    Args:
        audio_path (str): Ruta al archivo de audio
    
    Returns:
        float: Duración en segundos, o None si falla
    """
    try:
        # Intentar con ffprobe del sistema
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            audio_path
        ]
        
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
            timeout=10
        )
        
        data = json.loads(result.stdout)
        duration = float(data['format']['duration'])
        return duration
        
    except Exception:
        # Intentar con ffprobe local
        try:
            local_ffprobe = os.path.join(os.getcwd(), 'ffmpeg', 'ffprobe.exe')
            if os.path.exists(local_ffprobe):
                cmd[0] = local_ffprobe
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True,
                    timeout=10
                )
                data = json.loads(result.stdout)
                duration = float(data['format']['duration'])
                return duration
        except Exception:
            pass
        
        return None

