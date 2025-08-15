from ..adb_utils import crear_funciones_con_serial
from ..config import hilos_activos

def detener_funcion(serial):
    """Detiene cualquier función en ejecución para un dispositivo."""
    hilos_activos[serial] = False
    print(f"🛑 Señal enviada para detener funciones en {serial}")

def silenciar_dispositivo(serial):
    """Baja el volumen del dispositivo a 0."""
    run, tap, long_tap, move, write, buscarTextoEnRegion = crear_funciones_con_serial(serial)
    run("shell media volume --stream 3 --set 0")
    print(f"🔇 Dispositivo {serial} silenciado.")

def ejecteg(serial):
    """Sale a Home varias veces para resetear pantalla."""
    run, tap, long_tap, move, write, buscarTextoEnRegion = crear_funciones_con_serial(serial)
    for _ in range(4):
        run("shell input keyevent 4")
