from tkinter.simpledialog import askstring

import numpy as np
from matplotlib.lines import Line2D

from trading_alert.base.alert_equation import AlertEquation
from trading_alert.util.win10_toast import Win10Toast


class SingleLine:
    TLINE = 1
    HLINE = 2
    VLINE = 3

    def __init__(self, symbol, plt_line, line_type, annotation_point=None):
        self.enable_color = "red"
        self.is_debug = False
        self.symbol = symbol
        self.plt_line = plt_line
        self.line_type = line_type
        self.annotation_point = annotation_point
        self.alert_equation = None
        self.alert_annotation = None
        self.notify_msg = None
        self.win10_toast = None

    def calc_point_dist(self, p3):
        if self.line_type is SingleLine.TLINE:
            p1 = np.array(self.plt_line.get_xydata()[0])
            p2 = np.array(self.plt_line.get_xydata()[1])
            d = np.linalg.norm(np.cross(p2 - p1, p1 - p3)) / np.linalg.norm(p2 - p1)
        elif self.line_type is SingleLine.HLINE:
            d = abs(self.plt_line.get_ydata()[0][0] - p3[1])
        elif self.line_type is SingleLine.VLINE:
            d = abs(self.plt_line.get_xdata()[0][0] - p3[0])
        else:
            raise TypeError("Line type error!")

        return d

    def move_line_end(self, p3):
        if self.line_type is SingleLine.TLINE:
            p1 = np.array(self.plt_line.get_xydata()[0])
            p2 = np.array(self.plt_line.get_xydata()[1])
            if np.linalg.norm(p3 - p1) < np.linalg.norm(p3 - p2):
                self.plt_line.set_data(*zip(p3, p2))
            else:
                self.plt_line.set_data(*zip(p1, p3))
        elif self.line_type is SingleLine.HLINE:
            data = [[0, 1],
                    [[p3[1]], [p3[1]]]]
            self.plt_line.set_data(data)
        elif self.line_type is SingleLine.VLINE:
            data = [[[p3[0]], [p3[0]]],
                    [0, 1]]
            self.plt_line.set_data(data)
        else:
            AssertionError("Line type error!")

        if self.alert_equation:
            self.alert_annotation.set_position(p3)
            self.alert_annotation.set_color(self.enable_color)
            self.alert_equation = AlertEquation(self)

    def remove(self, lines):
        if isinstance(self.plt_line, list):
            self.plt_line.pop().remove()
        elif isinstance(self.plt_line, Line2D):
            self.plt_line.remove()
        else:
            raise TypeError
        self.unset_alert()

        lines.remove(self)
        del self

    def set_alert(self):
        if self.alert_annotation:
            print("重複設定鬧鐘!!!")
            return

        self.notify_msg = askstring("Trading Alert", "觸發時通知訊息")
        if not self.is_debug:
            self.set_win10_toast()

        self.add_annotation()
        self.alert_equation = AlertEquation(self)

    def set_win10_toast(self):
        self.win10_toast = Win10Toast(self.symbol + " " + self.notify_msg)

    def add_annotation(self):
        ax = self.plt_line.axes
        self.alert_annotation = ax.annotate('⏰',
                                            xy=self.annotation_point, xycoords='data', color=self.enable_color)

    def unset_alert(self):
        if self.alert_equation:
            self.alert_annotation.remove()
            self.alert_equation = None
            self.notify_msg = None
