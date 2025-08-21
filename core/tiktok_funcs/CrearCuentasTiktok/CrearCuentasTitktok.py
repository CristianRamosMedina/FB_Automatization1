# core/tiktok_funcs/CrearCuentasTiktok/crear_cuentas.py
import os
import json
import time
from pathlib import Path
import gspread

from core.adb_utils import crear_funciones_con_serial
from core.tiktok_funcs.utils import switchAccount,should_stop,cerrary_salir
from .fechito import fechito
from .puzzleSolver import puzzle
from ..entrenar import entrenar
from .VerifyHelpers import esperar_nickname_o_verificar, buscar_y_verificar_link

# ---------------- Rutas robustas ----------------
def _find_data_dir(start_file: Path) -> Path:
    p = start_file.resolve()
    for parent in [p.parent, *p.parents]:
        d = parent / "data"
        if d.is_dir():
            return d
    # Fallback (si tu estructura es ControlDePantallas/core/...):
    return p.parents[3] / "data"

DATA_DIR     = _find_data_dir(Path(__file__))
CRED_PATH    = DATA_DIR / "credenciales.json"
CORREOS_PATH = DATA_DIR / "correos.json"

if not CRED_PATH.exists():
    raise FileNotFoundError(f"No se encontró credenciales.json en: {CRED_PATH}")
if not CORREOS_PATH.exists():
    raise FileNotFoundError(f"No se encontró correos.json en: {CORREOS_PATH}")

# ---------------- Google Sheets ----------------
_gc = gspread.service_account(filename=str(CRED_PATH))
_sheet = _gc.open("Cuentas").sheet1
if (_sheet.cell(1, 1).value or "").strip().lower() != "correo":
    _sheet.insert_row(
        ["Correo", "UserName", "Contraseña", "Fecha de nacimiento", "Plataforma", "Marca", "Serial"],
        1
    )

# ---------------- Estado en memoria (opcional) ----------------
# Se llenará cuando llames preasignar_para_seriales([...])
_cuentas_por_serial: dict[str, dict] = {}

# ---------------- Lock de asignación ----------------
_LOCK_PATH = (CORREOS_PATH.parent / "correos.json.lock")

def _acquire_lock(timeout: float = 10.0, poll: float = 0.05):
    start = time.time()
    while True:
        try:
            fd = os.open(str(_LOCK_PATH), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            return
        except FileExistsError:
            if time.time() - start > timeout:
                raise TimeoutError("Lock de correos.json ocupado")
            time.sleep(poll)

def _release_lock():
    try:
        _LOCK_PATH.unlink(missing_ok=True)
    except Exception:
        pass

def _usados_globales(data: dict, app: str):
    correos_usados = set()
    apodos_usados = set()
    for s in data.get(app, {}).values():
        for c in s.get("cuentas", []):
            correos_usados.add(c.get("correo"))
            apodos_usados.add(c.get("apodo"))
    correos_usados.discard(None); apodos_usados.discard(None)
    return correos_usados, apodos_usados

# ---------------- Asignación atómica ----------------
def asignar_correo_y_apodo_a_serial(serial: str, path_json: Path = CORREOS_PATH, app: str = "Tiktok"):
    """
    Asigna a un serial un correo y un apodo que:
    - Estén en la lista de disponibles.
    - No hayan sido usados en ningún otro serial.
    """
    path_json = Path(path_json)
    _acquire_lock()
    try:
        with open(path_json, "r", encoding="utf-8") as f:
            data = json.load(f)

        data.setdefault("correos_disponibles", [])
        data.setdefault("apodos_disponibles", [])
        data.setdefault(app, {})

        if serial not in data[app]:
            data[app][serial] = {"cuentas": []}

        # 🔎 recolectar usados en TODO el archivo (todos los seriales)
        correos_usados, apodos_usados = _usados_globales(data, app)

        # buscar el primer correo/apodo disponible que no haya sido usado
        correo = next((c for c in data["correos_disponibles"] if c not in correos_usados), None)
        apodo  = next((a for a in data["apodos_disponibles"]  if a not in apodos_usados), None)

        if not correo or not apodo:
            print("❌ No hay correo/apodo disponible que no esté usado.")
            return None, None

        # ✅ registrar en el serial (pero NO quitarlos del pool)
        data[app][serial]["cuentas"].append({"correo": correo, "apodo": apodo})

        # guardar cambios
        tmp = path_json.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, path_json)

        print(f"✅ Asignado a {serial}: {correo} / {apodo}")
        return correo, apodo

    finally:
        _release_lock()

