from PySide6.QtWidgets import QPushButton
import palette

class PrimaryButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.set_palette_style()

    def set_palette_style(self):
        style = (
            f"QPushButton {{"
            f"background: {palette.palette['primary']};"
            f"color: {palette.palette['primary_text']};"
            f"border-radius: 8px;"
            f"font-weight: bold;"
            f"padding: 8px 28px;}}"
            f"QPushButton:hover {{"
            f"background: {palette.palette['primary_hover']};}}"
        )
        self.setStyleSheet(style)

    def update_palette(self):
        self.set_palette_style()
