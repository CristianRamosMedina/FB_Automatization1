# ui/main_window.py
import sys
import threading

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea,
    QGridLayout, QCheckBox, QApplication, QLabel, QGraphicsOpacityEffect,
    QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QObject, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap

# ✅ Importaciones locales
from ui.seleccion_cuentas_dialog import SeleccionCuentasDialog
from core.scrcpy_manager import obtener_seriales, abrir_scrcpy, cerrar_scrcpy
from core.tiktok_funcs import entrenar, detener_funcion, silenciar_dispositivo
from core.tiktok_funcs.cambiarCuentas import cambiar_todas_las_cuentas
from core.tiktok_funcs.TiktokCuentaScan import TitkokCuentas
from core.tiktok_funcs.VideosMujeres import Gestos_VIDEOS
from core.config import hilos_activos
from core.tiktok_funcs.CrearCuentasTiktok.CrearCuentasTitktok import crear_cuenta_para_serial


# =================== Workers en QThread ===================
class ScanWorker(QObject):
    finished = pyqtSignal(str)           # serial
    failed  = pyqtSignal(str, str)       # serial, error

    def __init__(self, serial):
        super().__init__()
        self.serial = serial

    def run(self):
        try:
            print(f"[ScanWorker] ▶ Iniciando escaneo en {self.serial}")
            hilos_activos[self.serial] = True
            TitkokCuentas(self.serial)
            print(f"[ScanWorker] ✅ Escaneo finalizado en {self.serial}")
            self.finished.emit(self.serial)
        except Exception as e:
            self.failed.emit(self.serial, str(e))
        finally:
            # Nota: no forzamos False; quizás quieras seguir con otro paso
            pass


class ChangeWorker(QObject):
    finished = pyqtSignal(str)
    failed  = pyqtSignal(str, str)

    def __init__(self, serial):
        super().__init__()
        self.serial = serial

    def run(self):
        try:
            print(f"[ChangeWorker] ▶ Iniciando cambio en {self.serial}")
            hilos_activos[self.serial] = True
            cambiar_todas_las_cuentas(self.serial)
            print(f"[ChangeWorker] ✅ Cambio finalizado en {self.serial}")
            self.finished.emit(self.serial)
        except Exception as e:
            self.failed.emit(self.serial, str(e))
        finally:
            hilos_activos[self.serial] = False


class GenericWorker(QObject):
    """Worker genérico para funciones que reciben solo (serial)."""
    finished = pyqtSignal(str)
    failed  = pyqtSignal(str, str)

    def __init__(self, serial, func):
        super().__init__()
        self.serial = serial
        self.func = func

    def run(self):
        try:
            print(f"[GenericWorker] ▶ Ejecutando {self.func.__name__} en {self.serial}")
            hilos_activos[self.serial] = True
            self.func(self.serial)
            print(f"[GenericWorker] ✅ {self.func.__name__} finalizado en {self.serial}")
            self.finished.emit(self.serial)
        except Exception as e:
            self.failed.emit(self.serial, str(e))
        finally:
            hilos_activos[self.serial] = False


