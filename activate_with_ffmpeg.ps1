
# Activar entorno virtual
& "C:\Users\marti\Desktop\transcript_whisper\venv\Scripts\Activate.ps1"

# Agregar FFmpeg al PATH
$env:PATH = "C:\Users\marti\Desktop\transcript_whisper\ffmpeg;$env:PATH"

Write-Host "Entorno virtual activado con FFmpeg configurado" -ForegroundColor Green