# ---------------- Preasignación masiva (desde UI) ----------------
def preasignar_para_seriales(rf_seriales, app: str = "Tiktok"):
    """
    Igual que tu bloque antiguo, pero atómico y seguro entre hilos.
    Rellena _cuentas_por_serial {serial: {correo, apodo}}.
    """
    for serial in rf_seriales:
        correo, apodo = asignar_correo_y_apodo_a_serial(serial, app=app)
        if correo and apodo:
            _cuentas_por_serial[serial] = {"correo": correo, "apodo": apodo}

# ---------------- API para la UI (por serial) ----------------
def crear_cuenta_para_serial(serial: str):
    """
    Usa preasignación si existe; si no, asigna on-demand y crea.
    La llamas desde el worker con crear_cuenta_para_serial(serial)
    """
    par = _cuentas_por_serial.get(serial)
    if par:
        correo, apodo = par["correo"], par["apodo"]
    else:
        correo, apodo = asignar_correo_y_apodo_a_serial(serial)
    if not correo or not apodo:
        print(f"⚠️ {serial}: no hay correo/apodo.")
        return
    CrearTiktokCuenta(serial, correo, apodo)

# ---------------- Flujo de creación (tu lógica) ----------------
def _sleep_coop(serial, secs):
    fin = time.time() + max(0.0, secs)
    while time.time() < fin:
        if should_stop(serial):
            return True  # indica que se solicitó stop
        time.sleep(0.1)
    return False

def _esta_en_switcher_add(serial, buscarTextoEnRegion):
    """
    Devuelve True si vemos 'Add account' (o 'Add') en la zona típica del switcher.
    Ajusta región/umbral según tu OCR.
    """
    # región amplia: casi toda la pantalla; puedes acotarla si te conviene
    region = ("0%", "0%", "100%", "100%")
    # prueba términos más robustos (OCR a veces devuelve minúsculas)
    if buscarTextoEnRegion(region, "Add account", "add account", umbral_similitud=0.80):
        return True
    if buscarTextoEnRegion(region, "Add", "add", umbral_similitud=0.85):
        return True
    return False

def _asegurar_switcher_con_add(serial, switch_fn, buscarTextoEnRegion):
    """
    Intenta dejar la UI en el switcher donde aparece 'Add account'.
    Reintenta en bucle cooperativo: switch -> verificar -> (si no) cerrar y reintentar.
    Sale si should_stop(serial) es True.
    """
    intento = 0
    while not should_stop(serial):
        intento += 1
        print(f"🔁 [{serial}] Yendo a Switch Account (intento #{intento})...")
        switch_fn(serial)

        # espera breve a que cargue
        if _sleep_coop(serial, 1.5):  # 1.5s cooperativo
            return False

        # ¿ya vemos 'Add account'?
        if _esta_en_switcher_add(serial, buscarTextoEnRegion):
            print(f"✅ [{serial}] Detectado 'Add account' en switcher.")
            return True

        print(f"⚠️ [{serial}] No se detectó 'Add account'. Cerrando y reintentando...")
        cerrary_salir(serial)
        if _sleep_coop(serial, 0.8):
            return False

    print(f"⏹ [{serial}] Stop solicitado antes de llegar a 'Add account'.")
    return False

def inputcorreo(serial,correo):
    run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap, leerTextoEnRegion = crear_funciones_con_serial(serial)
    print("📧 Ingresando correo…")
    tap("50.2%","47.6%")
    if _sleep_coop(serial, 2): return
    write(correo)
    if _sleep_coop(serial, 2.5): return
    coords = buscarTextoEnRegion(("0%","40%","100%","100%"), "continue", "next", umbral_similitud=0.60)
    if coords:
        tap(*coords)
    else:
        run("shell input keyevent 4")
        if _sleep_coop(serial, 0.6): 
            return
        tap("70%", "89.81%")

    
