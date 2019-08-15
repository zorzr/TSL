from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from settings import LabelTable, LabelDialog, pltc
from functions.time_function import TimeFunction
import config
import dialogs


# noinspection PyArgumentList
class FunctionDialog(QDialog):
    def __init__(self, title="Function setup", parameters=None):
        super().__init__()
        self.setWindowTitle(title)
        ts_list = config.data_config.datafile.get_data_header()

        self.name = None
        self.source = None
        self.parameters = dict()

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        self.setLayout(main_layout)

        # Function details
        self.name_input = QLineEdit()
        self.name_input.setMaxLength(20)
        self.name_input.textChanged.connect(self.validate_form)
        self.source_input = QComboBox()
        self.source_input.addItems(ts_list)

        layout = QFormLayout()
        layout.addRow(QLabel("Name"), self.name_input)
        layout.addRow(QLabel("Source"), self.source_input)
        self.details_box = QGroupBox("Function details")
        self.details_box.setLayout(layout)
        main_layout.addWidget(self.details_box)

        # Function parameters
        self.ret_func = dict()
        if parameters is not None:
            layout = QFormLayout()

            for key in parameters.keys():
                param = parameters[key]
                widget = None

                if param["type"] == "text":
                    widget = QLineEdit()
                    self.ret_func[key] = widget.text
                elif param["type"] == "combo":
                    widget = QComboBox()
                    widget.addItems(param["values"])
                    widget.setCurrentIndex(param["default"])
                    self.ret_func[key] = widget.currentText
                elif param["type"] == "int":
                    widget = QSpinBox()
                    widget.setRange(param["min"], param["max"])
                    widget.setValue(param["default"])
                    self.ret_func[key] = widget.value
                elif param["type"] == "double":  # TODO: replace with QDoubleSpinBox
                    widget = QLineEdit()
                    widget.setValidator(QDoubleValidator())
                    self.ret_func[key] = widget.text

                layout.addRow(QLabel(key), widget)

            self.param_box = QGroupBox("Function parameters")
            self.param_box.setLayout(layout)
            main_layout.addWidget(self.param_box)

        # Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)
        main_layout.addWidget(self.button_box)

        self.show()
        self.setFixedWidth(max(400, self.width()))
        self.setFixedHeight(self.height())

    def validate_form(self):
        if self.name_input.text() != "":
            self.button_box.button(QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)

    def accept(self):
        col_list = config.data_config.datafile.get_data_columns()

        self.name = self.name_input.text()
        self.source = col_list[self.source_input.currentIndex()]
        for key in self.ret_func.keys():
            self.parameters[key] = self.ret_func[key]()
        self.close()


class FunctionController:
    @staticmethod
    def add(func_index):
        function = TimeFunction.__subclasses__()[func_index]()

        dialog = FunctionDialog(function.get_name(), function.get_parameters())
        dialog.exec()

        if dialog.name is None:
            return False

        data_conf = config.data_config
        ts = data_conf.datafile.get_series_to_process(dialog.source, dialog.name)
        fs = function.process_series(ts, dialog.parameters)

        if fs is None:
            dialogs.notify_function_error()
            return False

        data_conf.add_function(fs)
        return True

    @staticmethod
    def remove(rem_index):
        # Here we could ask for confirmation
        config.data_config.remove_function(rem_index)

    @staticmethod
    def get_functions():
        func_names = []
        for function in TimeFunction.__subclasses__():
            func_names.append(function().get_name())
        return func_names
