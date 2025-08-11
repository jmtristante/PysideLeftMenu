from PySide6.QtWidgets import QWidget, QVBoxLayout, QCheckBox
import palette

class LabeledCheckBox(QWidget):
    def __init__(self, label, checked=False, parent=None):
        super().__init__(parent)
        self.setObjectName("LabeledCheckBox")
        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)
        self.checkbox = QCheckBox(label)
        self.checkbox.setChecked(checked)
        self.set_palette_style()
        layout.addWidget(self.checkbox)

    def set_palette_style(self):
        self.checkbox.setStyleSheet(
            f"font-size: 13px; margin-bottom: 0px; background: transparent; color: {palette.palette['text']};"
        )

    def update_palette(self):
        self.set_palette_style()
