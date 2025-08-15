import subprocess
import re
import io
import difflib
from PIL import Image
import pytesseract
from .config import ADB_PATH

# ------------------- FUNCIONES BASE ADB -------------------

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

def parse_coord(coord, base):
    """Convierte coordenadas en % o pixeles."""
    if isinstance(coord, str) and coord.endswith("%"):
        return int(float(coord.strip("%")) / 100 * base)
    return int(coord)

def crear_funciones_con_serial(serial):
    """Genera funciones adaptadas al tamaño del dispositivo."""
    Width, Height = get_screen_size(serial)

    def run(cmd):
        subprocess.run([ADB_PATH, "-s", serial] + cmd.split())

    def tap(x, y):
        run(f"shell input tap {parse_coord(x, Width)} {parse_coord(y, Height)}")

    def long_tap(x, y, duration=1000):
        run(f"shell input swipe {parse_coord(x, Width)} {parse_coord(y, Height)} "
            f"{parse_coord(x, Width)} {parse_coord(y, Height)} {duration}")

    def move(x1, y1, x2, y2, duration=300):
        run(f"shell input swipe {parse_coord(x1, Width)} {parse_coord(y1, Height)} "
            f"{parse_coord(x2, Width)} {parse_coord(y2, Height)} {duration}")

    def write(text):
        run(f'shell input text "{text}"')

    def buscarTextoEnRegion(region, *textos_buscados, umbral_similitud=None):
        """Busca texto en una región de la pantalla usando OCR."""
        try:
            resultado = subprocess.run(
                [ADB_PATH, "-s", serial, 'exec-out', 'screencap', '-p'],
                capture_output=True
            )
            imagen_bytes = resultado.stdout
            if not imagen_bytes:
                print("⚠️ Error al capturar la pantalla.")
                return None

            img_full = Image.open(io.BytesIO(imagen_bytes))
            region_abs = (
                parse_coord(region[0], Width),
                parse_coord(region[1], Height),
                parse_coord(region[2], Width),
                parse_coord(region[3], Height)
            )
            img_crop = img_full.crop(region_abs)

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
                            match = True

                    if match:
                        x_abs = region_abs[0] + data['left'][i] + data['width'][i] // 2
                        y_abs = region_abs[1] + data['top'][i] + data['height'][i] // 2
                        print(f"📍 '{texto}' encontrado en ({x_abs}, {y_abs})")
                        return x_abs, y_abs

            print(f"❌ Texto no encontrado: {textos_buscados}")
        except Exception as e:
            print(f"⚠️ Error OCR: {e}")
        return None

    return run, tap, long_tap, move, write, buscarTextoEnRegion
