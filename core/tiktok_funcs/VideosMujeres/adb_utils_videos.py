import os, subprocess, io,json
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
from core.paths import SERVICE_ACCOUNT_FILE, VIDEOS_FILE

# ============================
# Configuración
# ============================
ADB_PATH = r"C:\Users\Acer\Documents\platform-tools-latest-windows\platform-tools\adb.exe"
DEVICE_VIDEOS_DIR = "/sdcard/DCIM/Video"
DEVICE_CAMERA_DIR = "/sdcard/DCIM/Camera"

# Archivos locales


SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

# Carpeta de stickers en Drive
STICKERS_FOLDER_ID = "1A8xCcSs1oecVZsxtkzEyusmWC_GPW71q"

# Carpeta temporal local
TEMP_STICKERS_DIR = os.path.join("data", "temp_stickers")
os.makedirs(TEMP_STICKERS_DIR, exist_ok=True)


# ============================
# Funciones utilitarias
# ============================

def cargar_videos():
    if os.path.exists(VIDEOS_FILE):
        with open(VIDEOS_FILE, "r") as f:
            return json.load(f)
    return {}


def guardar_videos(dispositivos):
    with open(VIDEOS_FILE, "w", encoding="utf-8") as f:
        json.dump(dispositivos, f, indent=2, ensure_ascii=False)

  
  
        
def run_adb(serial, *args, check=True):
    cmd = [ADB_PATH, "-s", serial] + list(args)
    return subprocess.run(cmd, check=check)


def forzar_indexado(serial, carpeta):
    run_adb(serial, "shell", "am", "broadcast",
            "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE",
            "-d", f"file:///sdcard/{carpeta}")
    print(f"📂 Indexado forzado en {serial} → {carpeta}")


def listar_archivos(serial, carpeta):
    """Devuelve lista de archivos en una carpeta del dispositivo"""
    result = subprocess.run(
        [ADB_PATH, "-s", serial, "shell", "ls", "-1", carpeta],
        capture_output=True, text=True
    )
    salida = result.stdout.strip()
    if not salida or "No such file" in salida:
        return []
    return salida.split("\n")

def limpiar_memoria(serial):
    """Limpia Video y Camera en el dispositivo con verificación"""
    print(f"🧹 Limpiando {serial} → Videos y Camera...")

    for carpeta in [DEVICE_VIDEOS_DIR, DEVICE_CAMERA_DIR]:
        antes = listar_archivos(serial, carpeta)
        print(f"   📂 Archivos antes en {carpeta}: {len(antes)}")

        run_adb(serial, "shell", "rm", "-rf", f"{carpeta}/*")

        despues = listar_archivos(serial, carpeta)
        print(f"   ✅ Archivos después en {carpeta}: {len(despues)}")

        forzar_indexado(serial, carpeta.replace("/sdcard/", ""))  # indexar

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
    Busca la carpeta asignada a la cuenta en videos.json,
    selecciona un video y lo sube al dispositivo.
    """
    data_serial = dispositivos.get(serial, {})
    cuentas = data_serial.get("cuentas", [])

    cuenta_data = next((c for c in cuentas if c["cuenta"] == cuenta), None)
    if not cuenta_data:
        print(f"⚠️ No se encontró carpeta asignada para {cuenta} en {serial}")
        return None

    carpeta_path = cuenta_data.get("carpeta_path")
    if not carpeta_path or not os.path.exists(carpeta_path):
        print(f"❌ Carpeta no encontrada para {cuenta}: {carpeta_path}")
        return None

    # Buscar videos en la carpeta
    videos = [f for f in os.listdir(carpeta_path)
              if f.lower().endswith((".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v"))]

    if not videos:
        print(f"⚠️ No se encontraron videos en {carpeta_path}")
        return None

    videos.sort()
    video_a_subir = videos[0]
    ruta_video_local = os.path.join(carpeta_path, video_a_subir)

    # Asegurar carpeta en el dispositivo
    run_adb(serial, "shell", "mkdir", "-p", DEVICE_VIDEOS_DIR)

    # Subir video
    print(f"⬆️ Subiendo {ruta_video_local} → {serial}:{DEVICE_VIDEOS_DIR}")
    run_adb(serial, "push", ruta_video_local, DEVICE_VIDEOS_DIR)

    return video_a_subir  # nombre del archivo para usar en TikTok
