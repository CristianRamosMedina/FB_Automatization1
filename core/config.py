import os
import json
import subprocess
import time
import io
import re
from datetime import datetime
from core.paths import ADB_PATH, TESSERACT_PATH  # ✅ CORREGIDO
import pytesseract

from PIL import UnidentifiedImageError, Image

# Configuración pytesseract
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


# ------------------- VARIABLES GLOBALES -------------------
# Diccionario para saber si un hilo está activo o detenido
hilos_activos = {}
SERVICE_ACCOUNT_FILE = "data/credenciales.json"


