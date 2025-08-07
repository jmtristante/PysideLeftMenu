from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal

class CardFrame(QFrame):  # <-- Hereda de Card y QFrame
    closed = Signal()  # Señal emitida al pulsar el botón cerrar

    def __init__(self, title="Título", parent=None, padding=32, show_close=True):
        super().__init__(parent)
        self.setObjectName("CardFrame")
        self.setStyleSheet("""
            QFrame#CardFrame {
                background: #fff;
                border-radius: 16px;
                border: 1px solid #e0e0e0;
            }
        """)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(padding, padding, padding, padding)
        main_layout.setSpacing(18)

        # Cabecera con título y botón cerrar
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 26px; margin-bottom: 8px;")
        header_layout.addWidget(self.title_label, alignment=Qt.AlignLeft)
        header_layout.addStretch()
        if show_close:
            self.close_btn = QPushButton("✕")
            self.close_btn.setFixedSize(32, 32)
            self.close_btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    background: transparent;
                    font-size: 20px;
                    color: #888;
                }
                QPushButton:hover {
                    color: #ff4d4f;
                    background: #fbeaea;
                }
            """)
            self.close_btn.clicked.connect(self.closed.emit)
            header_layout.addWidget(self.close_btn)
        else:
            self.close_btn = None
        main_layout.addLayout(header_layout)

        # Layout para el contenido del card
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(18)
        main_layout.addLayout(self.content_layout)

    def set_title(self, text):
        self.title_label.setText(text)

    def layout(self):
        # Devuelve el layout donde añadir widgets de contenido
        return self.content_layout
