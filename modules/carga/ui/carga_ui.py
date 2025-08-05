from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from ..logic.carga import Carga

class CargaWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.carga = Carga()
        layout = QVBoxLayout()
        self.label = QLabel("Pantalla: Carga")
        self.btn = QPushButton("Cargar datos")
        self.btn.clicked.connect(self.cargar)
        layout.addWidget(self.label)
        layout.addWidget(self.btn)
        self.setLayout(layout)

    def cargar(self):
        resultado = self.carga.cargar_datos()
        self.label.setText(resultado)
