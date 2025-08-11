import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout,
    QDockWidget, QToolBar, QLabel, QPushButton, QFrame, QToolButton, QHBoxLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction
from modules_config import MODULES  # <-- Importa la configuración de módulos
from widgets.card_frame import CardFrame
from widgets.card_frame_viewer import CardFrameViewer
from modules.extraccion.ui.scope_editor_window import ScopeEditorWindow
from widgets.sidebar_menu import SidebarMenu, NoTitleDockWidget
from widgets.input_labeled import LabeledComboBox, LabeledLineEdit, LabeledFileInput, LabeledCheckBox, PrimaryButton, DangerButton
import palette


# Construir diccionario de clases de pantallas y lista de items de menú
SCREEN_CLASSES = {}
for module in MODULES:
    for comp in module["components"]:
        SCREEN_CLASSES[comp["key"]] = comp["widget"]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Proyecto PySide6 Modular")
        self.resize(900, 600)


        # Elimina el botón menú de la barra superior
        # self.menu_action = QAction()
        # self.menu_action.setText("Menú")
        # self.menu_action.triggered.connect(self.toggle_sidebar)
        # toolbar.addAction(self.menu_action)


        # # Central widget: visor de CardFrames (ahora importado)
        self.card_viewer = CardFrameViewer()
        self.setCentralWidget(self.card_viewer)
        self.screens = {}  # key -> CardFrame

        # Pantalla en blanco
        self.blank_screen = QWidget()
        # self.card_viewer.set_card(self.blank_screen)

        # Sidebar personalizado
        self.sidebar = NoTitleDockWidget(self)
        self.sidebar.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.sidebar.setMinimumWidth(180)
        self.sidebar.setMaximumWidth(220)

        self.sidebar_menu = SidebarMenu()
        self.sidebar_menu.funcionalidad_seleccionada.connect(self.cambiar_funcionalidad)
        self.sidebar_menu.palette_toggled.connect(self.update_palette_all)  # Conecta la señal
        self.sidebar.setWidget(self.sidebar_menu)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.sidebar)


        self.palette_widgets = [self.card_viewer, self.sidebar_menu]


        self.setStyleSheet(f"""
                           background: {palette.palette['mainbackground']};
                           """)

    def cambiar_funcionalidad(self, key):
        if key not in SCREEN_CLASSES:
            return
        if key not in self.screens:
            widget = SCREEN_CLASSES[key]()
            widget.closed.connect(lambda: self.cerrar_pantalla(key))
            self.screens[key] = widget
            self.sidebar_menu.set_screen_created(key, True)
        self.card_viewer.set_card(self.screens[key])
        for k in self.sidebar_menu.func_buttons:
            self.sidebar_menu.func_buttons[k].setChecked(k == key)

    def cerrar_pantalla(self, key):
        if key in self.screens:
            widget = self.screens[key]
            if hasattr(widget, "close_background_tasks"):
                widget.close_background_tasks()
            self.card_viewer.clear()
            del self.screens[key]
            self.sidebar_menu.set_screen_created(key, False)
            self.sidebar_menu.deselect(key)
            self.card_viewer.set_card(self.blank_screen)

    def toggle_sidebar(self):
        if self.sidebar.isVisible():
            self.sidebar.hide()
        else:
            self.sidebar.show()

    def update_palette_all(self):
        self.setStyleSheet(f"""
                           background: {palette.palette['mainbackground']};
                           """)
        for w in self.palette_widgets:
            w.update_palette()
        for s in self.screens.items():
            s[1].update_palette()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
