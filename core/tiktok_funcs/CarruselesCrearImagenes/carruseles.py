import os
import io
import json
import shutil
import time
import threading
import random
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from PIL import Image, ImageFile, UnidentifiedImageError
ImageFile.LOAD_TRUNCATED_IMAGES = True  # tolerar encabezados/archivos raros

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from core.paths import SERVICE_ACCOUNT_FILE
from ..utils import AbrirJsonCarruseles

# ================= Config =================
carpetas = AbrirJsonCarruseles()
ruta_documentos = os.path.expanduser("~/Documents")

base_salida = os.path.join(ruta_documentos, "Carrusel", "ImagenesCrudas", "Carrusel")
base_usadas = os.path.join(ruta_documentos, "Carrusel", "ImagenesCrudas", "ImagenCrudaUsada")

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

carpetas_descargadas = set()
EXTS = (".png", ".jpg", ".jpeg", ".webp")

# Ruta a img/ (donde están las carpetas 1..27)
RAIZ_PROYECTO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
RUTA_IMG = os.path.join(RAIZ_PROYECTO, "img")

# ================ Utiles ==================
def ordenar_natural(lista):
    import re
    def alfanum(clave):
        return [int(t) if t.isdigit() else t.lower()
                for t in re.split('([0-9]+)', clave)]
    return sorted(lista, key=alfanum)

def extraer_numero(nombre):
    import re
    base = os.path.splitext(nombre)[0]
    m = re.search(r'(\d+)', base)
    return int(m.group(1)) if m else None

def indexar_por_numero(archivos):
    archivos = ordenar_natural(archivos)
    idx = {}
    for f in archivos:
        n = extraer_numero(f)
        if n is not None and f.lower().endswith(EXTS):
            idx.setdefault(n, f)
    return idx

def _size_stable(path, tries=4, sleep_s=0.06):
    last = None
    for _ in range(tries):
        try:
            cur = os.path.getsize(path)
        except OSError:
            cur = None
        if cur is not None and cur == last and cur > 0:
            return True
        last = cur
        time.sleep(sleep_s)
    return last is not None and last > 0

def _read_bytes_strong(path, retries=4, sleep_s=0.08):
    last_err = None
    for _ in range(retries + 1):
        try:
            _size_stable(path)  # best-effort
            with open(path, "rb") as fh:
                data = fh.read()
            if not data:
                raise UnidentifiedImageError("archivo vacío")
            # chequeo rápido de firma
            if len(data) >= 12:
                head = data[:12]
                sig_ok = (
                    head.startswith(b"\x89PNG\r\n\x1a\n") or
                    head.startswith(b"\xff\xd8\xff") or
                    (head[:4] == b"RIFF" and data[8:12] == b"WEBP")
                )
                if not sig_ok:
                    raise UnidentifiedImageError("Header no reconocido (firma inválida)")
            return data
        except Exception as e:
            last_err = e
            time.sleep(sleep_s)
    raise last_err

def image_from_bytes_rgba(b: bytes):
    im = Image.open(io.BytesIO(b))
    im.load()
    return im.convert("RGBA")

