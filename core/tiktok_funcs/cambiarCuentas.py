# core/tiktok_funcs/cambiarCuentas.py
import os
import re
import shutil
import time
from datetime import datetime

from core.tiktok_funcs.utils import ejecteg, switchAccount
from core.tiktok_funcs.TiktokCuentaScan import (
     ultimacuenta, detectar_usuarios_en_pantalla,
    actualizar_estado_cuenta
)
from .utils import cargar_dispositivos
from .CarruselTiktok import ejecutar_gestos
from ..adb_utils import (
    modificar_fechas_en_orden, procesar_celular, get_screen_size,
    parse_coord, crear_funciones_con_serial
)
from ..config import hilos_activos  # ⬅️ mismo diccionario global

# ==================== helpers de parada ====================
def should_stop(serial: str) -> bool:
    return not hilos_activos.get(serial, False)

def _sleep(serial: str, segundos: float):
    fin = time.time() + max(0.0, segundos)
    while time.time() < fin:
        if should_stop(serial):
            return
        time.sleep(0.1)

# ==================== rutas locales ====================
BASE_PATH = os.path.join(os.path.expanduser("~/Documents"), "Carrusel", "ImagenesCrudas")
USADOS_PATH = os.path.join(BASE_PATH, "CarruselesUsados")

# ==================== flujo principal ====================
def cambiar_todas_las_cuentas(serial: str):
    """
    Itera sobre 'cuentasPorSubir' del dispositivo y ejecuta el flujo.
    """
    # 🔵 Enciende el flag al entrar (por si la UI no lo hizo)
    hilos_activos[serial] = True
    try:
        contador = 0
        while True:
            if should_stop(serial):
                print(f"⏹ [{serial}] Detenido por usuario (inicio de loop).")
                break

            datos_serial = cargar_dispositivos().get(serial, {})
            pendientes = datos_serial.get("cuentasPorSubir", [])
            if not pendientes:
                print(f"✅ [{serial}] Ya no hay más cuentas por subir.")
                break

            cuenta_actual = ultimacuenta(serial)
            if should_stop(serial):
                print(f"⏹ [{serial}] Detenido por usuario tras 'ultimacuenta'.")
                break

            print(f"[{serial}] Cambiar Cuentas detecta: {cuenta_actual}")

            if cuenta_actual in pendientes:
                print(f"[{serial}] Última cuenta está en pendientes (descarga + gestos + cambiar)")
                if descarga(serial, cuenta_actual):
                    if should_stop(serial): break
                    ejecteg(serial)
                    if should_stop(serial): break
                    ejecutar_gestos(serial)
                    if should_stop(serial): break
                    cambiarcuenta(serial)
                    if should_stop(serial): break
            else:
                print(f"[{serial}] La cuenta actual no está en pendientes → intentar cambiar.")
                cambiarcuenta(serial)
                if should_stop(serial): break

            _sleep(serial, 1.0)
            contador += 1

        print(f"[{serial}] Iteraciones: {contador}")
        print(f"[{serial}] Proceso terminado. Moviendo carpetas usadas…")
        if not should_stop(serial):
            MoverCarpetasUsadas(serial)
        else:
            print(f"⏹ [{serial}] Detenido antes de mover carpetas.")
    finally:
        # 🔴 Apagar al salir
        hilos_activos[serial] = False

# ==================== cambiar cuenta en el switcher ====================
def cambiarcuenta(serial: str):
    """
    Abre el switcher y selecciona la siguiente cuenta por subir.
    """
    intentos = 0
    while True:
        if should_stop(serial):
            print(f"⏹ [{serial}] Detenido antes/después de switchAccount.")
            return

        try:
            switchAccount(serial)
            if should_stop(serial): return

            cuenta = cambiar_a_siguiente_cuenta(serial)
            if should_stop(serial): return

            if cuenta == "FIN":
                print(f"🏁 [{serial}] Proceso finalizado: no hay más cuentas.")
                return

            if not cuenta:
                intentos += 1
                print(f"⚠️ [{serial}] No se pudo cambiar (intento #{intentos}), reintentando…")
                _sleep(serial, min(5, 1 + intentos))
                continue

            _sleep(serial, 5)
            return

        except Exception as e:
            intentos += 1
            print(f"💥 [{serial}] Error en cambiarcuenta: {e} (intento #{intentos})")
            _sleep(serial, min(5, 1 + intentos))
            # sigue reintentando (respetando stop)

