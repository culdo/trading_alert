import numpy as np
import pandas as pd
import mplfinance as mpf
from binance.client import Client
import json

from matplotlib import pyplot as plt
from matplotlib.lines import Line2D

from line_drawer import LineDrawer


class PricePlot:
    def __init__(self, symbol="BTCUSDT", interval='1m', start_str='22 August 2021 4:00 pm +0800'):
        self.is_show_volume = True
        self._load_client()

        self.symbol = symbol
        self.interval = interval
        self.start_str = start_str

        self.data = self.get_binance_df()
        self._creat_plot()
        self.fig.canvas.mpl_connect('key_press_event', self.on_press)
        self.ld = LineDrawer(self.fig, self.ax1)
        mpf.show()

    def _load_client(self):
        with open("api_key.json") as f:
            api_keys = json.load(f)
        self.client = Client(**api_keys)

    def get_binance_df(self):
        klines = np.array(self.client.get_historical_klines(self.symbol, self.interval, start_str=self.start_str))
        df = pd.DataFrame(klines.reshape(-1, 12), dtype=float, columns=('Open Time',
                                                                        'Open',
                                                                        'High',
                                                                        'Low',
                                                                        'Close',
                                                                        'Volume',
                                                                        'Close time',
                                                                        'Quote asset volume',
                                                                        'Number of trades',
                                                                        'Taker buy base asset volume',
                                                                        'Taker buy quote asset volume',
                                                                        'Ignore'))

        df['Open Time'] = pd.to_datetime(df['Open Time'], unit='ms')
        df = df.set_index('Open Time')
        return df

    def _creat_plot(self):
        self.fig, axes = mpf.plot(self.data, returnfig=True, figratio=(10, 6), type="candle",
                                  volume=True,
                                  title=f"Price of {self.symbol}",
                                  tight_layout=True, style="binance")
        self.ax1 = axes[0]
        self.ax3 = axes[2]

    def on_press(self, event):
        if event.key in "t-vr=u":
            # draw trend line
            if event.key == 't':
                self.ld.draw_tline()
            # draw horizontal line
            # because "h" key used as default shortcut of reset view, we use "-" key as shortcut
            elif event.key == '-':
                self.ld.draw_hline()
            # draw vertical line
            elif event.key == 'v':
                self.ld.draw_vline()
            # refresh plot
            elif event.key == 'r':
                self.refresh_plot()
            # open/close volume panel
            elif event.key == '=':
                if self.is_show_volume:
                    self.ax3.set_visible(False)
                    # values from mplfinance\_panels.py:207
                    self.ax1.set_position([0.108, 0.108+0, 0.868, 0.8632])
                    self.ax1.tick_params(axis='x', labelbottom=True, rotation=45)
                else:
                    self.ax3.set_visible(True)
                    # values from mplfinance\_panels.py:207
                    self.ax1.set_position([0.108, 0.108+0.24662857142857142, 0.868, 0.6165714285714285])
                    self.ax1.tick_params(axis='x', labelbottom=False)
                self.is_show_volume = not self.is_show_volume
            # undo
            elif event.key == 'u':
                line = self.ld.lines.pop()
                if isinstance(line, list):
                    line.pop().remove()
                elif isinstance(line, Line2D):
                    line.remove()
                else:
                    raise TypeError

            self.fig.canvas.draw()

    def refresh_plot(self):
        self.data = self.get_binance_df()
        self.ax1.clear()
        self.ax3.clear()
        mpf.plot(self.data, ax=self.ax1, volume=self.ax3, type='candle',
                 style="binance")
        self.ax1.autoscale()
        self.ax3.autoscale()


if __name__ == '__main__':
    pp = PricePlot()
