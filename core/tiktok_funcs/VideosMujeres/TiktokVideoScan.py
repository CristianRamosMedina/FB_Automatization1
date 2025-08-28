import threading, subprocess, os, json, io, time
from ..utils import switchAccount
from .adb_utils_videos import cargar_videos, guardar_videos
from core.tiktok_funcs.utils import ejecteg, cerrary_salir, get_screen_size
from core.adb_utils import parse_coord, crear_service_drive, modificar_fechas_en_orden, procesar_celular
from core.paths import ADB_PATH, TESSERACT_PATH, ASIGNACIONES_VIDEO
from ...config import hilos_activos
import pytesseract
from PIL import Image
from PIL import UnidentifiedImageError

# ===================== Configuración pytesseract =====================
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# ===================== Paths base locales (para listar carpetas) =====================
BASE_PATH = os.path.join(
    os.path.expanduser("~/Documents"),
    "Carrusel", "ImagenesCrudas", "Videos"
)

# ===================== Helpers STOP cooperativo =====================
def stop_requested(serial) -> bool:
    return not hilos_activos.get(serial, False)

def _sleep(serial: str, segundos: float):
    """Sleep cooperativo: permite salir rápido si se pidió stop."""
    fin = time.time() + max(0.0, segundos)
    while time.time() < fin:
        if stop_requested(serial):
            return
        time.sleep(0.1)

# ===================== Flujo principal de escaneo/assign =====================
def TitkokCuentasVideos(serial, cooldown=2.0, cierre_cada=3):
    hilos_activos[serial] = True
    fallos = 0
    while True:
        if stop_requested(serial):
            print(f"⏹ Detenido por usuario en {serial}")
            break
        try:
            ejecteg(serial)
            if stop_requested(serial): break

            switchAccount(serial)
            if stop_requested(serial): break

            resultado = escanear_cuentas_tiktok(serial)
            if stop_requested(serial): break

            motivo = resultado.get("motivo_fin")
            asignadas = resultado.get("asignadas", [])
            total_detectadas = resultado.get("total_detectadas", set())

            if motivo == "detenido":
                print(f"⏹ Flujo de escaneo detenido por usuario en {serial}")
                break

            if motivo == "ok" and asignadas:
                print("✅ Flujo completado: cuentas asignadas y guardadas.")
                break  # o return asignadas

            if motivo == "sin_carpetas":
                print("🛑 Hay cuentas, pero no se pudo asignar ninguna carpeta.")
                break  # o return []

            if motivo == "sin_cuentas":
                print("⚠️ No se detectaron cuentas. Cerrando y reintentando...")
                try:
                    cerrary_salir(serial)
                except Exception as e:
                    print(f"⚠️ Error al cerrar apps: {e}")
                if stop_requested(serial): break
                _sleep(serial, cooldown)
                continue

            # otros estados (no esperados)
            fallos += 1

            if fallos % max(1, cierre_cada) == 0:
                if stop_requested(serial): break
                try:
                    print("🧹 Intento de despegar: cerrando apps recientes...")
                    cerrary_salir(serial)
                except Exception as e:
                    print(f"⚠️ Error en cerrary_salir: {e}")

            if stop_requested(serial): break
            _sleep(serial, cooldown)

        except Exception as e:
            if stop_requested(serial):
                print(f"⏹ Detenido durante excepción en {serial}: {e}")
                break
            print(f"💥 Error en TitkokCuentas: {e}")
            try:
                cerrary_salir(serial)
            except Exception as e2:
                print(f"⚠️ Error al cerrar apps: {e2}")
            if stop_requested(serial): break
            _sleep(serial, cooldown)
            continue

    # marca apagado al salir
    hilos_activos[serial] = False
    return []

# ===================== Soporte: carpetas / asignaciones =====================
def listar_carpetas_locales_ordenadas():
    """Lista todas las carpetas dentro de BASE_PATH, ordenadas por nombre."""
    if not os.path.isdir(BASE_PATH):
        return []
    carpetas = []
    for nombre in os.listdir(BASE_PATH):
        ruta = os.path.join(BASE_PATH, nombre)
        if os.path.isdir(ruta):
            carpetas.append({"name": nombre, "path": ruta})
    carpetas.sort(key=lambda c: c["name"])
    return carpetas

