from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QColor, QPixmap
from PyQt5.QtWidgets import QSizePolicy, QPushButton, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
from matplotlib.colors import to_hex
import matplotlib.dates as mdates

from plotter import Plotter, get_nearest_index
from popup import RightClickMenu
import config
import dialogs

MOUSE_RIGHT = 3
MOUSE_LEFT = 1


# Implements the core functions of the application
class PlotCore:
    def __init__(self, plot_canvas):
        self.canvas = plot_canvas
        self.figure = plot_canvas.figure

        self.subplots = []
        self.plotters = []
        self.timestamp = None

    def clear(self):
        for plot in self.subplots:
            self.figure.delaxes(plot)
        del self.subplots[:]
        del self.plotters[:]

    def redraw(self):
        self.clear()
        self.plot()

    def reset(self):
        config.read_data_config()
        self.redraw()

    def plot(self):
        datafile = config.get_datafile()
        plot_set, normalize = config.get_plot_info()
        header = list(datafile.df)

        n_sub = len(plot_set)
        grid = GridSpec(n_sub, 1, left=0.08, right=0.92, top=0.99, bottom=0.04, hspace=0.1)
        self.timestamp = [mdates.date2num(date) for date in datafile.get_timestamp()]

        for i in range(n_sub):
            norm = bool(i in normalize)
            draw_set = [datafile.df[header[j]] for j in plot_set[i]]

            subplot = self.figure.add_subplot(grid[i])
            plotter = Plotter(subplot, draw_set, self.timestamp, norm)
            self.subplots.append(subplot)
            self.plotters.append(plotter)

            subplot.set_xticklabels([]) if i < n_sub-1 else None
            subplot.legend(loc=1, prop={'size': 8}) if draw_set else None

        self.manage_empty()
        self.insert_labels()
        self.canvas.refresh()

    def subplot_event(self, event_axes):
        subplot_number = 0
        #get subplot index where event is happening
        for subplot_index, subplot in enumerate(self.subplots):
            if event_axes == subplot:
                subplot_number = subplot_index
        return subplot_number

    def add_label(self, new_x, event_axis):
        x1 = min(self.canvas.prev_x, new_x)
        x2 = max(self.canvas.prev_x, new_x)

        datafile = config.get_datafile()
        label, color = config.get_current_label()

        if not self.timestamp:
            n_rows = datafile.get_shape()
            a = max(int(round(x1)), 0)
            b = max(int(round(x2)), 0)
            x1 = min(a, n_rows-1)
            x2 = min(b, n_rows-1)
            if x1 == x2:
                x1 = x1 - 0.5
                x2 = x2 + 0.5
        else:
            a = get_nearest_index(x1, self.timestamp)
            b = get_nearest_index(x2, self.timestamp)
            x1 = self.timestamp[a]
            x2 = self.timestamp[b]
            if x1 == x2:
                span = (self.timestamp[-1] - self.timestamp[0]) / (10 * len(self.timestamp))
                x1 = x1 - span
                x2 = x2 + span

        _, is_channel_independent = config.get_additional_options()
        if is_channel_independent == 'false':
            #add rectangle for each plot
            for plots in self.plotters:
                plots.add_rect(x1=x1, x2=x2, color=color)
        else:
            #add rectangle for one plot
            channel_index = self.subplot_event(event_axis)
            self.plotters[channel_index].add_rect(x1=x1, x2=x2, color=color)
            label = label + '_ch' + str(channel_index)

        datafile.labels_list.append([label, (a, b)])

        self.canvas.modified = True
        self.canvas.draw()

    def remove_label(self, event):
        clk = self.find_clicked_rect(event)
        if clk is None:
            return

        for plots in self.plotters:
            plots.remove_rect(clk)
        del config.get_datafile().labels_list[clk]

        self.canvas.modified = True
        self.canvas.draw()

    def find_clicked_rect(self, event):
        clicked_rects = None
        for plots in self.plotters:
            if event.inaxes == plots.plot:
                clicked_rects = plots.click_on_rect(event)
        index = [i for i, x in enumerate(clicked_rects) if x]
        if len(index) == 0:
            return None
        else:
            return index[-1]

    def insert_labels(self):
        datafile = config.get_datafile()
        for lab in datafile.labels_list:
            if self.timestamp:
                x1 = self.timestamp[lab[1][0]]
                x2 = self.timestamp[lab[1][1]]
                if x1 == x2:
                    span = (self.timestamp[-1] - self.timestamp[0]) / (10 * len(self.timestamp))
                    x1 = x1 - span
                    x2 = x2 + span
            else:
                x1 = lab[1][0]
                x2 = lab[1][1]
                if x1 == x2:
                    x1 = x1 - 0.5
                    x2 = x2 + 0.5

            for plot in self.plotters:
                plot.add_rect(x1=x1, x2=x2, color=config.get_label_color(lab[0]))

    def manage_empty(self):
        x_lim = None
        for plot in self.plotters:
            if not plot.is_empty():
                x_lim = plot.plot.get_xlim()
                break
        for plot in self.plotters:
            if plot.is_empty() and x_lim:
                plot.plot.set_xlim(x_lim)

    def move_cursor(self, xs, subplot_number):
        #move cursor
        _, is_channel_independent = config.get_additional_options()
        if is_channel_independent == 'false':
            for i in subplot_number:
                self.plotters[i].move_line(xs)
        else:
            self.plotters[subplot_number].move_line(xs)
        self.canvas.draw()

    def zoom_in(self):
        for p in self.plotters:
            p.zoom_in()
        self.canvas.draw()

    def zoom_out(self):
        for p in self.plotters:
            p.zoom_out()
        self.canvas.draw()


