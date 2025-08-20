import subprocess
import psutil
import time
import math
import ctypes
from core.paths import ADB_PATH, SCRCPY_PATH  


def obtener_seriales():
    """Obtiene lista de dispositivos conectados vía ADB."""
    result = subprocess.run([ADB_PATH, "devices"], capture_output=True, text=True)
    lines = result.stdout.strip().splitlines()[1:]  # saltar cabecera
    return [line.split()[0] for line in lines if "device" in line]

def obtener_tamano_pantalla():
    """Devuelve ancho y alto de la pantalla de la PC."""
    user32 = ctypes.windll.user32
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

def abrir_scrcpy(seriales):
    """Abre scrcpy en mosaico para los dispositivos dados."""
    if not seriales:
        print("❌ No hay dispositivos conectados.")
        return

    # Evita abrir duplicados
    procesos_activos = [
        p.info['cmdline'] for p in psutil.process_iter(attrs=['cmdline'])
    ]

    pantalla_ancho, pantalla_alto = obtener_tamano_pantalla()
    area_max_ancho = int(pantalla_ancho * 0.7)
    area_max_alto = pantalla_alto
    margen_x = 10
    margen_y = 50
    columnas = math.ceil(math.sqrt(len(seriales)))
    filas = math.ceil(len(seriales) / columnas)
    ancho_disp = (area_max_ancho - (columnas - 1) * margen_x) // columnas
    alto_disp = (area_max_alto - (filas - 1) * margen_y) // filas
    origen_x = 10
    origen_y = 40

    for i, serial in enumerate(seriales):
        ya_abierto = any(
            p and isinstance(p, list) and serial in ' '.join(p)
            for p in procesos_activos if p and p[0].endswith("scrcpy.exe")
        )
        fila = i // columnas
        columna = i % columnas
        pos_x = origen_x + columna * (ancho_disp + margen_x)
        pos_y = origen_y + fila * (alto_disp + margen_y)

        if not ya_abierto:
            subprocess.Popen(
                [
                    SCRCPY_PATH,
                    "-s", serial,
                    "--max-size", "720",
                    f"--window-title={serial}",
                    "--window-width", str(ancho_disp),
                    "--window-height", str(alto_disp),
                    "--window-x", str(pos_x),
                    "--window-y", str(pos_y),
                ],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            subprocess.run([ADB_PATH, "-s", serial, "shell", "settings", "put", "system", "accelerometer_rotation", "0"])
            subprocess.run([ADB_PATH, "-s", serial, "shell", "settings", "put", "system", "user_rotation", "0"])
            time.sleep(1.5)

def cerrar_scrcpy():
    """Cierra todos los procesos de scrcpy."""
    for proc in psutil.process_iter(attrs=['name']):
        if proc.info['name'] and "scrcpy" in proc.info['name'].lower():
            proc.kill()
    print("✅ scrcpy cerrado.")