def _tiene_archivos(ruta, extensiones=None):
    """True si la carpeta tiene al menos un archivo (filtra por extensión si se provee)."""
    if not os.path.isdir(ruta):
        return False
    if extensiones:
        exts = tuple(e.lower() for e in extensiones)
        for entry in os.scandir(ruta):
            if entry.is_file():
                _, ext = os.path.splitext(entry.name)
                if ext.lower() in exts:
                    return True
        return False
    else:
        return any(entry.is_file() for entry in os.scandir(ruta))

def _carpeta_valida_videos(carpeta_path):
    """Considera válida si tiene al menos 1 archivo de video común."""
    exts_video = ('.mp4', '.mov', '.mkv', '.webm', '.avi', '.m4v')
    return _tiene_archivos(carpeta_path, exts_video)

lock = threading.Lock()

def cargar_asignaciones():
    """
    Carga el JSON de asignaciones (ASIGNACIONES_VIDEO).
    Soporta valores str (legacy) o list[str] (nuevo con fallbacks).
    """
    if not os.path.exists(ASIGNACIONES_VIDEO):
        print("⚠️ No se encontró asignaciones.json, usando vacío.")
        return {}
    with open(ASIGNACIONES_VIDEO, "r", encoding="utf-8") as f:
        raw = json.load(f)
    norm = {}
    for k, v in raw.items():
        if isinstance(v, list):
            norm[k.strip().lower()] = [str(x).strip() for x in v if str(x).strip()]
        elif isinstance(v, str):
            norm[k.strip().lower()] = [v.strip()]
        else:
            # valor inesperado; ignora o conviértelo a string
            norm[k.strip().lower()] = [str(v).strip()]
    return norm

asignaciones_fijas = cargar_asignaciones()

def normalizar_nombre(nombre):
    return nombre.strip().lower()

def buscar_carpeta_por_nombre(nombre_objetivo):
    for carpeta in listar_carpetas_locales_ordenadas():
        if carpeta["name"] == nombre_objetivo:
            return carpeta
    return None

def buscar_carpeta_opciones(lista_opciones):
    """
    Recorre una lista de nombres de carpetas en orden.
    Devuelve la primera que exista y tenga contenido válido (al menos 1 video).
    """
    for nombre in lista_opciones:
        carpeta = buscar_carpeta_por_nombre(nombre)
        if carpeta:
            if _carpeta_valida_videos(carpeta["path"]):
                return carpeta
            else:
                print(f"⚠️ Carpeta '{nombre}' existe pero está vacía (sin videos). Probando siguiente...")
        else:
            print(f"⚠️ Carpeta '{nombre}' no encontrada. Probando siguiente...")
    return None