# Should handle the events and report the actions to the core
class PlotCanvas(FigureCanvas):
    def __init__(self, window):
        self.figure = Figure(figsize=(8, 6), dpi=100)
        FigureCanvas.__init__(self, self.figure)
        self.labeler = window

        self.setParent(window.scroll_canvas)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.core = PlotCore(self)
        self.toolbar = PlotToolbar(self, window)

        self.dragging = False
        self.modified = False
        self.prev_x = None

        self.figure.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        self.figure.canvas.mpl_connect('button_release_event', self.on_mouse_release)
        self.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)

    def init(self):
        self.toolbar.update_label()
        self.core.plot()

    def refresh(self):
        self.toolbar.update_label()
        self.draw()

    # noinspection PyPep8Naming
    def minimumSizeHint(self):
        return self.sizeHint()

    def figure_resize(self):
        plot_set, _ = config.get_plot_info()
        n_sub = len(plot_set)

        w, h = self.labeler.size().width(), self.labeler.size().height()
        sw = 20  # scrollbar width (plus margins)
        mh = config.get_plot_height()  # minimum subplot height

        toolbar_height = self.toolbar.sizeHint().height() / 100
        menubar_height = self.labeler.menubar.sizeHint().height() / 100
        eh = toolbar_height + menubar_height + 0.1  # extra height to be considered

        width = (w - sw) / 100
        height = max(n_sub * mh, (h / 100) - eh)

        self.figure.set_size_inches(width, height, forward=True)
        self.draw()

    def same_index(self, new_x):
        if not self.core.timestamp:
            datafile = config.get_datafile()
            n_rows = datafile.get_shape()
            x1 = max(int(round(self.prev_x)), 0)
            x2 = max(int(round(new_x)), 0)
            x1 = min(x1, n_rows-1)
            x2 = min(x2, n_rows-1)
        else:
            a = get_nearest_index(self.prev_x, self.core.timestamp)
            b = get_nearest_index(new_x, self.core.timestamp)
            x1 = self.core.timestamp[a]
            x2 = self.core.timestamp[b]
        return x1 == x2

    def on_mouse_press(self, event):
        if event.button not in (MOUSE_LEFT, MOUSE_RIGHT) or event.inaxes not in self.core.subplots:
            self.prev_x = None
            return

        if event.button == MOUSE_LEFT:
            if self.prev_x is None:
                self.prev_x = event.xdata
                self.dragging = True
            else:
                self.core.add_label(event.xdata, event.inaxes)
                self.prev_x = None
        elif event.button == MOUSE_RIGHT:
            index = self.core.subplots.index(event.inaxes)
            popup = RightClickMenu(self, index, event)
            popup.exec_()
            if popup.reload:
                self.core.redraw()

    def on_mouse_release(self, event):
        if event.button not in (MOUSE_LEFT, MOUSE_RIGHT) or event.inaxes not in self.core.subplots:
            self.prev_x = None
            return

        if self.prev_x is None:
            return

        if event.button == MOUSE_LEFT:
            if self.same_index(event.xdata):
                self.dragging = False
                return

            self.core.add_label(event.xdata, event.inaxes)
            self.prev_x = None

    def on_motion(self, event):
        subplot_number = range(0, len(self.core.subplots))

        if event.inaxes not in self.core.subplots:
            return

        #if channels are independend, move line just for one channel
        _, is_channel_independent = config.get_additional_options()
        if is_channel_independent == 'true':
            #get subplot number
            subplot_number = self.core.subplot_event(event.inaxes)

        xs = [event.xdata, event.xdata]
        self.core.move_cursor(xs, subplot_number)

    def on_key(self, event):
        key = event.key()
        if key == Qt.Key_Z:
            self.core.zoom_in()
        elif key == Qt.Key_X:
            self.core.zoom_out()
        elif key == Qt.Key_Up:
            self.prev_label()
        elif key == Qt.Key_Down:
            self.next_label()
        elif key == Qt.Key_Right:
            self.next_file()
        elif key == Qt.Key_Left:
            self.prev_file()
        elif key == Qt.Key_Escape:
            self.quit()

    def reset(self):
        self.prev_x = None
        self.modified = False
        self.core.reset()
        self.labeler.update_dimensions()
        self.labeler.update_functions()

    def save(self):
        if self.modified:
            config.save_file()
        config.save_data_config()
        self.modified = False

    def next_label(self):
        config.next_label()
        self.toolbar.update_label()

    def prev_label(self):
        config.prev_label()
        self.toolbar.update_label()

    def next_file(self):
        if self.modified or config.is_modified():
            if config.get_autosave():
                self.save()
            else:
                answer = dialogs.ask_to_continue()
                if not answer:
                    return
        config.next_file()
        self.reset()

    def prev_file(self):
        if self.modified or config.is_modified():
            if config.get_autosave():
                self.save()
            else:
                answer = dialogs.ask_to_continue()
                if not answer:
                    return
        config.prev_file()
        self.reset()

    def quit(self):
        if self.modified or config.is_modified():
            if config.get_autosave():
                self.save()
            else:
                answer = dialogs.ask_to_continue()
                if not answer:
                    return
        exit(0)


