#!/usr/bin/env python3
"""
Script para transcribir archivos de audio usando OpenAI Whisper.
Crea un entorno virtual e instala dentro de él openai-whisper.

Uso:
python transcripcion.py archivo_audio.wav

o simplemente ejecutar sin argumentos para un ejemplo interactivo.
"""

import os
import sys
import whisper
import argparse

def transcribir_audio(archivo_audio, modelo="base", idioma="es"):
    """
    Transcribe un archivo de audio usando OpenAI Whisper.
    
    Args:
        archivo_audio (str): Ruta al archivo de audio
        modelo (str): Modelo de Whisper a usar (tiny, base, small, medium, large)
        idioma (str): Código del idioma (es, en, fr, etc.)
    
    Returns:
        dict: Resultado de la transcripción
    """
    
    # Verificar que el archivo existe
    if not os.path.exists(archivo_audio):
        print(f"Error: El archivo {archivo_audio} no existe.")
        return None
    
    print(f"Cargando modelo '{modelo}'...")
    try:
        model = whisper.load_model(modelo)
    except Exception as e:
        print(f"Error al cargar el modelo: {e}")
        return None
    
    print(f"Transcribiendo '{archivo_audio}'...")
    print("Esto puede tardar unos minutos dependiendo del tamaño del archivo...")
    
    try:
        resultado = model.transcribe(archivo_audio, language=idioma)
        return resultado
    except Exception as e:
        print(f"Error durante la transcripción: {e}")
        return None

def guardar_transcripcion(resultado, archivo_salida):
    """
    Guarda la transcripción en un archivo de texto.
    
    Args:
        resultado (dict): Resultado de Whisper
        archivo_salida (str): Ruta del archivo de salida
    """
    try:
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            f.write(f"=== TRANSCRIPCIÓN ===\n\n")
            f.write(resultado['text'])
            f.write("\n\n=== SEGMENTOS DETALLADOS ===\n\n")
            
            for i, segmento in enumerate(resultado['segments']):
                inicio = int(segmento['start'])
                fin = int(segmento['end'])
                texto = segmento['text']
                f.write(f"[{inicio:02d}:{inicio%60:02d} - {fin:02d}:{fin%60:02d}] {texto}\n")
        
        print(f"Transcripción guardada en: {archivo_salida}")
    except Exception as e:
        print(f"Error al guardar la transcripción: {e}")

def main():
    parser = argparse.ArgumentParser(description='Transcribir archivos de audio usando OpenAI Whisper')
    parser.add_argument('archivo', nargs='?', help='Archivo de audio a transcribir')
    parser.add_argument('-m', '--modelo', default='base', 
                       choices=['tiny', 'base', 'small', 'medium', 'large'],
                       help='Modelo de Whisper a usar (default: base)')
    parser.add_argument('-i', '--idioma', default='es', 
                       help='Código del idioma (default: es para español)')
    parser.add_argument('-o', '--salida', help='Archivo de salida (opcional)')
    
    args = parser.parse_args()
    
    if not args.archivo:
        print("=== TRANSCRIPTOR DE AUDIO CON WHISPER ===")
        print()
        print("Este script transcribe archivos de audio a texto usando OpenAI Whisper.")
        print()
        print("Uso:")
        print("  python transcripcion.py archivo_audio.wav")
        print("  python transcripcion.py archivo_audio.mp3 -m small -i en")
        print()
        print("Modelos disponibles:")
        print("  - tiny   : Más rápido, menos preciso")
        print("  - base   : Equilibrio entre velocidad y precisión (recomendado)")
        print("  - small  : Mejor precisión, un poco más lento")
        print("  - medium : Muy buena precisión")
        print("  - large  : Máxima precisión, más lento")
        print()
        print("Formatos de audio soportados:")
        print("  MP3, WAV, M4A, FLAC, OGG, MP4, y muchos más")
        print()
        return
    
    # Transcribir el archivo
    resultado = transcribir_audio(args.archivo, args.modelo, args.idioma)
    
    if resultado:
        # Mostrar la transcripción en consola
        print("\n=== TRANSCRIPCIÓN COMPLETA ===")
        print(resultado['text'])
        
        # Determinar el archivo de salida
        if args.salida:
            archivo_salida = args.salida
        else:
            nombre_base = os.path.splitext(args.archivo)[0]
            archivo_salida = f"{nombre_base}_transcripcion.txt"
        
        # Guardar la transcripción
        guardar_transcripcion(resultado, archivo_salida)
        
        print(f"\n=== INFORMACIÓN ADICIONAL ===")
        print(f"Idioma detectado: {resultado.get('language', 'No detectado')}")
        print(f"Número de segmentos: {len(resultado.get('segments', []))}")
        
        # Mostrar algunos segmentos con timestamps
        if 'segments' in resultado and resultado['segments']:
            print("\n=== PRIMEROS SEGMENTOS CON TIMESTAMPS ===")
            for i, segmento in enumerate(resultado['segments'][:5]):
                inicio = segmento['start']
                fin = segmento['end']
                texto = segmento['text']
                print(f"[{inicio:.1f}s - {fin:.1f}s] {texto}")
                
            if len(resultado['segments']) > 5:
                print(f"... y {len(resultado['segments']) - 5} segmentos más")

if __name__ == "__main__":
    main()
