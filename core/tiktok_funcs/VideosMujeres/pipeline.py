# core/tiktok_funcs/VideosMujeres/pipeline.py

from .adb_utils_videos import (
    subir_video_a_dispositivo,
    limpiar_memoria,
    descargar_stickers_y_subir,
    cargar_videos,
)

from .TiktokVideoScan import TitkokCuentasVideos
from .gestos_videos import gestos_videos


def ejecutar_pipeline(serial=None):
    # 🔍 Escanear cuentas en el dispositivo y actualizar videos.json
    TitkokCuentasVideos(serial)

    # 📂 Cargar configuración de dispositivos desde videos.json
    dispositivos = cargar_videos()

    for serial, data in dispositivos.items():
        print(f"\n📱 Procesando dispositivo {serial}...")

        # 🔹 Limpiar memoria antes de empezar
        limpiar_memoria(serial)

        # 🔹 Descargar y subir stickers al dispositivo
        descargar_stickers_y_subir(serial)

        # 🔹 Subir los videos por cada cuenta pendiente
        for cuenta in data.get("cuentasPorSubir", [])[:]:
            video = subir_video_a_dispositivo(serial, cuenta, dispositivos)
            if not video:
                continue

            # 🔹 Automatizar flujo de subida en TikTok
            gestos_videos(serial, cuenta, video)

            # 🔹 Después de publicar → limpiar todo
            limpiar_memoria(serial)

            # 🔹 Volver a subir stickers
            descargar_stickers_y_subir(serial)

            # 🔹 Marcar cuenta como subida en el JSON
            marcar_cuenta_subida(serial, cuenta, dispositivos)

    print("\n🎉 Pipeline finalizado.")
