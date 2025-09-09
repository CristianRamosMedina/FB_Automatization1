# ui/seleccion_fecha_dialog.py
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QSpinBox, QPushButton, QMessageBox
)
from datetime import datetime
import calendar

class SeleccionFechaDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Seleccionar rango de fechas")

        layout = QVBoxLayout()

        # Mes actual y día de hoy
        self.hoy = datetime.today()
        self.mes_actual_index = self.hoy.month - 1
        self.mes_actual = self.hoy.strftime("%B")
        self.dia_actual = self.hoy.day

        # Lista de meses hasta el actual
        todos_meses = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        meses_validos = todos_meses[:self.mes_actual_index + 1]

        self.combo_mes = QComboBox()
        self.combo_mes.addItems(meses_validos)
        self.combo_mes.setCurrentIndex(len(meses_validos) - 1)  # seleccionar mes actual
        layout.addWidget(QLabel("Mes:"))
        layout.addWidget(self.combo_mes)

        # Día inicio
        self.spin_inicio = QSpinBox()
        self.spin_inicio.setRange(1, 31)
        self.spin_inicio.setValue(1)
        layout.addWidget(QLabel("Día inicio:"))
        layout.addWidget(self.spin_inicio)

        # Día fin
        self.spin_fin = QSpinBox()
        self.spin_fin.setRange(1, 31)
        self.spin_fin.setValue(self.dia_actual)
        layout.addWidget(QLabel("Día fin:"))
        layout.addWidget(self.spin_fin)

        # Botones
        btns = QHBoxLayout()
        btn_ok = QPushButton("Aceptar")
        btn_cancel = QPushButton("Cancelar")

        btn_ok.clicked.connect(self.validar_fecha)
        btn_cancel.clicked.connect(self.reject)

        btns.addWidget(btn_ok)
        btns.addWidget(btn_cancel)
        layout.addLayout(btns)

        self.setLayout(layout)

        # Ajustar límites iniciales
        self.combo_mes.currentIndexChanged.connect(self._ajustar_dias)
        self._ajustar_dias()

    def _ajustar_dias(self):
        """Ajusta el máximo de días según el mes y el año actual."""
        mes_sel = self.combo_mes.currentText()
        mes_index = self.combo_mes.currentIndex() + 1  # 1-based
        year = self.hoy.year

        # Último día del mes seleccionado
        _, ultimo_dia_mes = calendar.monthrange(year, mes_index)

        if mes_sel == self.mes_actual:
            max_dia = min(self.dia_actual, ultimo_dia_mes)  # hasta hoy
        else:
            max_dia = ultimo_dia_mes

        self.spin_inicio.setMaximum(max_dia)
        self.spin_fin.setMaximum(max_dia)

        # Ajustar valores si estaban fuera de rango
        if self.spin_inicio.value() > max_dia:
            self.spin_inicio.setValue(max_dia)
        if self.spin_fin.value() > max_dia:
            self.spin_fin.setValue(max_dia)

    def validar_fecha(self):
        """Evita seleccionar días fuera de rango."""
        dia_inicio = self.spin_inicio.value()
        dia_fin = self.spin_fin.value()

        if dia_inicio > dia_fin:
            QMessageBox.warning(self, "Fecha inválida",
                                "El día de inicio no puede ser mayor que el día fin.")
            return

        self.accept()

    def get_datos(self):
        return {
            "mes": self.combo_mes.currentText(),
            "dia_inicio": self.spin_inicio.value(),
            "dia_fin": self.spin_fin.value()
        }
