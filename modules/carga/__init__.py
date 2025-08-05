from .ui.carga_ui import CargaWidget
from .ui.importar_ui import ImportarWidget
from .ui.validar_ui import ValidarWidget

MENU_COMPONENTS = [
    {"key": "Carga", "label": "Principal", "widget": CargaWidget},
    {"key": "Carga/Importar", "label": "Importar", "widget": ImportarWidget},
    {"key": "Carga/Validar", "label": "Validar", "widget": ValidarWidget},
]