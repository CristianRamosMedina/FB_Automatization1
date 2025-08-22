import os, subprocess, io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account

ADB_PATH = r"C:\Users\Acer\Documents\platform-tools-latest-windows\platform-tools\adb.exe"
DEVICE_VIDEOS_DIR = "/sdcard/DCIM/Video"
DEVICE_CAMERA_DIR = "/sdcard/DCIM/Camera"

# credenciales del servicio (tu JSON de Google Drive API)
SERVICE_ACCOUNT_FILE = "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

# carpeta stickers en Drive
STICKERS_FOLDER_ID = "1A8xCcSs1oecVZsxtkzEyusmWC_GPW71q"


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


def descargar_stickers_y_subir(serial):
    """Descarga los stickers desde Google Drive y los sube directo a DCIM/Camera"""
    service = _drive_service()

    results = service.files().list(
        q=f"'{STICKERS_FOLDER_ID}' in parents and trashed=false",
        fields="files(id, name)").execute()
    files = results.get("files", [])

    if not files:
        print("⚠️ No se encontraron stickers en Google Drive")
        return

    print(f"📥 Descargando y subiendo {len(files)} stickers → {serial}")

    for f in files:
        file_id, name = f["id"], f["name"]

        # descarga en memoria
        request = service.files().get_media(fileId=file_id)
        fh = io.FileIO(name, "wb")
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            _, done = downloader.next_chunk()
        fh.close()

        # subir al dispositivo
        run_adb(serial, "shell", "mkdir", "-p", DEVICE_CAMERA_DIR)
        run_adb(serial, "push", name, DEVICE_CAMERA_DIR)
        os.remove(name)  # borrar archivo local temporal

    forzar_indexado(serial, "DCIM/Camera")
    print(f"✅ Stickers actualizados en {serial}")
