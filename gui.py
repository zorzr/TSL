from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from core import PlotCanvas
from settings import SettingsWindow
from functions.controller import FunctionController, FunctionDialog
from functions.time_function import TimeFunction
import config


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
        
        self.setWindowTitle('Time Series Labeler')
        self.setFixedSize(700, 500)

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

        self.setWindowTitle('Time Series Labeler')
        self.setGeometry(200, 200, 900, 700)
        self._init()

    def _init(self):
        central_widget = QWidget(flags=self.windowFlags())
        self.setCentralWidget(central_widget)
        self.scroll = QScrollArea(central_widget)
        self.plot_canvas = PlotCanvas(self)
        self._menubar()

        # layout = QVBoxLayout()
        # layout.addWidget(self.plot_canvas, alignment=Qt.Alignment())
        # layout.addWidget(self.plot_canvas.toolbar, alignment=Qt.Alignment())
        # central_widget.setLayout(layout)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.scroll.setWidget(self.plot_canvas)
        self.scroll.setWidgetResizable(True)
        layout.addWidget(self.scroll, alignment=Qt.Alignment())
        layout.addWidget(self.plot_canvas.toolbar, alignment=Qt.Alignment())
        central_widget.setLayout(layout)

        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(palette)

        # Fix background glitch by assigning a fixed scrollbar size
        self.scroll.setStyleSheet("QScrollBar:vertical { width: 18px; }")

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
        settings = file.addAction('Settings')
        ret = file.addAction('Return')
        close = file.addAction('Quit')

        reset.setShortcut('R')
        save.setShortcut('S')
        next_file.setShortcut('N')
        prev_file.setShortcut('P')
        settings.setShortcut('Ctrl+O')
        ret.setShortcut('Ctrl+R')
        close.setShortcut('Ctrl+Q')

        reset.setIcon(QIcon('./assets/reset.png'))
        save.setIcon(QIcon('./assets/save.png'))
        next_file.setIcon(QIcon('./assets/next_file.png'))
        prev_file.setIcon(QIcon('./assets/prev_file.png'))
        settings.setIcon(QIcon('./assets/setting.png'))
        ret.setIcon(QIcon('./assets/return.png'))
        close.setIcon(QIcon('./assets/quit.png'))

        reset.triggered.connect(self.plot_canvas.reset)
        save.triggered.connect(self.plot_canvas.save)
        next_file.triggered.connect(self.plot_canvas.next_file)
        prev_file.triggered.connect(self.plot_canvas.prev_file)
        settings.triggered.connect(self.open_settings)
        ret.triggered.connect(self.controller.to_opening)
        close.triggered.connect(self.plot_canvas.quit)

        # Label
        label = self.menubar.addMenu('Label')

        next_label = label.addAction('Next label')
        prev_label = label.addAction('Previous label')
        label.addSeparator()
        customize_label = label.addAction('Customize labels')

        next_label.setShortcut('L')
        prev_label.setShortcut('K')

        next_label.setIcon(QIcon('./assets/next_label.png'))
        prev_label.setIcon(QIcon('./assets/prev_label.png'))
        customize_label.setIcon(QIcon('./assets/customize.png'))

        next_label.triggered.connect(self.plot_canvas.next_label)
        prev_label.triggered.connect(self.plot_canvas.prev_label)
        customize_label.triggered.connect(lambda: self.open_settings(1))

        # Functions
        functions = self.menubar.addMenu('Functions')
        for i, function in enumerate(FunctionController.get_functions()):
            func_entry = functions.addAction(function)
            func_entry.triggered.connect(make_caller(self.open_function_setup, i))
        functions.addSeparator()
        self.remove_function = functions.addMenu("Remove function")
        self.update_functions()

    def keyPressEvent(self, event):
        self.plot_canvas.on_key(event)

    def closeEvent(self, event):
        self.plot_canvas.quit()
        event.ignore()

    def open_settings(self, active=0):
        settings_window = SettingsWindow()
        settings_window.tabs.setCurrentIndex(active)
        settings_window.exec()
        self.plot_canvas.core.redraw()

    def open_function_setup(self, func_index):
        if FunctionController.add(func_index):
            self.plot_canvas.modified = True
            self.update_functions()

    def open_function_removal(self, rem_index):
        FunctionController.remove(rem_index)
        self.plot_canvas.modified = True
        self.plot_canvas.core.redraw()
        self.update_functions()

    def update_functions(self):
        self.remove_function.clear()

        conf = config.data_config
        for i, func in enumerate(conf.get_functions()):
            func_entry = self.remove_function.addAction(func)
            func_entry.triggered.connect(make_caller(self.open_function_removal, i))

    def resizeEvent(self, event):
        self.plot_canvas.figure_resize()
        return super(LabelerWindow, self).resizeEvent(event)


def make_caller(method, index):
    def caller():
        method(index)
    return caller
