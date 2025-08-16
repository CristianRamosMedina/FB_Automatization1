

import threading,subprocess,os,json,io,time
from core.config import switchAccount
from core.tiktok_funcs.utils import ejecteg,cerrary_salir,get_screen_size
from adb_utils import parse_coord
from paths import ADB_PATH,pytesseract
from PIL import Image

BASE_PATH = os.path.join(
    os.path.expanduser("~/Documents"),
    "Carrusel", "ImagenesCrudas", "Carrusel"
)


def TitkokCuentas(serial, cooldown=2.0, cierre_cada=3):
    fallos = 0
    while True:
        try:
            ejecteg(serial)
            switchAccount(serial)

            resultado = escanear_cuentas_tiktok(serial)
            motivo = resultado.get("motivo_fin")
            asignadas = resultado.get("asignadas", [])
            total_detectadas = resultado.get("total_detectadas", set())

            # ✅ Éxito
            if motivo == "ok" and asignadas:
                print("✅ Flujo completado: cuentas asignadas y guardadas.")
                return asignadas

            # 🛑 Caso final
            if motivo == "sin_carpetas":
                print("🛑 Hay cuentas, pero no se pudo asignar ninguna carpeta.")
                return []

            # ❌ No se detectaron cuentas → cerrar y volver a intentar
            if motivo == "sin_cuentas":
                print("⚠️ No se detectaron cuentas. Cerrando y reintentando...")
                try:
                    cerrary_salir(serial)
                except Exception as e:
                    print(f"⚠️ Error al cerrar apps: {e}")
                time.sleep(cooldown)
                continue  # reintenta desde el inicio

            # ⚠️ Cuentas detectadas pero sin asignar
            elif total_detectadas and not asignadas:
                print("⚠️ Se detectaron cuentas pero no hubo asignaciones.")
                fallos += 1

            # Estado inesperado
            else:
                print("⚠️ Estado no esperado.")
                fallos += 1

            # Intento de despegar cada cierto número de fallos
            if fallos % max(1, cierre_cada) == 0:
                try:
                    print("🧹 Intento de despegar: cerrando apps recientes...")
                    cerrary_salir(serial)
                except Exception as e:
                    print(f"⚠️ Error en cerrary_salir: {e}")

            time.sleep(cooldown)

        except Exception as e:
            print(f"💥 Error en TitkokCuentas: {e}")
            try:
                cerrary_salir(serial)
            except Exception as e2:
                print(f"⚠️ Error al cerrar apps: {e2}")
            time.sleep(cooldown)
            continue


def listar_carpetas_locales_ordenadas():
    carpetas = []
    for nombre in os.listdir(BASE_PATH):
        ruta = os.path.join(BASE_PATH, nombre)
        if os.path.isdir(ruta):
            carpetas.append({
                "name": nombre,
                "path": ruta
            })
    carpetas.sort(key=lambda c: c["name"])  # ordenar por nombre
    return carpetas

carpetas_disponibles = listar_carpetas_locales_ordenadas()
lock = threading.Lock()

asignaciones_fijas = {
    "rachelshine.tips": "1",
    "naomiwellness.tip": "2",
    "naomiwelliness.tip": "2",
    "brooklyn.tipss": "3",
    "kristencare.healt": "4",
    "rebeccafresh.healthh": "5",
    "harper.health8": "6",
    "alexa.tips": "7",
    "alejandrahealth": "8",
    "ivyfresh.tips": "9",
    "jessicafit.tipss": "10",
    "ambervital.tips": "11",
    "brookecalm.tipss": "12",
    "harper.tipss": "13",
    "daniellecare.healthh": "14",
    "chloebeauty.health": "15",
    "taylorlife.healthh": "16",
    "nicolehealth.health": "17",
    "paigewellness.healthh": "18",
    "paigewelliness.healthh": "18",
    "sabrinaroutine.tipss": "19",
    "tayloractive.health": "20",
    "emilyfit.tips": "21",
    "fionasmooth.tipss": "22",
    "ursulawellness.tips": "23",
    "natalieglow.tipss": "24",
    "hannahwellness.healthh": "25",
    "hannahwelliness.healthh": "25",
    "victoriaglow.tipss": "26",
    "rachelsmooth.tipss": "27",
    "samanthafresh.health": "28",
    "daisysmooth.tipss": "29",
    "elainebeauty.health": "30",
    "francescarefresh.healthh": "31",
    "candiceglow.tips": "32",
    "georgiacare.tips": "33"
}


def normalizar_nombre(nombre):
    return nombre.strip().lower()

def buscar_carpeta_por_nombre(nombre_objetivo):
    for carpeta in carpetas_disponibles:
        if carpeta["name"] == nombre_objetivo:
            return carpeta
    return None

