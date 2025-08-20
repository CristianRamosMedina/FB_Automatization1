import subprocess,io,time
from PIL import Image
from ..utils import get_screen_size,crear_funciones_con_serial,parse_coord
from ...config import ADB_PATH,pytesseract
def fechito(serial): 
    Width,Height =get_screen_size(serial)
    run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap,leerTextoEnRegion = crear_funciones_con_serial(serial)
    def capture_screen_bytes(serial):
        # Captura directa del screenshot en bytes
        resultado = subprocess.run([ADB_PATH, "-s", serial, 'exec-out', 'screencap', '-p'], capture_output=True)
        return resultado.stdout if resultado.returncode == 0 else None

    def read_region(region,serial):
        imagen_bytes = capture_screen_bytes(serial)
        if not imagen_bytes:
            print("⚠️ Error al capturar la pantalla.")
            return ""
        try:
            img = Image.open(io.BytesIO(imagen_bytes))
            img_crop = img.crop(region)
            # No se guarda en archivo, todo queda en memoria
            return pytesseract.image_to_string(img_crop, lang='eng').strip()
        except Exception as e:
            print(f"⚠️ Error al procesar imagen: {e} del serial {serial}")
            return ""
    # Leer fecha completa (mes día, año)
    def read_fecha_completa(serial):
        region_percent = ("6.85%", "27.87%", "91.14%", "36.27%")  # en porcentaje
        region = [
            parse_coord(region_percent[0], Width),   # x1
            parse_coord(region_percent[1], Height),  # y1
            parse_coord(region_percent[2], Width),   # x2
            parse_coord(region_percent[3], Height),  # y2
        ] 
        return read_region(region,serial)

    # Parsear texto de fecha → mes, día, año
    def parse_fecha(fecha_str,serial):
        try:
            print(f"🧾 Texto OCR crudo: '{fecha_str}'")
            parts = fecha_str.replace(",", "").split()
            mes = parts[0].capitalize()
            dia = int(parts[1])
            anio = int(parts[2])
            return mes, dia, anio
        except Exception as e:
            print(f"⚠️ Error al parsear fecha: {fecha_str}")
            return "", -1, -1

    # SWIPE por componente
    def swipe( x_percent, y_start_percent, y_end_percent, duration=300):
        x = parse_coord(x_percent, Width)
        y_start = parse_coord(y_start_percent, Height)
        y_end = parse_coord(y_end_percent, Height)

        run(f'shell input swipe {x} {y_start} {x} {y_end} {duration}')

    # Swipes con coordenadas relativas sin redondear
    def swipe_mes_up(): swipe("23.70%", "69.61%", "64.10%")
    def swipe_mes_down(): swipe("23.70%", "64.10%", "69.61%")

    def swipe_dia_up(): swipe("49.44%", "69.61%", "64.10%")
    def swipe_dia_down(): swipe("49.44%", "64.10%", "69.61%")

    def swipe_anio_up(): swipe("76.57%", "69.61%", "64.10%")
    def swipe_anio_down(): swipe("76.57%", "64.10%", "69.61%")

    # --- Lógica principal ---
    objetivo_mes = "April"
    objetivo_dia = 15
    objetivo_anio = 2006

    meses_orden = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    for intento in range(30):
        texto_fecha = read_fecha_completa(serial)
        mes, dia, anio = parse_fecha(texto_fecha,serial)
        print(f"[{intento+1}] Fecha detectada: {mes} {dia} {anio}")
        todo_ok = True

        # Mes
        if mes not in meses_orden:
            print("⚠️ Mes inválido detectado.")
        elif mes != objetivo_mes:
            print("🌀 Ajustando mes...")
            if meses_orden.index(mes) < meses_orden.index(objetivo_mes):
                swipe_mes_up()
            else:
                swipe_mes_down()
            todo_ok = False
        # Día
        if dia != objetivo_dia:
            print("🌀 Ajustando día...")
            if dia < objetivo_dia:
                swipe_dia_up()
            else:
                swipe_dia_down()
            todo_ok = False
        # Año
        if anio != objetivo_anio:
            print("🌀 Ajustando año...")
            if anio < objetivo_anio:
                swipe_anio_up()
            else:
                swipe_anio_down()
            todo_ok = False
        if todo_ok:
            print("✅ Fecha final alcanzada.")
            break
        time.sleep(0.6)
    else:
        print("❌ No se logró encontrar la fecha exacta.")
