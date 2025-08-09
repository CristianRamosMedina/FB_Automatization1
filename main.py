import sys
import subprocess
import time
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer

class Ventana(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control de pantallas")
        self.setGeometry(200, 200, 800, 400)

        # Layout principal
        self.layout_principal = QVBoxLayout()
        self.setLayout(self.layout_principal)

        # Título
        self.titulo = QLabel()
        self.titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.titulo.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.layout_principal.addWidget(self.titulo)

        # Layout de pantallas
        self.layout_pantallas = QHBoxLayout()
        self.layout_principal.addLayout(self.layout_pantallas)

        # Timer para refrescar cada 2 segundos
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_pantallas)
        self.timer.start(2000)

        self.actualizar_pantallas()

    def obtener_cantidad_celulares(self):
        """Usa ADB para obtener lista de teléfonos conectados"""
        try:
            resultado = subprocess.check_output(["adb", "devices"], text=True)
            lineas = resultado.strip().split("\n")[1:]  # Saltar primera línea
            dispositivos = [l for l in lineas if l.strip() and "device" in l]
            return len(dispositivos)
        except:
            return 0

    def actualizar_pantallas(self):
        # Limpiar layout anterior
        while self.layout_pantallas.count():
            item = self.layout_pantallas.takeAt(0)
            if item.layout():
                while item.layout().count():
                    w = item.layout().takeAt(0).widget()
                    if w:
                        w.deleteLater()

        # Obtener cantidad
        cantidad = self.obtener_cantidad_celulares()
        self.titulo.setText(f"Cantidad de celulares conectados: {cantidad}")

        # Dibujar pantallas
        for i in range(cantidad):
            contenedor = QVBoxLayout()
            pantalla = QLabel()
            pantalla.setFixedSize(180, 250)
            pantalla.setStyleSheet("""
                border: 2px solid black;
                border-radius: 20px;
                background-color: white;
            """)
            texto = QLabel(f"pantalla #{i+1}")
            texto.setAlignment(Qt.AlignmentFlag.AlignCenter)
            contenedor.addWidget(pantalla, alignment=Qt.AlignmentFlag.AlignCenter)
            contenedor.addWidget(texto)
            self.layout_pantallas.addLayout(contenedor)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = Ventana()
    ventana.show()
    sys.exit(app.exec())