def escanear_cuentas_tiktok(serial):
 
    global carpeta_idx_global
    carpeta_idx_global = 0
    Width, Heigth = get_screen_size(serial)

    print(f"🔍 Escaneando cuentas en TikTok del {serial}...")

    todas_cuentas = set()
    scrolls = 0
    max_scrolls = 10

    while scrolls < max_scrolls:
        cuentas_actuales, hay_add = detectar_usuarios_en_pantalla(serial)

        if hay_add and scrolls == 0:
            print("🛑 'Add account' detectado al abrir el menú. No hay más cuentas para escanear.")
            todas_cuentas.update(cuentas_actuales)
            break

        nuevas = set(cuentas_actuales) - todas_cuentas
        if nuevas:
            print(f"➕ Nuevas: {nuevas}")
            todas_cuentas.update(nuevas)
        else:
            print("⛔ No hay nuevas cuentas, deteniendo scroll.")
            break

        # Scroll
        x1 = parse_coord("46.30%", Width)
        y1 = parse_coord("72.65%", Heigth)
        x2 = parse_coord("46.30%", Width)
        y2 = parse_coord("34.19%", Heigth)
        subprocess.run([ADB_PATH, "-s", serial, "shell", "input", "swipe",
                        str(x1), str(y1), str(x2), str(y2)])
        time.sleep(2)
        scrolls += 1

    print(f"✅ Total de cuentas encontradas: {todas_cuentas}")

    # Si no se detectó ninguna cuenta en este escaneo → no guardamos y señalamos para reintentar
    if not todas_cuentas:
        print("❌ No se detectaron cuentas en este escaneo.")
        return {
            "asignadas": [],
            "total_detectadas": set(),
            "motivo_fin": "sin_cuentas"
        }

    cuentas_con_carpetas = []
    carpetas_reservadas = set(asignaciones_fijas.values())
    carpetas_disponibles_filtradas = [c for c in carpetas_disponibles if c["name"] not in carpetas_reservadas]

    with lock:
        # Asignar cuentas fijas
        for cuenta in todas_cuentas:
            cuenta_norm = normalizar_nombre(cuenta)
            if cuenta_norm in asignaciones_fijas:
                nombre_carpeta_fija = asignaciones_fijas[cuenta_norm]
                carpeta_fija = buscar_carpeta_por_nombre(nombre_carpeta_fija)
                if carpeta_fija:
                    cuentas_con_carpetas.append({
                        "cuenta": cuenta,
                        "carpeta_path": carpeta_fija["path"],
                        "carpeta_nombre": carpeta_fija["name"]
                    })
                    print(f"📌 Cuenta fija: {cuenta} → {carpeta_fija['name']}")
                else:
                    print(f"⚠️ Carpeta fija '{nombre_carpeta_fija}' para {cuenta} no encontrada. No se guardará esta cuenta.")

        # Asignar dinámicamente
        for cuenta in todas_cuentas:
            cuenta_norm = normalizar_nombre(cuenta)
            if cuenta_norm in asignaciones_fijas:
                continue
            if carpeta_idx_global < len(carpetas_disponibles_filtradas):
                carpeta = carpetas_disponibles_filtradas[carpeta_idx_global]
                carpeta_idx_global += 1
                cuentas_con_carpetas.append({
                    "cuenta": cuenta,
                    "carpeta_path": carpeta["path"],
                    "carpeta_nombre": carpeta["name"]
                })
                print(f"📦 Cuenta asignada: {cuenta} → {carpeta['name']}")
            else:
                print(f"⚠️ No hay más carpetas disponibles para asignar a {cuenta}. No se guardará esta cuenta.")

    # Si no hay cuentas asignables → señal de corte por falta de carpetas
    if not cuentas_con_carpetas:
        print("❌ No hay cuentas con carpeta asignada. No se guardará nada.")
        return {
            "asignadas": [],
            "total_detectadas": todas_cuentas,
            "motivo_fin": "sin_carpetas"
        }

    # Guardar solo cuando hay cuentas válidas
    guardar_resultado2(serial, cuentas_con_carpetas)

    return {
        "asignadas": cuentas_con_carpetas,
        "total_detectadas": todas_cuentas,
        "motivo_fin": "ok"
    }

def guardar_resultado2(serial, cuentas_con_carpetas, archivo='dispositivos.json'):
    try:
        if os.path.exists(archivo):
            with open(archivo, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {}

        # 🟢 Interfaz para seleccionar cuentas

        # 🟡 Lista de todas las cuentas sin carpeta_id
        cuentas_detectadas = [cuenta["cuenta"] for cuenta in cuentas_con_carpetas]

        # Guardar estructura completa
        data[serial] = {
            "cuentas": cuentas_con_carpetas,
            "cuentasDetectadas":cuentas_detectadas,
            "cuentasPorSubir": [],
            "cuentasSubidas": []
        }

        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"💾 Guardado para {serial}")
    except Exception as e:
        print(f"❌ Error al guardar en JSON: {e}")

def detectar_usuarios_en_pantalla(serial):
    Width,Heigth= get_screen_size(serial)
    resultado = subprocess.run([ADB_PATH, "-s", serial, "exec-out", "screencap", "-p"], capture_output=True)
    imagen_bytes = resultado.stdout
    if not imagen_bytes:
        return [], False

    x1 = parse_coord("19.72%", Width)
    y1 = parse_coord("6.63%", Heigth)
    x2 = parse_coord("87.87%", Width)
    y2 = parse_coord("90.71%", Heigth)


    img = Image.open(io.BytesIO(imagen_bytes))
    img = img.crop((x1, y1, x2, y2))

    data = pytesseract.image_to_data(img, lang="eng", output_type=pytesseract.Output.DICT)

    cuentas_con_pos = []  # Lista de (palabra, y)
    recolectando = False

    for i, palabra in enumerate(data["text"]):
        palabra = palabra.strip()
        if not palabra:
            continue

        lower = palabra.lower()
        y = data["top"][i]

        if lower in ["switch", "account"] and not recolectando:
            recolectando = True
            continue
        if lower in ["add", "+", "add account"]:
            break
        if recolectando and lower not in ["account", "switch"]:
            cuentas_con_pos.append((palabra, y))

    # Ordenar por coordenada Y
    cuentas_ordenadas = [nombre for nombre, _ in sorted(cuentas_con_pos, key=lambda x: x[1])]

    texto_completo = [t.lower() for t in data["text"] if t.strip()]
    hay_add_account = any("add" in t for t in texto_completo) and any("account" in t for t in texto_completo)

    return cuentas_ordenadas, hay_add_account