class StickerPool:
    def __init__(self):
        self._lock = threading.RLock()
        self._pools = {}

    def _dir_signature(self, path_dir):
        latest_mtime = 0
        total_size = 0
        try:
            names = os.listdir(path_dir)
        except FileNotFoundError:
            names = []
        for fname in names:
            if not fname.lower().endswith(EXTS):
                continue
            p = os.path.join(path_dir, fname)
            try:
                st = os.stat(p)
                latest_mtime = max(latest_mtime, getattr(st, "st_mtime_ns", int(st.st_mtime * 1e9)))
                total_size += st.st_size
            except FileNotFoundError:
                continue
        return (latest_mtime, total_size)

    @staticmethod
    def _extract_number(name):
        import re
        base = os.path.splitext(name)[0]
        m = re.search(r"(\d+)", base)
        return int(m.group(1)) if m else None

    def _load_folder(self, path_dir):
        by_num = {}
        by_name = {}
        try:
            names = os.listdir(path_dir)
        except FileNotFoundError:
            names = []
        for fname in names:
            if not fname.lower().endswith(EXTS):
                continue
            p = os.path.join(path_dir, fname)
            try:
                data = _read_bytes_strong(p)
                by_name[fname] = data
                n = self._extract_number(fname)
                if n is not None and n not in by_num:
                    by_num[n] = data
            except Exception:
                continue
        return by_num, by_name

    def get_folder_pool(self, path_dir):
        path_dir = os.path.normpath(os.path.abspath(path_dir))
        with self._lock:
            sig = self._dir_signature(path_dir)
            entry = self._pools.get(path_dir)
            if entry and entry.get("sig") == sig:
                return entry
            by_num, by_name = self._load_folder(path_dir)
            entry = {"sig": sig, "by_num": by_num, "by_name": by_name}
            self._pools[path_dir] = entry
            return entry

    def get_sticker_bytes_by_num(self, path_dir, n):
        entry = self.get_folder_pool(path_dir)
        return entry["by_num"].get(n)

    def get_last_sticker_bytes(self, path_dir):
        entry = self.get_folder_pool(path_dir)
        if not entry["by_num"]:
            return None
        last_n = max(entry["by_num"].keys())
        return entry["by_num"][last_n], last_n

STICKERS = StickerPool()

# ================ Drive ===================
def descargar_carpeta_drive(folder_id, destino):
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    drive_service = build("drive", "v3", credentials=creds)
    os.makedirs(destino, exist_ok=True)

    query = f"'{folder_id}' in parents and trashed = false"
    page_token = None

    while True:
        response = drive_service.files().list(
            q=query,
            spaces="drive",
            fields="nextPageToken, files(id, name, mimeType)",
            pageToken=page_token
        ).execute()

        for file in response.get("files", []):
            file_path = os.path.join(destino, file["name"])
            if file["mimeType"] == "application/vnd.google-apps.folder":
                descargar_carpeta_drive(file["id"], file_path)
            else:
                request = drive_service.files().get_media(fileId=file["id"])
                with io.FileIO(file_path, "wb") as fh:
                    downloader = MediaIoBaseDownload(fh, request)
                    done = False
                    while not done:
                        _status, done = downloader.next_chunk()
        page_token = response.get("nextPageToken", None)
        if not page_token:
            break

def asegurar_y_descargar(ruta_relativa, drive_id):
    ruta_completa = os.path.join(ruta_documentos, ruta_relativa)
    os.makedirs(ruta_completa, exist_ok=True)
    if not os.listdir(ruta_completa):
        if drive_id in carpetas_descargadas:
            print(f"Carpeta ya descargada previamente: {ruta_relativa}")
            return
        print(f"Descargando carpeta desde Drive: {ruta_relativa}")
        descargar_carpeta_drive(drive_id, ruta_completa)
        carpetas_descargadas.add(drive_id)
    else:
        print(f"Carpeta ya tiene contenido: {ruta_relativa}")

