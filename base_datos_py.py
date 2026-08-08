import json
import os
import sys
if getattr(sys, 'frozen', False):
    DIRECTORIO_BASE = os.path.dirname(sys.executable)
else:
    DIRECTORIO_BASE = os.path.dirname(os.path.abspath(__file__))

ARCHIVO_JSON = os.path.join(DIRECTORIO_BASE, "historial_canciones.json")

def cargar_historial():
    """Lee el archivo JSON y devuelve la lista de canciones."""
    if not os.path.exists(ARCHIVO_JSON):
        return []

    with open(ARCHIVO_JSON, 'r', encoding='utf-8') as archivo:
        return json.load(archivo)

def guardar_cancion(titulo, genero):
    """Añade una nueva canción al archivo JSON."""
    historial = cargar_historial()
    historial.append({
        "titulo": titulo,
        "genero": genero
    })

    with open(ARCHIVO_JSON, 'w', encoding='utf-8') as archivo:
        json.dump(historial, archivo, indent=4)