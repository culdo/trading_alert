from threading import Thread

import numpy as np

from trading_alert.base.single_line import SingleLine
import tkinter as tk
from tkinter import font


class LineDrawer:

    def __init__(self, pp):
        self.is_move_done = False
        self.lines = []
        self.fig = pp.fig
        self.ax = pp.ax1
        self.pp = pp
        self.min_d = None
        self.clicked_line = None
        self.win10_toast = None
        self.root = tk.Tk()
        self.root.withdraw()
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family='Courier', size=20)
        self.root.option_add("*Font", default_font)

    def draw_tline(self):
        xy = self.fig.ginput(n=2)
        x = [p[0] for p in xy]
        y = [p[1] for p in xy]
        line = self.ax.plot(x, y)

        self.clicked_line = SingleLine(line[0], SingleLine.TLINE, annotation_point=xy[-1])
        self.lines.append(self.clicked_line)

    def draw_hline(self):
        xy = self.fig.ginput(n=1)

        y = [p[1] for p in xy]
        line = self.ax.axhline(y)

        self.clicked_line = SingleLine(line, SingleLine.HLINE, annotation_point=xy[-1])
        self.lines.append(self.clicked_line)

    def draw_vline(self):
        xy = self.fig.ginput(n=1)

        x = [p[0] for p in xy]
        line = self.ax.axvline(x)

        self.clicked_line = SingleLine(line, SingleLine.VLINE)
        self.lines.append(self.clicked_line)

    def get_clicked_line(self):
        xy = self.fig.ginput(n=1)
        p3 = np.array(xy[0])
        for line in self.lines:
            d = line.calc_point_dist(p3)
            if self.min_d is None or d < self.min_d:
                self.min_d = d
                self.clicked_line = line
        self.min_d = None
        return self.clicked_line

    def move_line_end(self):
        while not self.is_move_done:
            xy = self.fig.ginput(n=1)
            p3 = np.array(xy[0])
            self.clicked_line.move_line_end(p3)
            self.fig.canvas.draw()
        self.is_move_done = False

    def remove_clicked(self):
        self.clicked_line.remove(self.lines)

    def set_alert(self):
        if not self.clicked_line:
            print("Please click a line")
        self.clicked_line.set_alert(self.pp.symbol)

    def unset_alert(self):
        self.clicked_line.unset_alert()

    def when_alert_triggered(self, price, cb_alert):
        for line in self.lines:
            if line.alert_equation and line.alert_equation.is_alert_triggered(price, self.pp.data.index):
                cb_alert()
                if not line.is_debug:
                    line.win10_toast.notify()

    def has_alert(self):
        for line in self.lines:
            if line.alert_equation:
                return True
        return False
