# ui/seleccion_fecha_dialog.py
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QSpinBox, QPushButton
)

class SeleccionFechaDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Seleccionar rango de fechas")

        layout = QVBoxLayout()

        # Mes
        meses = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        self.combo_mes = QComboBox()
        self.combo_mes.addItems(meses)

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
        self.spin_fin.setValue(30)
        layout.addWidget(QLabel("Día fin:"))
        layout.addWidget(self.spin_fin)

        # Botones
        btns = QHBoxLayout()
        btn_ok = QPushButton("Aceptar")
        btn_cancel = QPushButton("Cancelar")

        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

        btns.addWidget(btn_ok)
        btns.addWidget(btn_cancel)
        layout.addLayout(btns)

        self.setLayout(layout)

    def get_datos(self):
        return {
            "mes": self.combo_mes.currentText(),
            "dia_inicio": self.spin_inicio.value(),
            "dia_fin": self.spin_fin.value()
        }
