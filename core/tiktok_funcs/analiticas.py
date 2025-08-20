from ..adb_utils import crear_funciones_con_serial
from .utils import cerrary_salir, ejecteg
import time
def analiticas(serial):
    run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap ,leerTextoEnRegion = crear_funciones_con_serial(serial)
    
    run("shell input keyevent 224")  # Encender pantalla
    time.sleep(1)
    move("50%","68%","50%","20%")
    time.sleep(1)
    cerrary_salir(serial)
    ejecteg(serial)
    print(f"\n🚀 Abriendo TikTok en {serial}...")
    run("shell monkey -p com.zhiliaoapp.musically -c android.intent.category.LAUNCHER 1")
    time.sleep(5)
      # Ir al perfil
      
      
    long_tap("90.09%", "92.31%")  # (973, 2160)
    time.sleep(0.6)
    coords = buscarTextoEnRegion(("2.13%", "2.13%", "99.35%", "13.75%"), "Cancel")
    if coords:
        tap(*coords)
        time.sleep(0.6)
        tap("95.29%", "5.50%")
    else:
        time.sleep(0.6)
        tap("95.29%", "5.50%")       # (991, 161)
    time.sleep(1.2)
    


    
    # Ir a Settings
    coords = buscarTextoEnRegion(("2.13%", "57.64%", "99.35%", "93.75%"), "Studio")
    if coords:
        tap(*coords)
    else:
        tap("50%", "71.06%")
    time.sleep(2.1)

    coords = buscarTextoEnRegion(("2.71%", "14.25%", "100.00%", "36.06%"), "all")
    if coords:
        tap(*coords)
    else:
        tap("85.71%", "17.50%")
    time.sleep(5)
    move("53.57%", "16.94%", "14.00%", "16.94%")
    coords = buscarTextoEnRegion(("2.71%", "14.25%", "100.00%", "36.06%"), "custom")
    if coords:
        tap(*coords)
    else:
        tap("91.29%", "16.94%")
    time.sleep(1.2)
