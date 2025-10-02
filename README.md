# Transcriptor de Audio con OpenAI Whisper

Este proyecto te permite transcribir archivos de audio a texto usando OpenAI Whisper.

## Instalación

### 1. Activar el entorno virtual

**En Windows (PowerShell):**
```powershell
venv\Scripts\activate
```

**En Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**En macOS/Linux:**
```bash
source venv/bin/activate
```

### 2. Verificar instalación

```bash
pip list
```

Deberías ver `openai-whisper` en la lista de paquetes instalados.

## Uso

### Uso básico
```bash
python transcripcion.py archivo_audio.wav
```

### Opciones avanzadas
```bash
# Usar un modelo más preciso
python transcripcion.py archivo_audio.mp3 -m small

# Especificar idioma (inglés en este caso)
python transcripcion.py audio.wav -m base -i en

# Especificar archivo de salida
python transcripcion.py audio.mp3 -o mi_transcripcion.txt
```

### Modelos disponibles

| Modelo | Tamaño | Velocidad | Precisión | Uso recomendado |
|--------|--------|-----------|-----------|-----------------|
| `tiny` | ~39 MB | Muy rápido | Básica | Pruebas rápidas |
| `base` | ~74 MB | Rápido | Buena | **Recomendado para uso general** |
| `small` | ~244 MB | Moderado | Mejor | Audio de calidad media |
| `medium` | ~769 MB | Lento | Muy buena | Audio profesional |
| `large` | ~1550 MB | Muy lento | Excelente | Máxima precisión |

## Formatos de audio soportados

- **Comunes:** MP3, WAV, M4A, FLAC
- **Otros:** OGG, MP4, WEBM, MKV, y muchos más

## Ejemplos de uso

### Transcribir un podcast
```bash
python transcripcion.py podcast.mp3 -m base -i es
```

### Transcribir una conferencia en inglés
```bash
python transcripcion.py conferencia.wav -m small -i en
```

### Transcripción de alta calidad
```bash
python transcripcion.py entrevista.m4a -m large -i es
```

## Archivos de salida

El script genera automáticamente un archivo `.txt` con:
- **Transcripción completa**: Todo el texto transcrito
- **Segmentos con timestamps**: Cada frase con su tiempo de inicio y fin
- **Información adicional**: Idioma detectado, número de segmentos, etc.

## Comandos útiles

### Desactivar el entorno virtual
```bash
deactivate
```

### Reinstalar dependencias
```bash
pip install -r requirements.txt
```

### Actualizar Whisper
```bash
pip install --upgrade openai-whisper
```

## Solución de problemas

### Error: "No module named 'whisper'"
Asegúrate de que el entorno virtual esté activado:
```bash
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

### Error de memoria
Si tienes problemas de memoria, usa un modelo más pequeño:
```bash
python transcripcion.py archivo.wav -m tiny
```

### Audio muy largo
Para archivos muy largos, Whisper los procesará automáticamente en segmentos.

## Notas

- **Primera ejecución**: La primera vez que uses un modelo, se descargará automáticamente
- **Rendimiento**: Los modelos más grandes requieren más RAM y tiempo de procesamiento
- **GPU**: Si tienes una GPU compatible, Whisper la usará automáticamente para acelerar el proceso
- **Idiomas**: Whisper soporta más de 90 idiomas diferentes

¡Listo para transcribir tus archivos de audio! 🎤→📝