# noinspection PyArgumentList
class PlotToolbar(NavigationToolbar):
    def __init__(self, canvas, root):
        self.toolitems = (
            ('Home', 'Reset original view', 'home', 'home'),
            (None, None, None, None),
            ('Back', 'Previous file', 'back', 'back'),
            ('Forward', 'Next file', 'forward', 'forward'),
            (None, None, None, None),
            ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
            ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
            ('Save', 'Save the figure', 'filesave', 'save_figure')
        )
        super().__init__(canvas, root, False)
        self.label_button = None
        self.init()

    def init(self):
        self._actions['back'].setEnabled(True)
        self._actions['forward'].setEnabled(True)

        self.label_button = QPushButton("", self)
        self.label_button.setFocusPolicy(Qt.NoFocus)
        self.label_button.setStyleSheet("padding: 10px 12px; height: 13px;")
        self.label_button.clicked.connect(self.canvas.next_label)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.addWidget(spacer)
        self.addWidget(self.label_button)
        self.layout().setSpacing(5)

    def home(self):
        self.canvas.reset()

    def back(self):
        self.canvas.prev_file()

    def forward(self):
        self.canvas.next_file()

    def update_label(self):
        text, color = config.get_current_label()

        image = QPixmap(15, 15).toImage()
        qt_color = QColor(to_hex(color))
        for x in range(image.width()):
            for y in range(image.height()):
                image.setPixelColor(x, y, qt_color)

        self.label_button.setText("  " + text)
        self.label_button.setIcon(QIcon(QPixmap.fromImage(image)))
