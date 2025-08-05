from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from ..logic.importar import Importar

class ImportarWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.importar = Importar()
        layout = QVBoxLayout()
        self.label = QLabel("Pantalla: Importar")
        self.btn = QPushButton("Ejecutar importación")
        self.btn.clicked.connect(self.ejecutar)
        layout.addWidget(self.label)
        layout.addWidget(self.btn)
        self.setLayout(layout)

    def ejecutar(self):
        resultado = self.importar.ejecutar()
        self.label.setText(resultado)
