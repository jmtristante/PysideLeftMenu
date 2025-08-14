import sqlite3
import pandas as pd
from PySide6.QtCore import Qt, QThread, Signal, QObject
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, \
    QTableWidgetItem, QProgressBar, QWidget
import os
from widgets.inputs.danger_button import DangerButton
from widgets.inputs.labeled_lineedit import LabeledLineEdit
from widgets.inputs.primary_button import PrimaryButton
from widgets.inputs.secondary_button import SecondaryButton
from widgets.results_table_widget import ResultsTableWidget

MODULE_BASE = os.path.dirname(os.path.dirname(__file__))


class FileLoaderWorker(QObject):
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, extractor_file, sql_query, page_start, page_size):
        super().__init__()
        self.extractor_file = extractor_file
        self.sql_query = sql_query
        self.page_start = page_start
        self.page_size = page_size

    def run(self):
        try:
            self.extractor_file.loader._ensure_db_polars(self.extractor_file)
            db_path = self.extractor_file.loader._db_path
            conn = sqlite3.connect(db_path)
            # Si no hay consulta, muestra todo paginado
            if not self.sql_query:
                query = f"SELECT * FROM data LIMIT {self.page_size} OFFSET {self.page_start}"
            else:
                # Si la consulta ya tiene LIMIT/OFFSET, no lo añadimos
                q = self.sql_query.lower()
                if "limit" in q or "offset" in q:
                    query = self.sql_query
                else:
                    query = f"{self.sql_query} LIMIT {self.page_size} OFFSET {self.page_start}"
            df = pd.read_sql_query(query, conn)
            conn.close()
            df = df.astype(str)
            df.columns = [str(x).upper().strip() for x in df.columns]
            self.finished.emit(df)
        except Exception as e:
            self.error.emit(str(e))


