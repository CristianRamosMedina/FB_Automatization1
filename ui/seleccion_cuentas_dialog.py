# ui/seleccion_cuentas_dialog.py
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget, QWidget,
    QScrollArea, QCheckBox, QFormLayout, QMessageBox, QLabel, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from core.tiktok_funcs.utils import cargar_dispositivos
from core.adb_utils import guardar_dispositivos
import json, os

DISPOSITIVOS_FILE = "data/videos.json"


class SeleccionCuentasDialog(QDialog):
    """
    Diálogo oscuro con pestañas por serial y listas de cuentas.
    Incluye botones para seleccionar/deseleccionar masivamente.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Seleccionar cuentas por subir")
        self.resize(680, 600)

        # -------- Tema oscuro y estilos mejorados --------
        self.setStyleSheet("""
            QDialog, QWidget {
                background-color: #0f1216;
                color: #E8EAED;
                font-size: 14px;
            }

            /* Contenedor de todo */
            .Card {
                background: #12161B;
                border: 1px solid #1E242B;
                border-radius: 12px;
            }

            /* Título y contador */
            QLabel#title {
                font-size: 18px;
                font-weight: 700;
                color: #FFFFFF;
            }
            QLabel#counter {
                font-size: 12px;
                color: #9AA0A6;
                padding-left: 8px;
            }

            /* QTabWidget */
            QTabWidget::pane {
                border: 1px solid #1E242B;
                border-radius: 10px;
                padding: 6px;
                margin-top: 8px;
                background: #0f1216;
            }
            QTabBar::tab {
                background: #12161B;
                color: #DADCE0;
                padding: 8px 14px;
                margin: 2px 2px 0 0;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border: 1px solid #1E242B;
            }
            QTabBar::tab:hover {
                background: #171C22;
            }
            QTabBar::tab:selected {
                background: #20262E;
                color: #FFFFFF;
            }

            /* Scroll / lista */
            QScrollArea {
                border: none;
                background: transparent;
            }
            QFormLayout, QFrame.ListCard {
                background: #12161B;
                border: 1px solid #1E242B;
                border-radius: 10px;
            }

            /* Checkboxes */
            QCheckBox {
                spacing: 8px;
                padding: 6px 8px;
                border-radius: 6px;
            }
            QCheckBox:hover {
                background: #171C22;
            }
            QCheckBox::indicator {
                width: 18px; height: 18px;
            }
            QCheckBox::indicator:unchecked {
                border: 1px solid #3A3F45;
                background: #141A20;
            }
            QCheckBox::indicator:checked {
                border: 1px solid #4CAF50;
                background: #24402A;
            }

            /* Botonera */
            QPushButton {
                background: #1A2129;
                color: #FFFFFF;
                border: 1px solid #29323B;
                padding: 8px 14px;
                border-radius: 10px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #202832;
            }
            QPushButton:pressed {
                background: #26303B;
            }
            QPushButton#accent {
                background: #2563EB;
                border-color: #2563EB;
            }
            QPushButton#accent:hover {
                background: #2B6EF3;
                border-color: #2B6EF3;
            }
            QPushButton#danger {
                background: #B91C1C;
                border-color: #B91C1C;
            }
            QPushButton#danger:hover {
                background: #D01F1F;
                border-color: #D01F1F;
            }

            /* Barra de herramientas superior */
            QFrame.Toolbar {
                background: #12161B;
                border: 1px solid #1E242B;
                border-radius: 10px;
            }
        """)

        self._data = cargar_dispositivos()
        self._checks_por_serial = {}  # serial -> [(cuenta, QCheckBox), ...]
        self._counters = {}           # serial -> QLabel contador

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        # -------- Header --------
        header = QHBoxLayout()
        title = QLabel("Seleccionar cuentas por subir")
        title.setObjectName("title")
        counter = QLabel("")  # vacío global (opcional)
        counter.setObjectName("counter")
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(counter)
        root.addLayout(header)

        # -------- Toolbar (selección masiva) --------
        toolbar_frame = QFrame()
        toolbar_frame.setObjectName("Toolbar")
        toolbar_layout = QHBoxLayout(toolbar_frame)
        toolbar_layout.setContentsMargins(10, 10, 10, 10)
        toolbar_layout.setSpacing(8)

        btn_sel_tab = QPushButton("✔ Seleccionar todas (tab)")
        btn_unsel_tab = QPushButton("✖ Deseleccionar (tab)")
        btn_sel_all = QPushButton("✔ Seleccionar todas (todos)")
        btn_unsel_all = QPushButton("✖ Deseleccionar (todos)")

        toolbar_layout.addWidget(btn_sel_tab)
        toolbar_layout.addWidget(btn_unsel_tab)
        toolbar_layout.addStretch(1)
        toolbar_layout.addWidget(btn_sel_all)
        toolbar_layout.addWidget(btn_unsel_all)

        root.addWidget(toolbar_frame)

        # -------- Tabs --------
        self.tabs = QTabWidget(self)
        root.addWidget(self.tabs, 1)

        # Construye tabs
        for serial, info in self._data.items():
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            tab_layout.setContentsMargins(6, 6, 6, 6)
            tab_layout.setSpacing(8)

            # Contador por serial
            lbl_count = QLabel("")
            lbl_count.setObjectName("counter")
            self._counters[serial] = lbl_count

            # Caja de lista (card)
            list_card = QFrame()
            list_card.setObjectName("ListCard")
            list_layout = QVBoxLayout(list_card)
            list_layout.setContentsMargins(8, 8, 8, 8)
            list_layout.setSpacing(8)

            # Scroll área para muchas cuentas
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            inner = QWidget()
            form = QFormLayout(inner)
            form.setContentsMargins(8, 8, 8, 8)
            form.setSpacing(6)

            checks = []
            for cuenta_obj in info.get("cuentas", []):
                cuenta = cuenta_obj.get("cuenta", "")
                carpeta_nombre = cuenta_obj.get("carpeta_nombre", "")
                texto = f"{cuenta}   📂 {carpeta_nombre}"

                chk = QCheckBox(texto)
                pre = cuenta in info.get("cuentasPorSubir", [])
                chk.setChecked(pre)
                # cada cambio de estado actualiza el contador
                chk.stateChanged.connect(lambda _, s=serial: self._update_counter_for(s))
                form.addRow(chk)
                checks.append((cuenta, chk))

            inner.setLayout(form)
            scroll.setWidget(inner)
            list_layout.addWidget(scroll)

            # Pie de cada tab con contador
            footer = QHBoxLayout()
            footer.addWidget(lbl_count)
            footer.addStretch(1)
            tab_layout.addWidget(list_card)
            tab_layout.addLayout(footer)

            self.tabs.addTab(tab, serial)
            self._checks_por_serial[serial] = checks

            # Inicializa contador de la tab
            self._update_counter_for(serial)

        # -------- Botonera inferior --------
        btns = QHBoxLayout()
        btn_guardar = QPushButton("Guardar y continuar ✅")
        btn_guardar.setObjectName("accent")
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("danger")

        btn_guardar.clicked.connect(self._guardar)
        btn_cancelar.clicked.connect(self.reject)

        btns.addStretch(1)
        btns.addWidget(btn_cancelar)
        btns.addWidget(btn_guardar)
        root.addLayout(btns)

        # Conexiones toolbar
        btn_sel_tab.clicked.connect(self._select_all_current_tab)
        btn_unsel_tab.clicked.connect(self._clear_all_current_tab)
        btn_sel_all.clicked.connect(self._select_all_global)
        btn_unsel_all.clicked.connect(self._clear_all_global)

        # Actualiza contador cuando cambie de pestaña
        self.tabs.currentChanged.connect(self._on_tab_changed)

    # ------------- Utilidades de selección -------------
    def _current_serial(self):
        idx = self.tabs.currentIndex()
        if idx < 0:
            return None
        return self.tabs.tabText(idx)

    def _select_checks(self, checks, value: bool, serial_for_counter=None):
        for _, chk in checks:
            chk.blockSignals(True)
            chk.setChecked(value)
            chk.blockSignals(False)
        # Actualiza contador (si se especifica serial; si no, intenta por cada grupo)
        if serial_for_counter:
            self._update_counter_for(serial_for_counter)
        else:
            for serial in self._checks_por_serial.keys():
                self._update_counter_for(serial)

    def _select_all_current_tab(self):
        serial = self._current_serial()
        if not serial: return
        checks = self._checks_por_serial.get(serial, [])
        self._select_checks(checks, True, serial_for_counter=serial)

    def _clear_all_current_tab(self):
        serial = self._current_serial()
        if not serial: return
        checks = self._checks_por_serial.get(serial, [])
        self._select_checks(checks, False, serial_for_counter=serial)

    def _select_all_global(self):
        for serial, checks in self._checks_por_serial.items():
            self._select_checks(checks, True, serial_for_counter=serial)

    def _clear_all_global(self):
        for serial, checks in self._checks_por_serial.items():
            self._select_checks(checks, False, serial_for_counter=serial)

    # ------------- Contadores -------------
    def _update_counter_for(self, serial):
        checks = self._checks_por_serial.get(serial, [])
        total = len(checks)
        selected = sum(1 for _, chk in checks if chk.isChecked())
        lbl = self._counters.get(serial)
        if lbl:
            lbl.setText(f"{selected}/{total} seleccionadas")

    def _on_tab_changed(self, _idx):
        serial = self._current_serial()
        if serial:
            self._update_counter_for(serial)

    # ------------- Guardado -------------
    def _guardar(self):
        # actualiza cuentasPorSubir en el dict y persiste
        for serial, checks in self._checks_por_serial.items():
            seleccionadas = [cuenta for cuenta, chk in checks if chk.isChecked()]
            if serial not in self._data:
                self._data[serial] = {}
            self._data[serial]["cuentasPorSubir"] = seleccionadas

        try:
            guardar_dispositivos(self._data)
        except Exception:
            with open(DISPOSITIVOS_FILE, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)

        QMessageBox.information(self, "OK", "Selección guardada.")
        self.accept()
