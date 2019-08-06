import sys
import ctypes
from PyQt5.QtWidgets import QApplication
from gui import OpeningWindow, LabelerWindow
from wizard import ProjectWizard
import dialogs
import config


def adjust_win_app_id():
    if sys.platform == 'win32':
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('zorzr.tsl')


class ApplicationController:
    def __init__(self):
        adjust_win_app_id()
        self.opening = OpeningWindow(self)
        self.labeler = None

        self.opening.show()

    def to_labeler(self, files=None, project=None):
        self.opening.close()

        if files:
            config.start_session(files=files)
        elif project:
            config.start_session(project=project)

        self.labeler = LabelerWindow(self)
        self.labeler.plot_canvas.init()
        self.labeler.show()

    def to_opening(self):
        self.labeler.destroy()
        self.opening.show()

    def to_wizard(self, folder):
        files = config.get_files_list(folder)
        if not files:
            dialogs.report_no_files()
            return

        self.opening.close()
        wizard = ProjectWizard(files)
        wizard.exec_()

        path = config.init_project(folder, wizard.project) if wizard.project else None
        if path:
            self.to_labeler(project=path)
        else:
            self.opening.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    controller = ApplicationController()
    sys.exit(app.exec_())
