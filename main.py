from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt
import sys

class Ventana(QWidget):
    def __init__(self, cantidad_celulares):
        super().__init__()
        self.setWindowTitle("Control de pantallas")
        self.setGeometry(200, 200, 800, 400)

        # Layout principal
        layout_principal = QVBoxLayout()

        # Título
        titulo = QLabel("Cantidad de celulares conectados: " + str(cantidad_celulares))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: none;")
        layout_principal.addWidget(titulo)

        # Layout para las pantallas (horizontal)
        layout_pantallas = QHBoxLayout()

        # Crear cada "celular" (pantalla simulada)
        for i in range(cantidad_celulares):
            contenedor = QVBoxLayout()

            # Rectángulo simulando pantalla
            pantalla = QLabel()
            pantalla.setFixedSize(180, 250)
            pantalla.setStyleSheet("""
                border: 2px solid black;
                border-radius: 20px;
                background-color: white;
            """)

            # Texto debajo
            texto = QLabel(f"pantalla #{i+1}")
            texto.setAlignment(Qt.AlignmentFlag.AlignCenter)

            contenedor.addWidget(pantalla, alignment=Qt.AlignmentFlag.AlignCenter)
            contenedor.addWidget(texto)

            layout_pantallas.addLayout(contenedor)

        layout_principal.addLayout(layout_pantallas)
        self.setLayout(layout_principal)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    cantidad_detectada = 3  # Aquí pondrías el número que obtienes de tu código serial
    ventana = Ventana(cantidad_detectada)
    ventana.show()
    sys.exit(app.exec())
