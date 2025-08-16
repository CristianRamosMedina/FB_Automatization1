from ..adb_utils import  get_screen_size
from ..config import hilos_activos
import time
import re
import subprocess
from PIL import Image
from ..adb_utils import parse_coord
from paths import ADB_PATH,pytesseract
import difflib,io

def detener_funcion(serial):
    """Detiene cualquier función en ejecución para un dispositivo."""
    hilos_activos[serial] = False
    print(f"🛑 Señal enviada para detener funciones en {serial}")

def silenciar_dispositivo(serial):
    """Baja el volumen del dispositivo a 0."""
    run, tap, long_tap, move, write, buscarTextoEnRegion = crear_funciones_con_serial(serial)
    run("shell media volume --stream 3 --set 0")
    print(f"🔇 Dispositivo {serial} silenciado.")

def ejecteg(serial):
    """Sale a Home varias veces para resetear pantalla."""
    run, tap, long_tap, move, write, buscarTextoEnRegion = crear_funciones_con_serial(serial)
    for _ in range(4):
        run("shell input keyevent 4")

def cerrary_salir(serial):
    run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap = crear_funciones_con_serial(serial)
     
    run("shell input keyevent 224")  # Encender pantalla
    time.sleep(1)
    move("50%","68%","50%","20%")
    time.sleep(1)

    run("shell input keyevent 187")
    time.sleep(1.5)

    # Cerrar todas las ventanas: buscar y tocar "Cerrar todo" (Close all)
    coords = buscarTextoEnRegion(("5%", "5%", "95%", "95%"), "Close")  # o "Close all"
    if coords:
        tap(*coords)
    else:
        tap("50%", "78.3%") 

    time.sleep(3)
   
def get_screen_size(serial):
    try:
        result = subprocess.run([ADB_PATH, "-s", serial, "shell", "wm", "size"],
                              capture_output=True, text=True)
        output = result.stdout.strip()
        match = re.search(r'(\d+)x(\d+)', output)
        if match:
            width, height = int(match.group(1)), int(match.group(2))
            return width, height
    except:
        print("Error al obtener tamaño")
    return None, None


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

    return run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap
