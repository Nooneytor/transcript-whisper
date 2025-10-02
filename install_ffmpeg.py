#!/usr/bin/env python3
"""
Script para descargar e instalar FFmpeg automáticamente en Windows
"""
import os
import sys
import urllib.request
import zipfile
import shutil
from pathlib import Path

def download_ffmpeg():
    """Descarga e instala FFmpeg en el directorio local"""
    
    # URL de descarga de FFmpeg (versión essentials)
    ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    
    print("Descargando FFmpeg...")
    print("Esto puede tardar unos minutos...")
    
    try:
        # Descargar FFmpeg
        urllib.request.urlretrieve(ffmpeg_url, "ffmpeg.zip")
        print("FFmpeg descargado exitosamente")
        
        # Extraer el archivo
        print("Extrayendo archivos...")
        with zipfile.ZipFile("ffmpeg.zip", 'r') as zip_ref:
            zip_ref.extractall(".")
        
        # Buscar la carpeta extraída
        ffmpeg_dirs = [d for d in os.listdir(".") if d.startswith("ffmpeg-") and os.path.isdir(d)]
        if not ffmpeg_dirs:
            print("Error: No se encontró la carpeta de FFmpeg")
            return False
            
        ffmpeg_dir = ffmpeg_dirs[0]
        
        # Crear carpeta ffmpeg en nuestro proyecto
        if os.path.exists("ffmpeg"):
            shutil.rmtree("ffmpeg")
        os.makedirs("ffmpeg")
        
        # Copiar los ejecutables necesarios
        bin_dir = os.path.join(ffmpeg_dir, "bin")
        for exe in ["ffmpeg.exe", "ffprobe.exe"]:
            src = os.path.join(bin_dir, exe)
            dst = os.path.join("ffmpeg", exe)
            if os.path.exists(src):
                shutil.copy2(src, dst)
                print(f"Copiado: {exe}")
        
        # Limpiar archivos temporales
        os.remove("ffmpeg.zip")
        shutil.rmtree(ffmpeg_dir)
        
        # Agregar ffmpeg al PATH del entorno virtual
        add_to_path()
        
        print("\n✅ FFmpeg instalado correctamente!")
        print("Ahora puedes usar Whisper para transcribir archivos de audio.")
        
        return True
        
    except Exception as e:
        print(f"Error durante la instalación: {e}")
        return False

def add_to_path():
    """Agregar ffmpeg al PATH creando un script de activación personalizado"""
    
    # Ruta absoluta al directorio de ffmpeg
    ffmpeg_path = os.path.abspath("ffmpeg")
    
    # Crear script de activación personalizado
    activate_script = f'''
# Activar entorno virtual
& "{os.path.abspath('venv/Scripts/Activate.ps1')}"

# Agregar FFmpeg al PATH
$env:PATH = "{ffmpeg_path};$env:PATH"

Write-Host "Entorno virtual activado con FFmpeg configurado" -ForegroundColor Green
'''
    
    with open("activate_with_ffmpeg.ps1", "w", encoding="utf-8") as f:
        f.write(activate_script)
    
    print(f"Creado: activate_with_ffmpeg.ps1")
    print("Para activar el entorno con FFmpeg, usa:")
    print("  PowerShell -ExecutionPolicy Bypass -File activate_with_ffmpeg.ps1")

if __name__ == "__main__":
    print("=== INSTALADOR DE FFMPEG PARA WHISPER ===")
    print()
    
    if download_ffmpeg():
        print("\n=== INSTALACIÓN COMPLETADA ===")
        print()
        print("Comandos para probar:")
        print('  PowerShell -ExecutionPolicy Bypass -File activate_with_ffmpeg.ps1')
        print('  whisper "audios\\Squirrel_Bolsa_Madrid_Abril_2025_SD.mp3" --language Spanish --model base')
    else:
        print("\n❌ Error en la instalación")
        sys.exit(1)