# ============== Proceso core ===============
def procesar_carpeta(carpeta):
    carpeta_num = carpeta["CarpetaNumero"]
    path_sticker = carpeta["pathSticker"]
    path_imagenes = carpeta["pathImagenes"]

    asegurar_y_descargar(path_sticker, carpeta["driveIdSticker"])
    os.makedirs(os.path.join(ruta_documentos, path_imagenes), exist_ok=True)

    path_sticker_completo = os.path.join(ruta_documentos, path_sticker)
    path_imagenes_completo = os.path.join(ruta_documentos, path_imagenes)

    subcarpetas_c = [d for d in os.listdir(path_imagenes_completo)
                     if os.path.isdir(os.path.join(path_imagenes_completo, d)) and d.lower().startswith("c")]

    if not subcarpetas_c:
        print(f"[{carpeta_num}] ❌ No se encontró carpeta 'c*' en {path_imagenes_completo}")
        return 0

    carpeta_c = ordenar_natural(subcarpetas_c)[0]
    ruta_carpeta_imagenes = os.path.join(path_imagenes_completo, carpeta_c)

    stickers_arch = [f for f in os.listdir(path_sticker_completo) if f.lower().endswith(EXTS)]
    imagenes_arch = [f for f in os.listdir(ruta_carpeta_imagenes) if f.lower().endswith(EXTS)]

    if not stickers_arch:
        print(f"[{carpeta_num}] ❌ No hay stickers en {path_sticker_completo}")
        return 0
    if not imagenes_arch:
        print(f"[{carpeta_num}] ❌ No hay imágenes en {ruta_carpeta_imagenes}")
        return 0

    idx_stickers = indexar_por_numero(stickers_arch)
    idx_imagenes = indexar_por_numero(imagenes_arch)

    if not idx_stickers:
        print(f"[{carpeta_num}] ❌ Ningún sticker tiene número en el nombre.")
        return 0
    if not idx_imagenes:
        print(f"[{carpeta_num}] ❌ Ninguna imagen tiene número en el nombre.")
        return 0

    numeros = sorted(idx_stickers.keys())
    ult_num_img = max(idx_imagenes.keys())
    ult_img = idx_imagenes[ult_num_img]

    pares = []
    faltantes_img = []
    faltantes_sticker = []

    for n in numeros:
        sticker_name = idx_stickers.get(n)
        img_name = idx_imagenes.get(n)
        if sticker_name and img_name:
            pares.append((sticker_name, img_name, n))
        elif sticker_name and not img_name:
            pares.append((sticker_name, ult_img, n))
            faltantes_img.append(n)
        else:
            faltantes_sticker.append(n)

    ruta_salida = os.path.join(base_salida, carpeta_num)
    os.makedirs(ruta_salida, exist_ok=True)

    existentes = [f for f in os.listdir(ruta_salida) if f.lower().endswith(EXTS)]
    if existentes:
        print(f"[{carpeta_num}] ⏭️ Ya existen imágenes en salida, salto.")
        return 0

    # 0️⃣ Guardar una imagen de la carpeta img/(CarpetaNumero-8) como 1.png y aplicarle el sticker fijo
    try:
        carpeta_idx = int(carpeta_num) 
        carpeta_extra = os.path.join(RUTA_IMG, str(carpeta_idx))
        sticker_fijo_path = os.path.join(RAIZ_PROYECTO, "sticker", "sticker.png")
        salida_1 = os.path.join(ruta_salida, "1.png")

        if os.path.exists(carpeta_extra):
            imagenes_extra = [f for f in os.listdir(carpeta_extra) if f.lower().endswith(EXTS)]
            if imagenes_extra:
                archivo_aleatorio = random.choice(imagenes_extra)
                ruta_archivo = os.path.join(carpeta_extra, archivo_aleatorio)

                # Fondo (imagen aleatoria)
                fondo = image_from_bytes_rgba(_read_bytes_strong(ruta_archivo))

                # Si existe el sticker fijo → cargarlo y superponerlo
                if os.path.exists(sticker_fijo_path):
                    sticker = image_from_bytes_rgba(_read_bytes_strong(sticker_fijo_path))
                    sticker = sticker.resize(fondo.size, Image.LANCZOS)
                    combinado = Image.alpha_composite(fondo, sticker)
                    combinado.save(salida_1)
                    print(f"[{carpeta_num}] Guardado 1.png con sticker fijo desde img/{carpeta_idx}/{archivo_aleatorio}")
                else:
                    fondo.save(salida_1)
                    print(f"[{carpeta_num}] Guardado 1.png desde img/{carpeta_idx}/{archivo_aleatorio} (sin sticker fijo)")
            else:
                print(f"[{carpeta_num}] ⚠️ Carpeta img/{carpeta_idx} sin imágenes válidas")
        else:
            print(f"[{carpeta_num}] ⚠️ Carpeta img/{carpeta_idx} no existe")
    except Exception as e:
        print(f"[{carpeta_num}] Error guardando imagen de img/{carpeta_idx}: {e}")

    print(
        f"Procesando carpeta {carpeta_num} | Stickers: {len(idx_stickers)} | "
        f"Imagenes: {len(idx_imagenes)} | Usando {carpeta_c}"
    )
    if faltantes_img:
        print(f"[{carpeta_num}] ℹ️ No había imagen para: {faltantes_img}. Se usó la última imagen '{ult_img}' como relleno.")

    STICKERS.get_folder_pool(path_sticker_completo)

    generadas = 1  # ya generamos 1.png aleatoria con sticker fijo
    for i, (nombre_sticker, nombre_imagen, n) in enumerate(pares, start=2):
        path_i = os.path.join(ruta_carpeta_imagenes, nombre_imagen)
        try:
            fondo = image_from_bytes_rgba(_read_bytes_strong(path_i))

            sticker_bytes = STICKERS.get_sticker_bytes_by_num(path_sticker_completo, n)
            if sticker_bytes is None:
                fallback = STICKERS.get_last_sticker_bytes(path_sticker_completo)
                if not fallback:
                    raise UnidentifiedImageError(f"no hay sticker disponible para n={n}")
                sticker_bytes, last_n = fallback

            sticker = image_from_bytes_rgba(sticker_bytes)
            sticker = sticker.resize((736, 1312), Image.LANCZOS)
            if sticker.size[0] > fondo.size[0] or sticker.size[1] > fondo.size[1]:
                sticker = sticker.resize(fondo.size, Image.LANCZOS)

            combinada = Image.alpha_composite(fondo, sticker)

            # ⚠️ Saltar 2.png → empezar desde 3.png
            if i == 2:
                nombre_salida = "3.png"
            else:
                nombre_salida = f"{i}.png"

            combinada.save(os.path.join(ruta_salida, nombre_salida))
            generadas += 1
            print(f"[{carpeta_num}] Guardado {nombre_salida}  (match {n}: {nombre_sticker} + {nombre_imagen})")
        except Exception as e:
            print(f"[{carpeta_num}] Error combinando (match {n}): {nombre_sticker} + {nombre_imagen}: {e}")

    if generadas > 0:
        try:
            origen_carpeta = ruta_carpeta_imagenes
            fecha = datetime.now().strftime("%d-%m_%H-%M")
            nombre_origen = os.path.basename(path_imagenes.rstrip("/\\"))
            nuevo_nombre = f"{nombre_origen}_{fecha}"
            destino = os.path.join(base_usadas, nuevo_nombre)
            shutil.move(origen_carpeta, destino)
            print(f"[{carpeta_num}] Carpeta usada '{carpeta_c}' movida a '{destino}'")
        except Exception as e:
            print(f"[{carpeta_num}] Error moviendo carpeta usada: {e}")
    else:
        print(f"[{carpeta_num}] ⚠️ No se generó ninguna imagen; no se mueve la carpeta usada.")

    return generadas

# ================ Main ====================
def main():
    os.makedirs(base_salida, exist_ok=True)
    os.makedirs(base_usadas, exist_ok=True)

    generadas_total = 0
    if not carpetas:
        raise RuntimeError("⚠️ No hay archivos para realizar carruseles, Ideogram necesario.")

    max_workers = min(16, len(carpetas))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(procesar_carpeta, carpeta) for carpeta in carpetas]
        for future in as_completed(futures):
            r = future.result()
            if isinstance(r, int):
                generadas_total += r

    if generadas_total == 0:
        raise RuntimeError("⚠️ No hay archivos para realizar carruseles, Ideogram necesario.")

    print(f"✅ Carruseles generados en total: {generadas_total}")
    return generadas_total

if __name__ == "__main__":
    main()
