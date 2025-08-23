import os, subprocess, io,json
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account

# ============================
# Configuración
# ============================
ADB_PATH = r"C:\Users\Acer\Documents\platform-tools-latest-windows\platform-tools\adb.exe"
DEVICE_VIDEOS_DIR = "/sdcard/DCIM/Video"
DEVICE_CAMERA_DIR = "/sdcard/DCIM/Camera"

# Archivos locales
SERVICE_ACCOUNT_FILE = os.path.join("data", "credenciales.json")
VIDEOS_FILE = os.path.join("data", "videos.json")

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

# Carpeta de stickers en Drive
STICKERS_FOLDER_ID = "1A8xCcSs1oecVZsxtkzEyusmWC_GPW71q"

# Carpeta temporal local
TEMP_STICKERS_DIR = os.path.join("data", "temp_stickers")
os.makedirs(TEMP_STICKERS_DIR, exist_ok=True)


# ============================
# Funciones utilitarias
# ============================





def cargar_dispositivos_video():
    if os.path.exists("data/videos.json"):
        with open("data/videos.json", "r") as f:
            return json.load(f)
    return {}


def guardar_dispositivos(dispositivos):
    with open("data/videos.json", "w") as f:
        json.dump(dispositivos, f, indent=2)
        
        
def run_adb(serial, *args, check=True):
    cmd = [ADB_PATH, "-s", serial] + list(args)
    return subprocess.run(cmd, check=check)


def forzar_indexado(serial, carpeta="DCIM/Camera"):
    run_adb(serial, "shell", "am", "broadcast",
            "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE",
            "-d", f"file:///sdcard/{carpeta}")
    print(f"📂 Indexado forzado en {serial} → {carpeta}")


def limpiar_memoria(serial):
    """Limpia Video y Camera en el dispositivo"""
    print(f"🧹 Limpiando {serial} → Videos y Camera...")
    run_adb(serial, "shell", "rm", "-rf", f"{DEVICE_VIDEOS_DIR}/*")
    run_adb(serial, "shell", "rm", "-rf", f"{DEVICE_CAMERA_DIR}/*")
    forzar_indexado(serial, "DCIM/Video")
    forzar_indexado(serial, "DCIM/Camera")


def _drive_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build("drive", "v3", credentials=creds)

# ============================
# Funciones principales
# ============================
def descargar_stickers_y_subir(serial: str) -> bool:
    """Descarga los stickers desde Google Drive y los sube directo a DCIM/Camera"""
    service = _drive_service()

    results = service.files().list(
        q=f"'{STICKERS_FOLDER_ID}' in parents and trashed=false",
        fields="files(id, name)").execute()
    files = results.get("files", [])

    if not files:
        print("⚠️ No se encontraron stickers en Google Drive")
        return False

    print(f"📥 Descargando y subiendo {len(files)} stickers → {serial}")

    for f in files:
        file_id, name = f["id"], f["name"]

        # archivo temporal
        temp_path = os.path.join(TEMP_STICKERS_DIR, name)

        # descarga desde Drive
        request = service.files().get_media(fileId=file_id)
        fh = io.FileIO(temp_path, "wb")
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            _, done = downloader.next_chunk()
        fh.close()

        # subir al dispositivo
        run_adb(serial, "shell", "mkdir", "-p", DEVICE_CAMERA_DIR)
        run_adb(serial, "push", temp_path, DEVICE_CAMERA_DIR)

        # limpiar archivo temporal
        os.remove(temp_path)

    forzar_indexado(serial, "DCIM/Camera")
    print(f"✅ Stickers actualizados en {serial}")
    return True


def subir_video_a_dispositivo(serial, cuenta, dispositivos):
    """
    Sube el video correspondiente a la cuenta indicada
    desde la carpeta local al dispositivo Android.
    """
    data_serial = dispositivos.get(serial, {})
    cuenta_data = data_serial.get("videos", {}).get(cuenta)

    if not cuenta_data:
        print(f"⚠️ No se encontró video asignado para {cuenta} en {serial}")
        return None

    ruta_video_local = cuenta_data.get("ruta")
    if not ruta_video_local or not os.path.exists(ruta_video_local):
        print(f"❌ Video no encontrado en ruta: {ruta_video_local}")
        return None

    # Asegurar carpeta en el dispositivo
    run_adb(serial, "shell", "mkdir", "-p", DEVICE_VIDEOS_DIR)

    # Subir video
    print(f"⬆️ Subiendo {ruta_video_local} → {serial}:{DEVICE_VIDEOS_DIR}")
    run_adb(serial, "push", ruta_video_local, DEVICE_VIDEOS_DIR)

    # Devolver el nombre del archivo (para usar en TikTok)
    return os.path.basename(ruta_video_local)
