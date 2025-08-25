import os

# Ruta base dinámica
BASE_VIDEOS_PATH = os.path.join(
    os.path.expanduser("~/Documents"),
    "Carrusel", "ImagenesCrudas", "Videos"
)

VIDEO_EXTS = (".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v")

def contar_videos_pendientes():
    """
    Revisa todas las carpetas dentro de BASE_VIDEOS_PATH y
    devuelve una lista con los nombres de las carpetas que
    no tienen ningún archivo de video.
    """
    if not os.path.exists(BASE_VIDEOS_PATH):
        print(f"⚠️ Carpeta base {BASE_VIDEOS_PATH} no existe.")
        return []

    vacias = []

    for nombre in os.listdir(BASE_VIDEOS_PATH):
        carpeta = os.path.join(BASE_VIDEOS_PATH, nombre)
        if not os.path.isdir(carpeta):
            continue
        if nombre.lower() == "videosusados":
            continue  # ignorar carpeta usada

        # buscar si hay al menos 1 video
        tiene_video = any(
            f.lower().endswith(VIDEO_EXTS)
            for f in os.listdir(carpeta)
        )

        if not tiene_video:
            vacias.append(nombre)

    return vacias
