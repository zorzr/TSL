from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon


def ask_to_continue():
    msg = QMessageBox()
    msg.setWindowIcon(QIcon('./assets/icon_green.png'))
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Information")
    msg.setText("Do you want to continue?\nUnsaved changes will be lost")
    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg.setDefaultButton(QMessageBox.No)
    msg.setStyleSheet("QLabel { margin-right: 7px; }")

    ret = msg.exec_()
    return bool(ret == QMessageBox.Yes)


def report_no_files():
    msg = QMessageBox()
    msg.setWindowIcon(QIcon('./assets/icon_green.png'))
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle("Error")
    msg.setText("No suitable files have been found in the selected folder.\n"
                "At least one file is needed to run a project")
    msg.setStyleSheet("QLabel { margin-right: 7px; }")

    msg.exec_()


def notify_read_error(filename):
    msg = QMessageBox()
    msg.setWindowIcon(QIcon('./assets/icon_green.png'))
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle("Warning")
    msg.setText("An error occurred while processing the file:\n" + filename +
                "\nPress Ok to open the following in the list.")
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Close)
    msg.setDefaultButton(QMessageBox.Ok)
    msg.setStyleSheet("QLabel { margin-right: 7px; }")

    ret = msg.exec_()
    if ret == QMessageBox.Close:
        exit(0)
