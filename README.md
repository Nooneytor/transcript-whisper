---
title: Transcriptor Whisper
emoji: 🎙️
colorFrom: red
colorTo: pink
sdk: streamlit
sdk_version: "1.50.0"
app_file: app.py
pinned: false
license: mit
---

# 🎙️ Transcriptor de Audio con OpenAI Whisper

Aplicación web para transcribir archivos de audio a texto usando OpenAI Whisper con una interfaz moderna y fácil de usar.

## ✨ Características

- **Interfaz intuitiva**: Sube archivos, selecciona modelo/idioma, transcribe y descarga
- **Múltiples formatos**: MP3, WAV, M4A, FLAC, OGG, MP4, WEBM, MKV
- **Exportación flexible**: TXT y DOCX con timestamps
- **Modelos optimizados**: tiny, base (small no disponible en CPU gratuita)
- **Progreso en tiempo real**: Barra de progreso con logs de Whisper
- **UI bloqueada durante procesamiento**: Evita cambios accidentales

## 🚀 Despliegue

### Hugging Face Spaces (Recomendado)
Esta aplicación está optimizada para Hugging Face Spaces:

- **CPU gratuita**: Funciona con modelos tiny y base
- **GPU T4 (opcional)**: Para procesamiento más rápido

URL: [https://huggingface.co/spaces/MartinNoone/transcript-whisper](https://huggingface.co/spaces/MartinNoone/transcript-whisper)

### Local

```bash
# Activar entorno virtual
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
streamlit run app.py
```

## 📁 Estructura del Proyecto

```
transcript_whisper/
├── app.py                      # Aplicación principal de Streamlit
├── src/                        # Módulos de la aplicación
│   ├── __init__.py
│   ├── config.py              # Configuración (modelos, idiomas, límites)
│   ├── utils.py               # Utilidades (ffmpeg, tiempo, etc.)
│   ├── export.py              # Exportación a TXT/DOCX
│   ├── transcription.py       # Lógica de transcripción con Whisper
│   └── ui_components.py       # Componentes de UI reutilizables
├── requirements.txt           # Dependencias Python
├── packages.txt              # Dependencias del sistema (ffmpeg)
├── runtime.txt               # Versión de Python
└── README.md                 # Este archivo
```

## 🎯 Uso

1. **Sube tu archivo de audio** (< 200MB, recomendado < 50MB)
2. **Selecciona el modelo**:
   - `tiny`: Rápido, precisión básica
   - `base`: Balance perfecto (recomendado)
   - `small`: ⚠️ No disponible en CPU gratuita
3. **Selecciona el idioma** o deja en "auto"
4. **Haz clic en "Transcribir Audio"**
5. **Espera** a que complete (puede tardar varios minutos)
6. **Descarga** el resultado en TXT o DOCX

## ⏱️ Rendimiento Esperado

### CPU gratuita
| Tamaño | Modelo | Tiempo aproximado |
|--------|--------|-------------------|
| 10 MB | tiny | 5 min |
| 10 MB | base | 12 min |
| 50 MB | tiny | 25 min |
| 50 MB | base | 60 min |

### GPU T4
| Tamaño | Modelo | Tiempo aproximado |
|--------|--------|-------------------|
| 10 MB | base | 1-2 min |
| 50 MB | base | 3-6 min |
| 200 MB | base | 10-15 min |

## 🛠️ Tecnologías

- **Streamlit**: Framework de UI
- **OpenAI Whisper**: Motor de transcripción
- **python-docx**: Exportación a Word
- **FFmpeg**: Procesamiento de audio

## 📝 Licencia

MIT License - Ver archivo LICENSE para más detalles

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o pull request.

## 📧 Contacto

- **GitHub**: [Nooneytor/transcript-whisper](https://github.com/Nooneytor/transcript-whisper)
- **Hugging Face**: [MartinNoone/transcript-whisper](https://huggingface.co/spaces/MartinNoone/transcript-whisper)

---

Desarrollado con ❤️ usando Streamlit y OpenAI Whisper