# ==================== descarga (carpeta local) ====================
def descarga(serial: str, cuentaactual: str):
    data = cargar_dispositivos()
    if serial not in data:
        print(f"❌ [{serial}] No existe entrada en dispositivos.json.")
        return None

    for cuenta in data[serial].get("cuentas", []):
        if should_stop(serial):
            print(f"⏹ [{serial}] Detenido durante 'descarga'.")
            return None

        if cuenta.get("cuenta") == cuentaactual:
            carpeta_path = cuenta.get("carpeta_path")
            if not carpeta_path or not os.path.exists(carpeta_path):
                print(f"❌ [{serial}] Carpeta local para {cuentaactual} no encontrada.")
                return None

            print(f"📂 [{serial}] Usando carpeta local: {carpeta_path}")
            if should_stop(serial): return None
            modificar_fechas_en_orden(carpeta_path)

            if should_stop(serial): return None
            procesar_celular(serial, carpeta_path)

            return True

    print(f"❌ [{serial}] Cuenta {cuentaactual} no encontrada en el JSON.")
    return None

# ==================== mover carpetas usadas ====================
def MoverCarpetasUsadas(serial: str):
    if not os.path.exists(USADOS_PATH):
        os.makedirs(USADOS_PATH, exist_ok=True)
        print(f"📂 Carpeta creada: {USADOS_PATH}")

    data = cargar_dispositivos().get(serial, {})
    cuentas = data.get("cuentas", [])
    subidas = set(data.get("cuentasSubidas", []))
    movidas = 0

    for cuenta in cuentas:
        if should_stop(serial):
            print(f"⏹ [{serial}] Detenido durante 'MoverCarpetasUsadas'.")
            break

        nombre = cuenta.get("cuenta")
        carpeta_path = cuenta.get("carpeta_path")
        if nombre in subidas and carpeta_path and os.path.exists(carpeta_path):
            try:
                nombre_actual = os.path.basename(carpeta_path)
                base_nombre = re.sub(r' usado \d{2}-\d{2}_\d{2}h$', '', nombre_actual)
                fecha_hora = datetime.now().strftime("%d-%m_%Hh")
                nuevo_nombre = f"{base_nombre} usado {fecha_hora}"
                destino = os.path.join(USADOS_PATH, nuevo_nombre)

                shutil.move(carpeta_path, destino)
                print(f"📦 [{serial}] Carpeta de {nombre} movida a '{destino}'.")
                movidas += 1
            except Exception as e:
                print(f"❌ [{serial}] Error al mover carpeta de {nombre}: {e}")

    print(f"✅ [{serial}] {movidas} carpeta(s) movida(s).")

# ==================== seleccionar siguiente cuenta ====================
def cambiar_a_siguiente_cuenta(serial: str):
    if should_stop(serial):
        return None

    Width, Height = get_screen_size(serial)
    run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap ,leerTextoEnRegion = crear_funciones_con_serial(serial)

    print(f"🔁 [{serial}] Cambiando cuenta…")

    cuentas_detectadas, _ = detectar_usuarios_en_pantalla(serial)
    if should_stop(serial):
        return None

    if not cuentas_detectadas:
        print(f"⚠️ [{serial}] No se detectaron cuentas visibles en el switcher.")
        return None

    cuenta_actual = list(cuentas_detectadas)[0]
    print(f"📌 [{serial}] Cuenta actual: {cuenta_actual}")

    siguiente = actualizar_estado_cuenta(serial, cuenta_actual)
    if should_stop(serial):
        return None

    if not siguiente:
        print(f"✅ [{serial}] Ya no quedan cuentas por subir.")
        return "FIN"

    print(f"🎯 [{serial}] Buscando próxima cuenta: {siguiente}")

      
    x1 = parse_coord("21.00%", Width)
    y1 = parse_coord("18.88%", Height)
    x2 = parse_coord("82.71%", Width)
    y2 = parse_coord("93.88%", Height)


    region = (x1, y1, x2, y2)

    coords = buscarTextoEnRegion(region, siguiente, umbral_similitud=0.8)
    if should_stop(serial):
        return None

    if coords:
        x, y = coords
        tap(x, y)
        print(f"🧭 [{serial}] Cambiado a cuenta: {siguiente}")
        _sleep(serial, 4)
        return siguiente

    print(f"❌ [{serial}] No se encontró '{siguiente}' en pantalla.")
    return None
