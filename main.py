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

# Construir diccionario de clases de pantallas y lista de items de menú
SCREEN_CLASSES = {}
MENU_ITEMS = []
for module in MODULES:
    for comp in module["components"]:
        SCREEN_CLASSES[comp["key"]] = comp["widget"]
        MENU_ITEMS.append({"module": module["name"], "key": comp["key"], "label": comp["label"]})

class SidebarMenu(QWidget):
    funcionalidad_seleccionada = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_key = None
        self.func_buttons = {}
        self.status_labels = {}
        self.module_btns = {}
        self.module_widgets = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        current_module = None
        module_btn = None
        module_widget = None
        module_layout = None

        for item in MENU_ITEMS:
            if item["module"] != current_module:
                # Nuevo módulo
                current_module = item["module"]
                module_btn = QToolButton()
                module_btn.setText(current_module)
                module_btn.setCheckable(True)
                module_btn.setChecked(False)  # <-- Por defecto, cerrado
                module_btn.setArrowType(Qt.RightArrow)  # <-- Flecha a la derecha
                module_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
                layout.addWidget(module_btn)
                self.module_btns[current_module] = module_btn

                module_widget = QWidget()
                module_layout = QVBoxLayout(module_widget)
                module_layout.setContentsMargins(20, 0, 0, 0)
                module_layout.setSpacing(4)
                module_widget.setVisible(False)  # <-- Por defecto, oculto
                layout.addWidget(module_widget)
                self.module_widgets[current_module] = module_widget

                # Conectar para minimizar/maximizar
                def make_toggle_func(btn, widget):
                    return lambda checked: (
                        btn.setArrowType(Qt.DownArrow if checked else Qt.RightArrow),
                        widget.setVisible(checked)
                    )
                module_btn.clicked.connect(make_toggle_func(module_btn, module_widget))

                # Separador entre módulos (excepto el primero)
                if layout.count() > 2:
                    sep = QFrame()
                    sep.setFrameShape(QFrame.HLine)
                    sep.setFrameShadow(QFrame.Sunken)
                    layout.insertWidget(layout.count() - 2, sep)

            # Añadir funcionalidad al módulo
            row = QHBoxLayout()
            btn = QPushButton(item["label"])
            btn.setObjectName(item["key"])
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, k=item["key"]: self.select_funcionalidad(k))
            row.addWidget(btn)
            status = QLabel("")
            status.setStyleSheet("color: red; font-size: 12px; margin-left: 6px;")
            row.addWidget(status)
            row.addStretch()
            module_layout.addLayout(row)
            self.func_buttons[item["key"]] = btn
            self.status_labels[item["key"]] = status

        layout.addStretch()

        # Estética
        self.setStyleSheet("""
            QToolButton {
                font-weight: bold;
                font-size: 14px;
                padding: 6px 8px;
                border: none;
                background: transparent;
                text-align: left;
            }
            QToolButton:checked {
                background: #e0e0e0;
            }
            QPushButton {
                text-align: left;
                padding: 6px 12px;
                border-radius: 6px;
                background: #f0f0f0;
            }
            QPushButton:checked {
                background: #b3d1ff;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #e0e0e0;
            }
            QLabel {
                color: #333;
            }
        """)

        # Selección inicial: ninguna
        self.select_funcionalidad(None)

    def select_funcionalidad(self, key):
        print(f"funcionalidad {key}")
        # Desmarcar todos
        for btn in self.func_buttons.values():
            btn.setChecked(False)
        # Marcar el seleccionado
        if key in self.func_buttons:
            self.func_buttons[key].setChecked(True)
        self.selected_key = key
        if key:
            self.funcionalidad_seleccionada.emit(key)

    def set_screen_created(self, key, created):
        # Solo mostrar punto rojo si la pantalla está creada
        if key in self.status_labels:
            self.status_labels[key].setText("●" if created else "")

    def deselect(self, key):
        if key in self.func_buttons:
            self.func_buttons[key].setChecked(False)
        if self.selected_key == key:
            self.selected_key = None

class NoTitleDockWidget(QDockWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitleBarWidget(QWidget(self))


class BlankScreen(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addStretch()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Proyecto PySide6 Modular")
        self.resize(900, 600)

        # Fondo gris global
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background: #f6f7fa;
            }
        """)

        # Barra superior con nombre y botón hamburguesa
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        self.menu_action = QAction()
        self.menu_action.setText("Menú")
        self.menu_action.triggered.connect(self.toggle_sidebar)
        toolbar.addAction(self.menu_action)


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
        self.sidebar.setWidget(self.sidebar_menu)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.sidebar)

        # Selección inicial: ninguna pantalla cargada
        #self.card_viewer.set_card(self.blank_screen)

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
