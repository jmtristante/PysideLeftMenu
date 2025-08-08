from PySide6.QtWidgets import QWidget, QVBoxLayout, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt
from widgets.card_frame import CardFrame

class CardFrameViewer(QWidget):
    """
    Widget visor de CardFrames: muestra solo un CardFrame a la vez,
    centrado y con margen para que se vea el fondo grisáceo.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        # Usa un layout con más margen y espaciadores para centrar la card
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(80, 48, 80, 48)  # margen más grande
        self._main_layout.setSpacing(0)
        self._main_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self._card_container = QVBoxLayout()
        self._card_container.setContentsMargins(0, 0, 0, 0)
        self._card_container.setSpacing(0)
        self._main_layout.addLayout(self._card_container)
        self._main_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.current = None

    def set_card(self, card_widget):
        # Quita el anterior
        if self.current is not None:
            self._card_container.removeWidget(self.current)
            self.current.setParent(None)
        self.current = card_widget
        if card_widget is not None:
            self._card_container.addWidget(card_widget, alignment=Qt.AlignHCenter | Qt.AlignVCenter)

    def clear(self):
        self.set_card(None)
