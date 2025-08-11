from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableView, QHeaderView
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
import palette

class ResultsTableWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.table = QTableView()
        self.table.setObjectName("ResultsTableView")
        # Oculta la vertical header (columna de selección de filas)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)
        self.set_palette_style()
        # Ajusta el tamaño de las columnas al contenido de la cabecera
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)

    def setModel(self, model):
        self.table.setModel(model)

    def setContextMenuPolicy(self, policy):
        self.table.setContextMenuPolicy(policy)

    def customContextMenuRequested(self, func):
        self.table.customContextMenuRequested.connect(func)

    def clicked(self, func):
        self.table.clicked.connect(func)

    def setHorizontalHeader(self, func):
        func(self.table.horizontalHeader())

    def setSelectionBehavior(self, behavior):
        self.table.setSelectionBehavior(behavior)

    def setSelectionMode(self, mode):
        self.table.setSelectionMode(mode)

    def set_palette_style(self):
        self.table.setStyleSheet(f"""
            QTableView#ResultsTableView {{
                background: {palette.palette['card_bg']};
                color: {palette.palette['text']};
                border: 1px solid {palette.palette['border']};
                selection-background-color: {palette.palette['selection']};
                selection-color: {palette.palette['primary_text']};
                gridline-color: {palette.palette['border']};
                font-size: 14px;
                alternate-background-color: {palette.palette['background']};
            }}
            QTableView::item {{
                color: {palette.palette['text']};
                background: transparent;
            }}
            QTableView::item:selected {{
                color: {palette.palette['primary_text']};
                background: {palette.palette['primary']};
            }}
            QHeaderView::section {{
                background: {palette.palette['button_bg']};
                color: {palette.palette['primary']};
                border: 1px solid {palette.palette['border']};
                font-weight: bold;
                font-size: 15px;
                padding: 6px 0px;
            }}
            QHeaderView {{
                background: {palette.palette['button_bg']};
            }}
            QScrollBar:vertical {{
                background: {palette.palette['background']};
                width: 12px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {palette.palette['primary']};
                min-height: 20px;
                border-radius: 6px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)

    def update_palette(self):
        self.set_palette_style()

    def model(self):
        return self.table.model()

    def horizontalHeader(self):
        return self.table.horizontalHeader()

    def indexAt(self, pos):
        return self.table.indexAt(pos)

    def viewport(self):
        return self.table.viewport()

class TestTableModel(QAbstractTableModel):
    def __init__(self, files, tests, test_classes, parent=None):
        super().__init__(parent)
        self.files = files
        self.test_classes = test_classes
        self.test_names = [cls.name for cls in self.test_classes]
        self.test_objects = tests

    def rowCount(self, parent=QModelIndex()):
        return len(self.files)

    def columnCount(self, parent=QModelIndex()):
        return 1 + len(self.test_names)

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
