import os
import sys
#import threading

MODULE_BASE = os.path.dirname(os.path.dirname(__file__))

from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex, Signal
from PySide6.QtCore import QThreadPool, QRunnable, QObject, Slot, QSortFilterProxyModel
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QHBoxLayout, QHeaderView,
    QLineEdit, QLabel
)
from PySide6.QtWidgets import QProgressBar
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QComboBox,
    QFileDialog, QPushButton, QTableView, QDialog, QTextEdit, QMenu
)


from modules.extraccion.src.FileViewer import FileViewerDialog
from modules.extraccion.ui.error_page import ErrorViewerDialog
from modules.extraccion.src.tests import TestExtractor
from modules.extraccion.src.tests.test_base import ExtractorFile
from modules.extraccion.src.tests import get_all_tests


class TestTableModel(QAbstractTableModel):
    def __init__(self, files, tests, parent=None):
        super().__init__(parent)
        self.files = files  # ["DV1", "DV2, ..."]
        self.test_classes = get_all_tests()
        # self.test_names = ["formato", "registros", "claves"]
        self.test_names = [cls.name for cls in self.test_classes]
        self.test_objects = tests  # [[Test1, Test2, Test3], [Test1, ...], ...]

    def rowCount(self, parent=QModelIndex()):
        return len(self.files)

    def columnCount(self, parent=QModelIndex()):
        return 1 + len(self.test_names)  # 1 para el nombre del fichero

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        row, col = index.row(), index.column()
        if role == Qt.DisplayRole:
            if col == 0:
                return self.files[row]
            else:
                return self.test_objects[row][col - 1].status
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if section == 0:
                return "Fichero"
            else:
                return self.test_names[section - 1]
        return None

    def update_test_status(self, row, col, status):
        self.test_objects[row][col - 1].status = status
        index = self.index(row, col)
        self.dataChanged.emit(index, index)
        # self.layoutChanged.emit()


# Señales personalizadas para comunicar con la UI
class TestSignals(QObject):
    finished = Signal(int, int, str)  # row, col, status


# Tarea que ejecuta un test en un hilo separado
class TestRunner(QRunnable):
    def __init__(self, test: TestExtractor, row: int, col: int, signals: TestSignals):
        super().__init__()
        self.test = test
        self.row = row
        self.col = col
        self.signals = signals

    @Slot()
    def run(self):
        print(f"Ejecutando test en fila {self.row}, columna {self.col}")
        self.test.run()
        print(f"Terminó test en fila {self.row}, columna {self.col} con estado {self.test.status}")
        self.signals.finished.emit(self.row, self.col, self.test.status)


