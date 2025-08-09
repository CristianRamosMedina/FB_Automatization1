import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QImage
import subprocess
import cv2
import numpy as np

class Ventana(QWidget):
    def __init__(self, seriales):
        super().__init__()
        self.setWindowTitle("Control de pantallas")
        self.setGeometry(200, 200, 800, 400)
        self.seriales = seriales
        self.capturas = []

        layout_principal = QVBoxLayout()
        titulo = QLabel(f"Cantidad de celulares conectados: {len(seriales)}")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout_principal.addWidget(titulo)

        layout_pantallas = QHBoxLayout()

        for serial in seriales:
            contenedor = QVBoxLayout()
            pantalla = QLabel()
            pantalla.setFixedSize(180, 250)
            pantalla.setStyleSheet(
                "border: 2px solid black; border-radius: 20px; background-color: black;"
            )
            texto = QLabel(serial)
            texto.setAlignment(Qt.AlignmentFlag.AlignCenter)
            contenedor.addWidget(pantalla, alignment=Qt.AlignmentFlag.AlignCenter)
            contenedor.addWidget(texto)
            layout_pantallas.addLayout(contenedor)
            self.capturas.append(pantalla)

        layout_principal.addLayout(layout_pantallas)
        self.setLayout(layout_principal)

        # Timer para refrescar
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_frames)
        self.timer.start(1000)  # 1 segundo para no saturar ADB

    def actualizar_frames(self):
        for i, serial in enumerate(self.seriales):
            try:
                proc = subprocess.Popen(
                    ["adb", "-s", serial, "exec-out", "screencap", "-p"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                imagen_bytes, _ = proc.communicate(timeout=5)

                if not imagen_bytes:
                    print(f"[ADVERTENCIA] No se recibió imagen de {serial}")
                    continue

                np_arr = np.frombuffer(imagen_bytes, np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                if frame is None:
                    print(f"[ADVERTENCIA] No se pudo decodificar la imagen de {serial}")
                    continue

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (180, 250))
                qimg = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format.Format_RGB888)
                self.capturas[i].setPixmap(QPixmap.fromImage(qimg))

            except subprocess.TimeoutExpired:
                print(f"[ERROR] Tiempo de espera agotado para {serial}")
            except Exception as e:
                print(f"[ERROR] Capturando de {serial}: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    try:
        salida = subprocess.check_output(["adb", "devices"], text=True).strip().split("\n")[1:]
        seriales_detectados = [line.split()[0] for line in salida if "device" in line]
    except Exception as e:
        print(f"[ERROR] No se pudieron detectar dispositivos: {e}")
        seriales_detectados = []

    ventana = Ventana(seriales_detectados if seriales_detectados else ["Sin dispositivos"])
    ventana.show()
    sys.exit(app.exec())
