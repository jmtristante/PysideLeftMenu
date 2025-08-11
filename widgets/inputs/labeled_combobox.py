from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox
import palette

class LabeledComboBox(QWidget):
    def __init__(self, label, items=None, combo_style=None, parent=None, is_dark=False):
        super().__init__(parent)
        self.setObjectName("LabeledComboBox")
        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)
        lbl = QLabel(label)
        lbl.setStyleSheet("font-size: 13px; margin-bottom: 0px; background: transparent;")
        self.combobox = QComboBox()
        if items:
            self.combobox.addItems(items)
        self.combobox.setFixedHeight(32)
        self.combo_style = combo_style
        self.set_palette_style()
        layout.addWidget(lbl)
        layout.addWidget(self.combobox)

    def set_palette_style(self):
        style = self.combo_style if self.combo_style is not None else f"""
            QComboBox {{
                border: 1px solid {palette.palette['border']};
                border-radius: 4px;
                padding-right: 28px;
                padding-left: 10px;
                background: {palette.palette['background']};
                color: {palette.palette['text']};
            }}
            QComboBox QAbstractItemView {{
                outline: none;
                selection-background-color: {palette.palette['selection']};
            }}
            QComboBox QAbstractItemView::item {{
                padding-left: 10px;
            }}
            QComboBox::drop-down {{
                border: none;
                background: transparent;
                width: 28px;
                subcontrol-origin: padding;
                subcontrol-position: top right;
            }}
            QComboBox::down-arrow {{
                width: 16px;
                height: 16px;
                margin-right: 6px;
                image: url(icons/arrow_drop_down.png);
            }}
        """
        self.combobox.setStyleSheet(style)

    def currentText(self):
        return self.combobox.currentText()

    def update_palette(self):
        self.set_palette_style()
