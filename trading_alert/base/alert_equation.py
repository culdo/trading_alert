from trading_alert.util.time_tool import calc_headless_delta


class AlertEquation:
    def __init__(self, single_line):
        self.single_line = single_line
        self.pp = single_line.pp
        self.diff = None
        self.is_been_triggered = False
        self.is_debug = False

        self.line_type = single_line.line_type
        self.HLINE = single_line.HLINE
        self._gen_equation(single_line.plt_line)

    def _gen_equation(self, line):
        if self.is_debug:
            print(line.get_xdata())
            print(line.get_ydata())
        if self.line_type is self.HLINE:
            self.m = 0
            self.b = line.get_ydata()[0][0]
        else:
            self.x1, self.x2 = line.get_xdata()
            self.y1, self.y2 = line.get_ydata()
            self.m = (self.y2 - self.y1) / (self.x2 - self.x1)
            self.b = self.y1 - (self.m * self.x1)

            self.x_end = sorted([self.x1, self.x2])[-1]

    def check_x_range(self, x):
        if self.line_type is self.HLINE or x < self.x_end:
            return True
        else:
            return False

    def is_alert_triggered(self, touch_threshold=None):
        if self.is_been_triggered:
            return False

        curr_x = len(self.pp.data.index) - 1
        alert_y = curr_x * self.m + self.b

        prev_diff = self.diff
        self.diff = alert_y - self.pp.price
        if self.is_debug:
            print(f"next_y - price: {alert_y} - {self.pp.price}")
            print(f"next_y diff:{self.diff}")
            print()
        is_crossed = prev_diff and (
                    (self.diff < 0 < prev_diff) or (self.diff > 0 > prev_diff))
        # is_touched = abs(self.diff) < touch_threshold
        if self.check_x_range(curr_x) and is_crossed:
            self.is_been_triggered = True
            return True


