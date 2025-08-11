import os
from PySide6.QtCore import QObject, Signal, QRunnable, Slot, QThreadPool
from modules.extraccion.src.tests import TestExtractor, get_all_tests
from modules.extraccion.src.tests.test_base import ExtractorFile

MODULE_BASE = os.path.dirname(os.path.dirname(__file__))

class TestSignals(QObject):
    finished = Signal(int, int, str)  # row, col, status

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
        scope_path = os.path.join(self.scopes_base_path, scope_name, version_name)
        self.files = self.get_expected_file_names(scope_path)
        self.test_objects = []
        for file_name in self.files:
            extractor_file = ExtractorFile(scope_name, version_name, file_name, input_folder)
            row_tests = [cls(extractor_file) for cls in self.test_classes]
            self.test_objects.append(row_tests)
        return self.files, self.test_objects

    def start_tests(self):
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
