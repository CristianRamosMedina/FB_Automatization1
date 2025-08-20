# core/tiktok_funcs/CrearCuentasTiktok/crear_cuentas.py
import os
import json
import time
from pathlib import Path
import gspread

from core.adb_utils import crear_funciones_con_serial
from core.tiktok_funcs.utils import switchAccount
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

        correos_usados, apodos_usados = _usados_globales(data, app)
        correo = next((c for c in data["correos_disponibles"] if c not in correos_usados), None)
        apodo  = next((a for a in data["apodos_disponibles"]  if a not in apodos_usados),  None)

        if not correo or not apodo:
            print("❌ No hay correo/apodo disponible.")
            return None, None

        # quitar del pool
        try: data["correos_disponibles"].remove(correo)
        except ValueError: pass
        try: data["apodos_disponibles"].remove(apodo)
        except ValueError: pass

        # registrar en el serial
        data[app][serial]["cuentas"].append({"correo": correo, "apodo": apodo})

        # guardar
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
def CrearTiktokCuenta(serial: str, correo: str, apodo: str):
    print(f"➡️ CrearTiktokCuenta: {serial} | {correo} / {apodo}")
    run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap, leerTextoEnRegion = crear_funciones_con_serial(serial)

    run("shell input keyevent 224")
    time.sleep(1)
    move("50%","64.1%","50%","21.4%")

    switchAccount(serial)

    tap("50%","88.29%")
    time.sleep(1.2)
    coords = buscarTextoEnRegion(("0%","0%","100%","100%"), "Sign")
    if coords: tap(*coords)

    time.sleep(1.2)
    coords = buscarTextoEnRegion(("24.07%","14.53%","85%","77.44%"), "email")
    tap(*coords) if coords else tap("50%","33.93%")
    time.sleep(3)

    if buscarTextoEnRegion(("3.43%","9.50%","98.57%","40.69%"), "birthday"):
        fechito(serial)
        tap("50%","82%")
        time.sleep(1.2)
        coords = buscarTextoEnRegion(("0%","0%","100%","100%"), "Email")
        tap(*coords) if coords else tap("72.4%","11.25%")
    else:
        coords = buscarTextoEnRegion(("3%","7%","100%","50%"), "Email")
        if coords: tap(*coords)

    print("📧 Ingresando correo…")
    tap("50.2%","47.6%"); time.sleep(2)
    write(correo); time.sleep(2.5)

    coords = buscarTextoEnRegion(("1.76%","37.39%","96.39%","93.59%"), "continue")
    if not coords:
        coords = buscarTextoEnRegion(("1.76%","37.39%","96.39%","93.59%"), "next")
    tap(*coords) if coords else tap("86.57%","97.47%")
    time.sleep(4)

    print("🔑 Ingresando contraseña…")
    write("AFifhrauhg342f@"); time.sleep(1)
    coords = buscarTextoEnRegion(("1.76%","37.39%","96.39%","93.59%"), "continue")
    if not coords:
        coords = buscarTextoEnRegion(("1.76%","37.39%","96.39%","93.59%"), "next")
    tap(*coords) if coords else tap("86.57%","97.47%")
    time.sleep(1)

    puzzle(serial); time.sleep(3)
    esperar_nickname_o_verificar(serial, correo, apodo); time.sleep(1)

    if buscarTextoEnRegion(("3.43%","9.50%","98.57%","40.69%"), "birthday"):
        fechito(serial)

    tap("51.2%","83.5%"); time.sleep(5)
    print("🤲 Verifica Email")
    esperar_nickname_o_verificar(serial, correo, apodo); time.sleep(9)

    print("👀 Buscando puzzle")
    puzzle(serial); time.sleep(3)
    esperar_nickname_o_verificar(serial, correo, apodo)

    buscar_y_verificar_link(
        serial,
        user="previ4303@gmail.com",
        app_password="tibf uoar hpvl kuog",   # ⚠️ llévalo a variables de entorno
        cuenta_hija=correo,
    )

    time.sleep(2)
    tap("49.4%","53.2%"); time.sleep(4)

    fila = [correo, apodo, "AFifhrauhg342f@", "April 15,2006", "Tiktok", "Samsung", serial]
    _sheet.append_row(fila)
    print("✅ Datos agregados a Google Sheets.")

    entrenar(serial)
