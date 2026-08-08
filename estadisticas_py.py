import matplotlib.pyplot as plt
from tkinter import messagebox  # Necesario para las ventanas de alerta
from base_datos_py import cargar_historial


def mostrar_grafico_generos():
    """Lee el JSON, cuenta los géneros y muestra un gráfico circular."""
    try:
        historial = cargar_historial()

        # Cambiamos el print por una ventana emergente de Tkinter
        if not historial:
            messagebox.showinfo("Sin Datos", "Aún no has descargado ninguna canción. No hay datos para graficar.")
            return

        # Contar los géneros
        conteo_generos = {}
        for cancion in historial:
            # Usamos .get() por si alguna canción antigua no tiene la clave "genero"
            genero = cancion.get("genero", "Desconocido")
            if genero in conteo_generos:
                conteo_generos[genero] += 1
            else:
                conteo_generos[genero] = 1

        # Separar los datos para Matplotlib
        etiquetas = list(conteo_generos.keys())
        valores = list(conteo_generos.values())

        # Crear el diseño del gráfico circular
        plt.figure(figsize=(6, 6))

        # Tu estilo original

        plt.pie(valores, labels=etiquetas, autopct="%1.1f%%", startangle=90, colors=plt.cm.Paired.colors)
        plt.title("Tus Géneros Más Descargados")

        # Mostrar la ventana en pantalla
        plt.show()

    except Exception as e:
        # Si algo falla en la base de datos o al graficar saldra esta ventana
        messagebox.showerror("Error en Estadísticas", f"No se pudo generar el gráfico. Detalle del error:\n{e}")