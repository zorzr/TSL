from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont, QFontDatabase
from settings import LabelTable, LabelDialog
import matplotlib.colors as pltc


# noinspection PyArgumentList
class ProjectWizard(QWizard):
    def __init__(self, files, parent=None):
        super(ProjectWizard, self).__init__(parent)
        self.setWindowTitle("Project setup")
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
        class_type, channels_type = self.labels_page.generate_additional_options()

        self.project = {
            "files": files_list,
            "labels": names_list,
            "colors": colors_list,
            "binary_class": class_type,
            "independent_channels": channels_type
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

        self.checkboxes = []

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

        labelFont    = QFont()
        ad_options   = QLabel("Additional options: ")
        ad_project   = QCheckBox(" Two class anomaly detection project ")
        label_method = QCheckBox(" Label channels independently ")

        labelFont.setBold(True)
        ad_options.setFont(labelFont)

        bar_layout_2 = QGridLayout()
        bar_layout_2.addWidget(ad_options)
        bar_layout_2.addWidget(ad_project)
        bar_layout_2.addWidget(label_method)

        bar_2 = QWidget()
        bar_2.setLayout(bar_layout_2)
        layout.addWidget(bar_2)

        self.checkboxes.append(ad_project)
        self.checkboxes.append(label_method)

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

    def generate_additional_options(self):
        additional_options = []
        for i, box in enumerate(self.checkboxes):
            if box.isChecked():
                additional_options.append('true')
            else:
                additional_options.append('false')
        return additional_options

    def isComplete(self):
        return self.table.rowCount() > 0
