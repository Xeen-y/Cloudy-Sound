import tkinter as tk
from tkinter import filedialog, messagebox
import os
from PIL import Image, ImageTk
import json

# Importamos los módulos de lógica:

from descargas_py import descargar_audio
import reproductor_py
from estadisticas_py import mostrar_grafico_generos

# Variables globales para el controlpy -m venv .venv:

carpeta_seleccionada = ""
lista_archivos_mp3 = []
indice_cancion_actual = -1
ARCHIVO_CONFIG = "config.json"
ruta_cancion_actual = ""
musica_pausada = False

def cargar_configuracion():
    if os.path.exists(ARCHIVO_CONFIG):
        try:
            with open(ARCHIVO_CONFIG, "r") as f:
                datos = json.load(f)
                return datos.get("carpeta_musica", "")
        except Exception:
            return ""
    return ""

def guardar_configuracion(ruta):
    datos = {"carpeta_musica": ruta}
    try:
        with open(ARCHIVO_CONFIG, "w") as f:
            json.dump(datos, f)
    except Exception as e:
        print(f"Error al guardar configuración: {e}")

def iniciar_interfaz():
    global carpeta_seleccionada

    root = tk.Tk()
    root.title("CloudySound Player")
    root.geometry("900x600")
    root.configure(bg="#000000")
    root.resizable(True, True)

    # FUNCIONES DE CONTROL DE ARCHIVOS Y CARPETAS:

    def seleccionar_carpeta():
        global carpeta_seleccionada
        ruta = filedialog.askdirectory(title="Selecciona la carpeta para tu música")
        if ruteo := ruta.strip():
            carpeta_seleccionada = ruteo
            lbl_ruta.config(text=os.path.basename(carpeta_seleccionada).upper())

            # Guardamos la ruta en el JSON para que el programa la recuerde mañana
            guardar_configuracion(carpeta_seleccionada)
            actualizar_lista_canciones()

    def actualizar_lista_canciones():
        global lista_archivos_mp3
        lista_visual.delete(0, tk.END)
        if not carpeta_seleccionada:
            return

        try:
            # Filtramos solo archivos .mp3 en la carpeta seleccionada
            lista_archivos_mp3 = [f for f in os.listdir(carpeta_seleccionada) if f.lower().endswith('.mp3')]
            for i, cancion in enumerate(lista_archivos_mp3, start=1):
                # Quitamos el .mp3 del nombre para que se vea más limpio
                nombre_limpio = os.path.splitext(cancion)[0]
                lista_visual.insert(tk.END, f"  {nombre_limpio}")
        except Exception as e:
            print(f"Error al leer carpeta: {e}")

    # DESPLIEGUE DINÁMICO:

    def toggle_panel_descarga():
        if frame_desplegable_descarga.winfo_manager() == "pack":
            frame_desplegable_descarga.pack_forget()
        else:
            frame_desplegable_descarga.pack(side="bottom", fill="x", before=frame_barra_control, pady=5)
            frame_desplegable_stats.pack_forget()

    def toggle_panel_stats():
        if frame_desplegable_stats.winfo_manager() == "pack":
            frame_desplegable_stats.pack_forget()
        else:
            frame_desplegable_stats.pack(side="bottom", fill="x", before=frame_barra_control, pady=5)
            frame_desplegable_descarga.pack_forget()


    # LÓGICA MULTIMEDIA Y ACCIONES:

    def ejecutar_descarga_sistema():
        global carpeta_seleccionada
        if not carpeta_seleccionada:
            messagebox.showwarning("Carpeta Requerida",
                                   "Por favor selecciona primero una carpeta en el panel izquierdo.")
            return

        url = entrada_url.get().strip()
        genero = entrada_genero.get().strip()

        if not url or url == " URL de YouTube..." or not genero or genero == " Género...":
            messagebox.showwarning("Campos Vacíos", "Rellena los campos de descarga.")
            return

        # Limpiamos el texto fantasma del género ANTES de enviarlo
        if genero == " Género..." or genero == "":
            genero = "Desconocido"

        # Cambiamos temporalmente el directorio de trabajo
        directorio_previo = os.getcwd()
        os.chdir(carpeta_seleccionada)

        lbl_estado_sistema.config(text="DESCARGANDO AUDIO...", fg="#FFFFFF")
        root.update()

        archivo_descargado = descargar_audio(url, genero)

        # Regresamos al directorio original
        os.chdir(directorio_previo)

        if archivo_descargado:
            lbl_estado_sistema.config(text="DESCARGA COMPLETADA", fg="#FFFFFF")
            entrada_url.delete(0, tk.END)
            entrada_genero.delete(0, tk.END)
            frame_desplegable_descarga.pack_forget()  # Ocultar barra al terminar
            actualizar_lista_canciones()  # Refresca la lista automáticamente
        else:
            lbl_estado_sistema.config(text="ERROR EN LA DESCARGA", fg="#FF3333")

    def reproducir_seleccionada():
        global indice_cancion_actual, ruta_cancion_actual, musica_pausada
        seleccion = lista_visual.curselection()
        if seleccion:
            indice = seleccion[0]
            archivo_seleccionado = os.path.join(carpeta_seleccionada, lista_archivos_mp3[indice])

            if archivo_seleccionado == ruta_cancion_actual and musica_pausada:
                reproductor_py.reanudar()
                musica_pausada = False
                lbl_estado_sistema.config(text=f"REPRODUCIENDO: {lista_archivos_mp3[indice]}", fg="#FFFFFF")
            else:
                indice_cancion_actual = indice
                ruta_cancion_actual = archivo_seleccionado
                reproductor_py.reproducir(archivo_seleccionado)
                musica_pausada = False
                lbl_estado_sistema.config(text=f"REPRODUCIENDO: {lista_archivos_mp3[indice]}", fg="#FFFFFF")

    def pausar_cancion():
        global musica_pausada
        reproductor_py.pausar()
        musica_pausada = True
        lbl_estado_sistema.config(text="SISTEMA // EN PAUSA", fg="#888888")

    def cancion_siguiente():
        global indice_cancion_actual
        if lista_archivos_mp3 and indice_cancion_actual < len(lista_archivos_mp3) - 1:
            lista_visual.selection_clear(0, tk.END)
            indice_cancion_actual += 1
            lista_visual.selection_set(indice_cancion_actual)
            reproducir_seleccionada()

    def cancion_anterior():
        global indice_cancion_actual
        if lista_archivos_mp3 and indice_cancion_actual > 0:
            lista_visual.selection_clear(0, tk.END)
            indice_cancion_actual -= 1
            lista_visual.selection_set(indice_cancion_actual)
            reproducir_seleccionada()

    def verificar_fin_cancion():
        global ruta_cancion_actual, musica_pausada

        # Solo revisamos si hay una canción cargada y NO está en pausa
        if ruta_cancion_actual and not musica_pausada:

            # Le preguntamos al reproductor si ya se quedó en silencio
            if not reproductor_py.esta_reproduciendo():
                cancion_siguiente()  # ¡Pasamos a la siguiente!

        # Volvemos a ejecutar esta misma revisión dentro de 1000 milisegundos (1 segundo)
        root.after(1000, verificar_fin_cancion)
        
    # ESTRUCTURA VISUAL (MAQUETACIÓN):

    frame_superior = tk.Frame(root, bg="#000000")
    frame_superior.pack(side="top", fill="both", expand=True)

    frame_lateral = tk.Frame(frame_superior, bg="#000000", width=160)
    frame_lateral.pack(side="left", fill="y")
    frame_lateral.pack_propagate(False)

    try:
        img_logo = Image.open("Logo CloundySound.jpg")
        img_logo = img_logo.resize((100, 100), Image.Resampling.LANCZOS)
        logo_tk = ImageTk.PhotoImage(img_logo)
        lbl_logo = tk.Label(frame_lateral, image=logo_tk, bg="#000000")
        lbl_logo.image = logo_tk
        lbl_logo.pack(pady=(20, 10))

    except Exception:
        lbl_logo = tk.Label(frame_lateral, text="CLOUDY\nSOUND", font=("Arial", 14, "bold"), bg="#000000", fg="#FFFFFF")
        lbl_logo.pack(pady=(20, 10))

    btn_carpeta = tk.Button(frame_lateral, text="📁 CARPETA", font=("Arial", 8, "bold"), bg="#000000", fg="#888888",
                            bd=0, activebackground="#111111", activeforeground="#FFFFFF", cursor="hand2",
                            command=seleccionar_carpeta)
    btn_carpeta.pack(pady=5)

    lbl_ruta = tk.Label(frame_lateral, text="NO SELECTED", font=("Arial", 7), bg="#000000", fg="#444444")
    lbl_ruta.pack()

    div_vertical = tk.Frame(frame_superior, bg="#FFFFFF", width=1)
    div_vertical.pack(side="left", fill="y")

    frame_playlist = tk.Frame(frame_superior, bg="#000000")
    frame_playlist.pack(side="left", fill="both", expand=True)

    lista_visual = tk.Listbox(frame_playlist, bg="#000000", fg="#FFFFFF", font=("Arial", 13), bd=0,
                              highlightthickness=0, selectbackground="#FFFFFF", selectforeground="#000000",
                              activestyle="none")
    lista_visual.pack(fill="both", expand=True, padx=30, pady=30)
    lista_visual.bind("<Double-Button-1>", lambda e: reproducir_seleccionada())

    div_horizontal = tk.Frame(root, bg="#FFFFFF", height=1)
    div_horizontal.pack(side="top", fill="x")


    # PANELES DESPLEGABLES:

    frame_desplegable_descarga = tk.Frame(root, bg="#111111", height=50)

    color_fantasma = "#888888"
    color_texto_real = "#FFFFFF"

    entrada_url = tk.Entry(frame_desplegable_descarga, bg="#000000", fg=color_fantasma, font=("Arial", 10), bd=0,
                           insertbackground="#FFFFFF")
    entrada_url.insert(0, " URL de YouTube...")
    entrada_url.pack(side="left", expand=True, fill="x", padx=15, ipady=6)

    def al_hacer_clic_url(event):
        if entrada_url.get() == " URL de YouTube...":
            entrada_url.delete(0, tk.END)
            entrada_url.config(fg=color_texto_real)

    def al_quitar_clic_url(event):
        if entrada_url.get().strip() == "":
            entrada_url.insert(0, " URL de YouTube...")
            entrada_url.config(fg=color_fantasma)

    entrada_url.bind("<FocusIn>", al_hacer_clic_url)
    entrada_url.bind("<FocusOut>", al_quitar_clic_url)

    entrada_genero = tk.Entry(frame_desplegable_descarga, bg="#000000", fg=color_fantasma, font=("Arial", 10), bd=0,
                              insertbackground="#FFFFFF", width=18)
    entrada_genero.insert(0, " Género...")
    entrada_genero.pack(side="left", padx=5, ipady=6)

    def al_hacer_clic_genero(event):
        if entrada_genero.get() == " Género...":
            entrada_genero.delete(0, tk.END)
            entrada_genero.config(fg=color_texto_real)

    def al_quitar_clic_genero(event):
        if entrada_genero.get().strip() == "":
            entrada_genero.insert(0, " Género...")
            entrada_genero.config(fg=color_fantasma)

    entrada_genero.bind("<FocusIn>", al_hacer_clic_genero)
    entrada_genero.bind("<FocusOut>", al_quitar_clic_genero)

    btn_confirmar_descarga = tk.Button(frame_desplegable_descarga, text="OK", bg="#FFFFFF", fg="#000000",
                                       font=("Arial", 9, "bold"), bd=0, command=ejecutar_descarga_sistema)
    btn_confirmar_descarga.pack(side="left", padx=15, ipady=4)

    frame_desplegable_stats = tk.Frame(root, bg="#111111")
    btn_ver_grafico = tk.Button(frame_desplegable_stats, text="GENERAR ANÁLISIS DE GRÁFICO DE GÉNEROS", bg="#FFFFFF",
                                fg="#000000", font=("Arial", 9, "bold"), bd=0, command=mostrar_grafico_generos)
    btn_ver_grafico.pack(fill="x", padx=40, pady=10, ipady=6)

    # DECK INFERIOR:

    frame_barra_control = tk.Frame(root, bg="#000000", height=80)
    frame_barra_control.pack(side="bottom", fill="x")
    frame_barra_control.pack_propagate(False)

    estilo_secciones = {"bg": "#000000", "fg": "#FFFFFF", "activebackground": "#111111", "activeforeground": "#FFFFFF",
                        "bd": 0, "cursor": "hand2"}

    btn_seccion_descarga = tk.Button(frame_barra_control, text="▼   DESCARGAR", font=("Arial", 11, "bold"),
                                     **estilo_secciones, command=toggle_panel_descarga)
    btn_seccion_descarga.pack(side="left", expand=True, fill="both")

    div_b1 = tk.Frame(frame_barra_control, bg="#FFFFFF", width=1)
    div_b1.pack(side="left", fill="y", pady=15)

    frame_multimedia = tk.Frame(frame_barra_control, bg="#000000")
    frame_multimedia.pack(side="left", expand=True, fill="both", padx=20)

    btn_prev = tk.Button(frame_multimedia, text="«", font=("Arial", 26), bg="#000000", fg="#FFFFFF", bd=0,
                         activebackground="#000000", activeforeground="#888888", command=cancion_anterior)
    btn_prev.pack(side="left", expand=True)

    btn_play = tk.Button(frame_multimedia, text="▶", font=("Arial", 24), bg="#000000", fg="#FFFFFF", bd=0,
                         activebackground="#000000", activeforeground="#888888", command=reproducir_seleccionada)
    btn_play.pack(side="left", expand=True)

    btn_pause = tk.Button(frame_multimedia, text="‖", font=("Arial", 24, "bold"), bg="#000000", fg="#FFFFFF", bd=0,
                          activebackground="#000000", activeforeground="#888888", command=pausar_cancion)
    btn_pause.pack(side="left", expand=True)

    btn_next = tk.Button(frame_multimedia, text="»", font=("Arial", 26), bg="#000000", fg="#FFFFFF", bd=0,
                         activebackground="#000000", activeforeground="#888888", command=cancion_siguiente)
    btn_next.pack(side="left", expand=True)

    div_b2 = tk.Frame(frame_barra_control, bg="#FFFFFF", width=1)
    div_b2.pack(side="left", fill="y", pady=15)


    btn_seccion_stats = tk.Button(frame_barra_control, text="📊   ESTADISTICAS", font=("Arial", 11, "bold"),
                                  **estilo_secciones, command=toggle_panel_stats)
    btn_seccion_stats.pack(side="left", expand=True, fill="both")

    lbl_estado_sistema = tk.Label(frame_playlist, text="STATUS // ONLINE", font=("Courier", 8), bg="#000000",
                                  fg="#222222")
    lbl_estado_sistema.pack(side="bottom", anchor="e", padx=10, pady=5)

    # Carga de configuración inicial
    carpeta_guardada = cargar_configuracion()
    if carpeta_guardada and os.path.exists(carpeta_guardada):
        carpeta_seleccionada = carpeta_guardada
        lbl_ruta.config(text=os.path.basename(carpeta_seleccionada).upper())
        actualizar_lista_canciones()
    verificar_fin_cancion()

    root.mainloop()

if __name__ == "__main__":
    iniciar_interfaz()