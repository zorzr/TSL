from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import config


class PlotMenuAction(QAction):
    def __init__(self, name, root, value):
        super().__init__(name, root)
        self.value = value
        self.plot_menu = root

        self.setCheckable(True)
        self.triggered.connect(self.report)

    def report(self):
        self.plot_menu.action(self.value)


class RightClickMenu(QMenu):
    def __init__(self, plot_canvas, plot_index, click_event):
        super().__init__(plot_canvas)
        self.canvas = plot_canvas
        self.click_event = click_event
        self.plot_index = plot_index

        self.plot_set = None
        self.normalize = None

        self.move(QCursor.pos())
        self.init()

    def init(self):
        # Remove label (if there is a label under the cursor)
        if self.canvas.core.find_clicked_rect(self.click_event) is not None:
            remove_label = QAction('Remove label', self)
            remove_label.triggered.connect(lambda: self.canvas.core.remove_label(self.click_event))
            self.addAction(remove_label)
            self.addSeparator()

        # Plot content (allows to customize the plotted series)
        datafile = config.data_config.datafile
        data_columns = datafile.get_data_columns()
        self.plot_set, self.normalize = config.data_config.get_plot_info()

        plot_menu = self.addMenu("Plot content")
        for i, col in enumerate(datafile.get_data_header()):
            plot_action = PlotMenuAction(col, self, i)
            plot_menu.addAction(plot_action)

            if data_columns[i] in self.plot_set[self.plot_index]:
                plot_action.setChecked(True)

        # Normalize (allows to display the series by ignoring their scale)
        normalize_plot = QAction("Normalize", self)
        normalize_plot.triggered.connect(self.normalize_plot)
        normalize_plot.setCheckable(True)
        self.addAction(normalize_plot)

        if self.plot_index in self.normalize:
            normalize_plot.setChecked(True)

        # Add empty plot (before or after the current)
        self.addSeparator()
        add_menu = self.addMenu("Add plot")
        before = QAction("Before", self)
        after = QAction("After", self)
        add_menu.addAction(before)
        add_menu.addAction(after)
        before.triggered.connect(self.add_before)
        after.triggered.connect(self.add_after)

        # Clear or remove selected plot
        clear = QAction("Clear plot", self)
        remove = QAction("Remove plot", self)
        clear.triggered.connect(self.clear_plot)
        remove.triggered.connect(self.remove_plot)
        self.addAction(clear)
        self.addAction(remove)

        # Reset the view of all plots to the default one
        self.addSeparator()
        reset_all = QAction("Reset all plots", self)
        reset_all.triggered.connect(self.reset_all)
        self.addAction(reset_all)

    def action(self, value):
        data_columns = config.data_config.datafile.get_data_columns()
        if data_columns[value] in self.plot_set[self.plot_index]:
            self.plot_set[self.plot_index].remove(data_columns[value])
        else:
            self.plot_set[self.plot_index].append(data_columns[value])
        config.data_config.set_plot_info(self.plot_set, self.normalize)

    def normalize_plot(self):
        if self.plot_index in self.normalize:
            self.normalize.remove(self.plot_index)
        else:
            self.normalize.append(self.plot_index)
            self.normalize.sort()
        config.data_config.set_plot_info(self.plot_set, self.normalize)

    def add_before(self):
        self.plot_set.insert(self.plot_index, [])
        self.normalize = [i if i < self.plot_index else i+1 for i in self.normalize[:]]
        config.data_config.set_plot_info(self.plot_set, self.normalize)

    def add_after(self):
        self.plot_set.insert(self.plot_index + 1, [])
        self.normalize = [i+1 if i > self.plot_index else i for i in self.normalize[:]]
        config.data_config.set_plot_info(self.plot_set, self.normalize)

    def clear_plot(self):
        self.plot_set[self.plot_index] = []
        config.data_config.set_plot_info(self.plot_set, self.normalize)

    def remove_plot(self):
        del self.plot_set[self.plot_index]
        self.normalize.remove(self.plot_index) if self.plot_index in self.normalize else None
        self.normalize = [i if i < self.plot_index else i-1 for i in self.normalize[:]]
        config.data_config.set_plot_info(self.plot_set, self.normalize)

    def reset_all(self):
        self.plot_set = [[i] for i in config.data_config.datafile.get_data_columns()]
        self.normalize = []
        config.data_config.set_plot_info(self.plot_set, self.normalize)
