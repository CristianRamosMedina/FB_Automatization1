import sys
import threading
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea,
    QGridLayout, QCheckBox, QApplication
)
from PyQt5.QtCore import Qt

from core.scrcpy_manager import obtener_seriales, abrir_scrcpy, cerrar_scrcpy
from core.tiktok_funcs import entrenar, detener_funcion, silenciar_dispositivo, gestos_videos_random, cambiar_todas_las_cuentas
from core.config import detectar_usuarios_en_pantalla, hilos_activos
from core.tiktok_funcs.TiktokCuentaScan import Tiktok_Cuentas

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1200, 500)  # Tamaño inicial
        self.setMinimumSize(800, 400)  # Tamaño mínimo
        self.setMaximumSize(1600, 900)  # Tamaño máximo opcional
        self.setWindowTitle("Control TikTok - Multi Dispositivo")
        self.setStyleSheet("background-color: #121212; color: white;")
        self.seriales = obtener_seriales()
        self.checkboxes = {}

        main_layout = QVBoxLayout()

        # ---------------- Botones globales ----------------
        top_buttons = QHBoxLayout()

        btn_init = QPushButton("📱 Inicializar")
        btn_init.setStyleSheet("background-color: #e91e63; color: white; font-weight: bold;")
        btn_init.clicked.connect(lambda: abrir_scrcpy(self.seriales))

        btn_close = QPushButton("❌ Cerrar scrcpy")
        btn_close.setStyleSheet("background-color: #ff5722; color: white; font-weight: bold;")
        btn_close.clicked.connect(cerrar_scrcpy)

        btn_entrenar_sel = QPushButton("▶ Entrenar seleccionados")
        btn_entrenar_sel.setStyleSheet("background-color: #4caf50; color: white; font-weight: bold;")
        btn_entrenar_sel.clicked.connect(self.entrenar_seleccionados)

        btn_gestos_video = QPushButton("🎬 Gestos Video Random")
        btn_gestos_video.setStyleSheet("background-color: #ff9800; color: white; font-weight: bold;")
        btn_gestos_video.clicked.connect(self.gestos_videos_seleccionados)

        btn_cambiar_cuentas = QPushButton("🔄 Cambiar cuentas seleccionados")
        btn_cambiar_cuentas.setStyleSheet("background-color: #2196f3; color: white; font-weight: bold;")
        btn_cambiar_cuentas.clicked.connect(self.cambiar_cuentas_seleccionadas)

        btn_detener_sel = QPushButton("⏹ Detener seleccionados")
        btn_detener_sel.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
        btn_detener_sel.clicked.connect(self.detener_seleccionados)

        btn_silenciar_sel = QPushButton("🔇 Silenciar seleccionados")
        btn_silenciar_sel.setStyleSheet("background-color: #9c27b0; color: white; font-weight: bold;")
        btn_silenciar_sel.clicked.connect(self.silenciar_seleccionados)

        # Añadir todos los botones globales en orden
        for btn in [
            btn_gestos_video, btn_cambiar_cuentas, btn_init, btn_close,
            btn_entrenar_sel, btn_detener_sel, btn_silenciar_sel
        ]:
            btn.setFixedHeight(30)  # Altura uniforme
            top_buttons.addWidget(btn)

        main_layout.addLayout(top_buttons)

        # ---------------- Lista de dispositivos ----------------
        scroll = QScrollArea()
        container = QWidget()
        grid = QGridLayout()

        for idx, serial in enumerate(self.seriales):
            chk = QCheckBox(serial)
            self.checkboxes[serial] = chk

            btn_entrenar = QPushButton("▶ Entrenar")
            btn_entrenar.setStyleSheet("background-color: #4caf50; color: white; font-weight: bold;")
            btn_entrenar.clicked.connect(lambda _, s=serial: self.run_thread(entrenar, s))

            btn_detener = QPushButton("⏹ Detener")
            btn_detener.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
            btn_detener.clicked.connect(lambda _, s=serial: detener_funcion(s))

            btn_silenciar = QPushButton("🔇 Silenciar")
            btn_silenciar.setStyleSheet("background-color: #9c27b0; color: white; font-weight: bold;")
            btn_silenciar.clicked.connect(lambda _, s=serial: self.run_thread(silenciar_dispositivo, s))

            # Botones con mismo tamaño
            for b in [btn_entrenar, btn_detener, btn_silenciar]:
                b.setFixedHeight(25)
                b.setMinimumWidth(120)

            grid.addWidget(chk, idx, 0)
            grid.addWidget(btn_entrenar, idx, 1)
            grid.addWidget(btn_detener, idx, 2)
            grid.addWidget(btn_silenciar, idx, 3)

        container.setLayout(grid)
        scroll.setWidget(container)
        scroll.setWidgetResizable(True)
        main_layout.addWidget(scroll)

        self.setLayout(main_layout)

    # ---------------- Métodos auxiliares ----------------
    def is_selected(self, serial):
        return self.checkboxes.get(serial) and self.checkboxes[serial].isChecked()

    def run_thread(self, func, serial):
        if not self.is_selected(serial):
            print(f"⚠ {serial} no está seleccionado.")
            return
        t = threading.Thread(target=func, args=(serial,), daemon=True)
        t.start()

    def entrenar_seleccionados(self):
        for serial in self.seriales:
            if self.is_selected(serial):
                self.run_thread(entrenar, serial)

    def detener_seleccionados(self):
        for serial in self.seriales:
            if self.is_selected(serial):
                detener_funcion(serial)

    def silenciar_seleccionados(self):
        for serial in self.seriales:
            if self.is_selected(serial):
                self.run_thread(silenciar_dispositivo, serial)

    def gestos_videos_seleccionados(self):
        for serial in self.seriales:
            if self.is_selected(serial):
                t = threading.Thread(target=gestos_videos_random, args=(serial,), daemon=True)
                t.start()

    def cambiar_cuentas_seleccionadas(self):
        for serial in self.seriales:
            if self.is_selected(serial):
                self.run_thread(cambiar_todas_las_cuentas, serial)

    def detectar_cuentas(self):
        for serial in self.seriales:
            if self.is_selected(serial):
                self.run_thread(Tiktok_Cuentas, serial)

# ---------------- Ejecución directa ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
