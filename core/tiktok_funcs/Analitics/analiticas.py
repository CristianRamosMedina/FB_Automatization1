from ...adb_utils import crear_funciones_con_serial, parse_coord,get_screen_size
import time, io, subprocess, pytesseract, re
from ..utils import cerrary_salir, ejecteg
from ...paths import ADB_PATH
from PIL import Image
from core import config
import json

def capturar_post_views(serial, archivo_json="data/analiticas.json"):
    import json, io, subprocess, re
    from PIL import Image
    import pytesseract
    from ...paths import ADB_PATH

    def parse_coord(value, size):
        """Convierte '23%' -> píxel absoluto según size."""
        if isinstance(value, str) and value.endswith("%"):
            return int(float(value.strip("%")) / 100 * size)
        return int(value)

    def parse_num(txt):
        """Convierte tokens tipo 25K / 2.4M / 3B en enteros."""
        txt = txt.replace(",", "").replace(" ", "")
        match = re.match(r"(\d+(?:\.\d+)?)([KMBkmb]?)", txt)
        if not match:
            return None
        num, sufijo = match.groups()
        try:
            val = float(num)
        except:
            return None
        sufijo = sufijo.upper()
        if sufijo == "K":
            val *= 1_000
        elif sufijo == "M":
            val *= 1_000_000
        elif sufijo == "B":
            val *= 1_000_000_000
        return int(val)

    def extraer_post_views(texto):
        """Devuelve el primer número válido encontrado en el OCR."""
        candidatos = re.split(r"[\s\n]+", texto)
        for token in candidatos:
            val = parse_num(token)
            if val:
                return val
        return None

    # Captura de pantalla
    resultado = subprocess.run([ADB_PATH, "-s", serial, "exec-out", "screencap", "-p"], capture_output=True)
    img_bytes = resultado.stdout
    if not img_bytes:
        print("❌ No se pudo capturar pantalla.")
        return

    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    Width, Height = img.size

    # Región Post views (ajustada en porcentajes)
    region_post_percent = ("6.94%", "29.56%", "48.47%", "36.25%")
    region_post = (
        parse_coord(region_post_percent[0], Width),
        parse_coord(region_post_percent[1], Height),
        parse_coord(region_post_percent[2], Width),
        parse_coord(region_post_percent[3], Height)
    )
    img_crop = img.crop(region_post)

    # OCR: más flexible
    config = "--psm 6"
    texto = pytesseract.image_to_string(img_crop, lang="eng", config=config).strip()
    print("📝 Texto OCR Post views:", repr(texto))

    numero = extraer_post_views(texto)

    if numero is None:
        print("⚠️ No se pudo leer Post views.")
        return

    print(f"📊 Post views detectado: {numero}")

    # Guardar en JSON
    try:
        with open(archivo_json, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = {}

    if serial not in data:
        data[serial] = {}

    data[serial]["post_views"] = numero

    with open(archivo_json, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"💾 Guardado en {archivo_json}")


def Reconocer_Mes(serial):
    """
    Reconoce el mes y año visibles en el selector de Analytics (ej: 'September 2025').
    """
    Width, Height = get_screen_size(serial)
    run, *_ = crear_funciones_con_serial(serial)

    def capture_screen_bytes():
        resultado = subprocess.run(
            [ADB_PATH, "-s", serial, 'exec-out', 'screencap', '-p'],
            capture_output=True
        )
        return resultado.stdout if resultado.returncode == 0 else None

    def read_region(region):
        imagen_bytes = capture_screen_bytes()
        if not imagen_bytes:
            print("⚠️ Error al capturar pantalla.")
            return ""
        try:
            img = Image.open(io.BytesIO(imagen_bytes))
            img_crop = img.crop(region)
            return pytesseract.image_to_string(img_crop, lang='eng').strip()
        except Exception as e:
            print(f"⚠️ Error al procesar OCR: {e}")
            return ""

    # Región del encabezado "September 2025"
    region_percent = ("22.22%", "53.18%", "76.11%", "57.18%")
    region = [
        parse_coord(region_percent[0], Width),
        parse_coord(region_percent[1], Height),
        parse_coord(region_percent[2], Width),
        parse_coord(region_percent[3], Height),
    ]

    texto = read_region(region)
    print(f"🧾 OCR crudo encabezado: '{texto}'")

    # Normalizar
    meses_orden = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    for mes in meses_orden:
        if mes.lower() in texto.lower():
            # Buscar año (4 dígitos)
            match = re.search(r"(20\d{2})", texto)
            anio = match.group(1) if match else ""
            mes_final = f"{mes} {anio}".strip()
            print(f"📆 Mes detectado: {mes_final}")
            return mes_final

    print("⚠️ No se reconoció un mes válido.")
    return None


def Reconocer_Dias(serial):
    """
    Devuelve posiciones absolutas de los días (1-31) en un dict.
    Siempre asegura que el día 1 esté presente.
    """
    run, tap, *_ = crear_funciones_con_serial(serial)

    # Captura de pantalla
    resultado = subprocess.run([ADB_PATH, "-s", serial, 'exec-out', 'screencap', '-p'], capture_output=True)
    imagen_bytes = resultado.stdout
    if not imagen_bytes:
        print("❌ No se pudo capturar pantalla.")
        return {}

    img = Image.open(io.BytesIO(imagen_bytes)).convert("RGB")

    # Región de días
    Width, Height = img.size
    region_dias = (
        int(0.05 * Width),   # x1
        int(0.30 * Height),  # y1
        int(0.95 * Width),   # x2
        int(0.95 * Height)   # y2
    )
    img_crop = img.crop(region_dias)

    # OCR restringido a números
    config = "--psm 6 -c tessedit_char_whitelist=0123456789"
    data = pytesseract.image_to_data(img_crop, lang="eng", config=config, output_type=pytesseract.Output.DICT)

    dias = {}
    candidatos_dia1 = []

    for i, txt in enumerate(data["text"]):
        txt = txt.strip()
        if txt.isdigit():
            dia = int(txt)

            if 1 <= dia <= 31:
                # Evitar duplicados (ejemplo: 11 no pisa al 1)
                if dia in dias:
                    continue

                # Coordenadas absolutas
                x_rel = data["left"][i] + data["width"][i] // 2
                y_rel = data["top"][i] + data["height"][i] // 2
                x_abs = region_dias[0] + x_rel
                y_abs = region_dias[1] + y_rel
                dias[dia] = (x_abs, y_abs)

                # Guardar posibles candidatos a "día 1"
                if dia == 1:
                    candidatos_dia1.append((x_abs, y_abs))

    # Forzar día 1 si no fue reconocido
    if 1 not in dias and candidatos_dia1:
        # Tomar el más a la izquierda (menor x)
        candidato = sorted(candidatos_dia1, key=lambda c: c[0])[0]
        dias[1] = candidato
        print(f"⚠️ Día 1 no reconocido claramente, usando candidato en {candidato}")
    elif 1 not in dias:
        print("⚠️ Día 1 no detectado, insertando coordenada aproximada.")
        dias[1] = (region_dias[0] + 50, region_dias[1] + 50)  # fallback

    print(f"📅 Días reconocidos: {sorted(dias.keys())}")
    return dias

def Tap_Dia(serial, dia):
    """
    Hace tap en un día específico.
    Si no existe, usa el último día detectado.
    Devuelve el día realmente usado.
    """
    run, tap, *_ = crear_funciones_con_serial(serial)
    dias = Reconocer_Dias(serial)

    if dia in dias:
        x, y = dias[dia]
        print(f"👉 Tap en día {dia} ({x}, {y})")
        tap(x, y)
        return dia
    else:
        if dias:
            ultimo = max(dias.keys())
            x, y = dias[ultimo]
            print(f"⚠️ Día {dia} no encontrado, usando último disponible ({ultimo}) en ({x}, {y})")
            tap(x, y)
            time.sleep(0.5)
            tap(x, y)  # 🔁 segundo tap por seguridad
            return ultimo
        else:
            print("❌ No se encontraron días en pantalla.")
            return None




def Tap_Update(serial):
    """
    Busca y hace tap en el botón Update.
    Si no lo detecta, usa fallback en el centro abajo.
    """
    run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap, leerTextoEnRegion = crear_funciones_con_serial(serial)

    coords = None
    try:
        coords = buscarTextoEnRegion(("5%", "85%", "95%", "98%"), "Update", "Apply", "Done", "Set")
    except Exception:
        pass

    if coords:
        print(f"✅ Botón Update encontrado en {coords}, haciendo tap...")
        tap(*coords)
    else:
        print("⚠️ Botón Update no detectado, usando fallback.")
        tap("50%", "92%")  # centro inferior
    

def analiticas(serial):
    run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap, leerTextoEnRegion = crear_funciones_con_serial(serial)

    # Preparar dispositivo
    run("shell input keyevent 224")
    time.sleep(1)
    move("50%", "68%", "50%", "20%")
    time.sleep(1)
    cerrary_salir(serial)
    ejecteg(serial)

    print(f"\n🚀 Abriendo TikTok en {serial}...")
    run("shell monkey -p com.zhiliaoapp.musically -c android.intent.category.LAUNCHER 1")
    time.sleep(5)

    # Ir al perfil
    long_tap("90.09%", "92.31%")
    time.sleep(0.6)
    coords = buscarTextoEnRegion(("2.13%", "2.13%", "99.35%", "13.75%"), "Cancel")
    if coords:
        tap(*coords)
        time.sleep(0.6)
        tap("95.29%", "5.50%")
    else:
        tap("95.29%", "5.50%")
    time.sleep(1.2)

    # Ir a Settings / Studio
    coords = buscarTextoEnRegion(("2.13%", "57.64%", "99.35%", "93.75%"), "Studio")
    if coords:
        tap(*coords)
    else:
        tap("50%", "71.06%")
    time.sleep(2.1)

    # Abrir sección "All"
    coords = buscarTextoEnRegion(("2.71%", "14.25%", "100.00%", "36.06%"), "all")
    if coords:
        tap(*coords)
    else:
        tap("85.71%", "17.50%")
    time.sleep(5)

    # Abrir Custom
    move("53.57%", "16.94%", "14.00%", "16.94%")
    coords = buscarTextoEnRegion(("2.71%", "14.25%", "100.00%", "36.06%"), "custom")
    if coords:
        tap(*coords)
    else:
        tap("91.29%", "16.94%")
    time.sleep(1.2)

    # 📌 Forzar mes y seleccionar días
    mes_detectado = Reconocer_Mes(serial)
    if mes_detectado:
        print(f"📆 Mes actual detectado: {mes_detectado}")
    else:
        print("⚠️ No se detectó mes, usando valor de config.")
        mes_detectado = config.MES_OBJETIVO

    Tap_Dia(serial, config.DIA_INICIO)
    time.sleep(1)
    Tap_Dia(serial, config.DIA_FIN)
    time.sleep(1)

    # Pulsar Update
    coords = buscarTextoEnRegion(("2.63%", "93%", "97.22%", "99.12%"), "Update")
    if coords:
        tap(*coords)
    else:
        tap("50%", "90%")
        
    time.sleep(4)  # esperar que cargue la pantalla de métricas
    capturar_post_views(serial)
    

    print(f"✅ Rango aplicado correctamente: {config.MES_OBJETIVO} {config.DIA_INICIO}-{config.DIA_FIN}")
