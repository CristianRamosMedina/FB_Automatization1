# core/tiktok_funcs/Analitics/analiticas_cuentas.py

import json, time
from core.tiktok_funcs.utils import cerrary_salir, ejecteg, switchAccount, cargar_dispositivos
from core.adb_utils import crear_funciones_con_serial
from .analiticas import capturar_post_views   # 👈 usamos la función ya hecha

ANALITICAS_FILE = "data/analiticas.json"


def capturar_vistas_por_cuenta(serial):
    """
    Itera sobre todas las cuentas detectadas para un serial,
    hace switch a cada una y captura sus Post Views.
    """
    # cargar todas las cuentas del dispositivo
    data = cargar_dispositivos()
    if serial not in data:
        print(f"❌ Serial {serial} no encontrado en dispositivos.json")
        return

    cuentas = data[serial].get("cuentasDetectadas", [])
    if not cuentas:
        print(f"⚠️ No hay cuentas detectadas para {serial}")
        return

    print(f"🔍 Capturando Post Views de {len(cuentas)} cuentas en {serial}...")

    # abrir JSON global de analíticas
    try:
        with open(ANALITICAS_FILE, "r", encoding="utf-8") as f:
            analiticas = json.load(f)
    except:
        analiticas = {}

    if serial not in analiticas:
        analiticas[serial] = {}

    # iterar sobre cada cuenta
    for cuenta in cuentas:
        print(f"\n👤 Cambiando a cuenta: {cuenta}")
        try:
            switchAccount(serial)   # 👈 debe aceptar cuenta como parámetro
            time.sleep(2)

            # aquí deberías abrir sección Analytics en la app (reutiliza tu lógica actual)

            numero = capturar_post_views(serial)

            if numero:
                analiticas[serial][cuenta] = {"post_views": numero}
                print(f"✅ {cuenta}: {numero} vistas")
            else:
                analiticas[serial][cuenta] = {"post_views": None}
                print(f"⚠️ {cuenta}: no se pudo leer Post Views")

        except Exception as e:
            print(f"💥 Error en cuenta {cuenta}: {e}")
            analiticas[serial][cuenta] = {"post_views": None}

    # guardar resultados
    with open(ANALITICAS_FILE, "w", encoding="utf-8") as f:
        json.dump(analiticas, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Analíticas guardadas en {ANALITICAS_FILE}")
    return analiticas[serial]
