from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget, QWidget
from PySide6.QtCore import Qt, Signal

class CardStacked(QFrame):
    closed = Signal()
    back = Signal()

    def __init__(self, title="Título", parent=None, padding=32, show_close=True, show_back=True):
        super().__init__(parent)
        self.setObjectName("CardStacked")
        self.setStyleSheet("""
            QFrame#CardStacked {
                background: #fff;
                border-radius: 16px;
                border: 1px solid #e0e0e0;
            }
        """)
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
            self.back_btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    background: transparent;
                    font-size: 20px;
                    color: #888;
                }
                QPushButton:hover {
                    color: #1976d2;
                    background: #e3f2fd;
                }
            """)
            header_layout.addWidget(self.back_btn)
        else:
            self.back_btn = None

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

        # Stacked widget para el contenido
        self.stacked = QStackedWidget()
        main_layout.addWidget(self.stacked)

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
