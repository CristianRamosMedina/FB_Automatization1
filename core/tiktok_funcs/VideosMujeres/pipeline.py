# core/tiktok_funcs/VideosMujeres/pipeline.py

from .adb_utils_videos import (
    subir_video_a_dispositivo,
    limpiar_memoria,
    descargar_stickers_y_subir
)
from .gestos_videos import Gestos_VIDEOS
from core.adb_utils import cargar_videos, marcar_cuenta_subida
from .TiktokVideoScan import TitkokCuentas

def ejecutar_pipeline():
    TitkokCuentas(serial)
     
    # 🔹 Limpiar todo (videos + cámara)
    limpiar_memoria(serial)
        
    # 🔹 Descargar stickers desde Google Drive a temp local
    print("\n⬇️ Descargando stickers desde Google Drive...")
    local_stickers_path = descargar_stickers_y_subir()

    # 🔹 Cargar dispositivos desde videos.json
    dispositivos = cargar_videos()

    for serial, data in dispositivos.items():
        print(f"\n📱 Procesando dispositivo {serial}...")

        # 🔹 Limpiar todo (videos + cámara)
        limpiar_memoria(serial)

        # 🔹 Subir stickers (desde temp local) una vez por dispositivo
        descargar_stickers_y_subir(serial, local_stickers_path)

        # 🔹 Subir los videos por cada cuenta pendiente
        for cuenta in data.get("cuentasPorSubir", [])[:]:
            video = subir_video_a_dispositivo(serial, cuenta, dispositivos)
            if not video:
                continue

            # 🔹 Automatiza el flujo dentro de TikTok
            Gestos_VIDEOS(serial, cuenta, video)

            # 🔹 Después de publicar → solo limpia todo
            limpiar_memoria(serial)

            # 🔹 Subir stickers (desde temp local) una vez por dispositivo
            descargar_stickers_y_subir(serial, local_stickers_path)
            
            # 🔹 Marca la cuenta como subida en el JSON
            marcar_cuenta_subida(serial, cuenta, dispositivos)

    print("\n🎉 Pipeline finalizado.")
