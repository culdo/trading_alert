from datetime import datetime

import numpy as np
import pandas as pd
import mplfinance as mpf
from binance.client import Client
import json


from trading_alert.util.line_drawer import LineDrawer
from trading_alert.util.time_tool import get_before_time

specify_date = datetime(year=2021, month=8, day=29, hour=1, minute=30).astimezone().strftime("%d %B %Y %H:%M %z")


class PricePlot:
    def __init__(self, start_str, symbol="BTCUSDT", interval='15m', theme="white"):
        if theme == "black":
            self.style = mpf.make_mpf_style(base_mpf_style='binance', base_mpl_style="dark_background",
                                            rc={'font.family': 'Segoe UI Emoji'})
        else:
            self.style = mpf.make_mpf_style(base_mpf_style='binance', rc={'font.family': 'Segoe UI Emoji'})
        self.theme = theme
        self.is_show_volume = True
        self._load_client()

        self.symbol = symbol
        self.interval = interval
        self.start_str = start_str

        self.data = self.get_binance_df()
        self._creat_plot()
        self.fig.canvas.mpl_connect('key_press_event', self.on_press)
        self.ld = LineDrawer(self)

    def get_data_index(self):
        return self.data.index

    def _load_client(self):
        with open("../api_key.json") as f:
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
                                  tight_layout=True, style=self.style)
        self.ax1 = axes[0]
        self.ax1.get_xaxis().label.set_visible(False)
        self.ax1.get_yaxis().label.set_visible(False)
        self.price_line = axes[1].get_lines()
        self.ax3 = axes[2]
        self.ax3.get_xaxis().label.set_visible(False)
        self.ax3.get_yaxis().label.set_visible(False)

        if self.theme == "black":
            self.ax1.set_facecolor("black")
            self.ax3.set_facecolor("black")

    def on_press(self, event):
        if event.key in "xmat-1u=zd":
            # get clicked line
            if event.key == 'x':
                self.ld.get_clicked_line()
            # move clicked line
            elif event.key == 'm':
                self.ld.move_line_end()
            # done move
            elif event.key == ',':
                self.ld.is_move_done = True
            # set alert on click draw line
            elif event.key == 'a':
                self.ld.set_alert()
            # draw trend line
            elif event.key == 't':
                self.ld.draw_tline()
            # draw horizontal line
            # because "h" key used as default shortcut of reset view, we use "-" key as shortcut
            elif event.key == '-':
                self.ld.draw_hline()
            # draw vertical line
            elif event.key == '1':
                self.ld.draw_vline()
            # refresh plot
            elif event.key == 'u':
                self.refresh_plot()
            # open/close volume panel
            elif event.key == '=':
                self.toggle_volume_panel()
            # delete clicked line
            elif event.key == 'd':
                self.ld.remove_clicked()
            # delete clicked alert
            elif event.key == 'z':
                self.ld.unset_alert()

            self.fig.canvas.draw()

    def toggle_volume_panel(self):
        if self.is_show_volume:
            self.ax3.set_visible(False)
            # values from mplfinance\_panels.py:207
            self.ax1.set_position([0.108, 0.108 + 0, 0.868, 0.8632])
            self.ax1.tick_params(axis='x', labelbottom=True, rotation=45)
        else:
            self.ax3.set_visible(True)
            # values from mplfinance\_panels.py:207
            self.ax1.set_position([0.108, 0.108 + 0.24662857142857142, 0.868, 0.6165714285714285])
            self.ax1.tick_params(axis='x', labelbottom=False)
        self.is_show_volume = not self.is_show_volume

    def refresh_plot(self, autoscale=False):
        self.data = self.get_binance_df()
        self.ax1.collections.clear()
        self.ax3.clear()
        mpf.plot(self.data, ax=self.ax1, volume=self.ax3, type='candle',
                 style="binance")
        if autoscale:
            self.ax1.autoscale()
            self.ax3.autoscale()


if __name__ == '__main__':
    pp = PricePlot(get_before_time(minutes=30))
