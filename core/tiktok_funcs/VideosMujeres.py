import os
import json
import subprocess
import time

# === tus imports locales ===
from ..adb_utils import crear_funciones_con_serial
from .utils import ejecteg
from .TiktokCuentaScan import escanear_cuentas_tiktok   # 👈 aquí usamos tu detector OCR

# =============================
# Config
# =============================
DISPOSITIVOS_FILE = "dispositivos.json"
DEVICE_VIDEOS_DIR = "/sdcard/DCIM/Video"
ADB_PATH = r"C:\Users\Acer\Documents\platform-tools-latest-windows\platform-tools\adb.exe"

# =============================
# Utils JSON
# =============================
def cargar_dispositivos():
    if not os.path.exists(DISPOSITIVOS_FILE):
        return {}
    with open(DISPOSITIVOS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_dispositivos(data):
    with open(DISPOSITIVOS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def marcar_cuenta_subida(serial, cuenta, dispositivos):
    data_serial = dispositivos.get(serial, {})
    if cuenta in data_serial.get("cuentasPorSubir", []):
        data_serial["cuentasPorSubir"].remove(cuenta)
        data_serial["cuentasSubidas"].append(cuenta)
    guardar_dispositivos(dispositivos)

# =============================
# ADB helpers
# =============================
def run_adb(serial, *args, check=True):
    cmd = [ADB_PATH, "-s", serial] + list(args)
    return subprocess.run(cmd, check=check)

def forzar_indexado(serial, carpeta="DCIM/Video"):
    try:
        run_adb(serial, "shell", "am", "broadcast",
                "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE",
                "-d", f"file:///sdcard/{carpeta}")
        print(f"📂 Indexado forzado en {serial} → {carpeta}")
    except Exception as e:
        print(f"⚠️ Error indexando {carpeta} en {serial}: {e}")

# =============================
# Flujo de subida
# =============================
def subir_video_de_cuenta(serial, cuenta, dispositivos):
    data_serial = dispositivos.get(serial, {})
    carpeta_path = None
    for item in data_serial.get("cuentas", []):
        if item["cuenta"] == cuenta:
            carpeta_path = item["carpeta_path"]
            break

    if not carpeta_path or not os.path.exists(carpeta_path):
        print(f"⚠️ No se encontró carpeta para {cuenta} en {serial}")
        return None

    videos = [f for f in os.listdir(carpeta_path)
              if f.lower().endswith(('.mp4', '.mov', '.mkv', '.webm', '.avi', '.m4v'))]
    if not videos:
        print(f"⚠️ No hay videos en {carpeta_path}")
        return None

    videos.sort()
    video_a_subir = videos[0]
    ruta_video = os.path.join(carpeta_path, video_a_subir)

    print(f"📤 Subiendo {video_a_subir} de {cuenta} → {serial}")
    try:
        run_adb(serial, "shell", "mkdir", "-p", DEVICE_VIDEOS_DIR)
        run_adb(serial, "push", ruta_video, DEVICE_VIDEOS_DIR)
        forzar_indexado(serial, "DCIM/Video")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error subiendo: {e}")
        return None

    return video_a_subir

# =============================
# Gestos TikTok (placeholder)
# =============================
def Gestos_VIDEOS(serial, cuenta, video):
   import os
import json
import subprocess
import time

# === tus imports locales ===
from ..adb_utils import crear_funciones_con_serial
from .utils import ejecteg
from .TiktokCuentaScan import escanear_cuentas_tiktok   # 👈 aquí usamos tu detector OCR

# =============================
# Config
# =============================
DISPOSITIVOS_FILE = "dispositivos.json"
DEVICE_VIDEOS_DIR = "/sdcard/DCIM/Video"
ADB_PATH = r"C:\Users\Acer\Documents\platform-tools-latest-windows\platform-tools\adb.exe"

# =============================
# Utils JSON
# =============================
def cargar_dispositivos():
    if not os.path.exists(DISPOSITIVOS_FILE):
        return {}
    with open(DISPOSITIVOS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_dispositivos(data):
    with open(DISPOSITIVOS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def marcar_cuenta_subida(serial, cuenta, dispositivos):
    data_serial = dispositivos.get(serial, {})
    if cuenta in data_serial.get("cuentasPorSubir", []):
        data_serial["cuentasPorSubir"].remove(cuenta)
        data_serial["cuentasSubidas"].append(cuenta)
    guardar_dispositivos(dispositivos)

# =============================
# ADB helpers
# =============================
def run_adb(serial, *args, check=True):
    cmd = [ADB_PATH, "-s", serial] + list(args)
    return subprocess.run(cmd, check=check)

def forzar_indexado(serial, carpeta="DCIM/Video"):
    try:
        run_adb(serial, "shell", "am", "broadcast",
                "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE",
                "-d", f"file:///sdcard/{carpeta}")
        print(f"📂 Indexado forzado en {serial} → {carpeta}")
    except Exception as e:
        print(f"⚠️ Error indexando {carpeta} en {serial}: {e}")

# =============================
# Flujo de subida
# =============================
def subir_video_de_cuenta(serial, cuenta, dispositivos):
    data_serial = dispositivos.get(serial, {})
    carpeta_path = None
    for item in data_serial.get("cuentas", []):
        if item["cuenta"] == cuenta:
            carpeta_path = item["carpeta_path"]
            break

    if not carpeta_path or not os.path.exists(carpeta_path):
        print(f"⚠️ No se encontró carpeta para {cuenta} en {serial}")
        return None

    videos = [f for f in os.listdir(carpeta_path)
              if f.lower().endswith(('.mp4', '.mov', '.mkv', '.webm', '.avi', '.m4v'))]
    if not videos:
        print(f"⚠️ No hay videos en {carpeta_path}")
        return None

    videos.sort()
    video_a_subir = videos[0]
    ruta_video = os.path.join(carpeta_path, video_a_subir)

    print(f"📤 Subiendo {video_a_subir} de {cuenta} → {serial}")
    try:
        run_adb(serial, "shell", "mkdir", "-p", DEVICE_VIDEOS_DIR)
        run_adb(serial, "push", ruta_video, DEVICE_VIDEOS_DIR)
        forzar_indexado(serial, "DCIM/Video")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error subiendo: {e}")
        return None

    return video_a_subir

# =============================
# Gestos TikTok (placeholder)
# =============================
def Gestos_VIDEOS(serial, cuenta, video):
    run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap = crear_funciones_con_serial(serial)

    run("shell input keyevent 224")  # encender pantalla
    time.sleep(1)
    move("50%","68%","50%","20%")
    time.sleep(1)
    ejecteg(serial)

    print(f"\n🚀 Publicando {video} con la cuenta {cuenta} en {serial}...")
    run("shell monkey -p com.zhiliaoapp.musically -c android.intent.category.LAUNCHER 1")
    time.sleep(5)

    # Aquí pones tu flujo real de taps / captions / stickers
    tap("50%", "90.34%")
    time.sleep(3)
    print(f"✅ Simulación subida TikTok de {cuenta}")
    time.sleep(5)

# =============================
# Preparación con OCR
# =============================
def preparar_dispositivos():
    dispositivos = cargar_dispositivos()

    for serial in dispositivos.keys():
        print(f"\n🔍 Escaneando cuentas en {serial}...")
        resultado = escanear_cuentas_tiktok(serial)

        if resultado["motivo_fin"] == "ok":
            cuentas_detectadas = list(resultado["total_detectadas"])
            dispositivos[serial]["cuentasDetectadas"] = cuentas_detectadas
            dispositivos[serial]["cuentasPorSubir"] = cuentas_detectadas
            dispositivos[serial]["cuentasSubidas"] = []
            print(f"✅ Detectadas y listas: {cuentas_detectadas}")
        else:
            print(f"⚠️ Escaneo en {serial} terminó con: {resultado['motivo_fin']}")

    guardar_dispositivos(dispositivos)
    return dispositivos

# =============================
# Pipeline principal
# =============================
def ejecutar_pipeline():
    dispositivos = preparar_dispositivos()

    for serial, data in dispositivos.items():
        print(f"\n📱 Procesando dispositivo {serial}...")
        for cuenta in data.get("cuentasPorSubir", [])[:]:
            video = subir_video_de_cuenta(serial, cuenta, dispositivos)
            if not video:
                continue
            Gestos_VIDEOS(serial, cuenta, video)
            marcar_cuenta_subida(serial, cuenta, dispositivos)

    print("\n🎉 Pipeline finalizado.")

# =============================
# Main
# =============================
if __name__ == "__main__":
    ejecutar_pipeline()


# =============================
# Preparación con OCR
# =============================
def preparar_dispositivos():
    dispositivos = cargar_dispositivos()

    for serial in dispositivos.keys():
        print(f"\n🔍 Escaneando cuentas en {serial}...")
        resultado = escanear_cuentas_tiktok(serial)

        if resultado["motivo_fin"] == "ok":
            cuentas_detectadas = list(resultado["total_detectadas"])
            dispositivos[serial]["cuentasDetectadas"] = cuentas_detectadas
            dispositivos[serial]["cuentasPorSubir"] = cuentas_detectadas
            dispositivos[serial]["cuentasSubidas"] = []
            print(f"✅ Detectadas y listas: {cuentas_detectadas}")
        else:
            print(f"⚠️ Escaneo en {serial} terminó con: {resultado['motivo_fin']}")

    guardar_dispositivos(dispositivos)
    return dispositivos

# =============================
# Pipeline principal
# =============================
def ejecutar_pipeline():
    dispositivos = preparar_dispositivos()

    for serial, data in dispositivos.items():
        print(f"\n📱 Procesando dispositivo {serial}...")
        for cuenta in data.get("cuentasPorSubir", [])[:]:
            video = subir_video_de_cuenta(serial, cuenta, dispositivos)
            if not video:
                continue
            Gestos_VIDEOS(serial, cuenta, video)
            marcar_cuenta_subida(serial, cuenta, dispositivos)

    print("\n🎉 Pipeline finalizado.")

# =============================
# Main
# =============================
if __name__ == "__main__":
    ejecutar_pipeline()
