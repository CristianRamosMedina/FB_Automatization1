import os

# Ruta base dinámica
BASE_CARRUSEL_PATH = os.path.join(
    os.path.expanduser("~/Documents"),
    "Carrusel", "ImagenesCrudas", "Carrusel"
)

NUM_CARPETAS = 37
GRUPO = "GRUPO150"

def chequear_carruseles_pendientes():
    """
    Cuenta cuántas de las carpetas 1..37 + GRUPO150 existen en BASE_CARRUSEL_PATH.
    Devuelve un entero (0..38).
    """
    if not os.path.exists(BASE_CARRUSEL_PATH):
        print(f"⚠️ Carpeta base {BASE_CARRUSEL_PATH} no existe.")
        return 0

    pendientes = 0

    # Revisar carpetas 1 a 37
    for i in range(1, NUM_CARPETAS + 1):
        carpeta = os.path.join(BASE_CARRUSEL_PATH, str(i))
        if os.path.exists(carpeta):
            pendientes += 1

    # Revisar GRUPO150
    grupo_path = os.path.join(BASE_CARRUSEL_PATH, GRUPO)
    if os.path.exists(grupo_path):
        pendientes += 1

    return pendientes
