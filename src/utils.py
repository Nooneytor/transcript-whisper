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


def calcular_tiempo_estimado(tamano_mb, modelo, config):
    """Calcula el tiempo estimado de transcripción"""
    if modelo in config and 'tiempo_por_mb' in config[modelo]:
        return tamano_mb * config[modelo]['tiempo_por_mb']
    return tamano_mb * 1.0  # Default


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

