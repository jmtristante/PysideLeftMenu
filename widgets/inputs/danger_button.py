from PySide6.QtWidgets import QPushButton
import palette

class DangerButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.set_palette_style()

    def set_palette_style(self):
        style = (
            f"QPushButton {{"
            f"background: {palette.palette['danger']};"
            f"color: {palette.palette['danger_text']};"
            f"border-radius: 8px;"
            f"font-weight: bold;"
            f"padding: 6px 18px;}}"
            f"QPushButton:hover {{"
            f"background: {palette.palette['danger_hover']};}}"
        )
        self.setStyleSheet(style)

    def update_palette(self):
        self.set_palette_style()
