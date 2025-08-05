import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTreeView,
    QVBoxLayout, QWidget, QPushButton, QFileDialog, QMessageBox, QDialog
)
from PySide6.QtGui import QStandardItemModel, QStandardItem
import pandas as pd

MAX_ERRORES_POR_TIPO = 10

def obtener_errores_de_ejemplo():
    return {
        'Nombre': {
            'supera los 10 caracteres': [(i, f'NombreLargo{i}') for i in range(1, 1001)],
            'no cumple regex': [(i, '???') for i in range(1, 6)],
        },
        'Edad': {
            'valores no numéricos': [(i, 'texto') for i in range(1, 51)],
        }
    }

def cargar_errores_en_treeview(tree_view: QTreeView, errores: dict):
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels(["Errores de validación"])

    for campo, tipos_error in errores.items():
        total_errores_campo = sum(len(errs) for errs in tipos_error.values())
        item_campo = QStandardItem(f"🧾 Campo: {campo} ({total_errores_campo})")

        for tipo_error, errores_linea in tipos_error.items():
            total_errores_tipo = len(errores_linea)
            item_error = QStandardItem(f"⚠️ {tipo_error} ({total_errores_tipo})")

            errores_mostrados = errores_linea[:MAX_ERRORES_POR_TIPO]
            for linea, valor in errores_mostrados:
                item_detalle = QStandardItem(f"Línea {linea}: {valor}")
                item_error.appendRow(item_detalle)

            if total_errores_tipo > MAX_ERRORES_POR_TIPO:
                item_extra = QStandardItem(f"… y {total_errores_tipo - MAX_ERRORES_POR_TIPO} más")
                item_extra.setEnabled(False)
                item_error.appendRow(item_extra)

            item_campo.appendRow(item_error)

        model.appendRow(item_campo)

    tree_view.setModel(model)
    # Expande nivel 1 (campo) y nivel 2 (tipo_error)
    for i in range(model.rowCount()):
        index_campo = model.index(i, 0)
        tree_view.setExpanded(index_campo, True)
        for j in range(model.item(i).rowCount()):
            index_tipo = model.index(j, 0, index_campo)
            tree_view.setExpanded(index_tipo, True)
    # No expandimos los hijos de tipo_error (nivel 3)

def tree_to_list(model: QStandardItemModel):
    # Recorremos el modelo y extraemos filas para Excel: campo, tipo error, linea, valor
    datos = []
    for i in range(model.rowCount()):
        item_campo = model.item(i)
        campo_text = item_campo.text()
        # Extraemos solo el nombre real (sin emoji y conteo)
        campo = campo_text.split(':')[1].split('(')[0].strip()

        for j in range(item_campo.rowCount()):
            item_error = item_campo.child(j)
            tipo_text = item_error.text()
            tipo_error = tipo_text.split('⚠️')[1].split('(')[0].strip()

            for k in range(item_error.rowCount()):
                item_detalle = item_error.child(k)
                detalle_text = item_detalle.text()
                if detalle_text.startswith("… y"):
                    continue  # No incluimos línea resumen

                # detalle_text esperado: "Línea N: valor"
                if detalle_text.startswith("Línea "):
                    parts = detalle_text.split(':', 1)
                    linea = parts[0].replace("Línea", "").strip()
                    valor = parts[1].strip()
                    datos.append({
                        "Campo": campo,
                        "Tipo de error": tipo_error,
                        "Línea": linea,
                        "Valor": valor
                    })
    return datos

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeView, QPushButton, QFileDialog, QMessageBox
)
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt
import pandas as pd

class ErrorViewerWidget(QWidget):
    def __init__(self, errores, max_n3=100, parent=None):
        super().__init__(parent)
        self.errores = errores
        self.max_n3 = max_n3

        self.setWindowTitle("Errores detectados")
        self.resize(800, 600)

        layout = QVBoxLayout(self)
        self.tree_view = QTreeView(self)
        layout.addWidget(self.tree_view)

        self.export_button = QPushButton("Exportar a Excel", self)
        self.export_button.clicked.connect(self.exportar_a_excel)
        layout.addWidget(self.export_button)

        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Errores"])
        self.tree_view.setModel(self.model)

        self._cargar_datos()

    def _cargar_datos(self):
        for campo, errores_por_tipo in self.errores.items():
            item_campo = QStandardItem(f"{campo} ({sum(len(v) for v in errores_por_tipo.values())})")
            for tipo_error, detalles in errores_por_tipo.items():
                item_error = QStandardItem(f"{tipo_error} ({len(detalles)})")
                for i, detalle in enumerate(detalles):
                    if i >= self.max_n3:
                        item_error.appendRow(QStandardItem("... (más errores no mostrados)"))
                        break
                    item_detalle = QStandardItem(f"Línea {detalle[0]}: {detalle[1]}")
                    item_error.appendRow(item_detalle)
                item_campo.appendRow(item_error)
            self.model.appendRow(item_campo)
        # Elimina el expandAll para que nada se expanda por defecto
        # self.tree_view.expandAll()

    def exportar_a_excel(self):
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar como Excel", "", "Excel Files (*.xlsx)")
        if not ruta:
            return

        rows = []
        for campo, errores_por_tipo in self.errores.items():
            for tipo_error, detalles in errores_por_tipo.items():
                for linea, valor in detalles[:self.max_n3]:
                    rows.append({
                        "Campo": campo,
                        "Tipo de error": tipo_error,
                        "Línea": linea,
                        "Valor": valor
                    })

        df = pd.DataFrame(rows)
        try:
            df.to_excel(ruta, index=False)
            QMessageBox.information(self, "Exportación", "Errores exportados correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo exportar: {e}")


class ErrorViewerDialog(QDialog):
    def __init__(self, errores, max_n3=100, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Errores detectados")
        self.resize(800, 600)

        layout = QVBoxLayout(self)
        self.error_widget = ErrorViewerWidget(errores, max_n3=max_n3)
        layout.addWidget(self.error_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Simulación de errores para prueba
    errores_simulados = {
        "Nombre": {
            "supera tamaño": [(2, "JuanCarlos"), (10, "MaríaIsabel")],
            "caracteres no válidos": [(5, "1234")]
        },
        "Edad": {
            "no es numérico": [(3, "veinte")],
            "supera dígitos": [(8, "123456")]
        }
    }

    ventana = QMainWindow()
    widget = ErrorViewerWidget(errores_simulados)
    ventana.setCentralWidget(widget)
    ventana.setWindowTitle("Visor de errores")
    ventana.resize(900, 600)
    ventana.show()

    sys.exit(app.exec())
