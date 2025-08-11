import sys
import subprocess
import psutil
import math
import time
import shutil
import ctypes
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout
)
from PyQt6.QtCore import Qt


# ====== CONFIG ======
SCRCPY_PATH = shutil.which("scrcpy") or "scrcpy"
ADB_PATH = shutil.which("adb") or "adb"


# ====== DETECCIÓN DE DISPOSITIVOS ======
def obtener_seriales():
    try:
        salida = subprocess.check_output(
            [ADB_PATH, "devices"],
            text=True
        ).strip().split("\n")[1:]

        seriales = [line.split()[0] for line in salida if "\tdevice" in line]
        return seriales
    except Exception as e:
        print(f"[ERROR] No se pudieron detectar dispositivos: {e}")
        return []



# ====== ABRIR SCRCPY PARA UN SOLO DISPOSITIVO ======
def abrir_scrcpy_uno(serial):
    try:
        procesos_activos = [
            p.info['cmdline']
            for p in psutil.process_iter(attrs=['cmdline'])
        ]
        if any(serial in " ".join(cmd) for cmd in procesos_activos if cmd):
            print(f"[INFO] scrcpy ya está abierto para {serial}")
            return

        subprocess.Popen([SCRCPY_PATH, "-s", serial])
    except Exception as e:
        print(f"[ERROR] No se pudo abrir scrcpy para {serial}: {e}")


# ====== ABRIR SCRCPY PARA TODOS LOS DISPOSITIVOS ======
def abrir_scrcpy_todos(seriales):
    procesos_activos = [p.info['cmdline'] for p in psutil.process_iter(attrs=['cmdline'])]
    total = len(seriales)
    if total == 0:
        print("❌ No hay dispositivos conectados.")
        return

    pantalla_ancho, pantalla_alto = obtener_tamano_pantalla()

    area_max_ancho = int(pantalla_ancho * 0.7)
    area_max_alto = pantalla_alto

    margen_x = 10
    margen_y = 50

    columnas = math.ceil(math.sqrt(total))
    filas = math.ceil(total / columnas)

    ancho_disp = (area_max_ancho - (columnas - 1) * margen_x) // columnas
    alto_disp = (area_max_alto - (filas - 1) * margen_y) // filas

    origen_x = 10
    origen_y = 40

    for i, serial in enumerate(seriales):
        ya_abierto = any(
            p and isinstance(p, list) and serial in ' '.join(p)
            for p in procesos_activos if p and p[0].endswith("scrcpy.exe")
        )

        nombre_mostrado = f"Cel#{i+1}"
        fila = i // columnas
        columna = i % columnas
        pos_x = origen_x + columna * (ancho_disp + margen_x)
        pos_y = origen_y + fila * (alto_disp + margen_y)

        if ya_abierto:
            print(f"🔁 SCRCPY ya está abierto para {serial} ({nombre_mostrado}).")
        else:
            print(f"🪟 Abriendo SCRCPY para {nombre_mostrado} ({serial})")
            subprocess.Popen(
                [
                    SCRCPY_PATH,
                    "-s", serial,
                    "--max-size", "720",
                    f"--window-title={nombre_mostrado}",
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


# ====== INTERFAZ ======
class Ventana(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control de pantallas")
        self.setGeometry(300, 200, 500, 400)

        self.layout_principal = QVBoxLayout()
        self.setLayout(self.layout_principal)

        self.label_titulo = QLabel()
        self.label_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_titulo.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.layout_principal.addWidget(self.label_titulo)

        self.layout_dispositivos = QVBoxLayout()
        self.layout_principal.addLayout(self.layout_dispositivos)

        botones_accion = QHBoxLayout()

        self.btn_refrescar = QPushButton("🔄 Refrescar lista")
        self.btn_refrescar.clicked.connect(self.refrescar)
        botones_accion.addWidget(self.btn_refrescar)

        self.btn_abrir_todos = QPushButton("📲 Abrir todos")
        self.btn_abrir_todos.clicked.connect(self.abrir_todos)
        botones_accion.addWidget(self.btn_abrir_todos)

        self.layout_principal.addLayout(botones_accion)

        self.listar_dispositivos()

    def listar_dispositivos(self):
        for i in reversed(range(self.layout_dispositivos.count())):
            item = self.layout_dispositivos.itemAt(i)
            if item.widget():
                item.widget().deleteLater()

        seriales = obtener_seriales()
        self.seriales_actuales = seriales

        self.label_titulo.setText(f"📱 Dispositivos conectados: {len(seriales)}")

        if not seriales:
            lbl = QLabel("❌ No hay dispositivos conectados.")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("color: red; font-size: 14px;")
            self.layout_dispositivos.addWidget(lbl)
            return

        for serial in seriales:
            fila = QHBoxLayout()

            lbl_serial = QLabel(serial)
            lbl_serial.setStyleSheet("font-size: 14px;")
            lbl_serial.setFixedWidth(200)

            btn_abrir = QPushButton("📲 Abrir pantalla")
            btn_abrir.clicked.connect(lambda _, s=serial: abrir_scrcpy_uno(s))

            fila.addWidget(lbl_serial)
            fila.addWidget(btn_abrir)
            self.layout_dispositivos.addLayout(fila)

    def refrescar(self):
        print("[INFO] Refrescando lista de dispositivos...")
        self.listar_dispositivos()

    def abrir_todos(self):
        abrir_scrcpy_todos(self.seriales_actuales)


# ====== PROGRAMA PRINCIPAL ======
def main():
    app = QApplication(sys.argv)
    ventana = Ventana()
    ventana.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main() , 