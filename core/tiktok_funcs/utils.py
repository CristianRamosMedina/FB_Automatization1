import time
import re
import subprocess
import difflib, io
from PIL import Image
import pytesseract

from core.adb_utils import get_screen_size, parse_coord , crear_funciones_con_serial
from core.config import hilos_activos                    
from core.paths import ADB_PATH, SCRCPY_PATH, TESSERACT_PATH  

# Configuración pytesseract
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

def detener_funcion(serial):
    """Detiene cualquier función en ejecución para un dispositivo."""
    hilos_activos[serial] = False
    print(f"🛑 Señal enviada para detener funciones en {serial}")

def silenciar_dispositivo(serial):
    """Baja el volumen del dispositivo a 0."""
    run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap = crear_funciones_con_serial(serial)
    run("shell media volume --stream 3 --set 0")
    print(f"🔇 Dispositivo {serial} silenciado.")

def ejecteg(serial):
    """Sale a Home varias veces para resetear pantalla."""
    run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap = crear_funciones_con_serial(serial)
    for _ in range(4):
        run("shell input keyevent 4")

def cerrary_salir(serial):
    run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap = crear_funciones_con_serial(serial)
     
    run("shell input keyevent 224")  # Encender pantalla
    time.sleep(1)
    move("50%","68%","50%","20%")
    time.sleep(1)

    run("shell input keyevent 187")
    time.sleep(1.5)

    # Cerrar todas las ventanas: buscar y tocar "Cerrar todo" (Close all)
    coords = buscarTextoEnRegion(("5%", "5%", "95%", "95%"), "Close")  # o "Close all"
    if coords:
        tap(*coords)
    else:
        tap("50%", "78.3%") 

    time.sleep(3)
   
def get_screen_size(serial):
    try:
        result = subprocess.run([ADB_PATH, "-s", serial, "shell", "wm", "size"],
                              capture_output=True, text=True)
        output = result.stdout.strip()
        match = re.search(r'(\d+)x(\d+)', output)
        if match:
            width, height = int(match.group(1)), int(match.group(2))
            return width, height
    except:
        print("Error al obtener tamaño")
    return None, None

def switchAccount(serial):
    # ✅ Import local para evitar circular import
    from core.tiktok_funcs.utils import crear_funciones_con_serial

    run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap = crear_funciones_con_serial(serial)
    run("shell input keyevent 224")  # Encender pantalla
    time.sleep(0.5)
    move("50%","68%","50%","20%")
    time.sleep(0.5)
    run("shell input keyevent 4")
    run("shell input keyevent 4")
    run("shell input keyevent 4")
    run("shell input keyevent 4")

    print(f"\n🚀 Abriendo TikTok en {serial}...")
    run("shell monkey -p com.zhiliaoapp.musically -c android.intent.category.LAUNCHER 1")
    time.sleep(5)
    # Ir al perfil
    long_tap("90.09%", "92.31%")
    time.sleep(1)

    # Menú superior
    tap("95.29%", "5.50%")
    time.sleep(1)

    coords = buscarTextoEnRegion(("2.13%", "57.64%", "99.35%", "93.75%"), "Settings")
    if coords:
        tap(*coords)
    else:
        time.sleep(0.6)
        tap("50.46%", "89.87%")  
    time.sleep(1.8)

    move("50.46%", "85.68%", "50.46%", "8.42%")
    time.sleep(0.6)
    move("50.46%", "85.68%", "50.46%", "8.42%")
    time.sleep(0.8)

    coords = buscarTextoEnRegion(("2.13%", "57.64%", "99.35%", "93.75%"), "switch")
    if coords:
        tap(*coords)
    else:
        tap("50.46%", "76.92%") 
    time.sleep(0.7)

