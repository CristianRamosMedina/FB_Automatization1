import time,cv2,numpy as np,subprocess,io
from ..utils import get_screen_size,parse_coord,crear_funciones_con_serial
from PIL import Image
from ...config import ADB_PATH,pytesseract

def puzzle(serial):
    fallos = 0
    while fallos < 2:
        if detectarTextoObjetivo("Drag the puzzle piece into place", ("11.76%", "31.41%", "65.93%", "34.10%"),serial):
            print("Puzzle aún no resuelto.")
            mover_puzzle(serial)
            time.sleep(3)
            fallos = 0
        else:
            fallos += 1
            print(f"No detectado ({fallos}/2)")
            time.sleep(1)

def mover_puzzle(serial):
    Width,Height = get_screen_size(serial)
    run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap ,leerTextoEnRegion = crear_funciones_con_serial(serial)


    print("📸 Capturando pantalla...")
    img = capture_screen(serial)
    if img is None: return print("❌ No se pudo capturar la pantalla")

    print("✂️ Recortando áreas del puzzle...")

    coords_pct = {
        "completa": ("13.1%", "36.2%", "86.1%", "56.8%"),
        "origen":   ("13.1%", "36.2%", "28.4%", "56.8%"),
        "busqueda": ("28.4%", "36.2%", "86.1%", "56.8%"),
    }

    for k, (x1p, y1p, x2p, y2p) in coords_pct.items():
        box = (
            parse_coord(x1p, Width),
            parse_coord(y1p, Height),
            parse_coord(x2p, Width),
            parse_coord(y2p, Height)
        )
        img.crop(box).save(f"{k}.png")

    array_origen = cv2.cvtColor(np.array(Image.open("origen.png")), cv2.COLOR_RGB2BGR)
    array_busqueda = cv2.cvtColor(np.array(Image.open("busqueda.png")), cv2.COLOR_RGB2BGR)

    print("🎯 Detectando centro de pieza origen...")
    co = detectar_centro(array_origen, min_area=1000, debug_file="debug_pieza_origen.png", label="Origen")
    if co[0] is None: return print("❌ No se pudo detectar el centro de la pieza origen")

    print("🎯 Detectando centro de pieza destino...")
    cd = detectar_centro(array_busqueda, min_area=1000, debug_file="debug_pieza_destino.png", label="Destino")
    if cd[0] is None:
        print("⚠️ Método principal falló, probando método alternativo...")
        cd = detectar_centro(array_busqueda, min_area=1500, debug_file="debug_pieza_destino_alt.png", label="Destino ALT")
    if cd[0] is None: return print("❌ No se pudo detectar el centro de la pieza destino")

    print(f"✅ Origen: {co[0]}, {co[1]} | Destino: {cd[0]}, {cd[1]}")

    xo = parse_coord("13.1%", Width) + co[0]
    yo = parse_coord("36.2%", Height) + co[1]
    xd = parse_coord("28.4%", Width) + cd[0]
    yd = yo

    img_debug = np.array(img.convert("RGB"))
    cv2.rectangle(img_debug,
                  (parse_coord("13.1%", Width), parse_coord("36.2%", Height)),
                  (parse_coord("28.4%", Width), parse_coord("56.8%", Height)), (255, 0, 0), 2)
    cv2.rectangle(img_debug,
                  (parse_coord("28.4%", Width), parse_coord("36.2%", Height)),
                  (parse_coord("86.1%", Width), parse_coord("56.8%", Height)), (0, 255, 0), 2)
    cv2.circle(img_debug, (xo, yo), 8, (255, 0, 0), -1)
    cv2.circle(img_debug, (xd, yd), 8, (0, 255, 0), -1)
    cv2.arrowedLine(img_debug, (xo, yo), (xd, yo), (0, 255, 255), 4)
    cv2.putText(img_debug, f"Origen: ({xo}, {yo})", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
    cv2.putText(img_debug, f"Destino: ({xd}, {yo})", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
    cv2.imwrite("debug_movimiento_final.png", img_debug)

    print("🚀 Ejecutando movimiento...")
    run(f'shell input swipe {xo} {yo} {xd-120} {yo} 1500')
    print("✅ ¡Movimiento completado!")

def detectarTextoObjetivo(texto_objetivo, region, serial):
    Width,Height = get_screen_size(serial)
    run, tap, long_tap, move, write, buscarTextoEnRegion , leerTextoEnRegion = crear_funciones_con_serial(serial)

    resultado = subprocess.run([ADB_PATH, "-s", serial, "exec-out", "screencap", "-p"], capture_output=True)
    imagen_bytes = resultado.stdout
    if not imagen_bytes:
        print("⚠️ Error al capturar la pantalla.")
        return False

    try:
            
        
        img_full = Image.open(io.BytesIO(imagen_bytes))
        region_absoluta = (
            parse_coord(region[0], Width),
            parse_coord(region[1], Height),
            parse_coord(region[2], Width),
            parse_coord(region[3], Height)
        )

        img_crop = img_full.crop(region_absoluta)
     

        # Extraer texto con OCR
        texto_detectado = pytesseract.image_to_string(img_crop, lang='eng').strip().lower()
        print(f"🧠 Texto detectado: '{texto_detectado}'")
        return texto_objetivo.lower() in texto_detectado

    except Exception as e:
        print(f"❌ Error procesando imagen OCR: {e}")
        return False

def capture_screen(serial):
    run, tap, long_tap, move, write, buscarTextoEnRegion , leerTextoEnRegion = crear_funciones_con_serial(serial)
    resultado = subprocess.run([ADB_PATH, "-s", serial, "exec-out", "screencap", "-p"], capture_output=True)
    imagen_bytes = resultado.stdout
    if not imagen_bytes:
        print("⚠️ Error al capturar la pantalla.")
        return None
    return Image.open(io.BytesIO(imagen_bytes))

def detectar_centro(img_array, min_area=1000, debug_file=None, label="Centro"):
    gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    contornos_validos = [c for c in contours if cv2.contourArea(c) > min_area]
    if not contornos_validos: return None, None, None

    c = max(contornos_validos, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(c)
    cx, cy = x + w // 2, y + h // 2

    if debug_file:
        img_dbg = img_array.copy()
        cv2.drawContours(img_dbg, [c], -1, (255, 0, 0), 2)
        cv2.rectangle(img_dbg, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.circle(img_dbg, (cx, cy), 8, (0, 0, 255), -1)
        cv2.putText(img_dbg, f"{label}: ({cx}, {cy})", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.imwrite(debug_file, img_dbg)

    return cx, cy, c
