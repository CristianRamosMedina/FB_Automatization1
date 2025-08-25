# ui/main_window.py
import sys
import threading
import os
import subprocess
from pathlib import Path

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea,
    QGridLayout, QCheckBox, QApplication, QLabel, QGraphicsOpacityEffect,
    QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QObject, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap

# ✅ Importaciones locales
from ui.seleccion_cuentas_dialog import SeleccionCuentasDialog
from core.scrcpy_manager import obtener_seriales, abrir_scrcpy, cerrar_scrcpy
from core.tiktok_funcs import entrenar, detener_funcion, silenciar_dispositivo
from core.tiktok_funcs.cambiarCuentas import cambiar_todas_las_cuentas
from core.tiktok_funcs.TiktokCuentaScan import TitkokCuentas
from core.tiktok_funcs.VideosMujeres.TiktokVideoScan import TitkokCuentasVideos
from core.tiktok_funcs.VideosMujeres.cambiarcuentasVideo import cambiar_todas_las_cuentas_videos
from ui.seleecion_cuentas_videos_dialog import  SeleccionCuentasDialogVideo
from core.tiktok_funcs.VideosMujeres.pipeline import ejecutar_pipeline

from core.config import hilos_activos
# en ui/main_window.py (importa arriba)
from core.tiktok_funcs.CrearCuentasTiktok.CrearCuentasTitktok import (
    preasignar_para_seriales,
    crear_cuenta_para_serial,
)

# 🚀 Módulos de carruseles/unpack (se intentará usar .main() si existe)
from core.tiktok_funcs.CarruselesCrearImagenes import carruseles, unpack

from core.tiktok_funcs.verificacion.carruseles_pendientes import chequear_carruseles_pendientes
from core.tiktok_funcs.verificacion.videos_pendites import contar_videos_pendientes


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


# ====== Workers VIDEO ======
class ScanWorkerVideo(QObject):
    finished = pyqtSignal(str)           # serial
    failed  = pyqtSignal(str, str)       # serial, error

    def __init__(self, serial):
        super().__init__()
        self.serial = serial

    def run(self):
        try:
            print(f"[ScanWorkerVideo] ▶ Iniciando escaneo VIDEO en {self.serial}")
            hilos_activos[self.serial] = True
            TitkokCuentasVideos(self.serial)
            print(f"[ScanWorkerVideo] ✅ Escaneo VIDEO finalizado en {self.serial}")
            self.finished.emit(self.serial)
        except Exception as e:
            self.failed.emit(self.serial, str(e))
        finally:
            pass


class ChangeWorkerVideo(QObject):
    finished = pyqtSignal(str)
    failed  = pyqtSignal(str, str)

    def __init__(self, serial):
        super().__init__()
        self.serial = serial

    def run(self):
        try:
            print(f"[ChangeWorkerVideo] ▶ Iniciando cambio VIDEO en {self.serial}")
            hilos_activos[self.serial] = True
            cambiar_todas_las_cuentas_videos(self.serial)
            print(f"[ChangeWorkerVideo] ✅ Cambio VIDEO finalizado en {self.serial}")
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


