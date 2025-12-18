import subprocess
import psutil
import time
import math
import ctypes
from ctypes import wintypes
from core.paths import ADB_PATH, SCRCPY_PATH


# ==============================
# Utilidades de pantalla/Windows
# ==============================

SPI_GETWORKAREA = 0x0030  # Área usable (excluye barra de tareas)
ABM_GETTASKBARPOS = 0x0005

# Structs/Tipos Win32
class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long),
                ("top", ctypes.c_long),
                ("right", ctypes.c_long),
                ("bottom", ctypes.c_long)]

class APPBARDATA(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_uint),
        ("hWnd", wintypes.HWND),
        ("uCallbackMessage", ctypes.c_uint),
        ("uEdge", ctypes.c_uint),
        ("rc", RECT),
        ("lParam", ctypes.c_int),
    ]


def obtener_seriales():
    """Obtiene lista de dispositivos conectados vía ADB."""
    result = subprocess.run([ADB_PATH, "devices"], capture_output=True, text=True)
    lines = result.stdout.strip().splitlines()[1:]  # saltar cabecera
    return [line.split()[0] for line in lines if "device" in line]


def obtener_tamano_pantalla():
    """Devuelve (ancho_total, alto_total) del monitor primario (incluye barra de tareas)."""
    user32 = ctypes.windll.user32
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)


def obtener_work_area():
    """
    Devuelve el área usable del escritorio (excluye barra de tareas)
    como (left, top, right, bottom, width, height).
    """
    user32 = ctypes.windll.user32
    rect = RECT()
    res = user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(rect), 0)
    if not res:
        # Fallback: usar pantalla completa si falla
        w, h = obtener_tamano_pantalla()
        return 0, 0, w, h, w, h
    width = rect.right - rect.left
    height = rect.bottom - rect.top
    return rect.left, rect.top, rect.right, rect.bottom, width, height


def obtener_posicion_barra_tareas():
    """
    Devuelve 'bottom' | 'top' | 'left' | 'right' o None si no se pudo determinar.
    No es estrictamente necesario para el layout, pero útil para debug.
    """
    shell32 = ctypes.windll.shell32
    abd = APPBARDATA()
    abd.cbSize = ctypes.sizeof(APPBARDATA)
    res = shell32.SHAppBarMessage(ABM_GETTASKBARPOS, ctypes.byref(abd))
    if not res:
        return None
    edges = {0: "left", 1: "top", 2: "right", 3: "bottom"}
    return edges.get(abd.uEdge, None)


# ==============================
# Layout y apertura de scrcpy
# ==============================

def abrir_scrcpy(seriales, porcentaje_ancho=0.70, margen_x=20, margen_y=40, origen_x=None, origen_y=None):
    total = len(seriales)
    print(f"Total de celulares {total}")
    if total == 0:
        print("No hay dispositivos conectados.")
        return

    # Verificar si SCRCPY está instalado
    import os
    if not os.path.exists(SCRCPY_PATH):
        print("ERROR: SCRCPY no esta instalado o no se encuentra en la ruta configurada.")
        print(f"Ruta esperada: {SCRCPY_PATH}")
        print("Descarga SCRCPY desde: https://github.com/Genymobile/scrcpy/releases")
        return

    # Área usable (excluye barra de tareas)
    wa_left, wa_top, wa_right, wa_bottom, wa_w, wa_h = obtener_work_area()

    area_max_ancho = int(wa_w * max(0.1, min(1.0, porcentaje_ancho)))
    area_max_alto = wa_h

    if origen_x is None:
        origen_x = wa_left + 10
    if origen_y is None:
        origen_y = wa_top + 45

    # Grid cuadrado
    columnas = max(1, math.ceil(math.sqrt(total)))
    filas = max(1, math.ceil(total / columnas))

    ancho_disp = max(200, (area_max_ancho - (columnas - 1) * margen_x) // columnas)
    alto_disp  = max(200, (area_max_alto  - (filas    - 1) * margen_y) // filas)

    max_w = wa_right - origen_x - (columnas - 1) * margen_x
    max_h = wa_bottom - origen_y - (filas    - 1) * margen_y
    if columnas > 0:
        ancho_disp = min(ancho_disp, max_w // columnas)
    if filas > 0:
        alto_disp = min(alto_disp, max_h // filas)

    ancho_disp = max(ancho_disp, 240)
    alto_disp  = max(alto_disp, 320)


    for i, serial in enumerate(seriales):
        fila = i // columnas
        columna = i % columnas
        pos_x = origen_x + columna * (ancho_disp + margen_x)
        pos_y = origen_y + fila    * (alto_disp  + margen_y)

        pos_x = max(wa_left, min(pos_x, wa_right  - ancho_disp))
        pos_y = max(wa_top,  min(pos_y, wa_bottom - alto_disp))

        # 🔎 Verificar si ya hay scrcpy abierto para este serial
        procesos_activos = [p.info['cmdline'] for p in psutil.process_iter(attrs=['cmdline'])]
        ya_abierto = any(
            (p and isinstance(p, list) and serial in " ".join(p))
            for p in procesos_activos if p and len(p) > 0 and p[0].lower().endswith("scrcpy.exe")
        )
        if ya_abierto:
            print(f"🔁 SCRCPY ya está abierto para {serial}, saltando.")
            continue

        # Guardar snapshot de procesos antes de abrir
        procesos_previos = procesos_activos[:]

        print(f"🪟 Abriendo SCRCPY para {serial} en ({pos_x},{pos_y}) tamaño {ancho_disp}×{alto_disp}")
        subprocess.Popen(
            [
                SCRCPY_PATH,
                "-s", serial,
                "--max-size", "720",
                f"--window-title={serial}",
                "--window-width",  str(ancho_disp),
                "--window-height", str(alto_disp),
                "--window-x",      str(pos_x),
                "--window-y",      str(pos_y),
            ],
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        # Esperar un poco y validar que realmente se abrió
        time.sleep(1.2)
        procesos_nuevos = [p.info['cmdline'] for p in psutil.process_iter(attrs=['cmdline'])]
        opened = any(
            (p and isinstance(p, list) and serial in " ".join(p))
            for p in procesos_nuevos if p not in procesos_previos
        )
        if not opened:
            print(f"⚠️ ERROR: scrcpy no se abrió para {serial}, saltando.")
            continue

        # Bloquear rotación (opcional)
        try:
            subprocess.run([ADB_PATH, "-s", serial, "shell", "settings", "put", "system", "accelerometer_rotation", "0"], check=False)
            subprocess.run([ADB_PATH, "-s", serial, "shell", "settings", "put", "system", "user_rotation", "0"], check=False)
        except Exception:
            pass


def cerrar_scrcpy():
    """Cierra todos los procesos de scrcpy."""
    for proc in psutil.process_iter(attrs=['name']):
        if proc.info['name'] and "scrcpy" in proc.info['name'].lower():
            try:
                proc.kill()
            except Exception:
                pass
    print("✅ scrcpy cerrado.")
