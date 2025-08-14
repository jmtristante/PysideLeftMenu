from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit
import palette

class LabeledLineEdit(QWidget):
    def __init__(self, label= False, placeholder="", lineedit_style=None, height=32, parent=None):
        super().__init__(parent)
        self.setObjectName("LabeledLineEdit")
        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)
        if label:
            lbl = QLabel(label)
            lbl.setStyleSheet("font-size: 13px; margin-bottom: 0px; background: transparent;")
            layout.addWidget(lbl)

        self.lineedit = QLineEdit()
        self.lineedit.setPlaceholderText(placeholder)
        self.lineedit.setFixedHeight(height)
        self.lineedit_style = lineedit_style
        self.set_palette_style()
        layout.addWidget(self.lineedit)

    def set_palette_style(self):
        style = self.lineedit_style if self.lineedit_style is not None else (
            f"border: 1px solid {palette.palette['border']}; "
            f"border-radius: 4px; padding-left: 10px; background: {palette.palette['background']}; color: {palette.palette['text']};"
        )
        self.lineedit.setStyleSheet(style)

    def update_palette(self):
        self.set_palette_style()

    def text(self):
        return self.lineedit.text()
