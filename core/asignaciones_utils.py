import json
import os
from pathlib import Path
from .paths import ASIGNACIONES_FILE , ASIGNACIONES_VIDEO


def _asignar_carpeta(apodo: str, file_path: Path) -> str:
    """
    Asigna una nueva carpeta (número consecutivo) a un apodo
    en el archivo JSON indicado.
    """
    if not file_path.exists():
        data = {}
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}

    # obtener último número usado
    if data:
        numeros = [int(v) for v in data.values() if str(v).isdigit()]
        ultimo = max(numeros) if numeros else 0
    else:
        ultimo = 0

    nuevo_numero = str(ultimo + 1)
    data[apodo] = nuevo_numero

    # guardar actualizado de forma atómica
    tmp = file_path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, file_path)

    print(f"📂 Apodo '{apodo}' asignado a carpeta {nuevo_numero} en {file_path.name}")
    return nuevo_numero


def asignar_carpeta_a_apodo(apodo: str) -> str:
    """
    Asigna carpeta a un apodo en ambos archivos:
    - asignaciones.json
    - asignacionesVideo.json
    Devuelve el número asignado.
    """
    numero1 = _asignar_carpeta(apodo, ASIGNACIONES_FILE)
    numero2 = _asignar_carpeta(apodo,  ASIGNACIONES_VIDEO)
    # ambos deberían coincidir siempre
    return numero1
