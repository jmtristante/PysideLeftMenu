from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt

class LabeledComboBox(QWidget):
    DEFAULT_STYLE = """
        QComboBox {
            border: 1px solid #d0d0d0;
            border-radius: 4px;
            padding-right: 28px;
            padding-left: 10px;
        }
        QComboBox QAbstractItemView {
            outline: none;
            selection-background-color: #e6f0ff;
        }
        QComboBox QAbstractItemView::item {
            padding-left: 10px;  /* margen izquierdo SOLO en el texto de los items */
        }
        QComboBox::drop-down {
            border: none;
            background: transparent;
            width: 28px;
            subcontrol-origin: padding;
            subcontrol-position: top right;
        }
        QComboBox::down-arrow {
            width: 16px;
            height: 16px;
            margin-right: 6px;
            image: url(icons/arrow_drop_down.png);
        }
    """
    def __init__(self, label, items=None, combo_style=None, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)
        lbl = QLabel(label)
        lbl.setStyleSheet("font-size: 13px; margin-bottom: 0px; background: transparent;")
        self.combobox = QComboBox()
        if items:
            self.combobox.addItems(items)
        self.combobox.setFixedHeight(32)
        self.combobox.setStyleSheet(combo_style if combo_style is not None else self.DEFAULT_STYLE)
        layout.addWidget(lbl)
        layout.addWidget(self.combobox)

class LabeledLineEdit(QWidget):
    DEFAULT_STYLE = "border: 1px solid #d0d0d0; border-radius: 4px;"
    def __init__(self, label, placeholder="", lineedit_style=None, height=32, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)
        lbl = QLabel(label)
        lbl.setStyleSheet("font-size: 13px; margin-bottom: 0px; background: transparent;")
        self.lineedit = QLineEdit()
        self.lineedit.setPlaceholderText(placeholder)
        self.lineedit.setFixedHeight(height)
        # Solo el texto tiene margen izquierdo
        self.lineedit.setStyleSheet((lineedit_style if lineedit_style is not None else self.DEFAULT_STYLE) + " padding-left: 10px;")
        layout.addWidget(lbl)
        layout.addWidget(self.lineedit)

class LabeledFileInput(QWidget):
    DEFAULT_LINEEDIT_STYLE = "border: 1px solid #d0d0d0;border-radius: 4px; border-top-right-radius: 0px; border-bottom-right-radius: 0px;"
    DEFAULT_BUTTON_STYLE = """
        border: 1px solid #d0d0d0;
        border-left: none;
        border-radius: 4px;
        border-top-left-radius: 0px;
        border-bottom-left-radius: 0px;
        margin-left: 0px;
    """
    def __init__(self, label, placeholder="", button_text="Buscar...", lineedit_style=None, button_style=None, height=32, parent=None):
        super().__init__(parent)
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
        # Solo el texto tiene margen izquierdo
        self.lineedit.setStyleSheet((lineedit_style if lineedit_style is not None else self.DEFAULT_LINEEDIT_STYLE) + " padding-left: 10px;")
        self.button = QPushButton(button_text)
        self.button.setFixedHeight(height)
        self.button.setFixedWidth(90)
        self.button.setStyleSheet(button_style if button_style is not None else self.DEFAULT_BUTTON_STYLE)
        row.addWidget(self.lineedit)
        row.addWidget(self.button)
        layout.addLayout(row)
