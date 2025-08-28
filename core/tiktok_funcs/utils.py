# core/tiktok_funcs/utils.py
import time
import re
import subprocess
import io,json,os
from PIL import Image, UnidentifiedImageError
import pytesseract

from core.adb_utils import get_screen_size as adb_get_screen_size, parse_coord, crear_funciones_con_serial
from core.config import hilos_activos                    # ✅ una sola fuente de verdad
from core.paths import CARRUSEL_FILE,DISPOSITIVOS_FILE,VIDEOS_FILE,TESSERACT_PATH
# Configuración pytesseract
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


# ------------------- Control de hilos -------------------
def iniciar_funcion(serial: str):
    """Marca el hilo del dispositivo como activo."""
    hilos_activos[serial] = True

def detener_funcion(serial: str):
    """Detiene cualquier función en ejecución para un dispositivo."""
    hilos_activos[serial] = False
    print(f"🛑 Señal enviada para detener funciones en {serial}")


def should_stop(serial: str) -> bool:
    if not hilos_activos.get(serial, True):
        print(f" ⏹ Proceso detenido en {serial}")
        return True
    return False

def cargar_dispositivos():
    if os.path.exists(DISPOSITIVOS_FILE):
        with open(DISPOSITIVOS_FILE, "r") as f:
            return json.load(f)
    return {}
def AbrirJsonCarruseles():
    if os.path.exists(CARRUSEL_FILE):
        with open(CARRUSEL_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

def cargar_videos():
    if os.path.exists(VIDEOS_FILE):
        with open(VIDEOS_FILE, "r") as f:
            return json.load(f)


def limpiar_json(archivo):
   
    
    try:
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=2, ensure_ascii=False)
        print(f"🧹 Archivo {archivo} limpiado con éxito.")
    except Exception as e:
        print(f"❌ Error al limpiar JSON: {e}")      

# ------------------- Helpers ADB/UI -------------------
def silenciar_dispositivo(serial: str):
    """Baja el volumen del dispositivo a 0."""
    run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap ,leerTextoEnRegion = crear_funciones_con_serial(serial)
    run("shell media volume --stream 3 --set 0")
    print(f"🔇 Dispositivo {serial} silenciado.")

def ejecteg(serial: str):
    """Sale hacia atrás varias veces para resetear pantalla (similar a ir a Home)."""
    run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap ,leerTextoEnRegion = crear_funciones_con_serial(serial)
    for _ in range(4):
        if should_stop(serial): 
            return
        run("shell input keyevent 4")
        time.sleep(0.1)

def cerrary_salir(serial: str):
    """Abre recientes y cierra todo (o intenta cerrar)."""
    run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap ,leerTextoEnRegion = crear_funciones_con_serial(serial)
    if should_stop(serial): 
        return
    run("shell input keyevent 224")  # Encender pantalla
    time.sleep(0.2)
    move("50%","68%","50%","20%")    # Desbloqueo rápido (swipe)
    time.sleep(0.2)

    if should_stop(serial): 
        return
    run("shell input keyevent 187")  # App Recents
    time.sleep(0.7)

    # Intentar tocar "Close" o "Close all"
    coords = buscarTextoEnRegion(("5%", "5%", "95%", "95%"), "Close")
    if coords:
        tap(*coords)
    else:
        # fallback: tap zona inferior
        tap("50%", "78.3%")

    # breve espera cooperativa
    for _ in range(10):
        if should_stop(serial):
            return
        time.sleep(0.1)

def get_screen_size(serial: str):
    """Proxy a adb_utils.get_screen_size, mantenido por compatibilidad."""
    try:
        return adb_get_screen_size(serial)
    except Exception:
        print("Error al obtener tamaño de pantalla")
        return None, None


# ------------------- Flujo: Switch Account (cooperativo con stop) -------------------
def switchAccount(serial: str):
    """
    Abre TikTok y navega a Settings → Switch account.
    Respeta should_stop() entre pasos para poder detener rápido.
    """
    run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap ,leerTextoEnRegion = crear_funciones_con_serial(serial)

    # Encender y desbloquear un poco
    if should_stop(serial): return
    run("shell input keyevent 224")
    time.sleep(0.3)
    move("50%","68%","37%","20%")
    time.sleep(0.3)

    if should_stop(serial): return
    cerrary_salir(serial)  # limpiar apps recientes

    if should_stop(serial): return
    print(f"\n🚀 Abriendo TikTok en {serial}...")
    run("shell monkey -p com.zhiliaoapp.musically -c android.intent.category.LAUNCHER 1")

    # Espera cooperativa a que abra
    for _ in range(25):   # ~2.5s
        if should_stop(serial): return
        time.sleep(0.1)

    # Ir al perfil (press & hold como tenías)
    if should_stop(serial): return
    long_tap("90.09%", "92.31%")
    time.sleep(1)

    # Si aparece "keep", tocar el texto a la izquierda (tu lógica original)
    if should_stop(serial): return
    if buscarTextoEnRegion(("20.57%","4.6%","98%","8%"), "keep"):
        tap("40%","10.5%")
        time.sleep(0.8)
    else:
        print("Estamos safe")

    # Abrir menú superior (…)
    if should_stop(serial): return
    tap("95.29%", "5.50%")
    time.sleep(0.4)

    # Ir a Settings
    if should_stop(serial): return
    coords = buscarTextoEnRegion(("2.13%", "57.64%", "99.35%", "93.75%"), "Settings")
    if coords:
        tap(*coords)
    else:
        time.sleep(0.3)
        tap("50.46%", "89.87%")  # fallback
    time.sleep(0.6)

    # Scroll para encontrar "Switch account"
    if should_stop(serial): return
    move("50.46%", "85.68%", "50.46%", "8.42%")
    time.sleep(0.3)
    move("50.46%", "85.68%", "50.46%", "8.42%")
    time.sleep(0.4)

    if should_stop(serial): return
    coords = buscarTextoEnRegion(("2.13%", "57.64%", "99.35%", "93.75%"), "switch")
    if coords:
        tap(*coords)
    else:
        tap("50.46%", "76.92%")  # fallback
    time.sleep(0.4)
