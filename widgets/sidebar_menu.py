from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QToolButton, QFrame, QHBoxLayout, QPushButton, QLabel, QDockWidget, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon
import qtawesome as qta

from modules_config import MODULES

# Construir diccionario de clases de pantallas y lista de items de menú
MENU_ITEMS = []
MODULE_ICONS = {}  # Nuevo: para guardar iconos de módulos
for module in MODULES:
    MODULE_ICONS[module["name"]] = module.get("icon", None)
    for comp in module["components"]:
        MENU_ITEMS.append({
            "module": module["name"],
            "key": comp["key"],
            "label": comp["label"],
            "icon": comp.get("icon", None)
        })

def get_icon(icon_spec):
    if not icon_spec:
        return None
    if icon_spec.startswith("mdi."):
        return qta.icon(icon_spec)
    return QIcon(icon_spec)

class SidebarMenu(QWidget):
    funcionalidad_seleccionada = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.expanded = True
        self.selected_key = None
        self.func_buttons = {}
        self.status_labels = {}
        self.module_btns = {}
        self.module_widgets = {}

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        

        # Botón de expandir/colapsar menú
        self.toggle_btn = QToolButton()
        self.toggle_btn.setIcon(qta.icon("mdi.menu"))
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(True)
        self.toggle_btn.setToolTip("Contraer menú")
        self.toggle_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.toggle_btn.setStyleSheet("border: none; background: blue;")
        self.toggle_btn.clicked.connect(self.toggle_menu)
        self.main_layout.addWidget(self.toggle_btn, alignment=Qt.AlignLeft)

        # Contenedor para el resto del menú
        self.menu_widget = QWidget()
        self.menu_layout = QVBoxLayout(self.menu_widget)
        self.menu_layout.setContentsMargins(10, 10, 10, 10)
        self.menu_layout.setSpacing(8)
        # Puedes establecer el fondo blanco del layout (realmente del widget que lo contiene)
        self.menu_widget.setStyleSheet("background: purple;")
        self.main_layout.addWidget(self.menu_widget)

        current_module = None
        module_btn = None
        module_widget = None
        module_layout = None

        for item in MENU_ITEMS:
            if item["module"] != current_module:
                current_module = item["module"]
                module_btn = QToolButton()
                module_btn.setText(current_module)
                module_btn.setCheckable(True)
                module_btn.setChecked(False)
                module_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
                module_btn.setStyleSheet("background: transparent;")
                module_icon = MODULE_ICONS.get(current_module)
                icon_obj = get_icon(module_icon)
                if icon_obj:
                    module_btn.setIcon(icon_obj)
                    module_btn.setIconSize(QSize(20, 20))
                module_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                self.menu_layout.addWidget(module_btn)
                self.module_btns[current_module] = module_btn

                module_widget = QWidget()
                module_layout = QVBoxLayout(module_widget)
                module_layout.setContentsMargins(20, 0, 0, 0)
                module_layout.setSpacing(4)
                module_widget.setVisible(False)
                module_widget.setStyleSheet("background: transparent;")  # Fondo transparente
                self.menu_layout.addWidget(module_widget)
                self.module_widgets[current_module] = module_widget

                # Cambia: Si el menú está comprimido, expándelo y despliega el módulo
                def make_toggle_func(btn, widget, name):
                    def handler(checked):
                        from PySide6.QtCore import QTimer
                        if not self.expanded:
                            self.set_expanded(True)
                            # Espera a que el menú se expanda, luego despliega el módulo
                            def expand_and_open():
                                btn.setChecked(True)
                                widget.setVisible(True)
                            QTimer.singleShot(10, expand_and_open)
                        else:
                            widget.setVisible(checked)
                    return handler
                module_btn.clicked.connect(make_toggle_func(module_btn, module_widget, current_module))

                if self.menu_layout.count() > 2:
                    sep = QFrame()
                    sep.setFrameShape(QFrame.HLine)
                    sep.setFrameShadow(QFrame.Sunken)
                    self.menu_layout.insertWidget(self.menu_layout.count() - 2, sep)

            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(0)
            btn = QPushButton(item["label"])
            btn.setObjectName(item["key"])
            btn.setCheckable(True)
            icon_obj = get_icon(item.get("icon"))
            if icon_obj:
                btn.setIcon(icon_obj)
            btn.clicked.connect(lambda checked, k=item["key"]: self.select_funcionalidad(k))
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            row.addWidget(btn, stretch=1)
            status = QLabel("")
            status.setStyleSheet("color: red; font-size: 12px; margin-left: 6px;")
            row.addWidget(status)
            module_layout.addLayout(row)
            self.func_buttons[item["key"]] = btn
            self.status_labels[item["key"]] = status

        self.menu_layout.addStretch()

        self.setObjectName("SidebarMenu")  # <-- Añadido para el selector QWidget#SidebarMenu
        self.setStyleSheet("""
            QWidget {
                background: yellow;
                border-right: 1.5px solid #d0d0d0;
            }
            QToolButton {
                font-weight: bold;
                font-size: 14px;
                padding: 6px 8px;
                border: none;
                background: black;
                text-align: left;
            }
            QToolButton:checked {
                background: #e0e0e0;
            }
            QPushButton {
                text-align: left;
                padding: 6px 12px;
                border: none;
                background: transparent;
                border-radius: 0px;
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
        """ )

        

        self.select_funcionalidad(None)
        self.set_expanded(True)  # Inicialmente expandido

    def toggle_menu(self):
        self.set_expanded(not self.expanded)

    def set_expanded(self, expanded):
        self.expanded = expanded
        # Cambia icono y tooltip del botón de expandir/colapsar
        if expanded:
            self.toggle_btn.setIcon(qta.icon("mdi.menu-open"))
            self.toggle_btn.setToolTip("Contraer menú")
            self.menu_widget.setVisible(True)
            self.setMinimumWidth(180)
            self.setMaximumWidth(220)
        else:
            self.toggle_btn.setIcon(qta.icon("mdi.menu"))
            self.toggle_btn.setToolTip("Expandir menú")
            self.menu_widget.setVisible(True)
            self.setMinimumWidth(56)
            self.setMaximumWidth(56)
        # Oculta o muestra los textos de los botones
        for key, btn in self.module_btns.items():
            btn.setText(key if expanded else "")
            btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon if expanded else Qt.ToolButtonIconOnly)
            # Cuando está comprimido, colapsa los módulos
            if not expanded:
                btn.setChecked(False)
                widget = self.module_widgets.get(key)
                if widget:
                    widget.setVisible(False)
        for key, btn in self.func_buttons.items():
            # Solo QPushButton: usa setText, NO setToolButtonStyle
            if isinstance(btn, QPushButton):
                # Usa el label original, no el objectName (que es la key)
                label = next((item["label"] for item in MENU_ITEMS if item["key"] == key), key)
                btn.setText(label if expanded else "")
                btn.setToolTip(label if not expanded else "")
            elif hasattr(btn, "setToolButtonStyle"):
                label = next((item["label"] for item in MENU_ITEMS if item["key"] == key), key)
                btn.setText(label if expanded else "")
                btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon if expanded else Qt.ToolButtonIconOnly)

    def select_funcionalidad(self, key):
        print(f"funcionalidad {key}")
        for btn in self.func_buttons.values():
            btn.setChecked(False)
        if key in self.func_buttons:
            self.func_buttons[key].setChecked(True)
        self.selected_key = key
        if key:
            self.funcionalidad_seleccionada.emit(key)

    def set_screen_created(self, key, created):
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
        self.setStyleSheet("background: green;")
