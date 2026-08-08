import yt_dlp
import os
import sys
from base_datos_py import guardar_cancion

if getattr(sys, 'frozen', False):
    # Si es un .exe, busca la ruta donde está guardado ese .exe
    DIRECTORIO_BASE = os.path.dirname(sys.executable)
else:
    # Si es el script de PyCharm, usa la ruta normal
    DIRECTORIO_BASE = os.path.dirname(os.path.abspath(__file__))

RUTA_FFMPEG = os.path.join(DIRECTORIO_BASE, "ffmpeg.exe")

def descargar_audio(url, genero):
    """Descarga el audio de YouTube, lo guarda como MP3 y registra el dato en el JSON."""
    opciones = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': False,
        'ffmpeg_location': RUTA_FFMPEG
    }

    print("Iniciando descarga... por favor espera.")
    try:
        with yt_dlp.YoutubeDL(opciones) as ydl:
            info = ydl.extract_info(url, download=True)
            titulo = info.get('title', 'Cancion_Desconocida')
            guardar_cancion(titulo, genero)

            print(f"¡Éxito! Se descargó: {titulo}")
            return f"{titulo}.mp3"

    except Exception as error:
        print(f"Ocurrió un error al descargar: {error}")
        return None