def inputpassword(serial):
    run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap, leerTextoEnRegion = crear_funciones_con_serial(serial)
    if buscarTextoEnRegion(("2.12%","8.43%","98.42%","41.37%"),"password"):
        print("🔑 Ingresando contraseña…")
        write("AFifhrauhg342f@")
        if _sleep_coop(serial, 1): return
        coords = buscarTextoEnRegion(("1.76%","37.39%","96.39%","93.59%"), "continue", "next", umbral_similitud=0.75)
        
        if coords:
            tap(*coords)  
        else :
            tap("79.58%","97.47%")
            time.sleep(0.4)
            tap("60%","90%")
        if _sleep_coop(serial, 1): return
    else:
        
        print("no password")    

def CrearTiktokCuenta(serial: str, correo: str, apodo: str):
    print(f"➡️ CrearTiktokCuenta: {serial} | {correo} / {apodo}")
    run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap, leerTextoEnRegion = crear_funciones_con_serial(serial)

    run("shell input keyevent 224")
    if _sleep_coop(serial, 1): return
    move("50%","64.1%","50%","21.4%")

    # 🔒 asegurar que estamos en el switcher (con 'Add account')
    ok = _asegurar_switcher_con_add(serial, switchAccount, buscarTextoEnRegion)
    if not ok or should_stop(serial):
        return

    # ya en switcher → flujo de “Sign” / email
    tap("50%","88.29%")
    if _sleep_coop(serial, 1.2): return

    coords = buscarTextoEnRegion(("0%","0%","100%","100%"), "Sign", "sign", umbral_similitud=0.80)
    if coords:
        tap(*coords)
    else:
        print("ℹ️ No se encontró 'Sign' (posible que ya esté en pantalla de login).")

    if _sleep_coop(serial, 1.2): return
    coords = buscarTextoEnRegion(("24.07%","14.53%","85%","77.44%"), "email", "Email", umbral_similitud=0.80)
    tap(*coords) if coords else tap("50%","33.93%")
    if _sleep_coop(serial, 3): return

    # birthday gate
    if buscarTextoEnRegion(("3.43%","9.50%","98.57%","40.69%"), "birthday", "Birthday", umbral_similitud=0.75):
        fechito(serial)
        tap("50%","82%")
        if _sleep_coop(serial, 1.2): return
        coords = buscarTextoEnRegion(("0%","0%","100%","100%"), "Email", "email", umbral_similitud=0.80)
        if coords :
            tap(*coords)
            inputcorreo(serial,correo)
        else:
            tap("72.4%","11.25%")
            inputcorreo(serial,correo)
    else:
        coords = buscarTextoEnRegion(("3%","7%","100%","50%"), "Email", "email", umbral_similitud=0.80)
        if coords:
            tap(*coords)
            inputcorreo(serial,correo)
   

    if _sleep_coop(serial,2):return
    puzzle(serial)
    
    
    if _sleep_coop(serial, 4): return
    inputpassword(serial)
    # pass
    if _sleep_coop(serial, 2): return
    esperar_nickname_o_verificar(serial, correo, apodo)
    if _sleep_coop(serial, 1): return
    inputpassword(serial)
    if _sleep_coop(serial, 1): return


    # captcha + nickname/email verify
    puzzle(serial)
    if _sleep_coop(serial, 3): return
    esperar_nickname_o_verificar(serial, correo, apodo)
    if _sleep_coop(serial, 1): return
    
    
    if buscarTextoEnRegion(("3.43%","9.50%","98.57%","40.69%"), "birthday", "Birthday", umbral_similitud=0.75):
        fechito(serial)

    tap("51.2%","83.5%")
    if _sleep_coop(serial, 5): return

    print("🤲 Verifica Email")
    esperar_nickname_o_verificar(serial, correo, apodo)
    if _sleep_coop(serial, 9): return

    print("👀 Buscando puzzle")
    puzzle(serial)
    if _sleep_coop(serial, 3): return
    esperar_nickname_o_verificar(serial, correo, apodo)
    if should_stop(serial): return

    buscar_y_verificar_link(
        serial,
        user="previ4303@gmail.com",
        app_password="tibf uoar hpvl kuog",   # ⚠️ pásalo a variables de entorno
        cuenta_hija=correo,
    )
    if _sleep_coop(serial, 2): return
    tap("49.4%","53.2%")
    if _sleep_coop(serial, 4): return

    fila = [correo, apodo, "AFifhrauhg342f@", "April 15,2006", "Tiktok", "Samsung", serial]
    _sheet.append_row(fila)
    print("✅ Datos agregados a Google Sheets.")
    if should_stop(serial): return
    entrenar(serial)
