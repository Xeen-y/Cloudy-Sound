import pygame
pygame.init()
import pygame

# Inicializamos el motor de audio al cargar este archivo
pygame.mixer.init()

def reproducir(ruta_archivo):
    """Carga una canción y la empieza a reproducir."""
    try:
        pygame.mixer.music.load(ruta_archivo)
        pygame.mixer.music.play()
        print(f"Reproduciendo: {ruta_archivo}")
    except Exception as error:
        print(f"No se pudo reproducir el archivo: {error}")

def pausar():
    """Pausa la canción actual."""
    pygame.mixer.music.pause()
    print("Música pausada.")


def reanudar():
    """Quita la pausa de la canción actual"""
    pygame.mixer.music.unpause()

def detener():
    """Detiene la música por completo."""
    pygame.mixer.music.stop()
    print("Música detenida.")

def esta_reproduciendo():
    """Devuelve True si la música está sonando, False si ya terminó o está detenida."""
    return pygame.mixer.music.get_busy()