import os
import yaml
from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QApplication, QComboBox,
    QTextEdit, QSpinBox, QCheckBox, QTabWidget, QScrollArea, QFrame, QInputDialog, QDialog, QSizePolicy,
    QGridLayout  # <-- Añadido aquí
)
from PySide6.QtCore import Qt
import sys

# Añade el import del CardFrame
from widgets.card_frame import CardFrame

class Scope:
    def __init__(self, scopes_dir, name):
        self.scopes_dir = scopes_dir
        self.name = name
        self.scope_dir = os.path.join(scopes_dir, name)
        self.metadata_path = os.path.join(self.scope_dir, "metadata.yaml")
        self.ddr_path = os.path.join(self.scope_dir, "ddr.yaml")
        self.metadata = {}
        self.ddr = {}

    def exists(self):
        return os.path.isdir(self.scope_dir)

    def load(self):
        # Carga ambos yaml si existen
        if os.path.isfile(self.metadata_path):
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                self.metadata = yaml.safe_load(f) or {}
        else:
            self.metadata = {}
        if os.path.isfile(self.ddr_path):
            with open(self.ddr_path, "r", encoding="utf-8") as f:
                self.ddr = yaml.safe_load(f) or {}
        else:
            self.ddr = {}

    def save(self, metadata_dict, ddr_dict):
        if not os.path.isdir(self.scope_dir):
            os.makedirs(self.scope_dir)
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            yaml.dump(metadata_dict, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
        with open(self.ddr_path, "w", encoding="utf-8") as f:
            yaml.dump(ddr_dict, f, allow_unicode=True, sort_keys=False, default_flow_style=False)

class GenericItemWidget(QWidget):
    """
    Widget genérico para mostrar un ítem con varios campos y un botón de eliminar.
    fields: lista de (nombre, tipo_widget, placeholder)
    data: dict con valores iniciales
    """
    def __init__(self, fields, data=None, remove_callback=None):
        super().__init__()
        self.setStyleSheet("QWidget { border: 1px solid #b0c4de; border-radius: 5px; background: #f6faff; }")
        self.fields = fields
        self.widgets = {}
        layout = QHBoxLayout(self)
        layout.setSpacing(8)
        for name, widget_type, placeholder in self.fields:
            if widget_type == QLineEdit:
                w = QLineEdit()
                w.setPlaceholderText(placeholder)
                w.setMinimumWidth(80)
                if data and name in data:
                    w.setText(str(data[name]))
            elif widget_type == QComboBox:
                w = QComboBox()
                w.addItems(placeholder)  # placeholder es lista de opciones
                if data and name in data:
                    idx = w.findText(str(data[name]))
                    if idx >= 0:
                        w.setCurrentIndex(idx)
            else:
                w = widget_type()
            self.widgets[name] = w
            layout.addWidget(w)
        self.remove_btn = QPushButton("✕")
        self.remove_btn.setFixedWidth(32)
        if remove_callback:
            self.remove_btn.clicked.connect(lambda: remove_callback(self))
        layout.addWidget(self.remove_btn)

    def get_data(self):
        result = {}
        for name, widget_type, _ in self.fields:
            w = self.widgets[name]
            if isinstance(w, QLineEdit):
                result[name] = w.text().strip()
            elif isinstance(w, QComboBox):
                result[name] = w.currentText().strip()
        return result

class SheetListWidget(QWidget):
    def __init__(self, sheets=None):
        super().__init__()
        self.setObjectName("SheetListWidget")
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(4)

        title = QLabel("Lista de Sheets")
        title.setStyleSheet("font-weight: bold; font-size: 15px; margin-bottom: 2px;")
        self.main_layout.addWidget(title, alignment=Qt.AlignLeft)

        subtitle = QLabel("Añade hojas a tu lista personalizada.")
        subtitle.setStyleSheet("color: #555; font-size: 11px;")
        self.main_layout.addWidget(subtitle, alignment=Qt.AlignLeft)

        # Input + botón añadir
        input_layout = QHBoxLayout()
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("Escribe un nuevo sheet...")
        input_layout.addWidget(self.input_edit)
        self.add_btn = QPushButton("+")
        self.add_btn.setFixedWidth(32)
        self.add_btn.clicked.connect(self.add_from_input)
        input_layout.addWidget(self.add_btn)
        self.main_layout.addLayout(input_layout)

        # Cuadro para los sheets añadidos (scrolleable)
        self.items_frame = QFrame()
        self.items_frame.setFrameShape(QFrame.StyledPanel)
        self.items_frame.setStyleSheet("QFrame { border: 1px solid #bbb; border-radius: 6px; background: #fafcff; }")
        self.items_layout = QVBoxLayout(self.items_frame)
        self.items_layout.setSpacing(6)
        self.items_layout.setContentsMargins(8, 8, 8, 8)
        self.items = []
        self.sheets = sheets or []
        for sheet in self.sheets:
            self.add_item(sheet)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setWidget(self.items_frame)
        self.scroll_area.setMinimumHeight(120)
        self.scroll_area.setMaximumHeight(220)
        self.main_layout.addWidget(self.scroll_area)

        # Línea separadora
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.main_layout.addWidget(line)

        # Total
        self.total_label = QLabel()
        self.total_label.setStyleSheet("color: #888; font-size: 11px;")
        self.main_layout.addWidget(self.total_label)
        self.update_total()

    def add_from_input(self):
        text = self.input_edit.text().strip()
        if text:
            self.add_item(text)
            self.input_edit.clear()
            self.update_total()

    def add_item(self, value=""):
        # Usar GenericItemWidget con un solo campo
        item = GenericItemWidget(
            fields=[("sheet", QLineEdit, "sheet")],
            data={"sheet": value},
            remove_callback=self.remove_item
        )
        item.widgets["sheet"].setReadOnly(True)
        self.items_layout.addWidget(item)
        self.items.append(item)
        self.update_total()

    def remove_item(self, item):
        self.items_layout.removeWidget(item)
        item.setParent(None)
        self.items.remove(item)
        self.update_total()

    def get_sheets(self):
        return [item.widgets["sheet"].text().strip() for item in self.items if item.widgets["sheet"].text().strip()]

    def set_sheets(self, sheets):
        for item in self.items:
            self.items_layout.removeWidget(item)
            item.setParent(None)
        self.items.clear()
        for sheet in sheets:
            self.add_item(sheet)
        self.update_total()

    def update_total(self):
        total = len(self.get_sheets())
        self.total_label.setText(f"Total de hojas: {total}")

# --- Similar para FormatListWidget ---
class FormatListWidget(QWidget):
    def __init__(self, formats=None):
        super().__init__()
        self.setObjectName("FormatListWidget")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(12, 12, 12, 12)
        self.layout.setSpacing(8)

        # Título
        title = QLabel("Lista de Formats")
        title.setStyleSheet("font-weight: bold; font-size: 15px;")
        self.layout.addWidget(title)

        subtitle = QLabel("Añade formatos a tu lista personalizada.")
        subtitle.setStyleSheet("color: #555; font-size: 11px;")
        self.layout.addWidget(subtitle)

        # Input de 4 campos + botón añadir
        input_layout = QHBoxLayout()
        self.input_pattern = QLineEdit()
        self.input_pattern.setPlaceholderText("pattern")
        self.input_pattern.setMinimumWidth(120)
        self.input_type = QComboBox()
        self.input_type.addItems(["VARCHAR", "INTEGER", "DECIMAL", "DATE"])
        self.input_type.setMinimumWidth(90)
        self.input_size = QLineEdit()
        self.input_size.setPlaceholderText("size")
        self.input_size.setMinimumWidth(60)
        self.input_precision = QLineEdit()
        self.input_precision.setPlaceholderText("precision (opcional)")
        self.input_precision.setMinimumWidth(90)
        input_layout.addWidget(self.input_pattern)
        input_layout.addWidget(self.input_type)
        input_layout.addWidget(self.input_size)
        input_layout.addWidget(self.input_precision)
        self.add_btn = QPushButton("+")
        self.add_btn.setFixedWidth(32)
        self.add_btn.clicked.connect(self.add_from_input)
        input_layout.addWidget(self.add_btn)
        self.layout.addLayout(input_layout)

        # Cuadro para los formatos añadidos (scrolleable)
        self.items_frame = QFrame()
        self.items_frame.setFrameShape(QFrame.StyledPanel)
        self.items_frame.setStyleSheet("QFrame { border: 1px solid #bbb; border-radius: 6px; background: #fafcff; }")
        self.items_layout = QVBoxLayout(self.items_frame)
        self.items_layout.setSpacing(6)
        self.items_layout.setContentsMargins(8, 8, 8, 8)
        self.items = []
        self.formats = formats or []
        for fmt in self.formats:
            self.add_item(fmt)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setWidget(self.items_frame)
        self.scroll_area.setMinimumHeight(120)
        self.scroll_area.setMaximumHeight(220)
        self.layout.addWidget(self.scroll_area)

        # Línea separadora
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(line)

        # Total
        self.total_label = QLabel()
        self.total_label.setStyleSheet("color: #888; font-size: 11px;")
        self.layout.addWidget(self.total_label)
        self.update_total()

        # Botón para probar todos los formatos
        self.collective_btn = QPushButton("Probar todos los formatos (get_type)")
        self.collective_btn.setToolTip("Probar todos los formatos sobre una cadena")
        self.collective_btn.clicked.connect(self.open_collective_test)
        self.layout.addWidget(self.collective_btn, alignment=Qt.AlignLeft)

    def add_from_input(self):
        pattern = self.input_pattern.text().strip()
        type_ = self.input_type.currentText().strip()
        size = self.input_size.text().strip()
        precision = self.input_precision.text().strip()
        if pattern:
            data = {"pattern": pattern, "type": type_, "size": size, "precision": precision}
            self.add_item(data)
            self.input_pattern.clear()
            self.input_size.clear()
            self.input_precision.clear()
            self.input_type.setCurrentIndex(0)
            self.update_total()

    def add_item(self, data=None):
        # Usar GenericItemWidget con los 4 campos
        fields = [
            ("pattern", QLineEdit, "pattern"),
            ("type", QComboBox, ["VARCHAR", "INTEGER", "DECIMAL", "DATE"]),
            ("size", QLineEdit, "size"),
            ("precision", QLineEdit, "precision (opcional)")
        ]
        item = GenericItemWidget(fields, data, remove_callback=self.remove_item)
        self.items_layout.addWidget(item)
        self.items.append(item)
        self.update_total()

    def remove_item(self, item):
        self.items_layout.removeWidget(item)
        item.setParent(None)
        self.items.remove(item)
        self.update_total()

    def get_formats(self):
        result = []
        for item in self.items:
            d = item.get_data()
            if d["pattern"]:
                # Solo incluir precision si no está vacío
                if not d["precision"]:
                    d.pop("precision")
                result.append(d)
        return result

    def set_formats(self, formats):
        for item in self.items:
            self.items_layout.removeWidget(item)
            item.setParent(None)
        self.items.clear()
        for fmt in formats:
            self.add_item(fmt)
        self.update_total()

    def update_total(self):
        total = len(self.get_formats())
        self.total_label.setText(f"Total de formatos: {total}")

    def open_collective_test(self):
        dlg = RegexCollectiveTestDialog(self.get_formats(), self)
        dlg.exec()

class RegexTestDialog(QDialog):
    """Ventana para probar una sola regex."""
    def __init__(self, pattern, test_value, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Probar Regex individual")
        layout = QVBoxLayout(self)
        self.pattern_edit = QLineEdit(pattern)
        self.pattern_edit.setPlaceholderText("Regex pattern")
        self.value_edit = QLineEdit(test_value)
        self.value_edit.setPlaceholderText("Valor a probar")
        self.result_label = QLabel("")
        self.result_label.setWordWrap(True)
        test_btn = QPushButton("Probar")
        test_btn.clicked.connect(self.run_test)
        layout.addWidget(QLabel("Pattern:"))
        layout.addWidget(self.pattern_edit)
        layout.addWidget(QLabel("Valor:"))
        layout.addWidget(self.value_edit)
        layout.addWidget(test_btn)
        layout.addWidget(self.result_label)
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        self.resize(400, 200)

    def run_test(self):
        import re
        pattern = self.pattern_edit.text()
        value = self.value_edit.text()
        try:
            match = re.match(pattern, value)
            if match:
                groups = match.groups()
                self.result_label.setText(f"<b>¡Coincide!</b><br>Grupos: {groups}")
            else:
                self.result_label.setText("<b>No coincide</b>")
        except Exception as e:
            self.result_label.setText(f"<b>Error:</b> {e}")

class RegexCollectiveTestDialog(QDialog):
    """Ventana para probar todas las regex (get_type) sobre una cadena."""
    def __init__(self, formats_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Probar todos los formatos (get_type)")
        layout = QVBoxLayout(self)
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("Introduce una cadena para get_type")
        self.result_label = QLabel("")
        self.result_label.setWordWrap(True)
        test_btn = QPushButton("Probar")
        test_btn.clicked.connect(lambda: self.run_gettype(formats_list))
        layout.addWidget(QLabel("Cadena a probar:"))
        layout.addWidget(self.input_edit)
        layout.addWidget(test_btn)
        layout.addWidget(self.result_label)
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        self.resize(400, 200)

    def run_gettype(self, formats_list):
        import re
        cadena = self.input_edit.text()
        formats = formats_list if formats_list is not None else []
        resultado = None
        for regla in formats:
            pattern = regla.get("pattern", "")
            match = re.match(pattern, cadena, flags=re.IGNORECASE)
            if match:
                resultado = {"type": regla.get("type", "")}
                for clave, valor in regla.items():
                    if clave in ("pattern", "type"):
                        continue
                    try:
                        resultado[clave] = re.sub(pattern, valor, cadena, flags=re.IGNORECASE)
                    except Exception:
                        resultado[clave] = valor
                break
        if resultado:
            self.result_label.setText(f"<b>Resultado get_type:</b><br>{resultado}")
        else:
            self.result_label.setText("<b>No coincide ningún patrón</b>")

class FormatItemWidget(QWidget):
    def __init__(self, data=None, formats_list_getter=None):
        super().__init__()
        # Añade borde para diferenciar el item
        self.setStyleSheet("QWidget { border: 1px solid #b0c4de; border-radius: 5px; background: #f6faff; }")
        layout = QHBoxLayout(self)
        layout.setSpacing(8)
        self.pattern_edit = QLineEdit()
        self.pattern_edit.setPlaceholderText("pattern")
        self.pattern_edit.setMinimumWidth(120)
        # Elimina setStyleSheet
        self.type_combo = QComboBox()
        self.type_combo.addItems(["VARCHAR", "INTEGER", "DECIMAL", "DATE"])
        self.type_combo.setMinimumWidth(90)
        # Elimina setStyleSheet
        self.size_edit = QLineEdit()
        self.size_edit.setPlaceholderText("size")
        self.size_edit.setMinimumWidth(60)
        # Elimina setStyleSheet
        self.precision_edit = QLineEdit()
        self.precision_edit.setPlaceholderText("precision (opcional)")
        self.precision_edit.setMinimumWidth(90)
        # Elimina setStyleSheet
        self.test_btn = QPushButton("🔍")
        self.test_btn.setToolTip("Probar regex individual")
        self.test_btn.setFixedWidth(32)
        # Elimina setStyleSheet
        self.formats_list_getter = formats_list_getter
        self.test_btn.clicked.connect(self.open_regex_test)
        layout.addWidget(QLabel("pattern:"))
        layout.addWidget(self.pattern_edit)
        layout.addWidget(self.test_btn)
        layout.addWidget(QLabel("type:"))
        layout.addWidget(self.type_combo)
        layout.addWidget(QLabel("size:"))
        layout.addWidget(self.size_edit)
        layout.addWidget(QLabel("precision:"))
        layout.addWidget(self.precision_edit)
        self.remove_btn = QPushButton("✕")
        self.remove_btn.setFixedWidth(32)
        # Elimina setStyleSheet
        layout.addWidget(self.remove_btn)
        if data:
            self.pattern_edit.setText(str(data.get("pattern", "")))
            type_val = str(data.get("type", ""))
            idx = self.type_combo.findText(type_val)
            if idx >= 0:
                self.type_combo.setCurrentIndex(idx)
            elif type_val:
                self.type_combo.addItem(type_val)
                self.type_combo.setCurrentIndex(self.type_combo.count() - 1)
            self.size_edit.setText(str(data.get("size", "")))
            self.precision_edit.setText(str(data.get("precision", "")))

    def open_regex_test(self):
        dlg = RegexTestDialog(self.pattern_edit.text(), "", self)
        dlg.exec()

    def get_data(self):
        d = {
            "pattern": self.pattern_edit.text().strip(),
            "type": self.type_combo.currentText().strip(),
            "size": self.size_edit.text().strip()
        }
        if self.precision_edit.text().strip():
            d["precision"] = self.precision_edit.text().strip()
        return d

class ExcelColumnsWidget(QWidget):
    """
    Widget para editar las columnas de Excel (spinboxes), con título incluido.
    """
    def __init__(self, values=None):
        super().__init__()
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(4)
        title = QLabel("Columnas de Excel")
        title.setStyleSheet("font-weight: bold; font-size: 15px; margin-bottom: 2px;")
        main_layout.addWidget(title, alignment=Qt.AlignLeft)
        layout = QVBoxLayout()
        layout.setSpacing(6)
        self.fields = [
            ("first_line", 3),
            ("field_column", 3),
            ("format_column", 6),
            ("calculation_column", 9),
            ("dimension_column", 10)
        ]
        self.spinboxes = {}
        for key, default in self.fields:
            hlayout = QHBoxLayout()
            hlayout.setSpacing(8)
            lbl = QLabel(key + ":")
            lbl.setMinimumWidth(110)
            sb = QSpinBox()
            sb.setMinimum(0)
            sb.setMaximum(100)
            sb.setValue(values.get(key, default) if values else default)
            hlayout.addWidget(lbl)
            hlayout.addWidget(sb)
            layout.addLayout(hlayout)
            self.spinboxes[key] = sb
        layout.addStretch(1)
        main_layout.addLayout(layout)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

    def set_values(self, values):
        for k, sb in self.spinboxes.items():
            sb.setValue(values.get(k, 0))

    def get_values(self):
        return {k: sb.value() for k, sb in self.spinboxes.items()}

    def clear(self):
        for k, sb in self.spinboxes.items():
            sb.setValue(0)

class ScopeEditorWindow(CardFrame):
    def __init__(self):
        super().__init__(title="Extracción/scope")
        self.setMinimumWidth(500)
        MODULE_BASE = 'modules/extraccion'
        self.SCOPES_DIR = os.path.join(MODULE_BASE, "data/scopes")

        card_layout = self.layout()  # Usa el layout de contenido de CardFrame

        # Scope selector y eliminar
        scope_row = QHBoxLayout()
        scope_row.setSpacing(12)
        scope_label = QLabel("Scope:")
        scope_label.setMinimumWidth(60)
        scope_label.setStyleSheet("font-size: 15px;")
        self.scope_combo = QComboBox()
        self.scope_combo.addItems(self.get_scopes() + ["[Nuevo Scope...]"])
        self.scope_combo.setEditable(False)
        self.scope_combo.setPlaceholderText("Selecciona o crea un scope")
        self.scope_combo.setMinimumWidth(220)
        self.delete_btn = QPushButton("Eliminar Scope")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background: #ff4d4f;
                color: #fff;
                border-radius: 8px;
                font-weight: bold;
                padding: 6px 18px;
            }
            QPushButton:hover {
                background: #ff7875;
            }
        """)
        scope_row.addWidget(scope_label)
        scope_row.addWidget(self.scope_combo)
        scope_row.addStretch()
        scope_row.addWidget(self.delete_btn)
        card_layout.addLayout(scope_row)

        # Tabs con fondo blanco y bordes redondeados
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                background: #f3f5f8;
                border: 1px solid #e0e0e0;
                border-bottom: none;
                border-radius: 8px 8px 0 0;
                min-width: 120px;
                min-height: 32px;
                font-weight: bold;
                margin-right: 2px;
                padding: 6px 18px;
            }
            QTabBar::tab:selected {
                background: #fff;
                color: #222;
                border-bottom: 2px solid #fff;
            }
            QTabBar::tab:!selected {
                color: #888;
            }
        """)

        # --- METADATA.YAML TAB ---
        self.meta_tab = QFrame()
        self.meta_tab.setStyleSheet("""
            QFrame {
                background: #fff;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)
        meta_layout = QGridLayout(self.meta_tab)
        meta_layout.setContentsMargins(32, 32, 32, 32)
        meta_layout.setHorizontalSpacing(24)
        meta_layout.setVerticalSpacing(18)
        self.meta_fields = {}

        # Primera columna
        meta_layout.addWidget(QLabel("Separator:"), 0, 0)
        sep_edit = QLineEdit()
        meta_layout.addWidget(sep_edit, 0, 1)
        self.meta_fields["Separator"] = sep_edit

        meta_layout.addWidget(QLabel("Extension:"), 1, 0)
        ext_edit = QLineEdit()
        meta_layout.addWidget(ext_edit, 1, 1)
        self.meta_fields["Extension"] = ext_edit

        meta_layout.addWidget(QLabel("Encoding:"), 2, 0)
        enc_edit = QLineEdit()
        meta_layout.addWidget(enc_edit, 2, 1)
        self.meta_fields["Encoding"] = enc_edit

        # Segunda columna
        header_chk = QCheckBox("Header")
        meta_layout.addWidget(header_chk, 0, 2)
        self.meta_fields["Header"] = header_chk

        nulable_chk = QCheckBox("Nulable")
        meta_layout.addWidget(nulable_chk, 1, 2)
        self.meta_fields["Nulable"] = nulable_chk

        meta_layout.addWidget(QLabel("Endline:"), 2, 2)
        endline_edit = QLineEdit()
        meta_layout.addWidget(endline_edit, 2, 3)
        self.meta_fields["Endline"] = endline_edit

        self.tabs.addTab(self.meta_tab, "metadata.yaml")

        # --- DDR.YAML TAB ---
        self.ddr_tab = QWidget()
        ddr_layout = QVBoxLayout(self.ddr_tab)
        ddr_layout.setContentsMargins(12, 12, 12, 12)
        ddr_layout.setSpacing(24)
        self.ddr_fields = {}

        # --- Primera fila: columnas de excel y sheets ---
        first_row_layout = QHBoxLayout()
        first_row_layout.setSpacing(24)

        # Columna izquierda: ExcelColumnsWidget (con título propio)
        self.excel_columns_widget = ExcelColumnsWidget()
        self.excel_columns_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        first_row_layout.addWidget(self.excel_columns_widget, stretch=1)

        self.ddr_fields["excel_columns"] = self.excel_columns_widget

        # Columna derecha: SheetListWidget (con título propio)
        self.sheets_widget = SheetListWidget()
        self.sheets_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        first_row_layout.addWidget(self.sheets_widget, stretch=2)

        self.ddr_fields["sheets"] = self.sheets_widget

        ddr_layout.addLayout(first_row_layout)

        # --- Segunda fila: formats ---
        self.formats_widget = FormatListWidget()
        ddr_layout.addWidget(self.formats_widget)
        self.ddr_fields["formats"] = self.formats_widget

        self.tabs.addTab(self.ddr_tab, "ddr.yaml")

        card_layout.addWidget(self.tabs)

        # Guardar y estado
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.save_btn = QPushButton("Guardar Scope")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: #1677ff;
                color: #fff;
                border-radius: 8px;
                font-weight: bold;
                padding: 8px 28px;
            }
            QPushButton:hover {
                background: #4096ff;
            }
        """)
        btn_row.addWidget(self.save_btn)
        card_layout.addLayout(btn_row)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #888; font-size: 14px; margin-top: 8px;")
        card_layout.addWidget(self.status_label, alignment=Qt.AlignLeft)

        # Conexiones
        self.save_btn.clicked.connect(self.save_scope)
        self.scope_combo.currentTextChanged.connect(self.on_scope_selected)
        self.delete_btn.clicked.connect(self.delete_scope)

        # Carga el scope inicial si existe
        if self.scope_combo.count() > 0 and self.scope_combo.currentText() != "[Nuevo Scope...]":
            self.load_scope(self.scope_combo.currentText())

    def get_scopes(self):
        if not os.path.isdir(self.SCOPES_DIR):
            return []
        return [name for name in os.listdir(self.SCOPES_DIR) if os.path.isdir(os.path.join(self.SCOPES_DIR, name))]

    def on_scope_selected(self, scope_name):
        if scope_name == "[Nuevo Scope...]":
            new_scope, ok = QInputDialog.getText(self, "Nuevo Scope", "Introduce el nombre del nuevo scope:")
            if ok and new_scope.strip():
                new_scope = new_scope.strip()
                # Añade el nuevo scope y selecciónalo
                if new_scope not in [self.scope_combo.itemText(i) for i in range(self.scope_combo.count())]:
                    self.scope_combo.insertItem(self.scope_combo.count() - 1, new_scope)
                self.scope_combo.setCurrentText(new_scope)
                # Limpia los campos
                self.clear_fields()
                self.status_label.setText(f"Nuevo scope '{new_scope}' creado. Rellena los datos y guarda.")
            else:
                # Si cancela, vuelve al anterior
                prev_scope = self.scope_combo.itemText(0) if self.scope_combo.count() > 1 else ""
                self.scope_combo.setCurrentText(prev_scope)
        else:
            self.load_scope(scope_name)

    def clear_fields(self):
        for key, widget in self.meta_fields.items():
            if isinstance(widget, QLineEdit):
                widget.setText("")
            elif isinstance(widget, QCheckBox):
                widget.setChecked(False)
        for key, widget in self.ddr_fields.items():
            if key == "excel_columns":
                widget.clear()
            elif key == "sheets":
                widget.set_sheets([])
            elif key == "formats":
                widget.set_formats([])

    def load_scope(self, scope_name):
        if not scope_name or scope_name == "[Nuevo Scope...]":
            self.clear_fields()
            return
        scope = Scope(self.SCOPES_DIR, scope_name)
        scope.load()
        # metadata.yaml
        meta = scope.metadata
        for key, widget in self.meta_fields.items():
            if key in meta:
                if isinstance(widget, QLineEdit):
                    widget.setText(str(meta[key]))
                elif isinstance(widget, QCheckBox):
                    widget.setChecked(bool(meta[key]))
            else:
                if isinstance(widget, QLineEdit):
                    widget.setText("")
                elif isinstance(widget, QCheckBox):
                    widget.setChecked(False)
        # ddr.yaml
        ddr = scope.ddr
        for key, widget in self.ddr_fields.items():
            if key == "excel_columns":
                widget.set_values({k: ddr.get(k, 0) for k in widget.spinboxes})
            elif key == "sheets":
                widget.set_sheets(ddr.get("sheets", []))
            elif key == "formats":
                widget.set_formats(ddr.get("formats", []))
        self.status_label.setText(f"Scope '{scope_name}' cargado.")

    def save_scope(self):
        scope_name = self.scope_combo.currentText().strip()
        if not scope_name or scope_name == "[Nuevo Scope...]":
            QMessageBox.warning(self, "Campos incompletos", "Selecciona o crea un scope válido.")
            return
        scope = Scope(self.SCOPES_DIR, scope_name)
        # metadata.yaml
        meta_dict = {}
        for key, widget in self.meta_fields.items():
            if isinstance(widget, QLineEdit):
                meta_dict[key] = widget.text()
            elif isinstance(widget, QCheckBox):
                meta_dict[key] = widget.isChecked()
        # ddr.yaml
        ddr_dict = {}
        # Excel columns
        if "excel_columns" in self.ddr_fields:
            ddr_dict.update(self.ddr_fields["excel_columns"].get_values())
        # Sheets
        if "sheets" in self.ddr_fields:
            ddr_dict["sheets"] = self.ddr_fields["sheets"].get_sheets()
        # Formats
        if "formats" in self.ddr_fields:
            ddr_dict["formats"] = self.ddr_fields["formats"].get_formats()
        try:
            scope.save(meta_dict, ddr_dict)
            self.status_label.setText(f"Scope '{scope_name}' guardado correctamente.")
            # Añade el scope si no está en el combo
            if scope_name not in [self.scope_combo.itemText(i) for i in range(self.scope_combo.count())]:
                self.scope_combo.insertItem(self.scope_combo.count() - 1, scope_name)
                self.scope_combo.setCurrentText(scope_name)
        except Exception as e:
            self.status_label.setText("Error al guardar.")
            QMessageBox.critical(self, "Error", f"Ocurrió un error:\n{str(e)}")

    def delete_scope(self):
        scope_name = self.scope_combo.currentText().strip()
        if not scope_name or scope_name == "[Nuevo Scope...]":
            QMessageBox.warning(self, "Eliminar Scope", "Selecciona un scope válido para eliminar.")
            return
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Seguro que quieres eliminar el scope '{scope_name}'?\nEsta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            import shutil
            scope_dir = os.path.join(self.SCOPES_DIR, scope_name)
            try:
                if os.path.isdir(scope_dir):
                    shutil.rmtree(scope_dir)
                # Elimina del combo y selecciona el primero
                idx = self.scope_combo.findText(scope_name)
                if idx >= 0:
                    self.scope_combo.removeItem(idx)
                # Selecciona el primer scope (índice 0)
                if self.scope_combo.count() > 0:
                    self.scope_combo.setCurrentIndex(0)
                self.clear_fields()
                self.status_label.setText(f"Scope '{scope_name}' eliminado.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar el scope:\n{str(e)}")
                # Selecciona el primer scope (índice 0)
                if self.scope_combo.count() > 0:
                    self.scope_combo.setCurrentIndex(0)
                self.clear_fields()
                self.status_label.setText(f"Scope '{scope_name}' eliminado.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar el scope:\n{str(e)}")