class FileViewerWidget(QWidget):
    PAGE_SIZE = 1000  # Número de filas por página

    def __init__(self, extractor_file, on_close=None, parent=None):
        super().__init__(parent)
        print("Inicializando visor de archivos...")
        self.extractor_file = extractor_file
        self.file_content = None
        self.current_page = 0
        self.total_rows = 0
        self.sql_query = ""
        self.filtered_df = None
        self.on_close = on_close

        layout = QVBoxLayout(self)

        # self.loading_label = QLabel("Cargando fichero...")
        # self.loading_label.setAlignment(Qt.AlignCenter)
        # self.loading_label.setVisible(True)
        # layout.addWidget(self.loading_label)

        # self.progress_bar = QProgressBar(self)
        # self.progress_bar.setRange(0, 0)
        # self.progress_bar.setVisible(True)
        # layout.addWidget(self.progress_bar)

        query_layout = QHBoxLayout()
        self.sql_edit = LabeledLineEdit(placeholder="Consulta SQL:")
        query_layout.addWidget(self.sql_edit)
        apply_btn = PrimaryButton("Ejecutar")
        apply_btn.clicked.connect(self.apply_sql_query)
        query_layout.addWidget(apply_btn)
        layout.addLayout(query_layout)

        self.guide_link = QLabel('<a href="#">Guía de filtros SQL</a>')
        self.guide_link.setTextFormat(Qt.RichText)
        self.guide_link.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.guide_link.setOpenExternalLinks(False)
        self.guide_link.setStyleSheet("color: #1976d2; font-weight: bold;")
        self.guide_link.linkActivated.connect(self.show_filter_guide)
        layout.addWidget(self.guide_link)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red; font-weight: bold;")
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)

        self.table = ResultsTableWidget(self)
        layout.addWidget(self.table)

        pag_layout = QHBoxLayout()
        self.prev_btn = SecondaryButton("Anterior")
        self.prev_btn.clicked.connect(self.prev_page)
        pag_layout.addWidget(self.prev_btn)
        self.page_label = QLabel()
        pag_layout.addWidget(self.page_label)
        self.next_btn = SecondaryButton("Siguiente")
        self.next_btn.clicked.connect(self.next_page)
        pag_layout.addWidget(self.next_btn)
        layout.addLayout(pag_layout)

        close_btn = DangerButton("Cerrar")
        close_btn.clicked.connect(self.handle_close)
        layout.addWidget(close_btn)

        # self.resize(900, 600)
        self.start_loading_threaded()

    def handle_close(self):
        print("Cerrando visor de archivos...")
        if self.on_close:
            self.on_close()
        # Si está en un QStackedWidget, puede ocultarse/eliminarse desde fuera

    def start_loading_threaded(self):
        # self.loading_label.setVisible(True)
        # self.progress_bar.setVisible(True)
        self.set_widgets_enabled(False)
        self.thread = QThread()
        self.worker = FileLoaderWorker(self.extractor_file, self.sql_query, self.current_page * self.PAGE_SIZE, self.PAGE_SIZE)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_loaded)
        self.worker.error.connect(self.on_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def set_widgets_enabled(self, enabled):
        for widget in [self.sql_edit, self.table,
                       self.prev_btn, self.next_btn, self.page_label,
                       self.guide_link, self.error_label]:
            widget.setEnabled(enabled)

    def getTotalRows(self):
        # Asegura que la base de datos esté creada antes de conectar
        #self.extractor_file.loader._ensure_db_polars(self.extractor_file)
        db_path = self.extractor_file.loader._db_path
        if self.total_rows == 0:
            conn = sqlite3.connect(db_path)
            if not self.sql_query:
                count_query = "SELECT COUNT(*) FROM data"
            else:
                count_query = f"SELECT COUNT(*) FROM ({self.sql_query})"
            try:
                self.total_rows = conn.execute(count_query).fetchone()[0]
            except Exception:
                self.total_rows = 0
            conn.close()

    def run_page_query(self):
        self.getTotalRows()
        self.start_loading_threaded()

    def on_loaded(self, df):
        self.file_content = df
        # self.loading_label.setVisible(False)
        # self.progress_bar.setVisible(False)
        self.set_widgets_enabled(True)
        # Si la página está vacía pero hay más registros, recalcula el total y muestra la página anterior
        if df is not None and df.empty and self.current_page > 0:
            self.current_page -= 1
            self.run_page_query()
            return
        self.load_data()

    def on_error(self, msg):
        # self.loading_label.setVisible(False)
        # self.progress_bar.setVisible(False)
        self.error_label.setText(f"Error al cargar: {msg}")
        self.error_label.setVisible(True)
        self.set_widgets_enabled(True)
        # Limpia el hilo y el worker para evitar problemas en siguientes queries
        # Solo intenta cerrar el hilo si sigue activo y no ha sido eliminado
        try:
            if hasattr(self, 'thread') and self.thread is not None and self.thread.isRunning():
                self.thread.quit()
                self.thread.wait()
        except RuntimeError:
            pass
        self.thread = None
        self.worker = None

    def apply_sql_query(self):
        self.sql_query = self.sql_edit.text().strip()
        self.error_label.setVisible(False)
        self.current_page = 0
        self.total_rows = 0  # recalcula el total
        #self.loading_label.setText("Ejecutando consulta...")
        # self.loading_label.setVisible(True)
        # self.progress_bar.setVisible(True)
        self.set_widgets_enabled(False)
        # Limpia el hilo anterior antes de lanzar uno nuevo
        try:
            if hasattr(self, 'thread') and self.thread is not None and self.thread.isRunning():
                self.thread.quit()
                self.thread.wait()
        except RuntimeError:
            pass
        self.thread = None
        self.worker = None
        self.run_page_query()

    def show_filter_guide(self, *args):
        dlg = QDialog(self)
        dlg.setWindowTitle("Guía de filtros SQL")
        layout = QVBoxLayout(dlg)
        guide_label = QLabel()
        guide_label.setTextFormat(Qt.RichText)
        guide_label.setText("""
        <h2>Guía de consultas SQL</h2>
        <ul>
        <li><b>Seleccionar columnas:</b><br>
            <code>SELECT nombre, edad FROM data</code>
        </li>
        <li><b>Filtrar por condición:</b><br>
            <code>SELECT * FROM data WHERE edad &lt; 18</code>
        </li>
        <li><b>Filtrar por texto:</b><br>
            <code>SELECT * FROM data WHERE nombre = 'Ana'</code>
        </li>
        <li><b>Filtrar por múltiples condiciones:</b><br>
            <code>SELECT * FROM data WHERE edad &gt;= 18 AND ciudad = 'Madrid'</code>
        </li>
        <li><b>Filtrar por valores nulos:</b><br>
            <code>SELECT * FROM data WHERE salario IS NULL</code>
        </li>
        <li><b>Filtrar por valores distintos:</b><br>
            <code>SELECT * FROM data WHERE nombre != 'Pedro'</code>
        </li>
        <li><b>Filtrar por pertenencia a una lista:</b><br>
            <code>SELECT * FROM data WHERE nombre IN ('Ana', 'Luis')</code>
        </li>
        <li><b>Filtrar por valores entre dos números:</b><br>
            <code>SELECT * FROM data WHERE edad BETWEEN 18 AND 65</code>
        </li>
        <li><b>Ordenar resultados:</b><br>
            <code>SELECT * FROM data ORDER BY edad DESC</code>
        </li>
        </ul>
        <p><b>Notas:</b><br>
        La tabla principal se llama <code>data</code>.<br>
        Puedes usar cualquier consulta SQL válida de SQLite.<br>
        </p>
        """)
        guide_label.setWordWrap(True)
        layout.addWidget(guide_label)
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(dlg.close)
        layout.addWidget(close_btn)
        dlg.resize(700, 600)
        dlg.show()

    def load_data(self):
        df = self.file_content
        if df is None or df.empty:
            self.table.setModel(None)
            self.page_label.setText("Sin datos")
            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(False)
            return

        self.getTotalRows()

        total_pages = ((self.total_rows - 1) // self.PAGE_SIZE) + 1 if self.total_rows else 1

        # Crea un modelo temporal para mostrar el DataFrame en ResultsTableWidget
        from PySide6.QtCore import QAbstractTableModel, QModelIndex

        class PandasTableModel(QAbstractTableModel):
            def __init__(self, df, parent=None):
                super().__init__(parent)
                self._df = df

            def rowCount(self, parent=QModelIndex()):
                return len(self._df)

            def columnCount(self, parent=QModelIndex()):
                return len(self._df.columns)

            def data(self, index, role=Qt.DisplayRole):
                if not index.isValid():
                    return None
                if role == Qt.DisplayRole:
                    value = self._df.iloc[index.row(), index.column()]
                    return str(value)
                return None

            def headerData(self, section, orientation, role=Qt.DisplayRole):
                if role == Qt.DisplayRole and orientation == Qt.Horizontal:
                    return str(self._df.columns[section])
                return None

        model = PandasTableModel(df)
        self.table.setModel(model)

        self.page_label.setText(f"Página {self.current_page + 1} / {total_pages}")
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(self.current_page < (total_pages - 1))

    def next_page(self):
        if (self.current_page + 1) * self.PAGE_SIZE < self.total_rows:
            self.current_page += 1
            self.run_page_query()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.run_page_query()

