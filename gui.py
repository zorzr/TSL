from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from core import PlotCanvas


class PicButton(QAbstractButton):
    def __init__(self, default, hover, pressed, parent=None):
        super(PicButton, self).__init__(parent)
        self.pixmap = QPixmap(default)
        self.pixmap_hover = QPixmap(hover)
        self.pixmap_pressed = QPixmap(pressed)

        self.pressed.connect(self.update)
        self.released.connect(self.update)

    def paintEvent(self, event):
        pix = self.pixmap_hover if self.underMouse() else self.pixmap
        if self.isDown():
            pix = self.pixmap_pressed

        painter = QPainter(self)
        painter.drawPixmap(event.rect(), pix)

    def enterEvent(self, event):
        self.update()

    def leaveEvent(self, event):
        self.update()

    def sizeHint(self):
        return self.pixmap.size()


# noinspection PyCallByClass,PyArgumentList
class OpeningWindow(QMainWindow):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller

        # Geometry: left, top, width, height
        self.setGeometry(450, 300, 700, 500)
        self.setWindowTitle('Time Series Labeler')
        self.setWindowIcon(QIcon('./assets/icon_green.png'))

        self._init()

    def _init(self):
        # Two section titles
        files_title = QLabel("Single files", self)
        projects_title = QLabel("Projects", self)
        files_title.move(130, 20)
        files_title.resize(200, 35)
        projects_title.move(130, 210)
        projects_title.resize(200, 35)
        font = files_title.font()
        font.setPointSize(18)
        files_title.setFont(font)
        projects_title.setFont(font)

        # Open file
        default = './assets/pic-buttons/open_files_default.png'
        hover = './assets/pic-buttons/open_files_hover.png'
        pressed = './assets/pic-buttons/open_files_pressed.png'
        self.file_button = PicButton(default, hover, pressed, self)
        self.file_button.clicked.connect(self.file_dialog)
        self.file_button.move(125, 60)
        self.file_button.resize(450, 100)

        # New project
        default = './assets/pic-buttons/open_folder_default.png'
        hover = './assets/pic-buttons/open_folder_hover.png'
        pressed = './assets/pic-buttons/open_folder_pressed.png'
        self.folder_button = PicButton(default, hover, pressed, self)
        self.folder_button.clicked.connect(self.folder_dialog)
        self.folder_button.move(125, 250)
        self.folder_button.resize(450, 100)

        # Open project
        default = './assets/pic-buttons/open_project_default.png'
        hover = './assets/pic-buttons/open_project_hover.png'
        pressed = './assets/pic-buttons/open_project_pressed.png'
        self.project_button = PicButton(default, hover, pressed, self)
        self.project_button.clicked.connect(self.project_dialog)
        self.project_button.move(125, 360)
        self.project_button.resize(450, 100)

    def file_dialog(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select files", "", "CSV Files (*.csv);;All Files (*)")
        if files:
            self.controller.to_labeler(files=files)

    def folder_dialog(self):
        folder = QFileDialog.getExistingDirectory(self, "Select folder")
        if folder:
            self.controller.to_wizard(folder=folder)

    def project_dialog(self):
        project, _ = QFileDialog.getOpenFileName(self, "Select project file", "", "JSON Files (*.json)")
        if project:
            self.controller.to_labeler(project=project)


class LabelerWindow(QMainWindow):
    def __init__(self, controller, **kwargs):
        super().__init__(**kwargs)
        self.controller = controller
        self.plot_canvas = PlotCanvas(self)

        self.setWindowTitle('Time Series Labeler')
        self.setWindowIcon(QIcon('./assets/icon_green.png'))

        self._init()

    def _init(self):
        central_widget = QWidget(flags=self.windowFlags())
        self.setCentralWidget(central_widget)
        self._menubar()

        layout = QVBoxLayout()
        layout.addWidget(self.plot_canvas, alignment=Qt.Alignment())
        layout.addWidget(self.plot_canvas.toolbar, alignment=Qt.Alignment())
        central_widget.setLayout(layout)

        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(palette)

    def _menubar(self):
        self.menubar = self.menuBar()

        # File
        file = self.menubar.addMenu('File')

        reset = file.addAction('Reset')
        save = file.addAction('Save')
        file.addSeparator()
        next_file = file.addAction('Next file')
        prev_file = file.addAction('Previous file')
        file.addSeparator()
        ret = file.addAction('Return')
        close = file.addAction('Quit')

        reset.setShortcut('R')
        save.setShortcut('S')
        next_file.setShortcut('N')
        prev_file.setShortcut('P')
        ret.setShortcut('Ctrl+R')
        close.setShortcut('Ctrl+Q')

        reset.setIcon(QIcon('./assets/reset.png'))
        save.setIcon(QIcon('./assets/save.png'))
        next_file.setIcon(QIcon('./assets/next_file.png'))
        prev_file.setIcon(QIcon('./assets/prev_file.png'))
        ret.setIcon(QIcon('./assets/return.png'))
        close.setIcon(QIcon('./assets/quit.png'))

        reset.triggered.connect(self.plot_canvas.reset)
        save.triggered.connect(self.plot_canvas.save)
        next_file.triggered.connect(self.plot_canvas.next_file)
        prev_file.triggered.connect(self.plot_canvas.prev_file)
        ret.triggered.connect(self.controller.to_opening)
        close.triggered.connect(self.plot_canvas.quit)

        # Label
        label = self.menubar.addMenu('Label')

        next_label = label.addAction('Next label')
        prev_label = label.addAction('Previous label')

        next_label.setShortcut('L')
        prev_label.setShortcut('K')

        next_label.setIcon(QIcon('./assets/next_label.png'))
        prev_label.setIcon(QIcon('./assets/prev_label.png'))

        next_label.triggered.connect(self.plot_canvas.next_label)
        prev_label.triggered.connect(self.plot_canvas.prev_label)

    def keyPressEvent(self, event):
        self.plot_canvas.on_key(event)

    def ask_to_continue(self):
        msg = QMessageBox()
        msg.setWindowIcon(self.windowIcon())
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Information")
        msg.setText("Do you want to continue?\nUnsaved changes will be lost")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        msg.setStyleSheet("QLabel { margin-right: 7px; }")

        ret = msg.exec_()
        return bool(ret == QMessageBox.Yes)
