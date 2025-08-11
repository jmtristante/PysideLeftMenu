from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget
from PySide6.QtCore import Qt, Signal
import palette  # Importa la paleta de colores

def update_palette_recursive(widget, visited=None):
    if visited is None:
        visited = set()
    if id(widget) in visited:
        return
    visited.add(id(widget))
    # Recorre todos los hijos directos
    for child in widget.findChildren(QWidget):
        if id(child) in visited:
            continue
        # Solo llama a update_palette en los hijos, no en el widget raíz
        if hasattr(child, "update_palette"):
            child.update_palette()
        update_palette_recursive(child, visited)

class CardFrame(QFrame):  # <-- Hereda de Card y QFrame
    closed = Signal()  # Señal emitida al pulsar el botón cerrar

    def __init__(self, title="Título", parent=None, padding=32, show_close=True):
        super().__init__(parent)
        self.setObjectName("CardFrame")
        self.show_close = show_close
        self.init_ui(title, padding)

    def init_ui(self, title, padding):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(padding, padding, padding, padding)
        main_layout.setSpacing(18)

        # Cabecera con título y botón cerrar
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)
        self.title_label = QLabel(title)
        header_layout.addWidget(self.title_label, alignment=Qt.AlignLeft)
        header_layout.addStretch()
        if self.show_close:
            self.close_btn = QPushButton("✕")
            self.close_btn.setFixedSize(32, 32)
            self.close_btn.clicked.connect(self.closed.emit)
            header_layout.addWidget(self.close_btn)
        else:
            self.close_btn = None
        main_layout.addLayout(header_layout)

        # Layout para el contenido del card
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(18)
        main_layout.addLayout(self.content_layout)
        self.set_palette_style()

    def set_palette_style(self):
        self.setStyleSheet(f"""
            QFrame#CardFrame {{
                background: {palette.palette['card_bg']};
                border-radius: 16px;
                border: none;
            }}
            QLabel, QLineEdit, QComboBox, QPushButton {{
                font-size: 14px;
                color: {palette.palette['text']};
            }}
        """)
        self.title_label.setStyleSheet(
            f"font-weight: bold; font-size: 26px; margin-bottom: 8px; background: transparent; color: {palette.palette['text']};"
        )
        if self.close_btn:
            self.close_btn.setStyleSheet(f"""
                QPushButton {{
                    border: none;
                    background: transparent;
                    font-size: 26px;
                    color: {palette.palette['close_icon']};
                    margin-bottom: 8px;
                }}
                QPushButton:hover {{
                    color: {palette.palette['danger']};
                }}
            """)
        # Fuerza el repolish y repintado
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def update_palette(self):
        self.set_palette_style()
        update_palette_recursive(self)

    def set_title(self, text):
        self.title_label.setText(text)

    def layout(self):
        # Devuelve el layout donde añadir widgets de contenido
        return self.content_layout