class TestController(QObject):
    test_status_changed = Signal(int, int, str)
    test_progress = Signal(int, int)
    tests_finished = Signal()

    def __init__(self, scopes_base_path, parent=None):
        super().__init__(parent)
        # Si la ruta no es absoluta, la hacemos relativa a MODULE_BASE
        if not os.path.isabs(scopes_base_path):
            scopes_base_path = os.path.join(os.path.join(MODULE_BASE,'data'), scopes_base_path)
        self.scopes_base_path = scopes_base_path
        self.test_classes = get_all_tests()
        self.files = []
        self.test_objects = []
        self.thread_pool = QThreadPool()
        self.test_queue = []
        self.tests_executed = 0
        self.total_tests = 0
        self.paused = False
        self.aborted = False
        self.running = False

    def load_scopes(self):
        return [name for name in os.listdir(self.scopes_base_path)
                if os.path.isdir(os.path.join(self.scopes_base_path, name))]

    def load_versions(self, scope):
        try:
            path = os.path.join(self.scopes_base_path, scope)

            return [name for name in os.listdir(path)
                    if os.path.isdir(os.path.join(path, name))]
        except:
            pass

    def get_expected_file_names(self, scope_path):
        return [name for name in os.listdir(scope_path)
                if os.path.isdir(os.path.join(scope_path, name))]

    def build_pending_matrix(self, scope_name, version_name, input_folder):
        # Limpia la caché de sqlite cada vez que se reconstruye la matriz
        #SQLiteFileLoader.clear_sqlite_cache(input_folder)
        scope_path = os.path.join(self.scopes_base_path, scope_name, version_name)
        self.files = self.get_expected_file_names(scope_path)
        self.test_objects = []
        for file_name in self.files:
            extractor_file = ExtractorFile(scope_name, version_name, file_name, input_folder)
            row_tests = [cls(extractor_file) for cls in self.test_classes]
            self.test_objects.append(row_tests)
        return self.files, self.test_objects

    def start_tests(self):
        # Limpia la caché de sqlite antes de cada ejecución
        if self.files and self.files[0]:
            input_folder = self.test_objects[0][0].extractor_file.file_path
        self.paused = False
        self.aborted = False
        self.running = True
        self.test_queue.clear()
        for row_index, row_tests in enumerate(self.test_objects):
            for col_offset, test in enumerate(row_tests, start=1):
                self.test_queue.append((test, row_index, col_offset))
        self.total_tests = len(self.test_queue)
        self.tests_executed = 0
        self.run_next_test()

    def run_next_test(self):
        if self.aborted or self.paused:
            return
        if not self.test_queue:
            self.running = False
            self.tests_finished.emit()
            return
        test, row, col = self.test_queue.pop(0)
        signals = TestSignals()
        signals.finished.connect(self.on_test_finished)
        runner = TestRunner(test, row, col, signals)
        self.thread_pool.start(runner)

    def on_test_finished(self, row, col, status):
        self.test_status_changed.emit(row, col, status)
        self.tests_executed += 1
        self.test_progress.emit(self.tests_executed, self.total_tests)
        self.run_next_test()

    def pause(self):
        self.paused = True

    def resume(self):
        if self.paused:
            self.paused = False
            self.run_next_test()

    def abort(self):
        self.aborted = True
        self.test_queue.clear()
        self.running = False
        # Limpia la caché de sqlite al abortar
        if self.files and self.files[0]:
            input_folder = self.test_objects[0][0].extractor_file.file_path

    def restart(self):
        self.tests_executed = 0
        self.running = False

    def reenqueue_test(self, test, row, col):
        test.status = "🕓 Pendiente"
        test.log = ""
        self.test_queue.append((test, row, col))
        if not self.running:
            self.run_next_test()

    def reenqueue_row(self, row_index):
        for col_offset, test in enumerate(self.test_objects[row_index], start=1):
            test.status = "🕓 Pendiente"
            self.test_queue.append((test, row_index, col_offset))
        if not self.running:
            self.run_next_test()



