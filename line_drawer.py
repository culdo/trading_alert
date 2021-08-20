import mplfinance as mpf


class LineDrawer:

    def __init__(self):
        self.lines = []

    def draw_line(self, fig, ax):
        xy = fig.ginput(n=2)

        print(xy)
        x = [p[0] for p in xy]
        y = [p[1] for p in xy]
        line = ax.plot(x, y)
        ax.figure.canvas.draw()

        self.lines.append(line)
