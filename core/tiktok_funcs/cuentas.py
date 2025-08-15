import time
from .utils import ejecteg
from ..adb_utils import crear_funciones_con_serial
from .gestos_videos import gestos_videos_random as ejecutar_gestos
from ..config import hilos_activos, cargar_dispositivos, ultimacuenta, descarga,ejecteg, cambiarcuenta, MoverCarpetasUsadas


# Aquí deberías importar las funciones que uses
# como ultimacuenta, descarga, cambiarcuenta, MoverCarpetasUsadas
# desde donde las tengas definidas.

def cambiar_todas_las_cuentas(serial):
    hilos_activos[serial] = True
    contador = 0
    while True:
        data = cargar_dispositivos().get(serial, {})
        pendientes = data.get("cuentasPorSubir", [])
        if not pendientes:
            print(f"✅ {serial}: Ya no hay más cuentas por subir.")
            break

        cuenta_actual = ultimacuenta(serial)
        print("Cambiar Cuentas detecta : ")
        print(cuenta_actual)

        if cuenta_actual in pendientes:
            print("Ultima cuenta en pendientes 🥰")
            descarga(serial, cuenta_actual)
            ejecteg(serial)
            ejecutar_gestos(serial)
            cambiarcuenta(serial)
        else:
            print("Cambiando CUENTAS ")
            cambiarcuenta(serial)

        time.sleep(1)

    print(contador)
    print("\n Proceso terminado Eliminando Carpetas del Drive")
    MoverCarpetasUsadas(serial)
