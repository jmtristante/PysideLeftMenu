from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QToolButton, QFrame, QHBoxLayout, QPushButton, QLabel, QDockWidget, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon
import qtawesome as qta

from modules_config import MODULES
import palette  # Añade esta línea para importar la paleta

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

def get_icon(icon_spec, color=None):
    if not icon_spec:
        return None
    if icon_spec.startswith("mdi."):
        return qta.icon(icon_spec, color=color)
    return QIcon(icon_spec)

class SidebarMenu(QWidget):
    funcionalidad_seleccionada = Signal(str)
    palette_toggled = Signal()  # Nueva señal para notificar cambio de paleta

    def __init__(self, parent=None):
        super().__init__(parent)
        self.expanded = True
        self.selected_key = None
        self.func_buttons = {}
        self.status_labels = {}
        self.module_btns = {}
        self.module_widgets = {}
        self.icon_specs = {}  # Guarda el spec de icono para cada botón
        self.dividers = []  # Guarda referencias a los QFrame divisores

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        

        # Botón de expandir/colapsar menú
        self.toggle_btn = QToolButton()
        self.toggle_btn.setIcon(qta.icon("mdi.menu", color=palette.palette['text']))
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(True)
        self.toggle_btn.setToolTip("Contraer menú")
        self.toggle_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.toggle_btn.setFixedHeight(40)  # Ajusta la altura si lo deseas
        self.toggle_btn.setStyleSheet("""
            border: none;
            background: white;
        """)
        self.toggle_btn.clicked.connect(self.toggle_menu)
        self.main_layout.addWidget(self.toggle_btn)

        # Contenedor para el resto del menú
        self.menu_widget = QWidget()
        self.menu_layout = QVBoxLayout(self.menu_widget)
        self.menu_layout.setContentsMargins(10, 10, 10, 10)
        self.menu_layout.setSpacing(8)
        # Puedes establecer el fondo blanco del layout (realmente del widget que lo contiene)
        self.menu_widget.setStyleSheet("background: white;")
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
                icon_obj = get_icon(module_icon, color=palette.palette['text'])
                if icon_obj:
                    module_btn.setIcon(icon_obj)
                    module_btn.setIconSize(QSize(20, 20))
                # Guarda el spec para actualizar luego
                self.icon_specs[module_btn] = module_icon
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
                    sep.setFrameShadow(QFrame.Plain)  # <-- Cambia a Plain para evitar doble línea/sombra
                    sep.setStyleSheet(f"color: {palette.palette['border']}; ")
                    self.menu_layout.insertWidget(self.menu_layout.count() - 2, sep)
                    self.dividers.append(sep)

            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(0)
            btn = QPushButton(item["label"])
            btn.setObjectName(item["key"])
            btn.setCheckable(True)
            icon_obj = get_icon(item.get("icon"), color=palette.palette['text'])
            if icon_obj:
                btn.setIcon(icon_obj)
            # Guarda el spec para actualizar luego
            self.icon_specs[btn] = item.get("icon")
            btn.clicked.connect(lambda checked, k=item["key"]: self.select_funcionalidad(k))
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            row.addWidget(btn, stretch=1)
            status = QLabel("")
            status.setStyleSheet("color: red; font-size: 12px; margin-left: 6px;")
            row.addWidget(status)
            module_layout.addLayout(row)
            self.func_buttons[item["key"]] = btn
            self.status_labels[item["key"]] = status

        # Botón para cambiar tema
        self.toggle_theme_btn = QPushButton()
        self.toggle_theme_btn.setCheckable(False)
        self.toggle_theme_btn.setFixedHeight(36)
        self.toggle_theme_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.toggle_theme_btn.clicked.connect(self.toggle_palette)
        self.update_toggle_theme_btn_icon()
        self.menu_layout.addStretch()
        self.menu_layout.addWidget(self.toggle_theme_btn)  # Añade el botón al final

        self.setObjectName("SidebarMenu")
        self.update_palette()

        

        self.select_funcionalidad(None)
        self.set_expanded(True)  # Inicialmente expandido

    def toggle_menu(self):
        self.set_expanded(not self.expanded)

    def set_expanded(self, expanded):
        self.expanded = expanded
        # Cambia icono y tooltip del botón de expandir/colapsar
        if expanded:
            self.toggle_btn.setIcon(qta.icon("mdi.menu-open", color=palette.palette['text']))
            self.toggle_btn.setToolTip("Contraer menú")
            self.menu_widget.setVisible(True)
            self.setMinimumWidth(180)
            self.setMaximumWidth(220)
        else:
            self.toggle_btn.setIcon(qta.icon("mdi.menu", color=palette.palette['text']))
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

    def set_palette_style(self):
        self.setStyleSheet(f"""
            #SidebarMenu {{
                background: {palette.palette['background']};
                border-right: 1.5px solid {palette.palette['border']};
            }}
            QToolButton {{
                font-weight: bold;
                font-size: 14px;
                padding: 6px 8px;
                border: none;
                background: {palette.palette['background']};
                text-align: left;
                color: {palette.palette['text']};
            }}
            QToolButton:checked {{
                background: {palette.palette['selection']};
            }}
            QPushButton {{
                text-align: left;
                padding: 6px 12px;
                border: none;
                background: transparent;
                border-radius: 0px;
                color: {palette.palette['text']};
            }}
            QPushButton:checked {{
                background: {palette.palette['primary']};
                font-weight: bold;
                color: {palette.palette['text']};
            }}
            QPushButton:hover {{
                background: {palette.palette['selection']};
            }}
            QLabel {{
                color: {palette.palette['text']};
            }}
            QFrame[frameShape="4"] {{
                color: {palette.palette['border']};
                background: {palette.palette['border']};
                min-height: 1px;
                max-height: 1px;
            }}
        """)

    def update_toggle_theme_btn_icon(self):
        # Cambia icono y texto según el modo actual
        if palette.palette is palette.light_palette:
            self.toggle_theme_btn.setIcon(qta.icon("mdi.weather-night", color=palette.palette['text']))
            self.toggle_theme_btn.setText("Modo oscuro")
            self.toggle_theme_btn.setToolTip("Cambiar a modo oscuro")
        else:
            self.toggle_theme_btn.setIcon(qta.icon("mdi.white-balance-sunny", color=palette.palette['text']))
            self.toggle_theme_btn.setText("Modo claro")
            self.toggle_theme_btn.setToolTip("Cambiar a modo claro")

    def toggle_palette(self):
        # Cambia la paleta global y emite señal
        if palette.palette is palette.light_palette:
            palette.palette = palette.dark_palette
        else:
            palette.palette = palette.light_palette
        self.update_palette()
        self.palette_toggled.emit()

    def update_palette(self):
        self.set_palette_style()
        # Actualiza los botones y labels si es necesario
        for btn in self.func_buttons.values():
            btn.setStyleSheet("")
        for btn in self.module_btns.values():
            btn.setStyleSheet("")
        for lbl in self.status_labels.values():
            lbl.setStyleSheet(f"color: {palette.palette['danger']}; font-size: 12px; margin-left: 6px;")
        self.menu_widget.setStyleSheet(f"background: {palette.palette['background']};")
        self.toggle_btn.setStyleSheet(f"border: none; background: {palette.palette['background']}; color: {palette.palette['text']};")
        # Actualiza los iconos con el color de la paleta
        for btn, icon_spec in self.icon_specs.items():
            if icon_spec and isinstance(btn, (QPushButton, QToolButton)):
                if icon_spec.startswith("mdi."):
                    btn.setIcon(get_icon(icon_spec, color=palette.palette['text']))
        # Actualiza el icono de hamburguesa según el estado
        if self.expanded:
            self.toggle_btn.setIcon(qta.icon("mdi.menu-open", color=palette.palette['text']))
        else:
            self.toggle_btn.setIcon(qta.icon("mdi.menu", color=palette.palette['text']))
        # Actualiza las líneas divisorias
        for sep in self.dividers:
           sep.setStyleSheet(f"color: {palette.palette['border']};")
        self.update()
        self.update_toggle_theme_btn_icon()  # <-- Asegura que el icono y texto se actualizan
        self.toggle_theme_btn.setStyleSheet(
            f"background: transparent; color: {palette.palette['text']}; font-size: 15px; border: none;"
        )

class NoTitleDockWidget(QDockWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitleBarWidget(QWidget(self))
        self.setStyleSheet("background: green;")
