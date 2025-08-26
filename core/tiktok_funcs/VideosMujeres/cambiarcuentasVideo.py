# core/tiktok_funcs/cambiarCuentas.py
import os
import re
import shutil
import time
import tempfile
import subprocess
from datetime import datetime
from typing import List, Optional

# === Google Drive ===
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account

from core.tiktok_funcs.utils import ejecteg, switchAccount
from core.tiktok_funcs.VideosMujeres.TiktokVideoScan import (
     ultimacuenta, detectar_usuarios_en_pantalla,
    actualizar_estado_cuenta
)
from .gestos_videos import gestos_videos
from .adb_utils_videos import cargar_videos, limpiar_memoria,forzar_indexado

from ...adb_utils import (
    get_screen_size, parse_coord, crear_funciones_con_serial
)
from ...config import hilos_activos, ADB_PATH  # ⬅️ mismo diccionario global
from core.paths import SERVICE_ACCOUNT_FILE

# ==================== CONFIG GOOGLE DRIVE ====================
# Usa tu service account JSON (ruta relativa o absoluta)

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

# Carpeta única y compartida para TODAS las cuentas:
FOLDER_ID = "1A8xCcSs1oecVZsxtkzEyusmWC_GPW71q"  # ⬅️ el que enviaste


def get_drive_service():
    """
    Construye el cliente de Google Drive usando service account (credentials.json).
    Asegúrate de que la carpeta FOLDER_ID esté compartida con el email del service account (Viewer).
    """
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds)


# ==================== helpers de parada ====================
def should_stop(serial: str) -> bool:
    return not hilos_activos.get(serial, False)

def _sleep(serial: str, segundos: float):
    fin = time.time() + max(0.0, segundos)
    while time.time() < fin:
        if should_stop(serial):
            return
        time.sleep(0.1)


# ==================== rutas en el dispositivo ====================
DEVICE_VIDEOS_DIR   = "/sdcard/DCIM/Video"
DEVICE_IMAGENES_DIR = "/sdcard/DCIM/Camera"

# ==================== utilidades ADB/FS ====================
def run_adb(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def adb_shell(serial: str, *shell_cmd: str) -> subprocess.CompletedProcess:
    return run_adb([ADB_PATH, "-s", serial, "shell", *shell_cmd])

def adb_push(serial: str, local_path: str, remote_dir: str) -> bool:
    res = run_adb([ADB_PATH, "-s", serial, "push", local_path, f"{remote_dir}/"])
    if res.returncode != 0:
        print(f"❌ [{serial}] adb push falló: {res.stderr.strip()}")
        return False
    print(f"✅ [{serial}] Subido: {os.path.basename(local_path)} → {remote_dir}")
    return True

def ensure_device_dirs(serial: str):
    adb_shell(serial, "mkdir", "-p", DEVICE_VIDEOS_DIR)
    adb_shell(serial, "mkdir", "-p", DEVICE_IMAGENES_DIR)

def _natural_keys(s: str):
    import re
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s)]

def listar_videos(carpeta_path: str) -> list[str]:
    exts = (".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v")
    files = [os.path.join(carpeta_path, f)
             for f in os.listdir(carpeta_path)
             if f.lower().endswith(exts)]
    files.sort(key=lambda p: _natural_keys(os.path.basename(p)))
    return files


# ==================== descarga imágenes desde Drive (compartidas) ====================
def descargar_imagenes_desde_drive_global(
    folder_id: str,
    destino_local: str,
    max_imagenes: Optional[int] = None,
    ordenar_natural: bool = True,
) -> List[str]:
    """
    Descarga imágenes (image/*) desde un único folder_id compartido para todas las cuentas.
    Retorna paths locales descargados (ordenados por nombre natural si corresponde).
    """
    if not folder_id:
        print("⚠️ FOLDER_ID vacío. Configura el ID de la carpeta de Drive.")
        return []

    os.makedirs(destino_local, exist_ok=True)
    service = get_drive_service()

    query = f"'{folder_id}' in parents and trashed=false"
    results = service.files().list(
        q=query,
        pageSize=1000,
        fields="files(id, name, mimeType)"
    ).execute()

    files = results.get("files", []) or []
    imagenes = [f for f in files if f.get("mimeType", "").startswith("image/")]

    if ordenar_natural:
        imagenes.sort(key=lambda f: _natural_keys(f["name"]))
    else:
        imagenes.sort(key=lambda f: f["name"].lower())

    if max_imagenes is not None:
        imagenes = imagenes[:max_imagenes]

    descargadas = []
    for f in imagenes:
        local_path = os.path.join(destino_local, f["name"])
        request = service.files().get_media(fileId=f["id"])
        with io.FileIO(local_path, "wb") as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
        descargadas.append(local_path)
        print(f"📥 Descargada: {f['name']}")

    return descargadas


