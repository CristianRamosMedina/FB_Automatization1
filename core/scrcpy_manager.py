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
    """Abre scrcpy en mosaico para los dispositivos dados (evitando la barra de tareas)."""
    if not seriales:
        print("❌ No hay dispositivos conectados.")
        return

    print(f"📱 Seriales conectados: {len(seriales)}")

    # Evita abrir duplicados
    procesos_activos = [p.info['cmdline'] for p in psutil.process_iter(attrs=['cmdline'])]

    # --- Tamaño de pantalla original (por si falla el work area) ---
    pantalla_ancho, pantalla_alto = obtener_tamano_pantalla()

    # --- Obtener área de trabajo (excluye la barra de tareas) SIN crear funciones extra ---
    try:
        SPI_GETWORKAREA = 0x0030
        class RECT(ctypes.Structure):
            _fields_ = [("left", ctypes.c_long),
                        ("top", ctypes.c_long),
                        ("right", ctypes.c_long),
                        ("bottom", ctypes.c_long)]
        rect = RECT()
        ctypes.windll.user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(rect), 0)
        work_left, work_top, work_right, work_bottom = rect.left, rect.top, rect.right, rect.bottom
        work_w = max(0, work_right - work_left)
        work_h = max(0, work_bottom - work_top)
    except Exception:
        # Fallback si no estamos en Windows o falla la API
        work_left, work_top = 0, 0
        work_w, work_h = pantalla_ancho, pantalla_alto

    # Usa tu 70% del ancho si quieres espacio lateral
    area_max_ancho = int(work_w * 0.7)
    area_max_alto  = work_h

    # Márgenes y origen dentro del área útil (no (0,0))
    margen_x = 10
    margen_y = 10
    origen_x = work_left + 10
    origen_y = work_top  + 38

    # Grid
    columnas = math.ceil(math.sqrt(len(seriales)))
    filas = math.ceil(len(seriales) / columnas)

    # Tamaños
    ancho_disp = max(200, (area_max_ancho - (columnas - 1) * margen_x) // columnas)
    alto_disp  = max(200, (area_max_alto  - (filas    - 1) * margen_y) // filas)

    # Pequeña corrección por barra de título/bordes de la ventana
    TITLE_BAR_PAD  = 32
    WIN_BORDER_PAD = 6
    ancho_win = max(150, ancho_disp - WIN_BORDER_PAD)
    alto_win  = max(150, alto_disp  - TITLE_BAR_PAD)

    for i, serial in enumerate(seriales):
        ya_abierto = any(
            p and isinstance(p, list) and serial in ' '.join(p)
            for p in procesos_activos
            if p and p[0] and p[0].lower().endswith("scrcpy.exe")
        )

        fila = i // columnas
        columna = i % columnas
        pos_x = origen_x + columna * (ancho_disp + margen_x)
        pos_y = origen_y + fila    * (alto_disp  + margen_y)

        if not ya_abierto:
            subprocess.Popen(
                [
                    SCRCPY_PATH,
                    "-s", serial,
                    "--max-size", "720",
                    f"--window-title={serial}",
                    "--window-width",  str(ancho_win),
                    "--window-height", str(alto_win),
                    "--window-x",      str(pos_x),
                    "--window-y",      str(pos_y),
                ],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            # Bloquear rotación
            subprocess.run([ADB_PATH, "-s", serial, "shell", "settings", "put", "system", "accelerometer_rotation", "0"])
            subprocess.run([ADB_PATH, "-s", serial, "shell", "settings", "put", "system", "user_rotation", "0"])
            time.sleep(1.5)


def cerrar_scrcpy():
    """Cierra todos los procesos de scrcpy."""
    for proc in psutil.process_iter(attrs=['name']):
        if proc.info['name'] and "scrcpy" in proc.info['name'].lower():
            proc.kill()
    print("✅ scrcpy cerrado.")
