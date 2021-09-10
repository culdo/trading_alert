import numpy as np

from trading_alert.base.single_line import SingleLine


class LineDrawer:

    def __init__(self, pp):
        self.is_move_done = False
        self.lines = []
        self.fig = pp.fig
        self.ax = pp.ax1
        self.pp = pp
        self._min_d = None
        self.selected_line = None

    def draw_tline(self):
        xy = self.fig.ginput(n=2)
        x = [p[0] for p in xy]
        y = [p[1] for p in xy]
        line = self.ax.plot(x, y)

        self.selected_line = SingleLine(self.pp, line[0], SingleLine.TLINE, annotation_point=xy[-1])
        self.lines.append(self.selected_line)

    def draw_hline(self):
        xy = self.fig.ginput(n=1)

        y = [p[1] for p in xy]
        line = self.ax.axhline(y)

        self.selected_line = SingleLine(self.pp, line, SingleLine.HLINE, annotation_point=xy[-1])
        self.lines.append(self.selected_line)

    def draw_vline(self):
        xy = self.fig.ginput(n=1)

        x = [p[0] for p in xy]
        line = self.ax.axvline(x)

        self.selected_line = SingleLine(self.pp, line, SingleLine.VLINE)
        self.lines.append(self.selected_line)

    def restore_notify(self):
        for line in self.lines:
            if line.notify_msg:
                line.set_win10_toast()

    def get_clicked_line(self):
        xy = self.fig.ginput(n=1)
        p3 = np.array(xy[0])
        for line in self.lines:
            d = line.calc_point_dist(p3)
            if self._min_d is None or d < self._min_d:
                self._min_d = d
                self.selected_line = line
        self._min_d = None
        return self.selected_line

    def move_line_end(self):
        while not self.is_move_done:
            xy = self.fig.ginput(n=1)
            if self.is_move_done:
                print("move line done")
                break
            p3 = np.array(xy[0])
            self.selected_line.move_line_end(p3)
            self.fig.canvas.draw()
        self.is_move_done = False

    def remove_clicked(self):
        self.selected_line.remove(self.lines)

    def set_alert(self):
        if not self.selected_line:
            print("Please click a line")
        self.selected_line.set_alert()

    def unset_alert(self):
        self.selected_line.unset_alert()

    def has_alert(self):
        for line in self.lines:
            if line.alert_equation:
                return True
        return False
