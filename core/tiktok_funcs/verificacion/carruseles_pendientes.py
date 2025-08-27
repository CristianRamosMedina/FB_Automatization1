import os

# Ruta base dinámica
BASE_CARRUSEL_PATH = os.path.join(
    os.path.expanduser("~/Documents"),
    "Carrusel", "ImagenesCrudas", "Carrusel"
)

GRUPO = "GRUPO150"

def chequear_carruseles_pendientes():
    """
    Detecta:
      - cuántas carpetas con nombre numérico existen
      - si la carpeta GRUPO150 existe
    """
    if not os.path.exists(BASE_CARRUSEL_PATH):
        return {"numericas": 0, "grupo150": False}

    # contar carpetas con nombre numérico
    num_presentes = [
        nombre for nombre in os.listdir(BASE_CARRUSEL_PATH)
        if os.path.isdir(os.path.join(BASE_CARRUSEL_PATH, nombre))
        and nombre.isdigit()
    ]

    # verificar GRUPO150
    grupo150 = os.path.exists(os.path.join(BASE_CARRUSEL_PATH, GRUPO))

    return {
        "numericas": len(num_presentes),
        "grupo150": grupo150
    }
