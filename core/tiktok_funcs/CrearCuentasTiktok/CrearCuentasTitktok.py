# core/tiktok_funcs/CrearCuentasTiktok/CrearCuentasTitktok.py
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


# ---------- Ubicar la carpeta "data" de forma robusta ----------
def _find_data_dir(start_file: Path) -> Path:
    p = start_file.resolve()
    for parent in [p.parent, *p.parents]:
        candidate = parent / "data"
        if candidate.exists() and candidate.is_dir():
            return candidate
    # Fallback: asume proyecto en 3 niveles arriba (tu estructura original)
    return p.parents[3] / "data"

DATA_DIR = _find_data_dir(Path(__file__))
CRED_PATH = DATA_DIR / "credenciales.json"
CORREOS_PATH = DATA_DIR / "correos.json"

if not CRED_PATH.exists():
    raise FileNotFoundError(f"No se encontró credenciales.json en: {CRED_PATH}")
if not CORREOS_PATH.exists():
    raise FileNotFoundError(f"No se encontró correos.json en: {CORREOS_PATH}")

# ---------- Google Sheets ----------
_gc = gspread.service_account(filename=str(CRED_PATH))
_sheet = _gc.open("Cuentas").sheet1
# Encabezados (idempotente)
if (_sheet.cell(1, 1).value or "").strip().lower() != "correo":
    _sheet.insert_row(
        ["Correo", "UserName", "Contraseña", "Fecha de nacimiento", "Plataforma", "Marca", "Serial"], 1
    )


# ---------- Asignar correo + apodo ----------
def asignar_correo_y_apodo_a_serial(serial: str, path_json: Path = CORREOS_PATH, app: str = "Tiktok"):
    path_json = Path(path_json)
    if not path_json.exists():
        raise FileNotFoundError(f"No se encontró {path_json}")

    with open(path_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    data.setdefault("correos_disponibles", [])
    data.setdefault("apodos_disponibles", [])
    data.setdefault(app, {})

    if serial not in data[app]:
        data[app][serial] = {"cuentas": []}

    cuentas_existentes = data[app][serial]["cuentas"]

    # Usados globalmente en la app
    correos_usados = {c["correo"] for s in data[app].values() for c in s.get("cuentas", [])}
    apodos_usados  = {c["apodo"]  for s in data[app].values() for c in s.get("cuentas", [])}

    correo = next((c for c in data["correos_disponibles"] if c not in correos_usados), None)
    apodo  = next((a for a in data["apodos_disponibles"]  if a not in apodos_usados),  None)

    if not correo:
        print("❌ No hay correos disponibles.")
        return None, None
    if not apodo:
        print("❌ No hay apodos disponibles.")
        return None, None

    cuentas_existentes.append({"correo": correo, "apodo": apodo})

    with open(path_json, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Asignado a '{serial}': {correo} / {apodo}")
    return correo, apodo


# ---------- API pública para la UI ----------
def crear_cuenta_para_serial(serial: str):
    correo, apodo = asignar_correo_y_apodo_a_serial(serial)
    if not correo or not apodo:
        print(f"⚠️ {serial}: No se pudo asignar correo/apodo.")
        return
    CrearTiktokCuenta(serial, correo, apodo)


# ---------- Flujo de creación ----------
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
    if coords:
        tap(*coords)
    else:
        print("No 'Sign' (puede ya estar en login)")

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
        else: print("No se encontró 'Email'")

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

    # ⚠️ Mueve estas credenciales a variables de entorno en producción
    buscar_y_verificar_link(
        serial,
        user="previ4303@gmail.com",
        app_password="tibf uoar hpvl kuog",
        cuenta_hija=correo,
    )

    time.sleep(2)
    tap("49.4%","53.2%"); time.sleep(4)

    if apodo:
        fila = [correo, apodo, "AFifhrauhg342f@", "April 15,2006", "Tiktok", "Samsung", serial]
        _sheet.append_row(fila)
        print("✅ Datos agregados a Google Sheets.")
    else:
        print("⚠️ Apodo inválido, no se guarda en Sheets.")

    entrenar(serial)
