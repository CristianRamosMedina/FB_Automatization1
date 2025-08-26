import subprocess
import re
from core.paths import ADB_PATH               
from google.oauth2 import service_account
from googleapiclient.discovery import build
from pathlib import Path
from datetime import datetime, timedelta
import os
import json
from PIL import Image
import io
from .config import pytesseract
import difflib
from core.paths import DISPOSITIVOS_FILE, SERVICE_ACCOUNT_FILE

# ------------------- FUNCIONES BASE ADB -------------------



def crear_service_drive():
    """Crea el servicio de Google Drive"""
    try:
        SCOPES = ['https://www.googleapis.com/auth/drive']
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
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
    with open("data/dispositivos.json", "w") as f:
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

def crear_funciones_con_serial(serial):
    Width,Height = get_screen_size(serial)

    def run(cmd):
        subprocess.run([ADB_PATH, "-s", serial] + cmd.split())

    def parse_hex_color(c):
        # Acepta "#RRGGBB", "RRGGBB" o tupla (R,G,B)
        if isinstance(c, (tuple, list)) and len(c) == 3:
            return tuple(int(v) for v in c)
        c = c.strip()
        if c.startswith("#"):
            c = c[1:]
        if len(c) != 6:
            raise ValueError(f"Color inválido: {c}")
        r = int(c[0:2], 16)
        g = int(c[2:4], 16)
        b = int(c[4:6], 16)
        return (r,g,b)

    def _dentro_tolerancia(rgb, objetivo, tol):
        return (abs(rgb[0]-objetivo[0]) <= tol and
                abs(rgb[1]-objetivo[1]) <= tol and
                abs(rgb[2]-objetivo[2]) <= tol)

    def tap(x, y):
        x = parse_coord(x, Width)
        y = parse_coord(y, Height)
        run(f"shell input tap {x} {y}")

    def long_tap(x, y, duration=1000):
        x = parse_coord(x, Width)
        y = parse_coord(y, Height)
        run(f"shell input swipe {x} {y} {x} {y} {duration}")

    def move(x1, y1, x2, y2, duration=300):
        x1 = parse_coord(x1, Width)
        y1 = parse_coord(y1, Height)
        x2 = parse_coord(x2, Width)
        y2 = parse_coord(y2, Height)
        run(f"shell input swipe {x1} {y1} {x2} {y2} {duration}")

    def buscarTextoEnRegion(region, *textos_buscados, umbral_similitud=None):
        try:
            resultado = subprocess.run([ADB_PATH, "-s", serial, 'exec-out', 'screencap', '-p'], capture_output=True)
            imagen_bytes = resultado.stdout
            if not imagen_bytes:
                print("⚠️ Error al capturar la pantalla.")
                return None

            img_full = Image.open(io.BytesIO(imagen_bytes))

            region_absoluta = (
                parse_coord(region[0], Width),
                parse_coord(region[1], Height),
                parse_coord(region[2], Width),
                parse_coord(region[3], Height)
            )

            img_crop = img_full.crop(region_absoluta)

            data = pytesseract.image_to_data(img_crop, lang='eng', output_type=pytesseract.Output.DICT)

            for i in range(len(data['text'])):
                palabra = data['text'][i].strip().lower()
                if not palabra:
                    continue

                for texto in textos_buscados:
                    texto_buscado = texto.lower()

                    match = False
                    if umbral_similitud is None:
                        if texto_buscado in palabra:
                            match = True
                    else:
                        ratio = difflib.SequenceMatcher(None, palabra, texto_buscado).ratio()
                        if ratio >= umbral_similitud:
                            print(f"🔍 Similitud {ratio:.2f} entre '{palabra}' y '{texto_buscado}'")
                            match = True

                    if match:
                        x_rel = data['left'][i]
                        y_rel = data['top'][i]
                        w = data['width'][i]
                        h = data['height'][i]
                        x_abs = region_absoluta[0] + x_rel + w // 2
                        y_abs = region_absoluta[1] + y_rel + h // 2
                        print(f"📍 Texto '{texto}' encontrado en ({x_abs}, {y_abs})")
                        return x_abs, y_abs

            print(f"❌ Ningún texto encontrado: {textos_buscados}")
        except Exception as e:
            print(f"⚠️ Error al procesar OCR: {e}")
        return None

    def write(text):
        run(f'shell input text "{text}"')

    # ============================
    # 🔎 Detección de color + Tap
    # ============================
    def detectarColorOTap(
        color_objetivo,
        region=None,
        tolerancia=25,
        tap_si_no=("50%","50%"),
        muestreo=64,
        exigir_pixeles=1
    ):
        """
        Busca un color dentro de una región (o toda la pantalla).
        - color_objetivo: "#RRGGBB", "RRGGBB" o (R,G,B)
        - region: (x1,y1,x2,y2) en porcentaje o px. Si None, usa toda la pantalla.
        - tolerancia: 0-255 por canal.
        - tap_si_no: (x,y) en porcentaje o px si NO se detecta el color.
        - muestreo: reduce la imagen a NxN para acelerar.
        - exigir_pixeles: cuántos píxeles que coincidan (>=) se requieren para darlo por detectado.
        Retorna: dict {"detectado": bool, "encontrados": int}
        """
        try:
            # Captura pantalla
            resultado = subprocess.run([ADB_PATH, "-s", serial, 'exec-out', 'screencap', '-p'], capture_output=True)
            imagen_bytes = resultado.stdout
            if not imagen_bytes:
                print("⚠️ Error al capturar la pantalla.")
                # En caso de falla, hacer tap para no frenar el flujo
                tx, ty = tap_si_no
                tap(tx, ty)
                return {"detectado": False, "encontrados": 0}

            img = Image.open(io.BytesIO(imagen_bytes)).convert("RGB")

            if region is None:
                x1, y1, x2, y2 = 0, 0, Width, Height
            else:
                x1 = parse_coord(region[0], Width)
                y1 = parse_coord(region[1], Height)
                x2 = parse_coord(region[2], Width)
                y2 = parse_coord(region[3], Height)

            # Normaliza bounding box
            x1, x2 = sorted((max(0, x1), min(Width, x2)))
            y1, y2 = sorted((max(0, y1), min(Height, y2)))

            if x2 <= x1 or y2 <= y1:
                print("⚠️ Región inválida para detección de color; haciendo tap fallback.")
                tx, ty = tap_si_no
                tap(tx, ty)
                return {"detectado": False, "encontrados": 0}

            crop = img.crop((x1, y1, x2, y2))

            # Redimensiona para muestrear menos píxeles (más rápido)
            try:
                crop_small = crop.resize((muestreo, muestreo), Image.BILINEAR)
            except Exception:
                crop_small = crop

            objetivo = parse_hex_color(color_objetivo)
            encontrados = 0

            # Recorre píxeles
            px = crop_small.load()
            w, h = crop_small.size
            for yy in range(h):
                for xx in range(w):
                    if _dentro_tolerancia(px[xx, yy], objetivo, tolerancia):
                        encontrados += 1
                        if encontrados >= exigir_pixeles:
                            print(f"🎯 Color detectado (>= {exigir_pixeles} píxeles) en región {x1,y1,x2,y2}")
                            return {"detectado": True, "encontrados": encontrados}

            # No detectado → Tap fallback
            print(f"❌ Color no detectado (encontrados={encontrados} < {exigir_pixeles}). Haciendo tap en {tap_si_no}...")
            tx, ty = tap_si_no
            tap(tx, ty)
            return {"detectado": False, "encontrados": encontrados}

        except Exception as e:
            print(f"⚠️ Error en detectarColorOTap: {e}. Haciendo tap fallback.")
            tx, ty = tap_si_no
            tap(tx, ty)
            return {"detectado": False, "encontrados": 0}

    
       
    def leerTextoEnRegion(region):
        resultado = subprocess.run([ADB_PATH, "-s", serial, 'exec-out', 'screencap', '-p'], capture_output=True)
        imagen_bytes = resultado.stdout
        if not imagen_bytes:
            return ""
        img_crop = Image.open(io.BytesIO(imagen_bytes)).crop(region)
        texto = pytesseract.image_to_string(img_crop, lang='eng').strip().lower()
        print(f"🧠 Texto detectado: '{texto}'")
        return texto

    
    return run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap,leerTextoEnRegion
    

import os, json

VIDEOS_FILE = "data/videos.json"

def cargar_videos():
    if not os.path.exists(VIDEOS_FILE):
        return {}
    with open(VIDEOS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_videos(data):
    with open(VIDEOS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def marcar_cuenta_subida(serial, cuenta, dispositivos):
    data_serial = dispositivos.get(serial, {})
    if cuenta in data_serial.get("cuentasPorSubir", []):
        data_serial["cuentasPorSubir"].remove(cuenta)
        data_serial["cuentasSubidas"].append(cuenta)
    guardar_videos(dispositivos)
