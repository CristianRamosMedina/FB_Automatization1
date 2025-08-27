import os

# Ruta base dinámica
BASE_VIDEOS_PATH = os.path.join(
    os.path.expanduser("~/Documents"),
    "Carrusel", "ImagenesCrudas", "Videos"
)

VIDEO_EXTS = (".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v")

def contar_videos_pendientes():
    """
    Revisa todas las carpetas dentro de BASE_VIDEOS_PATH.
    Devuelve un dict con {carpeta: cantidad_de_videos}.
    """
    resultado = {}

    if not os.path.exists(BASE_VIDEOS_PATH):
        print(f"⚠️ Carpeta base {BASE_VIDEOS_PATH} no existe.")
        return resultado

    for nombre in os.listdir(BASE_VIDEOS_PATH):
        carpeta = os.path.join(BASE_VIDEOS_PATH, nombre)
        if not os.path.isdir(carpeta):
            continue
        if nombre.lower() == "videosusados":
            continue  # ignorar carpeta usada

        try:
            archivos = os.listdir(carpeta)
        except Exception as e:
            print(f"⚠️ No se pudo leer {carpeta}: {e}")
            resultado[nombre] = -1  # error al leer
            continue

        # Filtrar solo videos válidos
        videos = [
            f for f in archivos
            if os.path.isfile(os.path.join(carpeta, f))
            and f.lower().endswith(VIDEO_EXTS)
        ]

        resultado[nombre] = len(videos)

    return resultado
