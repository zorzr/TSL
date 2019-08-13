from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from settings import LabelTable, LabelDialog
import matplotlib.colors as pltc


# noinspection PyArgumentList
class ProjectWizard(QWizard):
    def __init__(self, files, parent=None):
        super(ProjectWizard, self).__init__(parent)
        self.setWindowTitle("Project setup")
        # self.setWindowIcon(QIcon('./assets/icon_green.png'))
        # self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setFixedSize(640, 480)
        self.project = None

        self.files_page = Page1(files, self)
        self.labels_page = Page2(self)
        self.addPage(self.files_page)
        self.addPage(self.labels_page)

        self.button(QWizard.FinishButton).clicked.connect(self.on_finish)

    def mousePressEvent(self, event):
        self.labels_page.clear_selected()

    def on_finish(self):
        files_list = self.files_page.generate_files_list()
        names_list, colors_list = self.labels_page.table.generate_labels_list()

        self.project = {
            "files": files_list,
            "labels": names_list,
            "colors": colors_list
        }


# noinspection PyArgumentList
class Page1(QWizardPage):
    def __init__(self, files, parent=None):
        super(Page1, self).__init__(parent)
        self.setTitle("Include files")
        self.setSubTitle("Select the files you would like to add to the project.")
        self.files = files

        layout = QVBoxLayout()
        scroll = QScrollArea()
        layout.addWidget(scroll)
        self.setLayout(layout)

        content = QWidget()
        content_layout = QVBoxLayout()
        content.setLayout(content_layout)

        self.checkboxes = []
        for i in range(len(files)):
            self.checkboxes.append(QCheckBox(files[i]))
        for i, box in enumerate(self.checkboxes):
            box.setChecked(True)
            box.clicked.connect(lambda: self.completeChanged.emit())
            content_layout.addWidget(box)

        scroll.setWidget(content)

    def generate_files_list(self):
        files_list = []
        for i, box in enumerate(self.checkboxes):
            if box.isChecked():
                files_list.append(self.files[i])
        return files_list

    def isComplete(self):
        complete = False
        for box in self.checkboxes:
            if box.isChecked():
                complete = True
                break
        return complete


# noinspection PyArgumentList
class Page2(QWizardPage):
    def __init__(self, parent=None):
        super(Page2, self).__init__(parent)
        self.setTitle("Customize labels")
        self.setSubTitle("Indicate the labels to be used in the created project.")
        self.setFinalPage(True)

        default_labels = [("Label", "#1f77b4")]
        self.table = LabelTable(default_labels)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)

        add = QPushButton("Add")
        edit = QPushButton("Edit")
        remove = QPushButton("Remove")
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        bar_layout = QHBoxLayout()
        bar_layout.addWidget(add)
        bar_layout.addWidget(edit)
        bar_layout.addWidget(remove)
        bar_layout.addWidget(spacer)
        bar_layout.setSpacing(2)
        bar_layout.setContentsMargins(0, 0, 0, 0)

        bar = QWidget()
        bar.setLayout(bar_layout)
        layout.addWidget(bar)

        add.clicked.connect(self.add)
        edit.clicked.connect(self.edit)
        remove.clicked.connect(self.remove)

    def mousePressEvent(self, event):
        self.clear_selected()

    def clear_selected(self):
        self.table.clearSelection()
        self.table.setCurrentCell(-1, -1)

    def add(self):
        dialog = LabelDialog()
        ret = dialog.exec_()
        if ret == 0:
            return

        name = dialog.name.text()
        color = dialog.color.text()

        if pltc.is_color_like(color):
            self.table.insert_row(name, pltc.to_hex(color))

        if self.table.rowCount() > 0:
            self.completeChanged.emit()

    def edit(self):
        if self.table.rowCount() == 0:
            return

        row = self.table.currentRow()
        row_name = self.table.item(row, 0).text()
        row_color = self.table.item(row, 1).text()

        dialog = LabelDialog(row_name, row_color)
        ret = dialog.exec_()
        if ret == 0:
            return

        name = dialog.name.text()
        color = dialog.color.text()

        if pltc.is_color_like(color):
            self.table.item(row, 0).setText(name)
            self.table.item(row, 1).setText(pltc.to_hex(color))

    def remove(self):
        self.table.removeRow(self.table.currentRow())

        if self.table.rowCount() == 0:
            self.completeChanged.emit()

    def isComplete(self):
        return self.table.rowCount() > 0
