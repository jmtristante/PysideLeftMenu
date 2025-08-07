from .ui.test_page import TestPage
from .ui.scope_editor_window import ScopeEditorWindow
from .ui.load_ddr_window import LoadDDRWindow

MENU_COMPONENTS = [
    {"key": "Extracción/test", "label": "Test fich", "widget": TestPage, "icon": "mdi.test-tube"},
    {"key": "Extracción/scope", "label": "Scope editor", "widget": ScopeEditorWindow, "icon": "mdi.pencil"},
    {"key": "Extracción/ddr", "label": "Load DDR", "widget": LoadDDRWindow, "icon": "mdi.cloud-upload"},
]