# =================== Ventana principal ===================
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1200, 700)
        self.setMinimumSize(900, 600)
        self.setMaximumSize(2000, 1200)
        self.setWindowTitle("Control TikTok - Multi Dispositivo")

        # ====== Estilos base (oscuro) ======
        self.setStyleSheet("""
            QWidget { background-color: #0f1115; color: #e8eaed; font-size: 13px; }
            QCheckBox { font-size: 13px; }
            QPushButton {
                border: 1px solid #2a2f3a; border-radius: 8px; padding: 8px 12px;
                background-color: #1a1f29; color: #e8eaed;
            }
            QPushButton:hover { background-color: #202635; }
            QPushButton#ok { background-color: #204b2d; border-color:#2e6b41; }
            QPushButton#ok:hover { background-color: #236236; }
            QPushButton#danger { background-color: #4a1c1c; border-color:#6a2a2a; }
            QPushButton#danger:hover { background-color: #5a2323; }
            QPushButton#warn { background-color: #5a2a46; border-color:#7a3a5e; }
            QPushButton#warn:hover { background-color: #6a3152; }
            QPushButton#accent { background-color: #1f3458; border-color:#2b4a7f; }
            QPushButton#accent:hover { background-color: #244069; }
            QPushButton#create { background-color: #3b2566; border-color:#53358f; }
            QPushButton#create:hover { background-color: #452c78; }

            QFrame#Toolbar {
                background-color: #121620; border: 1px solid #242a36; border-radius: 12px;
            }
            QScrollArea {
                border: 1px solid #242a36; border-radius: 12px; background: #0f1115;
            }
        """)

        # ====== Estado ======
        self.seriales = obtener_seriales()
        self.checkboxes = {}           # serial -> QCheckBox
        self.estado_dispositivos = {}  # serial -> accion actual (str|None)
        self.iconos_dispositivos = {}  # serial -> QLabel
        self.status_buttons = {}       # serial -> QFrame (dot)
        self._animations = {}          # serial -> (effect, anim)

        # QThread references
        self._scan_threads   = {}
        self._scan_workers   = {}
        self._change_threads = {}
        self._change_workers = {}
        self._generic_threads = {}
        self._generic_workers = {}
        self._pending_scans  = set()
        self._pending_changes = set()
        self._last_scanned   = set()

        # Iconos opcionales
        self.iconos = {
            "entrenar": QPixmap("icons/entrenar.png").scaled(16, 16),
            "gestos": QPixmap("icons/gestos.png").scaled(16, 16),
            "cambiar_cuentas": QPixmap("icons/cuentas.png").scaled(16, 16),
            "crear_cuenta": QPixmap("icons/cuentas.png").scaled(16, 16),
            None: QPixmap()
        }

        # Paleta de color por acción (para dots)
        self.color_accion = {
            "entrenar": "#4caf50",
            "gestos": "#ff9800",
            "cambiar_cuentas": "#2196f3",
            "crear_cuenta": "#8b5cf6",
            None: "#606060"
        }

        # ====== Layout raíz ======
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        # ====== Toolbar en DOS FILAS ======
        toolbar = QFrame()
        toolbar.setObjectName("Toolbar")
        tbv = QVBoxLayout(toolbar)
        tbv.setContentsMargins(10, 10, 10, 10)
        tbv.setSpacing(8)

        row1 = QHBoxLayout(); row1.setSpacing(8)
        row2 = QHBoxLayout(); row2.setSpacing(8)

        # --- Botones ---
        btn_init = QPushButton("📱 Inicializar SCRCPY"); btn_init.setObjectName("warn")
        btn_init.clicked.connect(lambda: abrir_scrcpy(self.seriales))

        btn_close = QPushButton("❌ Cerrar SCRCPY"); btn_close.setObjectName("danger")
        btn_close.clicked.connect(cerrar_scrcpy)

        btn_gestos_video = QPushButton("🎬 Detectar cuentas → Seleccionar → Cambiar"); btn_gestos_video.setObjectName("accent")
        btn_gestos_video.clicked.connect(self.flujo_cuentas)

        btn_cambiar_cuentas = QPushButton("🔄 Cambiar cuentas (directo)"); btn_cambiar_cuentas.setObjectName("accent")
        btn_cambiar_cuentas.clicked.connect(
            lambda: self.ejecutar_seleccionados("cambiar_cuentas", cambiar_todas_las_cuentas)
        )

        # Fila 2
        btn_entrenar_sel = QPushButton("▶ Entrenar (seleccionados)"); btn_entrenar_sel.setObjectName("ok")
        btn_entrenar_sel.clicked.connect(lambda: self.ejecutar_seleccionados("entrenar", entrenar))

        btn_gestos_videos = QPushButton("🌀 Gestos Videos (seleccionados)"); btn_gestos_videos.setObjectName("accent")
        btn_gestos_videos.clicked.connect(lambda: self.ejecutar_seleccionados("gestos", Gestos_VIDEOS))

        btn_crear_cuentas = QPushButton("➕ Crear cuenta (seleccionados)"); btn_crear_cuentas.setObjectName("create")
        btn_crear_cuentas.clicked.connect(lambda: self.ejecutar_seleccionados("crear_cuenta", crear_cuenta_para_serial))

        btn_detener_sel = QPushButton("⏹ Detener (seleccionados)"); btn_detener_sel.setObjectName("danger")
        btn_detener_sel.clicked.connect(self.detener_seleccionados)

        btn_silenciar_sel = QPushButton("🔇 Silenciar (seleccionados)")
        btn_silenciar_sel.clicked.connect(lambda: self.ejecutar_seleccionados(None, silenciar_dispositivo))

        btn_clear = QPushButton("🧹 Limpiar selección")
        btn_clear.clicked.connect(self.limpiar_checkboxes)

        # tamaños
        for b in [btn_init, btn_close, btn_gestos_video, btn_cambiar_cuentas,
                  btn_entrenar_sel, btn_gestos_videos, btn_crear_cuentas,
                  btn_detener_sel, btn_silenciar_sel, btn_clear]:
            b.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            b.setMinimumHeight(34)

        # Distribución filas
        for b in [btn_init, btn_close, btn_gestos_video, btn_cambiar_cuentas]:
            row1.addWidget(b)
        row1.addStretch(1)

        for b in [btn_entrenar_sel, btn_gestos_videos, btn_crear_cuentas, btn_detener_sel, btn_silenciar_sel, btn_clear]:
            row2.addWidget(b)
        row2.addStretch(1)

        tbv.addLayout(row1)
        tbv.addLayout(row2)
        root.addWidget(toolbar)

        # ====== Checkbox "Marcar todos" ======
        marcar_todos_layout = QHBoxLayout()
        self.chk_marcar_todos = QCheckBox("✅ Marcar todos")
        self.chk_marcar_todos.stateChanged.connect(self.toggle_marcar_todos)
        marcar_todos_layout.addWidget(self.chk_marcar_todos)
        marcar_todos_layout.addStretch(1)
        root.addLayout(marcar_todos_layout)

        # ====== Lista de dispositivos ======
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        grid = QGridLayout(container)
        grid.setContentsMargins(10, 10, 10, 10)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(8)

        for idx, serial in enumerate(self.seriales):
            cel_layout = QHBoxLayout()
            cel_layout.setContentsMargins(0, 0, 0, 0)
            cel_layout.setSpacing(8)

            # Dot circular
            dot_size = 14
            dot = QFrame()
            dot.setFixedSize(dot_size, dot_size)
            r = dot_size // 2
            dot.setStyleSheet(f"""
                QFrame {{
                    background-color: #606060;
                    border: none;
                    border-radius: {r}px;
                    margin-right: 6px;
                }}
            """)
            self.status_buttons[serial] = dot

            # Nombre del dispositivo (serial)
            chk = QCheckBox(f"{serial}")
            self.checkboxes[serial] = chk

            # Icono opcional
            lbl_icono = QLabel()
            lbl_icono.setPixmap(self.iconos[None])
            self.iconos_dispositivos[serial] = lbl_icono

            cel_layout.addWidget(dot)
            cel_layout.addWidget(chk)
            cel_layout.addWidget(lbl_icono)

            cel_widget = QFrame()
            cel_widget.setLayout(cel_layout)
            cel_widget.setStyleSheet("QFrame { background: #0f1115; }")

            # Botones por dispositivo (acciones rápidas)
            btn_entrenar = QPushButton("▶ Entrenar")
            btn_entrenar.setObjectName("ok")
            btn_entrenar.clicked.connect(lambda _, s=serial: self._start_generic_worker(s, "entrenar", entrenar))

            btn_detener = QPushButton("⏹ Detener")
            btn_detener.setObjectName("danger")
            btn_detener.clicked.connect(lambda _, s=serial: self.detener_con_icono(s))

            btn_silenciar = QPushButton("🔇 Silenciar")
            btn_silenciar.clicked.connect(lambda _, s=serial: self._start_generic_worker(s, None, silenciar_dispositivo))

            grid.addWidget(cel_widget, idx, 0)
            grid.addWidget(btn_entrenar, idx, 1)
            grid.addWidget(btn_detener, idx, 2)
            grid.addWidget(btn_silenciar, idx, 3)

            self._set_estado_visual(serial, None)

        scroll.setWidget(container)
        root.addWidget(scroll, 1)

    # ====== Flujo Detectar → Dialogo → Cambiar (sin bloquear UI) ======
    def flujo_cuentas(self):
        seleccionados = [s for s in self.seriales if self.is_selected(s)]
        if not seleccionados:
            print("⚠ No hay dispositivos seleccionados para escanear.")
            return

        print("🔍 Escaneando cuentas TikTok...")
        # Marcar estado visual
        for s in seleccionados:
            self.estado_dispositivos[s] = "gestos"
            self._set_estado_visual(s, "gestos")
            hilos_activos[s] = True

        self._last_scanned = set(seleccionados)
        self._pending_scans = set(seleccionados)

        for serial in seleccionados:
            th = QThread(self)
            worker = ScanWorker(serial)
            worker.moveToThread(th)

            th.started.connect(worker.run)
            worker.finished.connect(self._on_scan_finished)
            worker.failed.connect(self._on_scan_failed)

            # Limpieza y mantener refs
            worker.finished.connect(th.quit)
            worker.failed.connect(th.quit)
            th.finished.connect(th.deleteLater)

            self._scan_threads[serial] = th
            self._scan_workers[serial] = worker

            th.start()

    def _on_scan_finished(self, serial):
        print(f"✅ Escaneo terminado en {serial}")
        self._pending_scans.discard(serial)
        self._scan_workers.pop(serial, None)
        self._scan_threads.pop(serial, None)

        if not self._pending_scans:
            print("✅ Escaneo completo. Mostrando diálogo...")
            dlg = SeleccionCuentasDialog(self)
            if dlg.exec_():
                print("✅ Selección guardada. Cambiando cuentas...")
                self._iniciar_cambio_seleccionados()
            else:
                print("↩️ Selección cancelada. Reseteando indicadores.")
                for s in list(self.status_buttons.keys()):
                    self.estado_dispositivos[s] = None
                    self._set_estado_visual(s, None)

    def _on_scan_failed(self, serial, err):
        print(f"💥 Error escaneando {serial}: {err}")
        self.estado_dispositivos[serial] = None
        self._set_estado_visual(serial, None)
        self._pending_scans.discard(serial)
        self._scan_workers.pop(serial, None)
        self._scan_threads.pop(serial, None)

        if not self._pending_scans:
            print("⚠ Escaneo finalizado con errores.")

    def _iniciar_cambio_seleccionados(self):
        # Cambiar SOLO los que se escanearon, o los que sigan seleccionados si no hay set previo
        seleccionados = list(self._last_scanned) if self._last_scanned else [
            s for s in self.seriales if self.is_selected(s)
        ]
        if not seleccionados:
            print("⚠ No hay dispositivos para cambiar cuentas.")
            return

        for s in seleccionados:
            self.estado_dispositivos[s] = "cambiar_cuentas"
            self._set_estado_visual(s, "cambiar_cuentas")
            hilos_activos[s] = True

        self._pending_changes = set(seleccionados)

        for serial in seleccionados:
            th = QThread(self)
            worker = ChangeWorker(serial)
            worker.moveToThread(th)

            th.started.connect(worker.run)
            worker.finished.connect(self._on_change_finished)
            worker.failed.connect(self._on_change_failed)

            worker.finished.connect(th.quit)
            worker.failed.connect(th.quit)
            th.finished.connect(th.deleteLater)

            self._change_threads[serial] = th
            self._change_workers[serial] = worker

            th.start()

    def _on_change_finished(self, serial):
        print(f"✅ Cambio de cuentas terminado en {serial}")
        self.estado_dispositivos[serial] = None
        self._set_estado_visual(serial, None)
        self._pending_changes.discard(serial)
        self._change_workers.pop(serial, None)
        self._change_threads.pop(serial, None)

        if not self._pending_changes:
            print("✅ Proceso completado en todos los dispositivos.")

    def _on_change_failed(self, serial, err):
        print(f"💥 Error cambiando cuentas en {serial}: {err}")
        self.estado_dispositivos[serial] = None
        self._set_estado_visual(serial, None)
        self._pending_changes.discard(serial)
        self._change_workers.pop(serial, None)
        self._change_threads.pop(serial, None)

        if not self._pending_changes:
            print("⚠ Cambio finalizado con errores en algunos dispositivos.")

    # ====== Generic workers (para botones) ======
    def _start_generic_worker(self, serial, accion, func):
        """Lanza func(serial) en QThread con dot/anim."""
        if not self.is_selected(serial):
            print(f"⚠ {serial} no está seleccionado.")
            return
        self.estado_dispositivos[serial] = accion
        self._set_estado_visual(serial, accion)

        th = QThread(self)
        worker = GenericWorker(serial, func)
        worker.moveToThread(th)

        th.started.connect(worker.run)
        worker.finished.connect(lambda s=serial: self._on_generic_finished(s))
        worker.failed.connect(lambda s=serial, err="": self._on_generic_failed(s, err))

        worker.finished.connect(th.quit)
        worker.failed.connect(th.quit)
        th.finished.connect(th.deleteLater)

        self._generic_threads[serial] = th
        self._generic_workers[serial] = worker
        th.start()

        self.checkboxes[serial].setChecked(False)

    def _on_generic_finished(self, serial):
        print(f"✅ Acción genérica terminada en {serial}")
        self.estado_dispositivos[serial] = None
        self._set_estado_visual(serial, None)
        self._generic_workers.pop(serial, None)
        self._generic_threads.pop(serial, None)

    def _on_generic_failed(self, serial, err):
        print(f"💥 Error en acción genérica {serial}: {err}")
        self.estado_dispositivos[serial] = None
        self._set_estado_visual(serial, None)
        self._generic_workers.pop(serial, None)
        self._generic_threads.pop(serial, None)

    # ====== Indicadores (dot) ======
    def _set_estado_visual(self, serial, accion):
        color = self.color_accion.get(accion, "#606060")
        dot = self.status_buttons[serial]
        r = max(1, dot.width() // 2)
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
        if serial in self._animations:
            effect, anim = self._animations[serial]
            if anim.state() == QPropertyAnimation.Running:
                return
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
            try:
                effect.setOpacity(1.0)
                self.status_buttons[serial].setGraphicsEffect(None)
            except Exception:
                pass
            self._animations.pop(serial, None)

    # ====== Lógica de selección ======
    def toggle_marcar_todos(self, state):
        marcar = state == Qt.Checked
        for chk in self.checkboxes.values():
            chk.setChecked(marcar)

    def is_selected(self, serial):
        return self.checkboxes.get(serial) and self.checkboxes[serial].isChecked()

    # ====== Acciones por lote usando GenericWorker ======
    def ejecutar_seleccionados(self, accion, func):
        alguno = False
        for serial in self.seriales:
            if self.is_selected(serial):
                alguno = True
                self._start_generic_worker(serial, accion, func)
        if not alguno:
            print("⚠ No hay dispositivos seleccionados.")
        self.limpiar_checkboxes_checkbox_global()

    def detener_con_icono(self, serial):
        detener_funcion(serial)  # pone hilos_activos[serial] = False
        self.estado_dispositivos[serial] = None
        self._set_estado_visual(serial, None)
        self.checkboxes[serial].setChecked(False)

    def detener_seleccionados(self):
        alguno = False
        for serial in self.seriales:
            if self.is_selected(serial):
                alguno = True
                self.detener_con_icono(serial)
        if not alguno:
            print("⚠ No hay dispositivos seleccionados.")
        self.limpiar_checkboxes_checkbox_global()

    def limpiar_checkboxes_checkbox_global(self):
        for chk in self.checkboxes.values():
            chk.setChecked(False)
        self.chk_marcar_todos.setChecked(False)

    def limpiar_checkboxes(self):
        for chk in self.checkboxes.values():
            chk.setChecked(False)
        self.chk_marcar_todos.setChecked(False)


# ====== Ejecución directa ======
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
