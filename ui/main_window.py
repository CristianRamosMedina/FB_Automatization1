import sys
import threading

# ✅ Correcto: QGraphicsOpacityEffect viene de QtWidgets
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea,
    QGridLayout, QCheckBox, QApplication, QLabel, QGraphicsOpacityEffect, QFrame  # 👈 QFrame
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPixmap  # ✅ Solo QPixmap desde QtGui

# ⛔️ Elimina esta línea que causa el error:
# from PyQt5.QtGui import QPixmap, QGraphicsOpacityEffect


from core.scrcpy_manager import obtener_seriales, abrir_scrcpy, cerrar_scrcpy
from core.tiktok_funcs import entrenar, detener_funcion, silenciar_dispositivo
from core.config import hilos_activos
from core.tiktok_funcs.cambiarCuentas import cambiar_todas_las_cuentas
from core.tiktok_funcs.TiktokCuentaScan import TitkokCuentas
from core.tiktok_funcs.VideosMujeres import Gestos_VIDEOS
import json


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
        self.status_buttons = {}   # 🔵 indicadores por dispositivo
        self._animations = {}      # animaciones por dispositivo

        # Iconos (siguen disponibles si los usas en otro lado)
        self.iconos = {
            "entrenar": QPixmap("icons/entrenar.png").scaled(16, 16),
            "gestos": QPixmap("icons/gestos.png").scaled(16, 16),
            "cambiar_cuentas": QPixmap("icons/cuentas.png").scaled(16, 16),
            None: QPixmap()
        }

        # Paleta de colores por acción
        self.color_accion = {
            "entrenar": "#4caf50",
            "gestos": "#ff9800",
            "cambiar_cuentas": "#2196f3",
            None: "#606060"
        }

        main_layout = QVBoxLayout()

        # ---------------- Botones globales ----------------
        top_buttons = QHBoxLayout()

        btn_init = QPushButton("📱 Inicializar")
        btn_init.setStyleSheet("background-color: #e91e63; color: white; font-weight: bold;")
        btn_init.clicked.connect(lambda: abrir_scrcpy(self.seriales))

        btn_close = QPushButton("❌ Cerrar")
        btn_close.setStyleSheet("background-color: #ff5722; color: white; font-weight: bold;")
        btn_close.clicked.connect(cerrar_scrcpy)

        btn_entrenar_sel = QPushButton("▶ Entrenar ")
        btn_entrenar_sel.setStyleSheet("background-color: #4caf50; color: white; font-weight: bold;")
        btn_entrenar_sel.clicked.connect(lambda: self.ejecutar_seleccionados("entrenar", entrenar))

        btn_gestos_video = QPushButton("🎬 Detectar TikTok Cuentas ")
        btn_gestos_video.setStyleSheet("background-color: #ff9800; color: white; font-weight: bold;")
        btn_gestos_video.clicked.connect(lambda: self.ejecutar_seleccionados("gestos", TitkokCuentas))

        btn_cambiar_cuentas = QPushButton("🔄 Cambiar cuentas ")
        btn_cambiar_cuentas.setStyleSheet("background-color: #2196f3; color: white; font-weight: bold;")
        btn_cambiar_cuentas.clicked.connect(lambda: self.ejecutar_seleccionados("cambiar_cuentas", cambiar_todas_las_cuentas))

        btn_gestos_videos = QPushButton("🔄 Gestos Videos ")
        btn_gestos_videos.setStyleSheet("background-color: #2196f3; color: white; font-weight: bold;")
        btn_gestos_videos.clicked.connect(lambda: self.ejecutar_seleccionados("cambiar_cuentas", Gestos_VIDEOS))

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
            btn_init, btn_close, btn_gestos_video, btn_cambiar_cuentas,
            btn_entrenar_sel, btn_detener_sel, btn_gestos_videos,
            btn_silenciar_sel, btn_clear
        ]:
            btn.setFixedHeight(30)
            top_buttons.addWidget(btn)

        main_layout.addLayout(top_buttons)

        # ---------------- Checkbox "Marcar todos" ----------------
        marcar_todos_layout = QHBoxLayout()
        self.chk_marcar_todos = QCheckBox("✅ Marcar todos")
        self.chk_marcar_todos.stateChanged.connect(self.toggle_marcar_todos)
        marcar_todos_layout.addWidget(self.chk_marcar_todos)
        main_layout.addLayout(marcar_todos_layout)

        # ---------------- Lista de dispositivos ----------------
        scroll = QScrollArea()
        container = QWidget()
        grid = QGridLayout()

        for idx, serial in enumerate(self.seriales):
            cel_layout = QHBoxLayout()
            cel_layout.setContentsMargins(0, 0, 0, 0)

            dot_size = 14
            dot = QFrame()
            dot.setFixedSize(dot_size, dot_size)
            dot.setStyleSheet(f"""
                QFrame {{
                    background-color: #606060;
                    border: none;
                    border-radius: {dot_size//2}px;
                    margin-right: 6px;
                }}
            """)
            self.status_buttons[serial] = dot

            chk = QCheckBox(f"Cell #{idx+1}")
            self.checkboxes[serial] = chk

            lbl_icono = QLabel()
            lbl_icono.setPixmap(self.iconos[None])
            self.iconos_dispositivos[serial] = lbl_icono

            cel_layout.addWidget(dot)
            cel_layout.addWidget(chk)
            cel_layout.addWidget(lbl_icono)

            cel_widget = QWidget()
            cel_widget.setLayout(cel_layout)

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

            # Estado inicial
            self._set_estado_visual(serial, None)

        container.setLayout(grid)
        scroll.setWidget(container)
        scroll.setWidgetResizable(True)
        main_layout.addWidget(scroll)

        self.setLayout(main_layout)

    # ---------------- Animación e indicador ----------------
    def _set_estado_visual(self, serial, accion):
        """Pinta el dot y activa/desactiva pulso según la acción."""
        color = self.color_accion.get(accion, "#606060")
        dot = self.status_buttons[serial]
        # Mantiene el border-radius para que sea circular
        r = dot.width() // 2
        dot.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border: none;
                border-radius: {r}px;
                margin-right: 6px;
            }}
        """)
        if accion is None:
            self._stop_pulse(serial)
        else:
            self._start_pulse(serial)

    def _start_pulse(self, serial):
        dot = self.status_buttons[serial]
        effect = QGraphicsOpacityEffect(dot)
        dot.setGraphicsEffect(effect)

        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(800)
        anim.setStartValue(0.45)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.InOutQuad)
        anim.setLoopCount(-1)
        anim.start()

        self._animations[serial] = (effect, anim)

    def _stop_pulse(self, serial):
        pair = self._animations.get(serial)
        if pair:
            effect, anim = pair
            anim.stop()
            # Volver a opacidad normal
            try:
                effect.setOpacity(1.0)
                self.status_buttons[serial].setGraphicsEffect(None)
            except Exception:
                pass
            self._animations.pop(serial, None)

    # ---------------- Lógica de selección ----------------
    def toggle_marcar_todos(self, state):
        marcar = state == Qt.Checked
        for chk in self.checkboxes.values():
            chk.setChecked(marcar)

    def is_selected(self, serial):
        return self.checkboxes.get(serial) and self.checkboxes[serial].isChecked()

    # ---------------- Ejecución por hilo ----------------
    def run_thread(self, func, serial):
        if func == Gestos_VIDEOS:
            t = threading.Thread(target=func, args=(serial, self.data_json), daemon=True)
        else:
            t = threading.Thread(target=func, args=(serial,), daemon=True)
        t.start()

    def ejecutar_con_icono(self, serial, accion, func):
        if not self.is_selected(serial):
            print(f"⚠ {serial} no está seleccionado.")
            return
        # Visual ON
        self.estado_dispositivos[serial] = accion
        self._set_estado_visual(serial, accion)
        # Lanzar hilo
        self.run_thread(func, serial)
        # Desmarcar el checkbox de ese dispositivo
        self.checkboxes[serial].setChecked(False)

    def detener_con_icono(self, serial):
        detener_funcion(serial)
        self.estado_dispositivos[serial] = None
        self._set_estado_visual(serial, None)
        self.checkboxes[serial].setChecked(False)

    def ejecutar_seleccionados(self, accion, func):
        for serial in self.seriales:
            if self.is_selected(serial):
                self.ejecutar_con_icono(serial, accion, func)
        self.limpiar_checkboxes_checkbox_global()

    def detener_seleccionados(self):
        for serial in self.seriales:
            if self.is_selected(serial):
                self.detener_con_icono(serial)
        self.limpiar_checkboxes_checkbox_global()

    def limpiar_checkboxes_checkbox_global(self):
        for chk in self.checkboxes.values():
            chk.setChecked(False)
        self.chk_marcar_todos.setChecked(False)

    def limpiar_checkboxes(self):
        for chk in self.checkboxes.values():
            chk.setChecked(False)
        self.chk_marcar_todos.setChecked(False)


# ---------------- Ejecución directa ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
