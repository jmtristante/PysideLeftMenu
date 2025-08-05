from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from ..logic.validar import Validar

class ValidarWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.validar = Validar()
        layout = QVBoxLayout()
        self.label = QLabel("Pantalla: Validar")
        self.btn = QPushButton("Ejecutar validación")
        self.btn.clicked.connect(self.ejecutar)
        layout.addWidget(self.label)
        layout.addWidget(self.btn)
        self.setLayout(layout)

    def ejecutar(self):
        resultado = self.validar.ejecutar()
        self.label.setText(resultado)
