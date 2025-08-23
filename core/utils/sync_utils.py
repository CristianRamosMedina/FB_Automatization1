import json
import os

VIDEOS_FILE = "data/videos.json"
DISPOSITIVOS_FILE = "data/dispositivos.json"

def sincronizar_videos_a_dispositivos():
    """
    Mantiene sincronizados videos.json -> dispositivos.json
    Copia las claves de cada serial: cuentasPorSubir, cuentasSubidas, cuentasDetectadas.
    """
    if not os.path.exists(VIDEOS_FILE):
        print("⚠️ videos.json no existe, no se puede sincronizar.")
        return

    try:
        with open(VIDEOS_FILE, "r", encoding="utf-8") as f:
            videos_data = json.load(f)
    except Exception as e:
        print(f"❌ Error leyendo videos.json: {e}")
        return

    dispositivos_data = {}
    if os.path.exists(DISPOSITIVOS_FILE):
        try:
            with open(DISPOSITIVOS_FILE, "r", encoding="utf-8") as f:
                dispositivos_data = json.load(f)
        except Exception as e:
            print(f"⚠️ Error leyendo dispositivos.json: {e} → se sobrescribirá.")

    for serial, info in videos_data.items():
        if serial not in dispositivos_data:
            dispositivos_data[serial] = {}

        # Copiar solo las partes necesarias para cambiarCuentas
        dispositivos_data[serial]["cuentasPorSubir"]  = info.get("cuentasPorSubir", [])
        dispositivos_data[serial]["cuentasSubidas"]   = info.get("cuentasSubidas", [])
        dispositivos_data[serial]["cuentasDetectadas"] = info.get("cuentasDetectadas", [])
        dispositivos_data[serial]["cuentas"]          = info.get("cuentas", [])

    try:
        with open(DISPOSITIVOS_FILE, "w", encoding="utf-8") as f:
            json.dump(dispositivos_data, f, indent=2, ensure_ascii=False)
        print("🔄 dispositivos.json sincronizado con videos.json")
    except Exception as e:
        print(f"❌ Error guardando dispositivos.json: {e}")
