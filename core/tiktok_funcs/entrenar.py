import time
import random
from .utils import ejecteg, crear_funciones_con_serial
from ..config import hilos_activos
def entrenar(serial):
    """Simula ver videos en TikTok aleatoriamente."""
    hilos_activos[serial] = True
    run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap = crear_funciones_con_serial(serial)

    ciclos = random.randint(90, 110)
    run("shell input keyevent 224")  # Encender pantalla
    time.sleep(1)
    move("46.3%", "64.1%", "46.3%", "21.3%")  # Desbloquear
    time.sleep(1)
    ejecteg(serial)

    # Abrir TikTok
    run("shell monkey -p com.zhiliaoapp.musically -c android.intent.category.LAUNCHER 1")
    time.sleep(5)

    for _ in range(ciclos):
        if not hilos_activos.get(serial, False):
            print(f"⏹ Entrenamiento detenido en {serial}")
            break

        move("46.3%", "69.2%", "47.2%", "18.5%")  # Scroll video
        time.sleep(random.randint(8, 19))

        accion = random.randint(1, 7)
        if accion == 1:
            tap("91.5%", "14.5%")
            tap("91.5%", "14.5%")
        elif accion == 7:
            run("shell input keyevent 4")
