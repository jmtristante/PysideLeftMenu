from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QPushButton
import palette

class LabeledFileInput(QWidget):
    def __init__(self, label, placeholder="", button_text="Buscar...", lineedit_style=None, button_style=None, height=32, parent=None):
        super().__init__(parent)
        self.setObjectName("LabeledFileInput")
        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)
        lbl = QLabel(label)
        lbl.setStyleSheet("font-size: 13px; margin-bottom: 0px; background: transparent;")
        layout.addWidget(lbl)
        row = QHBoxLayout()
        row.setSpacing(0)
        self.lineedit = QLineEdit()
        self.lineedit.setPlaceholderText(placeholder)
        self.lineedit.setEnabled(False)
        self.lineedit.setFixedHeight(height)
        self.lineedit_style = lineedit_style
        self.button_style = button_style
        self.button = QPushButton(button_text)
        self.button.setFixedHeight(height)
        self.button.setFixedWidth(90)
        self.set_palette_style()
        row.addWidget(self.lineedit)
        row.addWidget(self.button)
        layout.addLayout(row)

    def set_palette_style(self):
        lineedit_style = self.lineedit_style if self.lineedit_style is not None else (
            f"border: 1px solid {palette.palette['border']};"
            f"border-radius: 4px; border-top-right-radius: 0px; border-bottom-right-radius: 0px;"
            f"padding-left: 10px;background: {palette.palette['background']}; color: {palette.palette['text']};"
        )
        button_style = self.button_style if self.button_style is not None else (
            f"border: 1px solid {palette.palette['border']};"
            f"border-left: none;"
            f"border-radius: 4px;"
            f"border-top-left-radius: 0px;"
            f"border-bottom-left-radius: 0px;"
            f"margin-left: 0px;"
            f"background: {palette.palette['button_bg']};"
            f"color: {palette.palette['button_text']};"
        )
        self.lineedit.setStyleSheet(lineedit_style)
        self.button.setStyleSheet(button_style)

    def setEnabled(self, arg__1):
        self.lineedit.setEnabled(False)
        self.button.setEnabled(arg__1)

    def currentText(self):
        return self.lineedit.text()

    def update_palette(self):
        self.set_palette_style()
