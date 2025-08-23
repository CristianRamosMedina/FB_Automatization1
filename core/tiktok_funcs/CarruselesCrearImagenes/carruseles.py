import os
import io
import json
import shutil
from PIL import Image
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from concurrent.futures import ThreadPoolExecutor, as_completed
from ..utils import AbrirJsonCarruseles

# Cargo las carpetas desde JSON
carpetas = AbrirJsonCarruseles()
ruta_documentos = os.path.expanduser("~/Documents")

base_salida = os.path.join(ruta_documentos, "Carrusel", "ImagenesCrudas", "Carrusel")
base_usadas = os.path.join(ruta_documentos, "Carrusel", "ImagenesCrudas", "ImagenCrudaUsada")

SERVICE_ACCOUNT_FILE = "data/credenciales.json"
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

carpetas_descargadas = set()


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
                print(f"Descargando: {file['name']}")
                request = drive_service.files().get_media(fileId=file["id"])
                with io.FileIO(file_path, "wb") as fh:
                    downloader = MediaIoBaseDownload(fh, request)
                    done = False
                    while not done:
                        status, done = downloader.next_chunk()
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


def ordenar_natural(lista):
    import re
    def alfanum(clave):
        return [int(t) if t.isdigit() else t.lower()
                for t in re.split('([0-9]+)', clave)]
    return sorted(lista, key=alfanum)


def procesar_carpeta(carpeta):
    carpeta_num = carpeta["CarpetaNumero"]
    path_sticker = carpeta["pathSticker"]   # ruta relativa a Documentos
    path_imagenes = carpeta["pathImagenes"] # ruta relativa a Documentos

    # Descarga y asegura carpetas
    asegurar_y_descargar(path_sticker, carpeta["driveIdSticker"])
    os.makedirs(os.path.join(ruta_documentos, path_imagenes), exist_ok=True)

    # Rutas absolutas
    path_sticker_completo = os.path.join(ruta_documentos, path_sticker)
    path_imagenes_completo = os.path.join(ruta_documentos, path_imagenes)

    subcarpetas_c = [d for d in os.listdir(path_imagenes_completo)
                     if os.path.isdir(os.path.join(path_imagenes_completo, d)) and d.startswith("c")]

    if not subcarpetas_c:
        print(f"No se encontró carpeta 'c*' en {path_imagenes_completo}")
        return

    carpeta_c = ordenar_natural(subcarpetas_c)[0]
    ruta_carpeta_imagenes = os.path.join(path_imagenes_completo, carpeta_c)

    stickers = ordenar_natural([
        f for f in os.listdir(path_sticker_completo) if f.lower().endswith(('.png', '.jpg', '.jpeg'))
    ])
    imagenes = ordenar_natural([
        f for f in os.listdir(ruta_carpeta_imagenes) if f.lower().endswith(('.png', '.jpg', '.jpeg'))
    ])

    # ✅ Repetir la última imagen hasta igualar la cantidad de stickers
    if len(imagenes) < len(stickers) and imagenes:
        ultima = imagenes[-1]
        diferencia = len(stickers) - len(imagenes)
        imagenes.extend([ultima] * diferencia)

    emparejados = zip(stickers, imagenes)
    ruta_salida = os.path.join(base_salida, carpeta_num)

    if os.path.exists(ruta_salida):
        archivos_existentes = [f for f in os.listdir(ruta_salida) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if archivos_existentes:
            print(f"Ya existen imágenes en '{carpeta_num}', se omite para evitar duplicados.")
            return

    os.makedirs(ruta_salida, exist_ok=True)
    print(f"Procesando carpeta {carpeta_num} | Stickers: {len(stickers)} | Imagenes: {len(imagenes)} | Usando {carpeta_c}")

    for i, (nombre_sticker, nombre_imagen) in enumerate(emparejados, start=1):
        path_s = os.path.join(path_sticker_completo, nombre_sticker)
        path_i = os.path.join(ruta_carpeta_imagenes, nombre_imagen)

        try:
            fondo = Image.open(path_i).convert("RGBA")
            sticker = Image.open(path_s).convert("RGBA")
            sticker = sticker.resize((736, 1312), Image.LANCZOS)

            if sticker.size[0] > fondo.size[0] or sticker.size[1] > fondo.size[1]:
                sticker = sticker.resize(fondo.size)

            combinada = Image.alpha_composite(fondo, sticker)
            nombre_salida = f"{i}.png"
            combinada.save(os.path.join(ruta_salida, nombre_salida))

            print(f"[{carpeta_num}] Guardado {nombre_salida}")
        except Exception as e:
            print(f"[{carpeta_num}] Error combinando: {nombre_sticker} + {nombre_imagen}: {e}")

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


def main():
    os.makedirs(base_salida, exist_ok=True)
    os.makedirs(base_usadas, exist_ok=True)
    # hilos de trabajo
    max_workers = min(16, len(carpetas))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(procesar_carpeta, carpeta) for carpeta in carpetas]
        for future in as_completed(futures):
            future.result()


if __name__ == "__main__":
    main()