# =================== Worker sin argumentos/serial ===================
class NoArgWorker(QObject):
    finished = pyqtSignal()
    failed   = pyqtSignal(str)

    def __init__(self, func):
        super().__init__()
        self.func = func  # callable sin args

    def run(self):
        try:
            print(f"[NoArgWorker] ▶ Ejecutando {getattr(self.func, '__name__', str(self.func))}()")
            self.func()
            print(f"[NoArgWorker] ✅ Finalizado")
            self.finished.emit()
        except Exception as e:
            self.failed.emit(str(e))


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

        # VIDEO refs
        self._scan_threads_v   = {}
        self._scan_workers_v   = {}
        self._change_threads_v = {}
        self._change_workers_v = {}
        self._pending_scans_v  = set()
        self._pending_changes_v= set()
        self._last_scanned_v   = set()

        # Iconos opcionales
        self.iconos = {
            "entrenar": QPixmap("icons/entrenar.png").scaled(16, 16),
            "gestos": QPixmap("icons/gestos.png").scaled(16, 16),
            "cambiar_cuentas": QPixmap("icons/cuentas.png").scaled(16, 16),
            "crear_cuenta": QPixmap("icons/cuentas.png").scaled(16, 16),
            "gestos_video": QPixmap("icons/gestos.png").scaled(16, 16),
            "cambiar_cuentas_video": QPixmap("icons/cuentas.png").scaled(16, 16),
            None: QPixmap()
        }

        # Paleta de color por acción (para dots)
        self.color_accion = {
            "entrenar": "#4caf50",
            "gestos": "#ff9800",
            "cambiar_cuentas": "#2196f3",
            "crear_cuenta": "#8b5cf6",
            "gestos_video": "#ffb74d",
            "cambiar_cuentas_video": "#42a5f5",
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

        btn_gestos_video = QPushButton("🔎 Subir Carruseles"); btn_gestos_video.setObjectName("accent")
        btn_gestos_video.clicked.connect(self.flujo_cuentas)

        btn_cambiar_cuentas = QPushButton("🔄 Cambiar cuentas"); btn_cambiar_cuentas.setObjectName("accent")
        btn_cambiar_cuentas.clicked.connect(
            lambda: self.ejecutar_seleccionados("cambiar_cuentas", cambiar_todas_las_cuentas)
        )

        # 👉 Nuevo botón para el flujo basado en SeleccionCuentasDialogVideo
        btn_gestos_video2 = QPushButton("🎬 Subir Videos de Mujeres")
        btn_gestos_video2.setObjectName("accent")
        btn_gestos_video2.clicked.connect(self.flujo_cuentas_video)

        # Fila 2
        btn_entrenar_sel = QPushButton("▶ Entrenar"); btn_entrenar_sel.setObjectName("ok")
        btn_entrenar_sel.clicked.connect(lambda: self.ejecutar_seleccionados("entrenar", entrenar))

        btn_gestos_videos = QPushButton("🌀 Gestos Videos (seleccionados)"); btn_gestos_videos.setObjectName("accent")
        btn_gestos_videos.clicked.connect(lambda: self.ejecutar_seleccionados("gestos", ejecutar_pipeline))

        btn_crear_cuentas = QPushButton("➕ Crear cuentas")
        btn_crear_cuentas.setObjectName("create")
        btn_crear_cuentas.clicked.connect(self.crear_cuentas_seleccionados)

        btn_detener_sel = QPushButton("⏹ Detener "); btn_detener_sel.setObjectName("danger")
        btn_detener_sel.clicked.connect(self.detener_seleccionados)

        btn_silenciar_sel = QPushButton("🔇 Silenciar")
        btn_silenciar_sel.clicked.connect(lambda: self.ejecutar_seleccionados(None, silenciar_dispositivo))

        btn_clear = QPushButton("🧹 Limpiar selección")
        btn_clear.clicked.connect(self.limpiar_checkboxes)

        # tamaños
        for b in [btn_init, btn_close, btn_gestos_video, btn_cambiar_cuentas, btn_gestos_video2,
                  btn_entrenar_sel, btn_gestos_videos, btn_crear_cuentas,
                  btn_detener_sel, btn_silenciar_sel, btn_clear]:
            b.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            b.setMinimumHeight(34)

        # Distribución filas
        for b in [btn_init, btn_close, btn_gestos_video, btn_cambiar_cuentas, btn_gestos_video2]:
            row1.addWidget(b)
        row1.addStretch(1)

        for b in [btn_entrenar_sel, btn_gestos_videos, btn_crear_cuentas, btn_detener_sel, btn_silenciar_sel, btn_clear]:
            row2.addWidget(b)
        row2.addStretch(1)

        tbv.addLayout(row1)
        tbv.addLayout(row2)
        root.addWidget(toolbar)

       
        
       # ====== Sección: Creación de carruseles ======
        carru_section = QFrame()
        carru_section.setObjectName("Toolbar")
        carru_layout = QVBoxLayout(carru_section)   # 👈 ahora vertical
        carru_layout.setContentsMargins(10, 10, 10, 10)
        carru_layout.setSpacing(8)

        # --- Fila 1: creación normal ---
        row1 = QHBoxLayout()
        lbl_carru = QLabel("🖼️  Creación de carruseles")
        lbl_carru.setStyleSheet("font-weight:600;")

        btn_crear_carruseles = QPushButton("🧩 Crear carruseles")
        btn_crear_carruseles.setObjectName("create")
        btn_crear_carruseles.clicked.connect(self._run_carruseles_async)

        btn_unpack = QPushButton("📦 Unpack")
        btn_unpack.setObjectName("create")
        btn_unpack.clicked.connect(self._run_unpack_async)

        lbl_carru_status = QLabel("—")
        lbl_carru_status.setStyleSheet("color:#a8b3cf;")
        self._lbl_carru_status = lbl_carru_status

        row1.addWidget(lbl_carru)
        row1.addStretch(1)
        row1.addWidget(btn_crear_carruseles)
        row1.addWidget(btn_unpack)
        row1.addWidget(lbl_carru_status)

        # --- Fila 2: pendientes dentro de la misma sección ---
        row2 = QHBoxLayout()
        lbl_pending = QLabel("📂 Carruseles pendientes:")
        lbl_pending.setStyleSheet("font-weight:600;")

        self._lbl_pending_carru = QLabel("—")
        self._lbl_pending_carru.setStyleSheet("color:#ffcc00;")  # amarillo inicial

        btn_check_pending = QPushButton("🔎 Verificar carruseles")
        btn_check_pending.setObjectName("warn")
        btn_check_pending.clicked.connect(self._update_carruseles_pendientes)

        row2.addWidget(lbl_pending)
        row2.addWidget(self._lbl_pending_carru)
        row2.addStretch(1)
        row2.addWidget(btn_check_pending)

        # Agregar ambas filas al layout vertical
        carru_layout.addLayout(row1)
        carru_layout.addLayout(row2)

        root.addWidget(carru_section)
        
        row_videos = QHBoxLayout()
        lbl_videos = QLabel("🎬 Carpeta de videos vacías:")
        lbl_videos.setStyleSheet("font-weight:600;")

        self._lbl_pending_videos = QLabel("—")
        self._lbl_pending_videos.setStyleSheet("color:#ffcc00;")

        btn_check_videos = QPushButton("🔎 Verificar videos")
        btn_check_videos.setObjectName("warn")
        btn_check_videos.clicked.connect(self._update_videos_pendientes)

        row_videos.addWidget(lbl_videos)
        row_videos.addWidget(self._lbl_pending_videos)
        row_videos.addStretch(1)
        row_videos.addWidget(btn_check_videos)

        carru_layout.addLayout(row_videos)


        
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

        # === Inicializa timer de animación de puntos (lazy)
        self._ell_timer = None
        self._ell_base_text = ""
        self._ell_count = 0

    # ====== Lanzadores backend (sin bloquear UI) ======
    def _call_carruseles(self):
        """Intenta carruseles.main(); si no existe, fallback a ejecutar el script."""
        if hasattr(carruseles, "main"):
            carruseles.main()
            return
        base = Path(__file__).resolve().parents[1]  # .../ControlDePantallas
        script = base / "core" / "tiktok_funcs" / "CarruselesCrearImagenes" / "carruseles.py"
        subprocess.run([sys.executable, str(script)], check=True)

    def _call_unpack(self):
        """Intenta unpack.main(); si no existe, fallback a ejecutar el script."""
        if hasattr(unpack, "main"):
            unpack.main()
            return
        base = Path(__file__).resolve().parents[1]
        script = base / "core" / "tiktok_funcs" / "CarruselesCrearImagenes" / "unpack.py"
        subprocess.run([sys.executable, str(script)], check=True)

    # ====== Animación "Realizando..." con puntos ======
    def _ensure_ell_timer(self):
        if self._ell_timer is not None:
            return
        self._ell_timer = QTimer(self)
        self._ell_timer.setInterval(400)  # velocidad de los puntos
        self._ell_timer.timeout.connect(self._on_ell_tick)

    def _on_ell_tick(self):
        self._ell_count = (self._ell_count + 1) % 4
        dots = "." * self._ell_count
        self._lbl_carru_status.setText(f"{self._ell_base_text}{dots}")

    def _start_busy(self, base_text: str):
        """Inicia animación 'Realizando…' y deshabilita botones."""
        self._ensure_ell_timer()
        self._ell_base_text = base_text
        self._ell_count = 0
        self._lbl_carru_status.setText(base_text)
        self._ell_timer.start()
        # deshabilitar botones mientras corre
        self._btn_crear_carruseles.setEnabled(False)
        self._btn_unpack.setEnabled(False)

    def _stop_busy(self, final_text: str, ok=True):
        """Detiene animación y muestra resultado."""
        self._ensure_ell_timer()
        self._ell_timer.stop()
        prefix = "✅ " if ok else "💥 "
        self._lbl_carru_status.setText(prefix + final_text)
        # re-habilitar
        self._btn_crear_carruseles.setEnabled(True)
        self._btn_unpack.setEnabled(True)

    # ====== Lanzadores async con animación ======
    def _run_carruseles_async(self):
        self._start_busy("Realizando carruseles")
        th = QThread(self)
        worker = NoArgWorker(self._call_carruseles)
        worker.moveToThread(th)

        th.started.connect(worker.run)
        worker.finished.connect(lambda: self._on_noarg_done("Carruseles"))
        worker.failed.connect(lambda err: self._on_noarg_fail("Carruseles", err))

        worker.finished.connect(th.quit)
        worker.failed.connect(th.quit)
        th.finished.connect(th.deleteLater)

        self._th_carru = th
        self._wk_carru = worker
        th.start()

    def _run_unpack_async(self):
        self._start_busy("Realizando unpack")
        th = QThread(self)
        worker = NoArgWorker(self._call_unpack)
        worker.moveToThread(th)

        th.started.connect(worker.run)
        worker.finished.connect(lambda: self._on_noarg_done("Unpack"))
        worker.failed.connect(lambda err: self._on_noarg_fail("Unpack", err))

        worker.finished.connect(th.quit)
        worker.failed.connect(th.quit)
        th.finished.connect(th.deleteLater)

        self._th_unpack = th
        self._wk_unpack = worker
        th.start()

    def _on_noarg_done(self, nombre):
        print(f"✅ {nombre} finalizado.")
        self._stop_busy(f"{nombre} listo", ok=True)

    def _on_noarg_fail(self, nombre, err):
        print(f"💥 Error en {nombre}: {err}")
        self._stop_busy(f"{nombre} con error", ok=False)
        
     # ====== Actualización de carruseles pendientes ======
    def _update_carruseles_pendientes(self):
        pendientes = chequear_carruseles_pendientes()
        if pendientes > 0:
          self._lbl_pending_carru.setText(f"⚠️{pendientes} Carruseles pendientes por subir")
          self._lbl_pending_carru.setStyleSheet("color:#ff4444; font-weight:600;")  # rojo alerta
        else:
          self._lbl_pending_carru.setText("✅ Ninguno carrusel por subir")
          self._lbl_pending_carru.setStyleSheet("color:#4caf50; font-weight:600;")  # verde OK
    
    def _update_videos_pendientes(self):
        vacias = contar_videos_pendientes()
        if vacias:
            resumen = ", ".join(vacias[:3])
            if len(vacias) > 3:
             resumen += " ..."
            self._lbl_pending_videos.setText(f"⚠️ {len(vacias)} carpetas vacías → {resumen}")
            self._lbl_pending_videos.setStyleSheet("color:#ff4444; font-weight:600;")
        else:
            self._lbl_pending_videos.setText("✅ Todas las carpetas tienen videos")
            self._lbl_pending_videos.setStyleSheet("color:#4caf50; font-weight:600;")

    # ====== Flujo Detectar → Dialogo → Cambiar (texto)
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

            # Limpieza y refs
            worker.finished.connect(th.quit)
            worker.failed.connect(th.quit)
            th.finished.connect(th.deleteLater)

            self._scan_threads[serial] = th
            self._scan_workers[serial] = worker

            th.start()

    # ====== Flujo Detectar → Dialogo → Cambiar (VIDEO)
    def flujo_cuentas_video(self):
        seleccionados = [s for s in self.seriales if self.is_selected(s)]
        if not seleccionados:
            print("⚠ No hay dispositivos seleccionados para escanear (VIDEO).")
            return

        print("🎬 Escaneando cuentas TikTok (VIDEO)...")
        for s in seleccionados:
            self.estado_dispositivos[s] = "gestos_video"
            self._set_estado_visual(s, "gestos_video")
            hilos_activos[s] = True

        self._last_scanned_v   = set(seleccionados)
        self._pending_scans_v  = set(seleccionados)

        for serial in seleccionados:
            th = QThread(self)
            worker = ScanWorkerVideo(serial)
            worker.moveToThread(th)

            th.started.connect(worker.run)
            worker.finished.connect(self._on_scan_finished_video)
            worker.failed.connect(self._on_scan_failed_video)

            worker.finished.connect(th.quit)
            worker.failed.connect(th.quit)
            th.finished.connect(th.deleteLater)

            self._scan_threads_v[serial] = th
            self._scan_workers_v[serial] = worker

            th.start()

    def crear_cuentas_seleccionados(self):
        seriales = [s for s in self.seriales if self.is_selected(s)]
        if not seriales:
            print("⚠ No hay dispositivos seleccionados.")
            return

        # 1) reservar pares únicos para TODOS los seleccionados
        preasignar_para_seriales(seriales)

        # 2) lanzar un worker por serial
        for s in seriales:
            self._start_generic_worker(s, "crear_cuenta", crear_cuenta_para_serial)

        self.limpiar_checkboxes_checkbox_global()

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

    # ====== Callbacks VIDEO ======
    def _on_scan_finished_video(self, serial):
        print(f"✅ Escaneo VIDEO terminado en {serial}")
        self._pending_scans_v.discard(serial)
        self._scan_workers_v.pop(serial, None)
        self._scan_threads_v.pop(serial, None)

        if not self._pending_scans_v:
            print("✅ Escaneo VIDEO completo. Mostrando diálogo (VIDEO)...")
            dlg = SeleccionCuentasDialogVideo(self)
            if dlg.exec_():
                print("✅ Selección VIDEO guardada. Cambiando cuentas (VIDEO)...")
                self._iniciar_cambio_seleccionados_video()
            else:
                print("↩️ Selección VIDEO cancelada. Reseteando indicadores.")
                for s in list(self.status_buttons.keys()):
                    self.estado_dispositivos[s] = None
                    self._set_estado_visual(s, None)

    def _on_scan_failed_video(self, serial, err):
        print(f"💥 Error escaneando VIDEO {serial}: {err}")
        self.estado_dispositivos[serial] = None
        self._set_estado_visual(serial, None)
        self._pending_scans_v.discard(serial)
        self._scan_workers_v.pop(serial, None)
        self._scan_threads_v.pop(serial, None)

        if not self._pending_scans_v:
            print("⚠ Escaneo VIDEO finalizado con errores.")

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

    # ====== Cambio VIDEO ======
    def _iniciar_cambio_seleccionados_video(self):
        seleccionados = list(self._last_scanned_v) if self._last_scanned_v else [
            s for s in self.seriales if self.is_selected(s)
        ]
        if not seleccionados:
            print("⚠ No hay dispositivos para cambiar cuentas (VIDEO).")
            return

        for s in seleccionados:
            self.estado_dispositivos[s] = "cambiar_cuentas_video"
            self._set_estado_visual(s, "cambiar_cuentas_video")
            hilos_activos[s] = True

        self._pending_changes_v = set(seleccionados)

        for serial in seleccionados:
            th = QThread(self)
            worker = ChangeWorkerVideo(serial)
            worker.moveToThread(th)

            th.started.connect(worker.run)
            worker.finished.connect(self._on_change_finished_video)
            worker.failed.connect(self._on_change_failed_video)

            worker.finished.connect(th.quit)
            worker.failed.connect(th.quit)
            th.finished.connect(th.deleteLater)

            self._change_threads_v[serial] = th
            self._change_workers_v[serial] = worker

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

    # ====== Callbacks fin de cambio VIDEO ======
    def _on_change_finished_video(self, serial):
        print(f"✅ Cambio de cuentas (VIDEO) terminado en {serial}")
        self.estado_dispositivos[serial] = None
        self._set_estado_visual(serial, None)
        self._pending_changes_v.discard(serial)
        self._change_workers_v.pop(serial, None)
        self._change_threads_v.pop(serial, None)

        if not self._pending_changes_v:
            print("✅ Proceso VIDEO completado en todos los dispositivos.")

    def _on_change_failed_video(self, serial, err):
        print(f"💥 Error cambiando cuentas (VIDEO) en {serial}: {err}")
        self.estado_dispositivos[serial] = None
        self._set_estado_visual(serial, None)
        self._pending_changes_v.discard(serial)
        self._change_workers_v.pop(serial, None)
        self._change_threads_v.pop(serial, None)

        if not self._pending_changes_v:
            print("⚠ Cambio VIDEO finalizado con errores en algunos dispositivos.")

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
