from .ui.test_page import MainScreen
from .ui.scope_editor_window import ScopeEditorWindow
from .ui.load_ddr_window import LoadDDRWindow

MENU_COMPONENTS = [
    {"key": "Extracción/test", "label": "Test fich", "widget": MainScreen},
    {"key": "Extracción/scope", "label": "Scope editor", "widget": ScopeEditorWindow},
    {"key": "Extracción/ddr", "label": "Load DDR", "widget": LoadDDRWindow},
]