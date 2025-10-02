# 🎙️ Transcriptor de Audio con OpenAI Whisper

Este proyecto te permite transcribir archivos de audio a texto usando OpenAI Whisper, tanto como script de línea de comandos como aplicación web con Streamlit.

## 🚀 Aplicación Web (Streamlit)

### Características de la App Web
- **Interfaz intuitiva**: Sube archivos, selecciona modelo/idioma, transcribe y descarga
- **Formatos soportados**: MP3, WAV, M4A, FLAC, OGG, MP4, WEBM, MKV
- **Exportación múltiple**: TXT y DOCX con timestamps
- **Modelos optimizados**: tiny, base, small (equilibrio velocidad/precisión)
- **Límite de archivo**: Hasta 200MB

### Ejecutar localmente
```bash
# Activar entorno virtual
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
streamlit run app.py
```

La aplicación se abrirá en `http://localhost:8501`

## 🌐 Despliegue en la Nube

### Opción 1: Streamlit Community Cloud (CPU - Recomendado)
1. **Subir a GitHub**: Haz push de este repositorio a GitHub
2. **Conectar a Streamlit Cloud**: 
   - Ve a [share.streamlit.io](https://share.streamlit.io)
   - Conecta tu repositorio de GitHub
   - Selecciona `app.py` como archivo principal
   - Despliega

**Ventajas**: Gratuito, fácil configuración, CPU suficiente para modelo `base`

### Opción 2: Hugging Face Spaces (GPU opcional)
1. **Crear Space**: En [huggingface.co/spaces](https://huggingface.co/spaces)
2. **Configurar**: 
   - Tipo: Streamlit
   - Hardware: CPU (gratuito) o GPU T4 (pago)
   - Conectar repositorio
3. **Desplegar**: El mismo código funciona en ambas plataformas

**Ventajas**: GPU disponible para transcripciones más rápidas

## 📝 Script de Línea de Comandos

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

## 🤖 Modelos disponibles

| Modelo | Tamaño | Velocidad | Precisión | Uso recomendado |
|--------|--------|-----------|-----------|-----------------|
| `tiny` | ~39 MB | Muy rápido | Básica | Pruebas rápidas |
| `base` | ~74 MB | Rápido | Buena | **Recomendado para uso general** |
| `small` | ~244 MB | Moderado | Mejor | Audio de calidad media |
| `medium` | ~769 MB | Lento | Muy buena | Audio profesional |
| `large` | ~1550 MB | Muy lento | Excelente | Máxima precisión |

## 📁 Formatos de audio soportados

- **Comunes:** MP3, WAV, M4A, FLAC
- **Otros:** OGG, MP4, WEBM, MKV, y muchos más

## 📊 Rendimiento esperado

### Con CPU (Streamlit Cloud)
- **Modelo base**: ~10-25 minutos para audio de 200MB
- **Modelo small**: ~15-35 minutos para audio de 200MB

### Con GPU (Hugging Face Spaces)
- **Modelo base**: ~2-6 minutos para audio de 200MB
- **Modelo small**: ~3-8 minutos para audio de 200MB

## 🛠️ Instalación local

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

Deberías ver `openai-whisper` y `streamlit` en la lista de paquetes instalados.

## 🔧 Solución de problemas

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

## 📋 Archivos del proyecto

- `app.py`: Aplicación Streamlit principal
- `transcripcion.py`: Script de línea de comandos
- `requirements.txt`: Dependencias de Python
- `packages.txt`: Dependencias del sistema (ffmpeg)
- `runtime.txt`: Versión de Python (3.11)
- `apt.txt`: Dependencias para Hugging Face Spaces

## 🌍 Idiomas soportados

Whisper soporta más de 90 idiomas diferentes. En la app web puedes seleccionar:
- **auto**: Detección automática
- **es**: Español
- **en**: Inglés
- **fr**: Francés
- **pt**: Portugués
- **it**: Italiano
- **de**: Alemán

## 📈 Próximas mejoras

- [ ] Soporte para más formatos de exportación (SRT, VTT)
- [ ] Procesamiento por lotes
- [ ] Integración con servicios de almacenamiento en la nube
- [ ] Análisis de sentimientos en las transcripciones

¡Listo para transcribir tus archivos de audio! 🎤→📝
