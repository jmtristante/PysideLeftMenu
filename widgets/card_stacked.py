from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget, QWidget
from PySide6.QtCore import Qt, Signal
import palette


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
        
class CardStacked(QFrame):
    closed = Signal()
    back = Signal()

    def __init__(self, title="Título", parent=None, padding=32, show_close=True, show_back=True):
        super().__init__(parent)
        self.setObjectName("CardStacked")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(padding, padding, padding, padding)
        main_layout.setSpacing(18)

        # Cabecera con título, botón atrás y botón cerrar
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)

        if show_back:
            self.back_btn = QPushButton("←")
            self.back_btn.setFixedSize(32, 32)
            
            header_layout.addWidget(self.back_btn)
        else:
            self.back_btn = None

        self.title_label = QLabel(title)
 
        header_layout.addWidget(self.title_label, alignment=Qt.AlignLeft)
        header_layout.addStretch()
        if show_close:
            self.close_btn = QPushButton("✕")
            self.close_btn.setFixedSize(32, 32)
            
            self.close_btn.clicked.connect(self.closed.emit)
            header_layout.addWidget(self.close_btn)
        else:
            self.close_btn = None
        main_layout.addLayout(header_layout)
        self.set_palette_style()


        # Stacked widget para el contenido
        self.stacked = QStackedWidget()
        main_layout.addWidget(self.stacked)

    def set_palette_style(self):
        self.setStyleSheet(f"""
            QFrame#CardStacked {{
                background: {palette.palette['card_bg']};
                border-radius: 16px;
                border: 1px solid {palette.palette['border']};
            }}
            QLabel, QLineEdit, QComboBox, QPushButton {{
                font-size: 14px;
                color: {palette.palette['text']};
            }}
            QWidget {{
                background: {palette.palette['card_bg']};
            }}
        """)
        self.title_label.setStyleSheet(
            f"font-weight: bold; font-size: 26px; margin-bottom: 8px; background: transparent; color: {palette.palette['text']};"
        )
        if self.back_btn:
            self.back_btn.setStyleSheet(f"""
                QPushButton {{
                    border: none;
                    background: transparent;
                    font-size: 20px;
                    color: {palette.palette['close_icon']};
                }}
                QPushButton:hover {{
                    color: {palette.palette['primary']};
                    background: {palette.palette['selection']};
                }}
            """)
        if self.close_btn:
            self.close_btn.setStyleSheet(f"""
                QPushButton {{
                    border: none;
                    background: transparent;
                    font-size: 20px;
                    color: {palette.palette['close_icon']};
                }}
                QPushButton:hover {{
                    color: {palette.palette['danger']};
                    background: {palette.palette['selection']};
                }}
            """)

        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def update_palette(self):
        self.set_palette_style()
        update_palette_recursive(self)

    def set_title(self, text):
        self.title_label.setText(text)

    def add_widget(self, widget: QWidget):
        self.stacked.addWidget(widget)

    def set_current_index(self, index: int):
        self.stacked.setCurrentIndex(index)

    def current_index(self):
        return self.stacked.currentIndex()

    def go_back(self):
        # Va al widget anterior si es posible
        idx = self.stacked.currentIndex()
        if idx > 0:
            self.stacked.setCurrentIndex(idx - 1)
            self.back.emit()
            self.back.emit()