class MainScreen(QWidget):
    def __init__(self, scopes_base_path="scopes"):
        super().__init__()
        self.initUI()
        # Si la ruta no es absoluta, la hacemos relativa a MODULE_BASE
        if not os.path.isabs(scopes_base_path):
            scopes_base_path = os.path.join(os.path.join(MODULE_BASE,'data'), scopes_base_path)
        self.controller = TestController(scopes_base_path)
        self.connect_controller_signals()
        self.input_folder = None
        self.model = None

        # UI setup
        self.load_scopes()

    def initUI(self):
        self.setWindowTitle("Matriz de Validación de Ficheros")

        self.principal_layout = QVBoxLayout(self)

        self.form_layout = QVBoxLayout(self)
        self.principal_layout.addLayout(self.form_layout)

        self.scope_form_layout = QHBoxLayout(self)
        self.folder_form_layout = QHBoxLayout(self)
        self.form_layout.addLayout(self.scope_form_layout)
        self.form_layout.addLayout(self.folder_form_layout)

        self.scope_form_layout.addWidget(QLabel("Scope:"))

        self.scope_combo = QComboBox()
        self.scope_combo.addItem("Selecciona un scope...")
        self.scope_combo.currentTextChanged.connect(self.on_scope_selected)
        self.scope_form_layout.addWidget(self.scope_combo)

        self.version_combo = QComboBox()
        self.version_combo.setEnabled(False)
        self.version_combo.currentTextChanged.connect(self.on_version_selected)
        self.scope_form_layout.addWidget(self.version_combo)

        self.folder_form_layout.addWidget(QLabel("Folder:"))

        self.input_folder_lineedit = QLineEdit()
        self.input_folder_lineedit.setEnabled(False)
        self.folder_form_layout.addWidget(self.input_folder_lineedit)

        self.select_input_button = QPushButton("Select folder")
        self.select_input_button.setEnabled(False)
        self.select_input_button.clicked.connect(self.select_input_folder)
        self.folder_form_layout.addWidget(self.select_input_button)

        self.principal_layout.addSpacing(40)

        # line edit for filtering
        self.filter_proxy_model = QSortFilterProxyModel()
        line_edit = QLineEdit()
        line_edit.setPlaceholderText("Filtrar...")
        line_edit.textChanged.connect(self.filter_proxy_model.setFilterRegularExpression)
        self.principal_layout.addWidget(line_edit)

        self.results_table = QTableView()
        self.results_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.results_table.customContextMenuRequested.connect(self.show_context_menu)
        self.principal_layout.addWidget(self.results_table)
        self.results_table.clicked.connect(self.show_log_dialog)

        self.principal_layout.addSpacing(20)

        # Contenedor horizontal para barra y botones
        progress_layout = QHBoxLayout()

        self.run_button = QPushButton("Ejecutar Tests")
        self.run_button.setEnabled(False)
        self.run_button.clicked.connect(self.run_tests)
        progress_layout.addWidget(self.run_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)

        self.pause_button = QPushButton("Pausar")
        self.pause_button.setEnabled(False)
        self.pause_button.clicked.connect(self.pause_tests)
        progress_layout.addWidget(self.pause_button)

        self.resume_button = QPushButton("Reanudar")
        self.resume_button.setEnabled(False)
        self.resume_button.clicked.connect(self.resume_tests)
        progress_layout.addWidget(self.resume_button)

        self.abort_button = QPushButton("Abortar")
        self.abort_button.setEnabled(False)
        self.abort_button.clicked.connect(self.abort_tests)
        progress_layout.addWidget(self.abort_button)

        self.restart_button = QPushButton("Reiniciar")
        self.restart_button.setEnabled(False)
        self.restart_button.clicked.connect(self.restart_tests)
        progress_layout.addWidget(self.restart_button)

        self.principal_layout.addLayout(progress_layout)

    def connect_controller_signals(self):
        self.controller.test_status_changed.connect(self.update_cell)
        self.controller.test_progress.connect(self.update_progress)
        self.controller.tests_finished.connect(self.on_tests_finished)

    def load_scopes(self):
        self.scope_combo.clear()
        self.scope_combo.addItem("Selecciona un scope...")
        for name in self.controller.load_scopes():
            self.scope_combo.addItem(name)

    def load_versions(self, scope):
        try:
            self.version_combo.clear()
            for name in self.controller.load_versions(scope):
                self.version_combo.addItem(name)
        except:
            pass

    def on_scope_selected(self, scope_name):
        self.reset_after_scope_selection()
        self.load_versions(scope_name)
        self.version_combo.setEnabled(scope_name != "Selecciona un scope...")

    def on_version_selected(self, version_name):
        self.reset_after_scope_selection()
        self.select_input_button.setEnabled(True)

    def select_input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecciona la carpeta con los ficheros reales")
        if folder:
            self.input_folder = folder
            self.input_folder_lineedit.setText(folder)
            self.build_pending_matrix()
            self.run_button.setEnabled(True)
            self.abort_button.setEnabled(True)

    def build_pending_matrix(self):
        self.progress_bar.setValue(0)
        self.progress_bar.setEnabled(False)
        scope_name = self.scope_combo.currentText()
        version_name = self.version_combo.currentText()
        files, test_objects = self.controller.build_pending_matrix(scope_name, version_name, self.input_folder)
        self.model = TestTableModel(files, test_objects)
        self.filter_proxy_model.setSourceModel(self.model)
        self.filter_proxy_model.setFilterKeyColumn(0)
        self.results_table.setModel(self.filter_proxy_model)
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for col in range(1, self.model.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.Fixed)
            header.resizeSection(col, 100)

    def run_tests(self):
        self.pause_button.setEnabled(True)
        self.abort_button.setEnabled(True)
        self.resume_button.setEnabled(False)
        self.restart_button.setEnabled(False)
        self.run_button.setEnabled(False)
        self.controller.start_tests()

    def update_cell(self, row, col, status):
        self.model.update_test_status(row, col, status)

    def update_progress(self, executed, total):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(executed)

    def on_tests_finished(self):
        self.pause_button.setEnabled(False)
        self.resume_button.setEnabled(False)
        self.abort_button.setEnabled(False)
        self.restart_button.setEnabled(True)
        self.run_button.setEnabled(False)

    def pause_tests(self):
        self.controller.pause()
        self.pause_button.setEnabled(False)
        self.resume_button.setEnabled(True)
        self.run_button.setEnabled(False)

    def resume_tests(self):
        self.controller.resume()
        self.pause_button.setEnabled(True)
        self.resume_button.setEnabled(False)

    def abort_tests(self):
        self.controller.abort()
        self.pause_button.setEnabled(False)
        self.resume_button.setEnabled(False)
        self.abort_button.setEnabled(False)
        self.restart_button.setEnabled(False)
        self.progress_bar.setValue(0)

    def restart_tests(self):
        self.progress_bar.setValue(0)
        self.run_button.setEnabled(True)
        self.restart_button.setEnabled(False)
        self.build_pending_matrix()

    def reset_after_scope_selection(self):
        self.model = None
        self.results_table.setModel(self.model)
        self.input_folder = None
        self.run_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.pause_button.setEnabled(False)
        self.resume_button.setEnabled(False)
        self.abort_button.setEnabled(False)
        self.restart_button.setEnabled(False)

    def show_context_menu(self, position):
        index = self.results_table.indexAt(position)
        if not index.isValid():
            return
        source_index = self.filter_proxy_model.mapToSource(index)
        row = source_index.row()
        col = index.column()
        menu = QMenu()
        if col == 0:
            action_view = QAction("Ver fichero", self)
            action_view.triggered.connect(lambda: self.show_file_dialog(row))
            menu.addAction(action_view)
            action = QAction("Reejecutar todos los tests de este fichero", self)
            action.triggered.connect(lambda: self.controller.reenqueue_row(row))
            menu.addAction(action)
        else:
            action = QAction("Reejecutar test", self)
            test = self.controller.test_objects[row][col - 1]
            action.triggered.connect(lambda: self.controller.reenqueue_test(test, row, col))
            menu.addAction(action)
            action2 = QAction("Ver errores", self)
            test = self.controller.test_objects[row][col - 1]
            action2.triggered.connect(lambda: self.show_error_dialog(test))
            menu.addAction(action2)
        menu.exec(self.results_table.viewport().mapToGlobal(position))

    def show_file_dialog(self, row):
        extractor_file = self.controller.test_objects[row][0].extractor_file
        dialog = FileViewerDialog(extractor_file, self)
        dialog.exec()

    def show_error_dialog(self, test):
        errors_dict = getattr(test, "errors", {})

        dialog = ErrorViewerDialog(errors_dict)

        dialog.exec()

    def show_log_dialog(self, index):
        row = index.row()
        col = index.column()

        if col == 0:
            return

        try:
            test = self.controller.test_objects[row][col - 1]
        except IndexError:
            return

        log_text = getattr(test, "log", "(Sin log)")

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Log - {self.model.test_names[col - 1]}")

        layout = QVBoxLayout(dialog)

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(log_text)
        layout.addWidget(text_edit)

        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.resize(500, 400)
        dialog.exec()

    def close_background_tasks(self):
        # Abortar tests y limpiar thread pool, además abortar tests individuales en ejecución
        if hasattr(self, "controller"):
            self.controller.abort()
            # Abortar tests individuales en ejecución
            for row_tests in getattr(self.controller, "test_objects", []):
                for test in row_tests:
                    if hasattr(test, "abort"):
                        test.abort()
            if hasattr(self.controller, "thread_pool"):
                self.controller.thread_pool.clear()
                self.controller.thread_pool.waitForDone(1000)  # Espera 1s máximo
        print("Tareas de fondo cerradas correctamente.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    scopes_base = os.path.join(MODULE_BASE, "data/scopes")
    window = MainScreen(scopes_base)
    window.resize(900, 500)
    window.show()
    sys.exit(app.exec())
