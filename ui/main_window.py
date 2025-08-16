import sys
import threading
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea,
    QGridLayout, QCheckBox, QApplication, QLabel
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from core.scrcpy_manager import obtener_seriales, abrir_scrcpy, cerrar_scrcpy
from core.tiktok_funcs import (
    entrenar, detener_funcion, silenciar_dispositivo,
    gestos_videos_random, cambiar_todas_las_cuentas
)
from core.config import hilos_activos



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1200, 500)
        self.setMinimumSize(800, 400)
        self.setMaximumSize(1600, 900)
        self.setWindowTitle("Control TikTok - Multi Dispositivo")
        self.setStyleSheet("background-color: #121212; color: white;")

        self.seriales = obtener_seriales()
        self.checkboxes = {}
        self.estado_dispositivos = {}
        self.iconos_dispositivos = {}

        # Iconos para cada acción
        self.iconos = {
            "entrenar": QPixmap("icons/entrenar.png").scaled(16, 16),
            "gestos": QPixmap("icons/gestos.png").scaled(16, 16),
            "cambiar_cuentas": QPixmap("icons/cuentas.png").scaled(16, 16),
            None: QPixmap()
        }

        main_layout = QVBoxLayout()

        # ---------------- Botones globales ----------------
        top_buttons = QHBoxLayout()

        btn_init = QPushButton("📱 Inicializar")
        btn_init.setStyleSheet("background-color: #e91e63; color: white; font-weight: bold;")
        btn_init.clicked.connect(lambda: abrir_scrcpy(self.seriales, {}))

        btn_close = QPushButton("❌ Cerrar")
        btn_close.setStyleSheet("background-color: #ff5722; color: white; font-weight: bold;")
        btn_close.clicked.connect(cerrar_scrcpy)

        btn_entrenar_sel = QPushButton("▶ Entrenar ")
        btn_entrenar_sel.setStyleSheet("background-color: #4caf50; color: white; font-weight: bold;")
        btn_entrenar_sel.clicked.connect(lambda: self.ejecutar_seleccionados("entrenar", entrenar))

        btn_gestos_video = QPushButton("🎬 Gestos Video Random")
        btn_gestos_video.setStyleSheet("background-color: #ff9800; color: white; font-weight: bold;")
        btn_gestos_video.clicked.connect(lambda: self.ejecutar_seleccionados("gestos", gestos_videos_random))

        btn_cambiar_cuentas = QPushButton("🔄 Cambiar cuentas ")
        btn_cambiar_cuentas.setStyleSheet("background-color: #2196f3; color: white; font-weight: bold;")
        btn_cambiar_cuentas.clicked.connect(lambda: self.ejecutar_seleccionados("cambiar_cuentas", cambiar_todas_las_cuentas))

        btn_detener_sel = QPushButton("⏹ Detener seleccionados")
        btn_detener_sel.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
        btn_detener_sel.clicked.connect(self.detener_seleccionados)

        btn_silenciar_sel = QPushButton("🔇 Silenciar seleccionados")
        btn_silenciar_sel.setStyleSheet("background-color: #9c27b0; color: white; font-weight: bold;")
        btn_silenciar_sel.clicked.connect(lambda: self.ejecutar_seleccionados(None, silenciar_dispositivo))

        btn_clear = QPushButton("🧹 Limpiar selección")
        btn_clear.setStyleSheet("background-color: #607d8b; color: white; font-weight: bold;")
        btn_clear.clicked.connect(self.limpiar_checkboxes)

        for btn in [
            btn_gestos_video, btn_cambiar_cuentas, btn_init, btn_close,
            btn_entrenar_sel, btn_detener_sel, btn_silenciar_sel, btn_clear
        ]:
            btn.setFixedHeight(30)
            top_buttons.addWidget(btn)

        main_layout.addLayout(top_buttons)

        # ---------------- Lista de dispositivos ----------------
        scroll = QScrollArea()
        container = QWidget()
        grid = QGridLayout()

        for idx, serial in enumerate(self.seriales):
            # Layout para checkbox + icono
            cel_layout = QHBoxLayout()
            cel_layout.setContentsMargins(0, 0, 0, 0)

            chk = QCheckBox(f"Cell #{idx+1}")
            self.checkboxes[serial] = chk

            lbl_icono = QLabel()
            lbl_icono.setPixmap(self.iconos[None])
            self.iconos_dispositivos[serial] = lbl_icono

            cel_layout.addWidget(chk)
            cel_layout.addWidget(lbl_icono)

            cel_widget = QWidget()
            cel_widget.setLayout(cel_layout)

            # Botones por dispositivo
            btn_entrenar = QPushButton("▶ Entrenar")
            btn_entrenar.setStyleSheet("background-color: #4caf50; color: white; font-weight: bold;")
            btn_entrenar.clicked.connect(lambda _, s=serial: self.ejecutar_con_icono(s, "entrenar", entrenar))

            btn_detener = QPushButton("⏹ Detener")
            btn_detener.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
            btn_detener.clicked.connect(lambda _, s=serial: self.detener_con_icono(s))

            btn_silenciar = QPushButton("🔇 Silenciar")
            btn_silenciar.setStyleSheet("background-color: #9c27b0; color: white; font-weight: bold;")
            btn_silenciar.clicked.connect(lambda _, s=serial: self.ejecutar_con_icono(s, None, silenciar_dispositivo))

            grid.addWidget(cel_widget, idx, 0)
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
        t = threading.Thread(target=func, args=(serial,), daemon=True)
        t.start()

    def ejecutar_con_icono(self, serial, accion, func):
        if not self.is_selected(serial):
            print(f"⚠ {serial} no está seleccionado.")
            return
        self.run_thread(func, serial)
        self.estado_dispositivos[serial] = accion
        self.iconos_dispositivos[serial].setPixmap(self.iconos[accion])
        self.checkboxes[serial].setChecked(False)

    def detener_con_icono(self, serial):
        detener_funcion(serial)
        self.estado_dispositivos[serial] = None
        self.iconos_dispositivos[serial].setPixmap(self.iconos[None])
        self.checkboxes[serial].setChecked(False)

    def ejecutar_seleccionados(self, accion, func):
        for serial in self.seriales:
            if self.is_selected(serial):
                self.ejecutar_con_icono(serial, accion, func)
        self.limpiar_checkboxes()

    def detener_seleccionados(self):
        for serial in self.seriales:
            if self.is_selected(serial):
                self.detener_con_icono(serial)
        self.limpiar_checkboxes()

    def limpiar_checkboxes(self):
        """Desmarca todos los checkboxes manualmente"""
        for chk in self.checkboxes.values():
            chk.setChecked(False)


# ---------------- Ejecución directa ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