# ===================== OCR / Detección de cuentas =====================
def escanear_cuentas_tiktok(serial):
    # Chequeo de stop antes de empezar
    if stop_requested(serial):
        return {"asignadas": [], "total_detectadas": set(), "motivo_fin": "detenido"}

    global carpeta_idx_global
    carpeta_idx_global = 0
    Width, Heigth = get_screen_size(serial)

    print(f"🔍 Escaneando cuentas en TikTok del {serial}...")

    todas_cuentas = set()
    scrolls = 0
    max_scrolls = 10

    while scrolls < max_scrolls:
        if stop_requested(serial):
            return {"asignadas": [], "total_detectadas": set(), "motivo_fin": "detenido"}

        cuentas_actuales, hay_add = detectar_usuarios_en_pantalla(serial)
        if stop_requested(serial):
            return {"asignadas": [], "total_detectadas": set(), "motivo_fin": "detenido"}

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
        _sleep(serial, 2)  # permite stop
        scrolls += 1

    print(f"✅ Total de cuentas encontradas: {todas_cuentas}")

    if stop_requested(serial):
        return {"asignadas": [], "total_detectadas": set(), "motivo_fin": "detenido"}

    # Si no se detectó ninguna cuenta → no guardamos y señalamos para reintentar
    if not todas_cuentas:
        print("❌ No se detectaron cuentas en este escaneo.")
        return {
            "asignadas": [],
            "total_detectadas": set(),
            "motivo_fin": "sin_cuentas"
        }

    cuentas_con_carpetas = []

    # 🔒 Zona crítica: asignación
    with lock:
        # 1) Asignaciones fijas con fallbacks (lista de opciones)
        for cuenta in todas_cuentas:
            cuenta_norm = normalizar_nombre(cuenta)
            if cuenta_norm in asignaciones_fijas:
                opciones = asignaciones_fijas[cuenta_norm]  # ya normalizado a lista
                carpeta_valida = buscar_carpeta_opciones(opciones)
                if carpeta_valida:
                    cuentas_con_carpetas.append({
                        "cuenta": cuenta,
                        "carpeta_path": carpeta_valida["path"],
                        "carpeta_nombre": carpeta_valida["name"]
                    })
                    print(f"📌 Cuenta fija: {cuenta} → {carpeta_valida['name']}")
                else:
                    print(f"⚠️ Ninguna opción válida encontrada para {cuenta}")

        # Lista de nombres de carpetas ya tomadas por fijas
        carpetas_usadas_fijas = set([c["carpeta_nombre"] for c in cuentas_con_carpetas])

        # Construir set de carpetas reservadas de TODAS las opciones (para no asignar dinámicas allí)
        carpetas_reservadas = set()
        for opciones in asignaciones_fijas.values():
            carpetas_reservadas.update(opciones)

        # 2) Dinámicas: asignar carpetas libres (no reservadas, no usadas) a cuentas sin fija válida
        carpetas_disponibles = [
            c for c in listar_carpetas_locales_ordenadas()
            if (c["name"] not in carpetas_reservadas) and (c["name"] not in carpetas_usadas_fijas) and _carpeta_valida_videos(c["path"])
        ]

        for cuenta in todas_cuentas:
            # si ya tiene fija válida, skip
            if any(item["cuenta"] == cuenta for item in cuentas_con_carpetas):
                continue

            if carpeta_idx_global < len(carpetas_disponibles):
                carpeta = carpetas_disponibles[carpeta_idx_global]
                carpeta_idx_global += 1
                cuentas_con_carpetas.append({
                    "cuenta": cuenta,
                    "carpeta_path": carpeta["path"],
                    "carpeta_nombre": carpeta["name"]
                })
                print(f"📦 Cuenta asignada (dinámica): {cuenta} → {carpeta['name']}")
            else:
                print(f"⚠️ No hay más carpetas disponibles para asignar a {cuenta}.")

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

# ===================== Guardado / lectura JSON resultado =====================
def guardar_resultado2(serial, cuentas_con_carpetas, archivo='data/videos.json'):
    try:
        if os.path.exists(archivo):
            with open(archivo, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {}

        # 🟡 Lista de todas las cuentas detectadas
        cuentas_detectadas = [cuenta["cuenta"] for cuenta in cuentas_con_carpetas]

        # Guardar estructura completa
        data[serial] = {
            "cuentas": cuentas_con_carpetas,
            "cuentasDetectadas": cuentas_detectadas,
            "cuentasPorSubir": [],
            "cuentasSubidas": []
        }

        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"💾 Guardado para {serial}")
    except Exception as e:
        print(f"❌ Error al guardar en JSON: {e}")

# ===================== Utilidades de cuentas =====================
def ultimacuenta(serial):
    # ✅ Import local para evitar circular import
    from core.tiktok_funcs.utils import ejecteg
    try:
        switchAccount(serial)

        try:
            cuentas_detectadas, _ = detectar_usuarios_en_pantalla(serial)
        except (subprocess.SubprocessError, UnidentifiedImageError, OSError) as e:
            print(f"⚠️ Error al detectar usuarios: {e}")
            _sleep(serial, 1)
            ejecteg(serial); ejecteg(serial)
            return ultimacuenta(serial)

        print("\n Cuentas Primera")
        if not cuentas_detectadas:
            print("⚠️ No se detectaron cuentas visibles. Reintentando...")
            _sleep(serial, 1)
            ejecteg(serial); ejecteg(serial)
            return ultimacuenta(serial)

        cuentaactual = list(cuentas_detectadas)[0]
        print(cuentaactual)
        return cuentaactual

    except Exception as e:
        print(f"💥 Error inesperado: {e}")
        _sleep(serial, 1)
        ejecteg(serial); ejecteg(serial)
        return ultimacuenta(serial)

