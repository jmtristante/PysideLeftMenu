import os
from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFileDialog, QMessageBox, QApplication, QComboBox,
    QHBoxLayout, QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import sys

from widgets.card_frame import CardFrame
from widgets.input_labeled import LabeledComboBox, LabeledLineEdit, LabeledFileInput, PrimaryButton

MODULE_BASE = os.path.dirname(os.path.dirname(__file__))

from modules.extraccion.src.load_excel import load_config, read_excel, create_scope

sys.path.append(MODULE_BASE)


class LoadDDRWindow(CardFrame):
    def __init__(self):
        super().__init__(title="Extracción/load ddr")
        self.SCOPES_DIR = os.path.join(MODULE_BASE, "data/scopes")
        self.setWindowTitle("Extractor DDR")
        self.setMinimumWidth(440)
        self.setMaximumWidth(480)

        main_layout = self.layout()
        main_layout.setContentsMargins(32, 32, 32, 32)
        main_layout.setSpacing(14)

        # --- Scope & Version row ---
        row1 = QHBoxLayout()
        row1.setSpacing(16)

        # Scope (nuevo widget)
        self.scope_input = LabeledComboBox(
            label="Scope:",
            items=self.get_scopes()
        )
        row1.addWidget(self.scope_input)

        # Version (nuevo widget)
        self.version_input = LabeledLineEdit(
            label="Versión:",
            placeholder="",
            height=32
        )
        row1.addWidget(self.version_input)
        row1.addStretch()
        main_layout.addLayout(row1)

        # --- Excel file row (nuevo widget) ---
        self.excel_input = LabeledFileInput(
            label="Fichero Excel:",
            placeholder="Selecciona un fichero ddr",
            button_text="Buscar...",
            height=32
        )
        main_layout.addWidget(self.excel_input)

        # --- Spacer ---
        main_layout.addItem(QSpacerItem(0, 30, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # --- Status label ---
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("background: transparent;")
        main_layout.addWidget(self.status_label)

        # --- Run button ---
        self.run_button = PrimaryButton("Ejecutar")
        self.run_button.setFixedHeight(40)
        main_layout.addWidget(self.run_button)
        
        self.setLayout(main_layout)

        # Conexiones
        self.excel_input.button.clicked.connect(self.select_excel_file)
        self.run_button.clicked.connect(self.run_extractor)

    def get_scopes(self):
        if not os.path.isdir(self.SCOPES_DIR):
            return []
        return [name for name in os.listdir(self.SCOPES_DIR) if os.path.isdir(os.path.join(self.SCOPES_DIR, name))]

    def select_excel_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecciona el fichero Excel", "",
                                                   "Excel Files (*.xlsm *.xlsx)")
        if file_path:
            self.excel_input.lineedit.setText(file_path)

    def run_extractor(self):
        scope = self.scope_input.combobox.currentText().strip()
        version = self.version_input.lineedit.text().strip()
        excel_path = self.excel_input.lineedit.text().strip()

        if not scope or not version or not excel_path:
            self.status_label.setText("Por favor, rellena todos los campos.")
            return

        if not os.path.isfile(excel_path):
            self.status_label.setText("El fichero Excel no existe.")
            return

        try:
            self.status_label.setText("Cargando configuración...")
            load_config(os.path.join(self.SCOPES_DIR, scope))
            self.status_label.setText("Leyendo Excel...")
            excel_data = read_excel(excel_path)
            self.status_label.setText("Creando archivos...")
            create_scope(os.path.join(self.SCOPES_DIR, scope, version), excel_data)
            self.status_label.setText("¡Proceso completado!")
        except Exception as e:
            self.status_label.setText(f"Ocurrió un error inesperado")
            QMessageBox.critical(self, "Error", f"{str(e)}")




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoadDDRWindow()
    window.show()
    sys.exit(app.exec())