def subir_imagenes_al_dispositivo(serial: str, imagenes_locales: list[str]) -> int:
    if not imagenes_locales:
        print(f"ℹ️ [{serial}] Sin imágenes para subir.")
        return 0
    ensure_device_dirs(serial)
    subidas = 0
    for img in imagenes_locales:
        if should_stop(serial):
            break
        if adb_push(serial, img, DEVICE_IMAGENES_DIR):
            subidas += 1
    print(f"🖼️ [{serial}] Imágenes subidas: {subidas}")
    return subidas


# ==================== flujo principal ====================
def cambiar_todas_las_cuentas_videos(serial: str):
    """
    Itera sobre 'cuentasPorSubir' y ejecuta:
      - subir 1 video (y borrar local si OK)
      - descargar (del folder global), ordenar y subir imágenes a DCIM/Imagenes
      - gestos y cambio de cuenta
    """
    hilos_activos[serial] = True
    try:
        contador = 0
        while True:
            if should_stop(serial):
                print(f"⏹ [{serial}] Detenido por usuario (inicio de loop).")
                break

            datos_serial = cargar_videos().get(serial, {})
            pendientes = datos_serial.get("cuentasPorSubir", [])
            if not pendientes:
                print(f"✅ [{serial}] Ya no hay más cuentas por subir.")
                break

            cuenta_actual = ultimacuenta(serial)
            if should_stop(serial):
                print(f"⏹ [{serial}] Detenido tras 'ultimacuenta'.")
                break

            print(f"[{serial}] Cambiar Cuentas detecta: {cuenta_actual}")

            if cuenta_actual in pendientes:
                print(f"[{serial}] Pendiente → (subir 1 video + imágenes + gestos + cambiar)")
                ok = descarga(serial, cuenta_actual)  # ⬅️ 1 video + imágenes
                if should_stop(serial): break
                if ok:
                    ejecteg(serial)          # “limpiador” si lo usas
                    if should_stop(serial): break
                    gestos_videos(serial)
                    if should_stop(serial): break
                cambiarcuenta(serial)
                if should_stop(serial): break
            else:
                print(f"[{serial}] La cuenta actual no está en pendientes → intentar cambiar.")
                cambiarcuenta(serial)
                if should_stop(serial): break

            _sleep(serial, 1.0)
            contador += 1

        print(f"[{serial}] Iteraciones: {contador}")
        # 🚫 no movemos carpetas
    finally:
        hilos_activos[serial] = False


# ==================== cambiar cuenta en el switcher ====================
def cambiarcuenta(serial: str):
    intentos = 0
    while True:
        if should_stop(serial):
            print(f"⏹ [{serial}] Detenido antes/después de switchAccount.")
            return
        try:
            switchAccount(serial)
            if should_stop(serial): return

            cuenta = cambiar_a_siguiente_cuenta(serial)
            if should_stop(serial): return

            if cuenta == "FIN":
                print(f"🏁 [{serial}] Proceso finalizado: no hay más cuentas.")
                return

            if not cuenta:
                intentos += 1
                print(f"⚠️ [{serial}] No se pudo cambiar (intento #{intentos}), reintentando…")
                _sleep(serial, min(5, 1 + intentos))
                continue

            _sleep(serial, 5)
            return

        except Exception as e:
            intentos += 1
            print(f"💥 [{serial}] Error en cambiarcuenta: {e} (intento #{intentos})")
            _sleep(serial, min(5, 1 + intentos))


