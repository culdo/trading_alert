class LineEquation:
    def __init__(self, single_line):
        self.single_line = single_line
        self.curr_x = None
        self.diff = None
        self.is_been_triggered = False

        self.line_type = single_line.line_type
        self.HLINE = single_line.HLINE
        self._gen_equation(single_line.plt_line)

    def _gen_equation(self, line):
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

    def is_alert_triggered(self, price, data_index, touch_threshold=2):
        prev_x = self.curr_x
        self.curr_x = len(data_index) - 1

        alert_x = self.curr_x
        alert_y = alert_x * self.m + self.b

        prev_diff = self.diff
        self.diff = alert_y - price
        print(f"prev_x curr_x: {prev_x} {self.curr_x}")
        print(f"next_y - price: {alert_y} - {price}")
        print(f"next_y diff:{self.diff}")
        print()
        is_same_bar = prev_x == self.curr_x
        is_crossed = prev_diff and is_same_bar and (
                    (self.diff < 0 < prev_diff) or (self.diff > 0 > prev_diff))
        is_touched = abs(self.diff) < touch_threshold
        if self.check_x_range(alert_x) and (is_crossed or is_touched) and not self.is_been_triggered:
            self.is_been_triggered = True
            return True
        else:
            return False
