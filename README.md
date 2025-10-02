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

Aplicación web para transcribir archivos de audio a texto usando OpenAI Whisper.

## 🚀 Características

- **Interfaz intuitiva**: Sube archivos, selecciona modelo/idioma, transcribe y descarga
- **Formatos soportados**: MP3, WAV, M4A, FLAC, OGG, MP4, WEBM, MKV
- **Exportación múltiple**: TXT y DOCX con timestamps
- **Modelos optimizados**: tiny, base, small
- **GPU acelerada**: Transcripción rápida con GPU T4

## 🎯 Uso

1. Sube tu archivo de audio (máximo 200MB)
2. Selecciona el modelo (tiny/base/small)
3. Selecciona el idioma o deja en "auto"
4. Haz clic en "Transcribir Audio"
5. Descarga el resultado en TXT o DOCX

## ⚡ Rendimiento con GPU

| Tamaño de archivo | Tiempo aproximado |
|-------------------|-------------------|
| 10 MB | 30 seg - 1 min |
| 50 MB | 1-3 min |
| 100 MB | 2-5 min |
| 200 MB | 3-8 min |

## 📋 Repositorio

Código completo: [github.com/Nooneytor/transcript-whisper](https://github.com/Nooneytor/transcript-whisper)

