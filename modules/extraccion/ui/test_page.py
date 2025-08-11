import os
import sys

from PySide6.QtCore import Qt, QSortFilterProxyModel
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QHeaderView, QSpacerItem, QSizePolicy,
    QFileDialog, QDialog, QTextEdit, QMenu, QPushButton, QProgressBar, QTableView, QLabel
)
from PySide6.QtGui import QAction

from widgets.card_stacked import CardStacked
from widgets.inputs.labeled_fileinput import LabeledFileInput
from widgets.inputs.labeled_combobox import LabeledComboBox
from widgets.inputs.labeled_lineedit import LabeledLineEdit
from widgets.inputs.primary_button import PrimaryButton
from widgets.inputs.danger_button import DangerButton
from widgets.results_table_widget import ResultsTableWidget, TestTableModel

from modules.extraccion.src.FileViewer import FileViewerDialog
from modules.extraccion.ui.error_page import ErrorViewerDialog
from modules.extraccion.src.test_controller import TestController

MODULE_BASE = os.path.dirname(os.path.dirname(__file__))

class TestFormPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.scope_form_layout = QHBoxLayout()
        self.folder_form_layout = QHBoxLayout()
        self.layout.addLayout(self.scope_form_layout)
        self.layout.addItem(QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.layout.addLayout(self.folder_form_layout)

        self.scope_combo = LabeledComboBox("Scope:")
        self.scope_form_layout.addWidget(self.scope_combo)

        self.version_combo = LabeledComboBox("Versión:")
        self.version_combo.combobox.setEnabled(False)
        self.scope_form_layout.addWidget(self.version_combo)

        self.input_folder_lineedit = LabeledFileInput("Carpeta de entrada:")
        self.input_folder_lineedit.lineedit.setEnabled(False)
        self.folder_form_layout.addWidget(self.input_folder_lineedit)

        self.layout.addStretch()

        self.next_button = PrimaryButton("Siguiente")
        self.next_button.setEnabled(False)
        self.layout.addWidget(self.next_button)

    def set_scopes(self, scopes):
        self.scope_combo.combobox.clear()
        self.scope_combo.combobox.addItem("Selecciona un scope...")
        for name in scopes:
            self.scope_combo.combobox.addItem(name)

    def set_versions(self, versions):
        self.version_combo.combobox.clear()
        for name in versions:
            self.version_combo.combobox.addItem(name)
        self.version_combo.combobox.setEnabled(True)

    def reset(self):
        self.scope_combo.combobox.setCurrentIndex(0)
        self.version_combo.combobox.clear()
        self.version_combo.combobox.setEnabled(False)
        self.input_folder_lineedit.lineedit.clear()
        self.input_folder_lineedit.setEnabled(False)
        self.next_button.setEnabled(False)

    def connect_signals(self, select_input_folder_func, next_func):
        self.input_folder_lineedit.button.clicked.connect(select_input_folder_func)
        self.next_button.clicked.connect(next_func)

    def ask_input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecciona la carpeta con los ficheros reales")
        if folder:
            self.input_folder_lineedit.lineedit.setText(folder)
            return folder
        return None

class TestResultsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        self.filter_proxy_model = QSortFilterProxyModel()
        self.filter_lineedit = LabeledLineEdit("Filtrar:")
        self.filter_lineedit.lineedit.setPlaceholderText("Filtrar...")
        self.layout.addWidget(self.filter_lineedit)

        self.results_table = QTableView()
        self.results_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.layout.addWidget(self.results_table)

        self.layout.addSpacing(20)

        progress_layout = QHBoxLayout()
        self.run_button = PrimaryButton("Ejecutar Tests")
        self.run_button.setEnabled(False)
        progress_layout.addWidget(self.run_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)

        self.pause_button = PrimaryButton("Pausar")
        self.pause_button.setEnabled(False)
        progress_layout.addWidget(self.pause_button)

        self.resume_button = PrimaryButton("Reanudar")
        self.resume_button.setEnabled(False)
        progress_layout.addWidget(self.resume_button)

        self.abort_button = DangerButton("Abortar")
        self.abort_button.setEnabled(False)
        progress_layout.addWidget(self.abort_button)

        self.restart_button = PrimaryButton("Reiniciar")
        self.restart_button.setEnabled(False)
        progress_layout.addWidget(self.restart_button)

        self.layout.addLayout(progress_layout)

    def set_model(self, model, filter_proxy_model):
        filter_proxy_model.setSourceModel(model)
        filter_proxy_model.setFilterKeyColumn(0)
        self.results_table.setModel(filter_proxy_model)
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for col in range(1, model.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.Fixed)
            header.resizeSection(col, 100)

    def reset(self):
        self.results_table.setModel(None)
        self.run_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.pause_button.setEnabled(False)
        self.resume_button.setEnabled(False)
        self.abort_button.setEnabled(False)
        self.restart_button.setEnabled(False)

    def connect_signals(self, filter_func, context_menu_func, log_func, run_func, pause_func, resume_func, abort_func, restart_func):
        self.filter_lineedit.lineedit.textChanged.connect(filter_func)
        self.results_table.customContextMenuRequested.connect(context_menu_func)
        self.results_table.clicked.connect(log_func)
        self.run_button.clicked.connect(run_func)
        self.pause_button.clicked.connect(pause_func)
        self.resume_button.clicked.connect(resume_func)
        self.abort_button.clicked.connect(abort_func)
        self.restart_button.clicked.connect(restart_func)

    def show_context_menu(self, controller, filter_proxy_model, parent):
        def handler(position):
            index = self.results_table.indexAt(position)
            if not index.isValid():
                return
            source_index = filter_proxy_model.mapToSource(index)
            row = source_index.row()
            col = index.column()
            menu = QMenu()
            if col == 0:
                action_view = QAction("Ver fichero", parent)
                action_view.triggered.connect(lambda: parent.show_file_dialog(row))
                menu.addAction(action_view)
                action = QAction("Reejecutar todos los tests de este fichero", parent)
                action.triggered.connect(lambda: controller.reenqueue_row(row))
                menu.addAction(action)
            else:
                action = QAction("Reejecutar test", parent)
                test = controller.test_objects[row][col - 1]
                action.triggered.connect(lambda: controller.reenqueue_test(test, row, col))
                menu.addAction(action)
                action2 = QAction("Ver errores", parent)
                test = controller.test_objects[row][col - 1]
                action2.triggered.connect(lambda: parent.show_error_dialog(test))
                menu.addAction(action2)
            menu.exec(self.results_table.viewport().mapToGlobal(position))
        return handler

    def show_log_dialog(self, controller, parent):
        def handler(index):
            row = index.row()
            col = index.column()
            if col == 0:
                return
            try:
                test = controller.test_objects[row][col - 1]
            except IndexError:
                return
            log_text = getattr(test, "log", "(Sin log)")
            dialog = QDialog(parent)
            dialog.setWindowTitle(f"Log - {parent.model.test_names[col - 1]}")
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
        return handler

    def set_progress(self, executed, total):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(executed)

    def set_buttons_on_run(self):
        self.pause_button.setEnabled(True)
        self.abort_button.setEnabled(True)
        self.resume_button.setEnabled(False)
        self.restart_button.setEnabled(False)
        self.run_button.setEnabled(False)

    def set_buttons_on_finish(self):
        self.pause_button.setEnabled(False)
        self.resume_button.setEnabled(False)
        self.abort_button.setEnabled(False)
        self.restart_button.setEnabled(True)
        self.run_button.setEnabled(False)

    def set_buttons_on_pause(self):
        self.pause_button.setEnabled(False)
        self.resume_button.setEnabled(True)
        self.run_button.setEnabled(False)

    def set_buttons_on_resume(self):
        self.pause_button.setEnabled(True)
        self.resume_button.setEnabled(False)

    def set_buttons_on_abort(self):
        self.pause_button.setEnabled(False)
        self.resume_button.setEnabled(False)
        self.abort_button.setEnabled(False)
        self.restart_button.setEnabled(False)
        self.progress_bar.setValue(0)

    def set_buttons_on_restart(self):
        self.progress_bar.setValue(0)
        self.run_button.setEnabled(True)
        self.restart_button.setEnabled(False)

class TestPage(CardStacked):
    def __init__(self, scopes_base_path="scopes"):
        super().__init__(title="Tests de Extracción")
        if not os.path.isabs(scopes_base_path):
            scopes_base_path = os.path.join(os.path.join(MODULE_BASE, 'data'), scopes_base_path)
        self.controller = TestController(scopes_base_path)
        self.input_folder = None
        self.model = None
        self.filter_proxy_model = QSortFilterProxyModel()
        self.init_pages()
        self.connect_signals()
        self.load_scopes()

    def init_pages(self):
        self.form_page = TestFormPage()
        self.results_page = TestResultsPage()
        self.add_widget(self.form_page)
        self.add_widget(self.results_page)
        self.set_current_index(0)
        if self.back_btn:
            self.back_btn.clicked.connect(lambda: self.set_current_index(0))

    def connect_signals(self):
        self.form_page.scope_combo.combobox.currentTextChanged.connect(self.on_scope_selected)
        self.form_page.version_combo.combobox.currentTextChanged.connect(self.on_version_selected)
        self.form_page.next_button.clicked.connect(lambda: self.set_current_index(1))
        self.form_page.input_folder_lineedit.button.clicked.connect(self.handle_select_input_folder)
        self.results_page.filter_lineedit.lineedit.textChanged.connect(self.filter_proxy_model.setFilterRegularExpression)
        self.results_page.results_table.customContextMenuRequested.connect(
            self.results_page.show_context_menu(self.controller, self.filter_proxy_model, self)
        )
        self.results_page.results_table.clicked.connect(
            self.results_page.show_log_dialog(self.controller, self)
        )
        self.results_page.run_button.clicked.connect(self.handle_run_tests)
        self.results_page.pause_button.clicked.connect(self.handle_pause_tests)
        self.results_page.resume_button.clicked.connect(self.handle_resume_tests)
        self.results_page.abort_button.clicked.connect(self.handle_abort_tests)
        self.results_page.restart_button.clicked.connect(self.handle_restart_tests)
        self.controller.test_status_changed.connect(self.handle_update_cell)
        self.controller.test_progress.connect(self.results_page.set_progress)
        self.controller.tests_finished.connect(self.results_page.set_buttons_on_finish)

    def load_scopes(self):
        scopes = self.controller.load_scopes()
        self.form_page.set_scopes(scopes)

    def on_scope_selected(self, scope_name):
        self.results_page.reset()
        self.input_folder = None
        if scope_name != "Selecciona un scope...":
            versions = self.controller.load_versions(scope_name)
            self.form_page.set_versions(versions)
            self.form_page.version_combo.combobox.setEnabled(True)

    def on_version_selected(self, version_name):
        self.form_page.input_folder_lineedit.setEnabled(True)
        self.results_page.reset()
        self.input_folder = None

    def handle_select_input_folder(self):
        folder = self.form_page.ask_input_folder()
        if folder:
            self.input_folder = folder
            self.build_pending_matrix()
            self.results_page.run_button.setEnabled(True)
            self.results_page.abort_button.setEnabled(True)
            self.form_page.next_button.setEnabled(True)

    def build_pending_matrix(self):
        self.results_page.progress_bar.setValue(0)
        self.results_page.progress_bar.setEnabled(False)
        scope_name = self.form_page.scope_combo.currentText()
        version_name = self.form_page.version_combo.currentText()
        files, test_objects = self.controller.build_pending_matrix(scope_name, version_name, self.input_folder)
        self.model = TestTableModel(files, test_objects, self.controller.test_classes)
        self.results_page.set_model(self.model, self.filter_proxy_model)

    def handle_run_tests(self):
        self.results_page.set_buttons_on_run()
        self.controller.start_tests()

    def handle_update_cell(self, row, col, status):
        self.model.update_test_status(row, col, status)

    def handle_pause_tests(self):
        self.controller.pause()
        self.results_page.set_buttons_on_pause()

    def handle_resume_tests(self):
        self.controller.resume()
        self.results_page.set_buttons_on_resume()

    def handle_abort_tests(self):
        self.controller.abort()
        self.results_page.set_buttons_on_abort()

    def handle_restart_tests(self):
        self.results_page.set_buttons_on_restart()
        self.build_pending_matrix()

    def show_file_dialog(self, row):
        extractor_file = self.controller.test_objects[row][0].extractor_file
        dialog = FileViewerDialog(extractor_file, self)
        dialog.exec()

    def show_error_dialog(self, test):
        errors_dict = getattr(test, "errors", {})
        dialog = ErrorViewerDialog(errors_dict)
        dialog.exec()

    def close_background_tasks(self):
        if hasattr(self, "controller"):
            self.controller.abort()
            for row_tests in getattr(self.controller, "test_objects", []):
                for test in row_tests:
                    if hasattr(test, "abort"):
                        test.abort()
            if hasattr(self.controller, "thread_pool"):
                self.controller.thread_pool.clear()
                self.controller.thread_pool.waitForDone(1000)
        print("Tareas de fondo cerradas correctamente.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    scopes_base = os.path.join(MODULE_BASE, "data/scopes")
    window = TestPage(scopes_base)
    window.resize(900, 500)
    window.show()
    sys.exit(app.exec())
    scopes_base = os.path.join(MODULE_BASE, "data/scopes")
    window = TestPage(scopes_base)
    window.resize(900, 500)
    window.show()
    sys.exit(app.exec())
