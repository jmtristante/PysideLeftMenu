import os
from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFileDialog, QMessageBox, QApplication, QComboBox
)
from PySide6.QtCore import Qt
import sys

from widgets.card_frame import CardFrame

MODULE_BASE = os.path.dirname(os.path.dirname(__file__))

from modules.extraccion.src.load_excel import load_config, read_excel, create_scope

sys.path.append(MODULE_BASE)


class LoadDDRWindow(CardFrame):
    def __init__(self):
        super().__init__(title="Extracción/load ddr")
        MODULE_BASE = 'modules/extraccion'
        self.SCOPES_DIR = os.path.join(MODULE_BASE, "data/scopes")
        self.setWindowTitle("Extractor DDR")
        self.setMinimumWidth(400)

        # Widgets
        self.scope_label = QLabel("Scope:")
        self.scope_combo = QComboBox()
        self.scope_combo.addItems(self.get_scopes())

        self.version_label = QLabel("Versión:")
        self.version_input = QLineEdit()

        self.excel_label = QLabel("Fichero Excel:")
        self.excel_input = QLineEdit()
        self.excel_input.setEnabled(False)
        self.excel_input.setPlaceholderText("Selecciona un fichero ddr")
        self.excel_button = QPushButton("Buscar...")

        self.run_button = QPushButton("Ejecutar")
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)

        # Layout
        layout = self.layout()
        layout.addWidget(self.scope_label)
        layout.addWidget(self.scope_combo)
        layout.addWidget(self.version_label)
        layout.addWidget(self.version_input)
        layout.addWidget(self.excel_label)
        layout.addWidget(self.excel_input)
        layout.addWidget(self.excel_button)
        layout.addWidget(self.run_button)
        layout.addWidget(self.status_label)
        self.setLayout(layout)

        # Conexiones
        self.excel_button.clicked.connect(self.select_excel_file)
        self.run_button.clicked.connect(self.run_extractor)

    def get_scopes(self):
        if not os.path.isdir(self.SCOPES_DIR):
            return []
        return [name for name in os.listdir(self.SCOPES_DIR) if os.path.isdir(os.path.join(self.SCOPES_DIR, name))]

    def select_excel_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecciona el fichero Excel", "",
                                                   "Excel Files (*.xlsm *.xlsx)")
        if file_path:
            self.excel_input.setText(file_path)

    def run_extractor(self):
        scope = self.scope_combo.currentText().strip()
        version = self.version_input.text().strip()
        excel_path = self.excel_input.text().strip()

        if not scope or not version or not excel_path:
            QMessageBox.warning(self, "Campos incompletos", "Por favor, rellena todos los campos.")
            return

        if not os.path.isfile(excel_path):
            QMessageBox.critical(self, "Error", "El fichero Excel no existe.")
            return

        try:
            self.status_label.setText("Cargando configuración...")
            load_config(os.path.join(self.SCOPES_DIR, scope))
            self.status_label.setText("Leyendo Excel...")
            excel_data = read_excel(excel_path)
            self.status_label.setText("Creando archivos...")
            create_scope(scope, version, excel_data)
            self.status_label.setText("¡Proceso completado!")
            QMessageBox.information(self, "Éxito", "Extracción completada correctamente.")
        except Exception as e:
            self.status_label.setText("Error en el proceso.")
            QMessageBox.critical(self, "Error", f"Ocurrió un error:\n{str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoadDDRWindow()
    window.show()
    sys.exit(app.exec())
