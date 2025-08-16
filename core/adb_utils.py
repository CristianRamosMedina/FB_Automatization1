import subprocess
import re
import io
import difflib
from PIL import Image
import pytesseract
from .paths import ADB_PATH
from google.oauth2 import service_account
from googleapiclient.discovery import build
from pathlib import Path
from datetime import datetime, timedelta
import os
import json
# ------------------- FUNCIONES BASE ADB -------------------

DISPOSITIVOS_JSON = "dispositivos.json"
CREDENTIALS_FILE = "credenciales.json"

def crear_service_drive():
    """Crea el servicio de Google Drive"""
    try:
        SCOPES = ['https://www.googleapis.com/auth/drive']
        credentials = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE, scopes=SCOPES
        )

        service = build('drive', 'v3', credentials=credentials)
        return service
    except Exception as e:
        print(f"❌ Error creando servicio Google Drive: {e}")

def get_screen_size(serial):
    """Obtiene tamaño de pantalla del dispositivo."""
    try:
        result = subprocess.run(
            [ADB_PATH, "-s", serial, "shell", "wm", "size"],
            capture_output=True, text=True
        )
        output = result.stdout.strip()
        match = re.search(r'(\d+)x(\d+)', output)
        if match:
            return int(match.group(1)), int(match.group(2))
    except:
        print("⚠️ Error al obtener tamaño de pantalla.")
    return None, None

def procesar_celular(serial, carpeta_imagenes):
    """Procesa un celular individual"""
    print(f"\n🚀 PROCESANDO CELULAR: {serial}")

    try:
        # Subir archivos y actualizar galería
        if subir_a_celular_con_scan(serial, carpeta_imagenes, "/sdcard/DCIM/Camera"):
            print(f"✅ CELULAR {serial} PROCESADO EXITOSAMENTE")
        else:
            print(f"❌ FALLÓ EL PROCESAMIENTO DE {serial}")

    except Exception as e:
        print(f"❌ Error procesando celular {serial}: {e}")
        import traceback
        traceback.print_exc()

def subir_a_celular_con_scan(serial, carpeta_origen, carpeta_destino):
    """Sube archivos al celular y actualiza la galería"""
    try:
        print(f"\n📱 Subiendo archivos a celular {serial}")

        # Verificar que la carpeta origen tenga archivos
        if not os.path.exists(carpeta_origen):
            print(f"❌ La carpeta {carpeta_origen} no existe")
            return False

        archivos = [f for f in os.listdir(carpeta_origen)
                   if os.path.isfile(os.path.join(carpeta_origen, f))
                   and f.lower().endswith(('.jpg', '.jpeg', '.png'))]

        if not archivos:
            print(f"❌ No hay archivos de imagen en {carpeta_origen}")
            return False

        # Ordenar archivos por número
        archivos.sort(key=extraer_numero)
        print(f"📦 Subiendo {len(archivos)} archivos ordenados")

        # Crear la carpeta destino si no existe
        try:
            subprocess.run([ADB_PATH, "-s", serial, "shell", "mkdir", "-p", carpeta_destino],
                           check=True, timeout=15, capture_output=True)
            print(f"📁 Carpeta {carpeta_destino} verificada/creada")
        except Exception as e:
            print(f"⚠️ Error creando carpeta (continuando): {e}")

        # Limpiar carpeta destino en el celular
        try:
            subprocess.run([ADB_PATH, "-s", serial, "shell", "rm", "-rf", f"{carpeta_destino}/*"],
                          check=True, timeout=30, capture_output=True)
            print(f"🧹 Carpeta {carpeta_destino} limpiada")
        except Exception as e:
            print(f"⚠️ Error limpiando carpeta (continuando): {e}")

        # Subir archivos uno por uno
        archivos_subidos = 0
        for archivo in archivos:
            ruta = str(Path(carpeta_origen, archivo).as_posix())  # <- ✅ esta línea resuelve el bug

            try:
                resultado = subprocess.run([ADB_PATH, "-s", serial, "push", ruta, carpeta_destino],
                                         check=True, timeout=60, capture_output=True)
                print(f"📲 Subido: {archivo}")
                archivos_subidos += 1
            except subprocess.TimeoutExpired:
                print(f"⏰ Timeout subiendo {archivo}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Error subiendo {archivo}: {e}")

        if archivos_subidos > 0:
            # Actualizar galería - múltiples métodos para asegurar que funcione
            print(f"🔄 Actualizando galería del celular {serial}...")

            try:
                # Método 1: Escanear carpeta específica
                subprocess.run([ADB_PATH, "-s", serial, "shell",
                              "am", "broadcast", "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE",
                              "-d", f"file://{carpeta_destino}"],
                              timeout=30, capture_output=True)

                # Método 2: Escanear todo el almacenamiento
                subprocess.run([ADB_PATH, "-s", serial, "shell",
                              "am", "broadcast", "-a", "android.intent.action.MEDIA_MOUNTED",
                              "-d", "file:///storage/emulated/0"],
                              timeout=30, capture_output=True)

                # Método 3: Forzar actualización de la base de datos de medios
                subprocess.run([ADB_PATH, "-s", serial, "shell",
                              "am", "broadcast", "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE",
                              "-d", "file:///storage/emulated/0/DCIM/"],
                              timeout=30, capture_output=True)

                print(f"✅ Galería actualizada para {serial}")

            except Exception as e:
                print(f"⚠️ Error actualizando galería (las fotos deberían aparecer eventualmente): {e}")

        print(f"📊 Resultado: {archivos_subidos}/{len(archivos)} archivos subidos a {serial}")
        return archivos_subidos > 0

    except Exception as e:
        print(f"❌ Error general en subida para {serial}: {e}")

def guardar_dispositivos(dispositivos):
    with open("dispositivos.json", "w") as f:
        json.dump(dispositivos, f, indent=2)

def modificar_fechas_en_orden(carpeta_path, intervalo_horas=1):
    carpeta = Path(carpeta_path)
    imagenes = [f for f in carpeta.iterdir() if f.suffix.lower() in {'.jpg', '.jpeg', '.png'}]
    imagenes.sort(key=lambda x: extraer_numero(x.name))

    fecha_inicio = datetime.now().replace(hour=15, minute=56, second=2, microsecond=0)
    for i, img in enumerate(imagenes):
        nueva_fecha = fecha_inicio + timedelta(hours=i * intervalo_horas)
        timestamp = nueva_fecha.timestamp()
        os.utime(img, (timestamp, timestamp))
        print(f"🕒 {img.name} => {nueva_fecha.strftime('%Y-%m-%d %H:%M:%S')}")

def extraer_numero(nombre_archivo):
    match = re.search(r'\d+', nombre_archivo)
    return int(match.group()) if match else float('inf')

def parse_coord(coord, base):
    """Convierte coordenadas en % o pixeles."""
    if isinstance(coord, str) and coord.endswith("%"):
        return int(float(coord.strip("%")) / 100 * base)
    return int(coord)