# ==================== descarga (1 video + imágenes) ====================
def descarga(serial: str, cuentaactual: str, max_imagenes: int | None = None) -> bool:
    """
    - Elige 1 video (orden natural), lo sube a DCIM/Video y lo borra local si el push fue OK.
    - Descarga imágenes desde el FOLDER_ID global de Drive, las ordena y las sube a DCIM/Imagenes.
    """
    data = cargar_videos()
    if serial not in data:
        print(f"❌ [{serial}] No existe entrada en dispositivos.json.")
        return False

    for cuenta in data[serial].get("cuentas", []):
        if should_stop(serial):
            print(f"⏹ [{serial}] Detenido durante 'descarga'.")
            return False

        if cuenta.get("cuenta") == cuentaactual:
            carpeta_path   = cuenta.get("carpeta_path")
            # carpeta_nombre ya no es necesario para Drive global, pero lo mantenemos por compatibilidad
            # carpeta_nombre = (cuenta.get("carpeta_nombre") or "").strip()

            if not carpeta_path or not os.path.exists(carpeta_path):
                print(f"❌ [{serial}] Carpeta local para {cuentaactual} no encontrada.")
                return False
            limpiar_memoria(serial)
            # 1) elegir UN video y subirlo a DCIM/Video
            videos = listar_videos(carpeta_path)
            if not videos:
                print(f"⚠️ [{serial}] No hay videos en: {carpeta_path}")
                return False

            video_a_subir = videos[0]  # puedes randomizar si prefieres
            ensure_device_dirs(serial)

            print(f"📤 [{serial}] Subiendo video: {os.path.basename(video_a_subir)} → {DEVICE_VIDEOS_DIR}")
            if not adb_push(serial, video_a_subir, DEVICE_VIDEOS_DIR):
                return False

            # borrar local SOLO si el push fue OK
            try:
                os.remove(video_a_subir)
                print(f"🧹 [{serial}] Eliminado local: {os.path.basename(video_a_subir)}")
            except Exception as e:
                print(f"⚠️ [{serial}] No se pudo borrar local: {e}")

            # 2) descargar imágenes desde Drive (folder global), ORDENAR y subir a DCIM/Imagenes
            with tempfile.TemporaryDirectory(prefix=f"imgs_{serial}_") as tempdir:
                imagenes_locales = descargar_imagenes_desde_drive_global(
                    folder_id=FOLDER_ID,
                    destino_local=tempdir,
                    max_imagenes=max_imagenes,  # e.g. 20 si quieres limitar
                    ordenar_natural=True
                )
                if should_stop(serial): 
                    return False
                subir_imagenes_al_dispositivo(serial, imagenes_locales)
            forzar_indexado(serial,"DCIM/Camera")    
            forzar_indexado(serial,"DCIM/Video")
            return True

    print(f"❌ [{serial}] Cuenta {cuentaactual} no encontrada en el JSON.")
    return False


# ==================== seleccionar siguiente cuenta ====================
def cambiar_a_siguiente_cuenta(serial: str):
    if should_stop(serial):
        return None

    Width, Height = get_screen_size(serial)
    run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap, leerTextoEnRegion = crear_funciones_con_serial(serial)

    print(f"🔁 [{serial}] Cambiando cuenta…")

    cuentas_detectadas, _ = detectar_usuarios_en_pantalla(serial)
    if should_stop(serial):
        return None

    if not cuentas_detectadas:
        print(f"⚠️ [{serial}] No se detectaron cuentas visibles en el switcher.")
        return None

    cuenta_actual = list(cuentas_detectadas)[0]
    print(f"📌 [{serial}] Cuenta actual: {cuenta_actual}")

    siguiente = actualizar_estado_cuenta(serial, cuenta_actual)
    if should_stop(serial):
        return None

    if not siguiente:
        print(f"✅ [{serial}] Ya no quedan cuentas por subir.")
        return "FIN"

    print(f"🎯 [{serial}] Buscando próxima cuenta: {siguiente}")

    x1 = parse_coord("21.00%", Width)
    y1 = parse_coord("18.88%", Height)
    x2 = parse_coord("82.71%", Width)
    y2 = parse_coord("93.88%", Height)
    region = (x1, y1, x2, y2)

    coords = buscarTextoEnRegion(region, siguiente, umbral_similitud=0.8)
    if should_stop(serial):
        return None

    if coords:
        x, y = coords
        tap(x, y)
        print(f"🧭 [{serial}] Cambiado a cuenta: {siguiente}")
        _sleep(serial, 4)
        return siguiente

    print(f"❌ [{serial}] No se encontró '{siguiente}' en pantalla.")
    return None
