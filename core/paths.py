import sys, os
from pathlib import Path

def resource_path(relative_path: str) -> str:
    """
    Devuelve la ruta válida tanto en desarrollo (python main.py)
    como en producción (pyinstaller .exe)
    """
    base_path = Path(getattr(sys, "_MEIPASS", os.path.abspath(".")))
    return base_path / relative_path

from .paths import resource_path

ASIGNACIONES_FILE    = resource_path("data/asignaciones.json")
ASIGNACIONES_VIDEO   = resource_path("data/asignacionesVideo.json")
CARRUSEL_FILE        = resource_path("data/carrusel.json")
CARRUSEL_MANUAL_FILE = resource_path("data/carrusel_manual.json")
CORREOS_FILE         = resource_path("data/correos.json")
SERVICE_ACCOUNT_FILE    = resource_path("data/credenciales.json")
DISPOSITIVOS_FILE    = resource_path("data/dispositivos.json")
VIDEOS_FILE          = resource_path("data/videos.json")

ADB_PATH = r"C:\Users\Cris\AppData\Local\Android\Sdk\platform-tools\adb.exe"
SCRCPY_PATH = r"C:\scrcpy\scrcpy.exe"  # Instalar en C:\scrcpy\
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"