def detectar_usuarios_en_pantalla(serial):
    # ➜ Devuelve rápido si ya pidieron detener
    if stop_requested(serial):
        return [], False

    Width, Heigth = get_screen_size(serial)

    # Captura de pantalla
    resultado = subprocess.run(
        [ADB_PATH, "-s", serial, "exec-out", "screencap", "-p"],
        capture_output=True
    )
    imagen_bytes = resultado.stdout
    if not imagen_bytes:
        return [], False

    if stop_requested(serial):
        return [], False

    x1 = parse_coord("21.00%", Width)
    y1 = parse_coord("18.88%", Heigth)
    x2 = parse_coord("82.71%", Width)
    y2 = parse_coord("93.88%", Heigth)

    img = Image.open(io.BytesIO(imagen_bytes))
    img = img.crop((x1, y1, x2, y2))

    if stop_requested(serial):
        return [], False

    data = pytesseract.image_to_data(img, lang="eng", output_type=pytesseract.Output.DICT)

    cuentas_con_pos = []  # Lista de (palabra, y)
    recolectando = False

    for i, palabra in enumerate(data["text"]):
        if stop_requested(serial):
            return [], False

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

# ===================== Descarga y actualización =====================
def descargar_carpeta_completa(folder_id, serial):
    carpeta_destino = f"./imagenes_temp/{serial}"
    service = crear_service_drive()

    if os.path.exists(carpeta_destino):
        import shutil
        shutil.rmtree(carpeta_destino)

    os.makedirs(carpeta_destino, exist_ok=True)
    try:
        query = f"'{folder_id}' in parents and mimeType != 'application/vnd.google-apps.folder'"
        result = service.files().list(q=query, fields="files(id, name)").execute()
        files = result.get('files', [])
        print(f"📦 {len(files)} archivos encontrados")
        if not files:
            print("⚠️ No se encontraron archivos en la carpeta")
            return False

        archivos_exitosos = 0
        archivos_fallidos = 0

        for i, file in enumerate(files, 1):
            if stop_requested(serial):
                print("⏹ Descarga detenida por usuario.")
                break
            try:
                print(f"📥 Descargando {i}/{len(files)}: {file['name']}")
                request = service.files().get_media(fileId=file['id'])
                file_content = request.execute()

                ruta_archivo = os.path.join(carpeta_destino, file['name'])
                with open(ruta_archivo, 'wb') as f:
                    f.write(file_content)

                archivos_exitosos += 1
                print(f"✅ Descargado: {file['name']}")

            except Exception as e:
                print(f"❌ Error descargando {file['name']}: {e}")
                archivos_fallidos += 1

        print(f"\n📈 Descarga completada: {archivos_exitosos} exitosos, {archivos_fallidos} fallidos")
        if archivos_exitosos > 0:
            return carpeta_destino  # ✅ Devuelve la ruta si fue exitoso
        else:
            return False

    except Exception as e:
        print(f"❌ Error general descargando carpeta: {e}")
        return False

def descarga(serial, cuentaactual):
    data = cargar_videos()
    if serial not in data:
        print(f"❌ Serial {serial} no encontrado en el JSON.")
        return None

    cuentas = data[serial].get("cuentas", [])

    for cuenta in cuentas:
        if cuenta["cuenta"] == cuentaactual:
            carpeta_id = cuenta.get("carpeta_id")  # podría no existir si solo trabajas local
            print(f"📂 Carpeta ID encontrada: {carpeta_id}")

            carpeta_descargada = descargar_carpeta_completa(carpeta_id, serial)

            if carpeta_descargada:
                modificar_fechas_en_orden(carpeta_descargada)
                procesar_celular(serial, carpeta_descargada)
            else:
                print(f"❌ No se pudo descargar la carpeta para el dispositivo {serial}")
                print(f"❌ Cuenta {cuentaactual} no encontrada para el serial {serial}.")
                return None

def actualizar_estado_cuenta(serial, cuenta_actual):
    dispositivos = cargar_videos()
    if serial not in dispositivos:
        print(f"❌ Serial {serial} no encontrado.")
        return None

    data = dispositivos[serial]

    por_subir = data.get("cuentasPorSubir", [])
    subidas = data.get("cuentasSubidas", [])

    if cuenta_actual in por_subir:
        por_subir.remove(cuenta_actual)
        subidas.append(cuenta_actual)
        print(f"📦 Movido '{cuenta_actual}' de cuentasPorSubir → cuentasSubidas")
    else:
        print(f"⚠️ '{cuenta_actual}' no estaba en cuentasPorSubir")

    dispositivos[serial]["cuentasPorSubir"] = por_subir
    dispositivos[serial]["cuentasSubidas"] = subidas
    guardar_videos(dispositivos)

    if por_subir:
        return por_subir[0]  # próxima cuenta a subir
    else:
        print("✅ No hay más cuentas por subir.")
        return None
