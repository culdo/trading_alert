import mplfinance as mpf


class LineDrawer:

    def __init__(self, fig, ax):
        self.lines = []
        self.fig = fig
        self.ax = ax

    def draw_tline(self):
        xy = self.fig.ginput(n=2)

        x = [p[0] for p in xy]
        y = [p[1] for p in xy]
        line = self.ax.plot(x, y)

        self.lines.append(line)

    def draw_hline(self):
        xy = self.fig.ginput(n=1)

        y = [p[1] for p in xy]
        line = self.ax.axhline(y)

        self.lines.append(line)

    def draw_vline(self):
        xy = self.fig.ginput(n=1)

        x = [p[0] for p in xy]
        line = self.ax.axvline(x)

        self.lines.append(line)
