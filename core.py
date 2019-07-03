from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QColor, QPixmap
from PyQt5.QtWidgets import QSizePolicy, QPushButton, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
from matplotlib.colors import to_hex

from plotter import Plotter, get_nearest_index
from config import get_session  # TODO: replace with import config and remove get_session
from popup import RightClickMenu
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
        self.timestamp = None  # TODO: implement timestamp

    def clear(self):
        for plot in self.subplots:
            self.figure.delaxes(plot)
        del self.subplots[:]
        del self.plotters[:]

    def reset(self):
        data_config = get_session()
        data_config.read()
        self.clear()
        self.plot()

    def plot(self):
        data_config = get_session()

        datafile = data_config.datafile
        plot_set, normalize = data_config.get_plot_info()
        header = datafile.get_data_header()  # TODO: treat functions as data?

        n_sub = len(plot_set)
        grid = GridSpec(n_sub, 1, left=0.08, right=0.92, top=0.99, bottom=0.04, hspace=0.1)

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
        self.canvas.draw()

    def add_label(self, new_x):
        x1 = min(self.canvas.prev_x, new_x)
        x2 = max(self.canvas.prev_x, new_x)

        data_config = get_session()
        datafile = data_config.datafile
        label, color = data_config.get_current_label()

        if not self.timestamp:
            n_rows = datafile.df.shape[0]
            a = max(int(round(x1)), 0)
            b = max(int(round(x2)), 0)
            x1 = min(a, n_rows-1)
            x2 = min(b, n_rows-1)
            if x1 == x2:
                x1 = x1 - 0.5
                x2 = x2 + 0.5
        else:
            # TODO: implement minimum label width for x1 = x2
            # TODO: implement (function still doesn't exist)
            a = get_nearest_index(x1, self.timestamp)
            b = get_nearest_index(x2, self.timestamp)
            x1 = self.timestamp[a]
            x2 = self.timestamp[b]

        for plots in self.plotters:
            plots.add_rect(x1=x1, x2=x2, color=color)
        datafile.labels_list.append([label, (a, b)])

        self.canvas.modified = True
        self.canvas.refresh()

    def remove_label(self, event):
        clk = self.find_clicked_rect(event)
        if clk is None:
            return

        data_config = get_session()
        for plots in self.plotters:
            plots.remove_rect(clk)
        del data_config.datafile.labels_list[clk]

        self.canvas.modified = True
        self.canvas.refresh()

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
        data_config = get_session()
        for lab in data_config.datafile.labels_list:
            x1 = self.timestamp[lab[1][0]] if self.timestamp else lab[1][0]
            x2 = self.timestamp[lab[1][1]] if self.timestamp else lab[1][1]
            for plot in self.plotters:
                plot.add_rect(x1=x1, x2=x2, color=data_config.get_label_color(lab[0]))

    def manage_empty(self):
        x_lim = None
        for plot in self.plotters:
            if not plot.is_empty():
                x_lim = plot.plot.get_xlim()
                break
        for plot in self.plotters:
            if plot.is_empty() and x_lim:
                plot.plot.set_xlim(x_lim)

    def move_cursor(self, xs):
        for p in self.plotters:
            p.move_line(xs)
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

        self.setParent(window)
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
        self.draw()

    def same_index(self, new_x):
        if not self.core.timestamp:
            n_rows = get_session().datafile.df.shape[0]
            x1 = max(int(round(self.prev_x)), 0)
            x2 = max(int(round(new_x)), 0)
            x1 = min(x1, n_rows-1)
            x2 = min(x2, n_rows-1)
        else:
            # TODO: implement (function still doesn't exist)
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
                self.core.add_label(event.xdata)
                self.prev_x = None
        elif event.button == MOUSE_RIGHT:
            index = self.core.subplots.index(event.inaxes)
            popup = RightClickMenu(self, index, event)
            popup.exec_()
            self.core.clear()
            self.core.plot()

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

            self.core.add_label(event.xdata)
            self.prev_x = None

    def on_motion(self, event):
        if event.inaxes not in self.core.subplots:
            return

        xs = [event.xdata, event.xdata]
        self.core.move_cursor(xs)

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

    def save(self):
        data_config = get_session()
        if self.modified:
            data_config.save_file()
        data_config.save_config()
        self.modified = False

    def next_label(self):
        get_session().next_label()
        self.toolbar.update_label()

    def prev_label(self):
        get_session().prev_label()
        self.toolbar.update_label()

    def next_file(self):
        data_config = get_session()
        if self.modified or data_config.modified:
            answer = self.labeler.ask_to_continue()
            if not answer:
                return
        data_config.next_file()
        self.reset()

    def prev_file(self):
        data_config = get_session()
        if self.modified or data_config.modified:
            answer = self.labeler.ask_to_continue()
            if not answer:
                return
        data_config.prev_file()
        self.reset()

    def quit(self):
        data_config = get_session()
        if self.modified or data_config.modified:
            answer = dialogs.ask_to_continue()
            if not answer:
                return
        exit(0)


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
        data_config = get_session()
        text, color = data_config.get_current_label()

        image = QPixmap(15, 15).toImage()
        qt_color = QColor(to_hex(color))
        for x in range(image.width()):
            for y in range(image.height()):
                image.setPixelColor(x, y, qt_color)

        self.label_button.setText("  " + text)
        self.label_button.setIcon(QIcon(QPixmap.fromImage(image)))
