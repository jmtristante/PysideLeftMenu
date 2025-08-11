from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, QHBoxLayout, QPushButton, QCheckBox
from PySide6.QtCore import Qt
import palette  # Importa la paleta de colores

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
        self.combobox.setStyleSheet(style)  # Aplica el estilo directamente al QComboBox

    def update_palette(self):
        self.set_palette_style()
        # No tiene hijos personalizados

class LabeledLineEdit(QWidget):
    def __init__(self, label, placeholder="", lineedit_style=None, height=32, parent=None):
        super().__init__(parent)
        self.setObjectName("LabeledLineEdit")
        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)
        lbl = QLabel(label)
        lbl.setStyleSheet("font-size: 13px; margin-bottom: 0px; background: transparent;")
        self.lineedit = QLineEdit()
        self.lineedit.setPlaceholderText(placeholder)
        self.lineedit.setFixedHeight(height)
        self.lineedit_style = lineedit_style
        self.set_palette_style()
        layout.addWidget(lbl)
        layout.addWidget(self.lineedit)

    def set_palette_style(self):
        style = self.lineedit_style if self.lineedit_style is not None else (
            f"border: 1px solid {palette.palette['border']}; "
            f"border-radius: 4px; padding-left: 10px; background: {palette.palette['background']}; color: {palette.palette['text']};"
        )
        self.lineedit.setStyleSheet(style)  # Aplica el estilo directamente al QLineEdit

    def update_palette(self):
        self.set_palette_style()
        # No tiene hijos personalizados

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

    def update_palette(self):
        self.set_palette_style()
        # No tiene hijos personalizados

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
        # No tiene hijos personalizados

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
        # No tiene hijos personalizados

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
        # No tiene hijos personalizados
    def update_palette(self):
        self.set_palette_style()
        # No tiene hijos personalizados


