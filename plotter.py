import lttb
import numpy as np
import pandas as pd
from matplotlib import patches as p
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

N_MAX = 4000


def get_nearest_index(x, values):
    prev = np.inf
    for i, v in enumerate(values):
        delta = abs(v - x)
        if delta < prev:
            prev = delta
        else:
            return i-1
    return len(values)-1


class Plotter:
    def __init__(self, plot, draw_set, timestamp, norm):
        self.plot = plot
        self.draw_set = draw_set
        self.timestamp = timestamp
        self.normalize = norm

        self.rects = []  # one for each label
        self.line = self.plot.axvline(x=0, linestyle='dashed', color='black', linewidth=1)

        self.y = 0
        self.h = 1

        if self.is_empty():
            plot.get_yaxis().set_visible(False)
            self.manage_timestamp() if self.timestamp else None
        else:
            self.draw()

    def is_empty(self):
        return not self.draw_set

    def is_sampled(self):
        if not self.draw_set:
            return False
        return self.draw_set[0].shape[0] > N_MAX

    def add_rect(self, x1, x2, color='C0'):
        w = x2 - x1
        new_r = p.Rectangle(xy=(x1, self.y), width=w, height=self.h, color=color, alpha=0.2)
        self.rects.append(new_r)
        self.plot.add_patch(new_r)

    def remove_rect(self, index):
        self.rects[index].remove()
        del self.rects[index]

    def click_on_rect(self, event):
        rect_list = []
        for r in self.rects:
            rlim = [r.get_x(), r.get_x()+r.get_width()]
            rect_list.append(rlim[0] <= event.xdata <= rlim[1])  # True if within rect limits
        return rect_list

    def draw(self):
        point_set = self.process_series()
        point_set = [(ts-ts.min())/(ts.max()-ts.min()) for ts in point_set] if self.normalize else point_set
        point_set = self.insert_timestamp(point_set) if self.timestamp else point_set

        [self.plot.plot(df, label=df.name) for df in point_set]
        self.manage_timestamp() if self.timestamp else None

        # Moves cursor above the time series
        self.plot.add_line(self.plot.get_lines()[0])

        ylim = self.plot.get_ylim()
        self.h = abs(ylim[1] - ylim[0])
        self.y = min(ylim)

    def zoom(self, factor):
        center_on = self.line.get_xdata()[0]
        xlim = self.plot.axes.get_xlim()
        dim = xlim[1] - xlim[0]

        new_xlim_min = center_on + (xlim[0] - center_on) / factor
        new_xlim_max = new_xlim_min + dim / factor

        # Requires special handling if downsampled: not all points can be shown at once
        if self.is_sampled():
            self.plot.clear()
            self.line = self.plot.axvline(x=center_on, linestyle='dashed', color='black', linewidth=1)

            zoomed_set = self.process_zoom([new_xlim_min, new_xlim_max])
            zoomed_set = self.insert_timestamp(zoomed_set) if self.timestamp else zoomed_set

            [self.plot.plot(df) for df in zoomed_set]
            self.manage_timestamp() if self.timestamp else None
            self.plot.lines.append(self.plot.lines.pop(0))

        self.plot.set_xlim([new_xlim_min, new_xlim_max])

    def zoom_out(self):
        self.zoom(0.5)

    def zoom_in(self):
        self.zoom(2)

    def move_line(self, xs):
        self.line.set_xdata(xs)
        self.adjust_legend()

    def adjust_legend(self):
        if self.is_empty():
            return
        x = self.line.get_xdata()[0]
        xlim = self.plot.get_xlim()
        half = xlim[0] + (xlim[1] - xlim[0])/2
        if x < half:
            self.plot.legend(loc=1, prop={'size': 8})
        else:
            self.plot.legend(loc=2, prop={'size': 8})

    def process_series(self):
        n_rows = self.draw_set[0].shape[0]

        if n_rows <= N_MAX:
            return self.draw_set

        sampled_set = []
        for ts in self.draw_set:
            out = lttb.downsample(np.array([ts.index, ts]).T, N_MAX)
            sampled_set.append(pd.Series(out[:, 1], index=out[:, 0], name=ts.name))
        return sampled_set

    def process_zoom(self, xlim):
        a = get_nearest_index(xlim[0], self.timestamp) if self.timestamp else max(int(xlim[0]), 0)
        b = get_nearest_index(xlim[1], self.timestamp) if self.timestamp else min(int(xlim[1])+1, len(self.draw_set[0]))
        zoomed_set = [df.iloc[a:b] for df in self.draw_set]

        if b - a <= N_MAX:
            return zoomed_set

        sampled_set = []
        for ts in zoomed_set:
            out = lttb.downsample(np.array([ts.index, ts]).T, N_MAX)
            sampled_set.append(pd.Series(out[:, 1], index=out[:, 0], name=ts.name))
        return sampled_set

    def insert_timestamp(self, point_set):
        for ts in point_set:
            ts.index = [self.timestamp[int(i)] for i in ts.index] if self.is_sampled() else self.timestamp
        return point_set

    def manage_timestamp(self):
        span = self.timestamp[-1] - self.timestamp[0]
        a = self.timestamp[0] - 0.05 * span
        b = self.timestamp[-1] + 0.05 * span

        self.plot.set_xlim(a, b)
        locator, formatter = self.format_timestamp(span)
        self.plot.xaxis.set_major_formatter(formatter)
        self.plot.xaxis.set_major_locator(locator)

    @staticmethod
    def format_timestamp(span):
        if span > 30:
            n_ticks = 6
            form = '%d/%m/%Y'
        elif span > 1:
            n_ticks = 6
            form = '%d/%m %H:%M'
        elif span > 1/24:
            n_ticks = 8
            form = '%H:%M'
        elif span > 1/1440:
            n_ticks = 6
            form = '%H:%M:%S'
        else:
            n_ticks = 8
            form = '%S:%f'

        locator = ticker.MaxNLocator(n_ticks)
        formatter = mdates.DateFormatter(form)
        return locator, formatter
