import time
from datetime import datetime, timedelta
from threading import Thread

import matplotlib
import numpy as np
import pandas as pd
import mplfinance as mpf
import pickle as pk

from mplfinance._styles import _apply_mpfstyle

from trading_alert.base.line_drawer import LineDrawer
from trading_alert.util.time_tool import calc_headless_delta
# matplotlib.use('tkagg')

specify_date = datetime(year=2021, month=8, day=29, hour=1, minute=30).astimezone().strftime("%d %B %Y %H:%M %z")


class PricePlot:
    def __init__(self, ta, symbol="BTCUSDT", interval='15m', theme="white"):
        self.curr_time = None
        if theme == "black":
            self.style = mpf.make_mpf_style(base_mpf_style='binance', base_mpl_style="dark_background",
                                            rc={'font.family': 'Segoe UI Emoji'})
        else:
            self.style = mpf.make_mpf_style(base_mpf_style='binance', rc={'font.family': 'Segoe UI Emoji'})
        self.theme = theme
        self.is_show_volume = True
        self.is_auto_update = True
        self.client = ta.client
        self.ta = ta
        self.interval = interval
        self.price = None
        self.symbol = symbol
        self.start_str = ta.start_str

        self._init_data_vars()

        self.update_delta_x()
        self._creat_plot()
        # self.fig.canvas = self.ta.main_window.canvas
        # self.fig.canvas.mpl_connect('key_press_event', self.on_press)
        self.ld = LineDrawer(self)
        self.is_delta_updated = False

    def restore(self):
        self._init_data_vars()

        self.update_delta_x()
        _apply_mpfstyle(self.style)
        # self.restore_mpl_event()
        self.ld.restore_notify()

    def _init_data_vars(self):
        self.data = self.get_binance_df()
        self.delta_x = 0
        self.init_data_x = self.data.index
        self.high = self.data.iloc[-1, 1]
        self.low = self.data.iloc[-1, 2]
        self.prev_delta = None

    def restore_mpl_event(self):
        self.ta.main_window.canvas.mpl_connect('key_press_event', self.on_press)

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
        self._add_account_info()
        self.ax3 = axes[2]
        self.ax3.get_xaxis().label.set_visible(False)
        self.ax3.get_yaxis().label.set_visible(False)

        if self.theme == "black":
            self.ax1.set_facecolor("black")
            self.ax3.set_facecolor("black")

    def _add_account_info(self):
        balance = self.client.get_asset_balance(asset="USDT")
        textstr = '\n'.join((
            'spot USDT',
            f'free: {float(balance["free"]):.2f}',
            f'locked: {float(balance["locked"]):.2f}',
            f'profit: {0}',
        ))

        # these are matplotlib.patch.Patch properties
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

        # place a text box in upper left in axes coords
        self.ax1.text(0.85, 0.95, textstr, transform=self.ax1.transAxes, fontsize=14,
                      verticalalignment='top', bbox=props)

    def on_press(self, event):
        if event.key in "xmat-1u=zd,S":
            # get clicked line
            if event.key == 'x':
                print("get_clicked_line")
                self.ld.get_clicked_line()
            # quit and save PricePlot
            elif event.key == 'S':
                self.save_as_pickle()
            # move clicked line
            elif event.key == 'm':
                print("start move line")
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
                self.is_auto_update = not self.is_auto_update
            # open/close volume panel
            elif event.key == '=':
                self.toggle_volume_panel()
            # delete clicked line
            elif event.key == 'd':
                self.ld.remove_clicked()
            # delete clicked alert
            elif event.key == 'z':
                print("unsetting alert...")
                self.ld.unset_alert()

            self.fig.canvas.draw()

    def save_as_pickle(self):
        for pp in self.ta.pp_collection:
            for line in pp.ld.lines:
                line.win10_toast = None
                line.alert_equation.diff_temp = line.alert_equation.diff
                line.alert_equation.diff = None
        pk.dump(self.ta, file=open('ta.pkl', 'wb'))
        print(f"Save TradingAlert as ta.pkl")
        for pp in self.ta.pp_collection:
            for line in pp.ld.lines:
                line.set_win10_toast()
                line.alert_equation.diff = line.alert_equation.diff_temp

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

    def update_delta_x(self):
        def _th():
            while True:
                self.delta_x = calc_headless_delta(self, self.interval)
                time.sleep(0.1)
        Thread(target=_th).start()

    def update_candle(self):
        if self.prev_delta is not None and self.delta_x - self.prev_delta > 0:
            new_index = self.curr_time
            new_open = self.data.iloc[-1, 3]
            self.data.loc[new_index, "Open": "Close"] = [new_open, self.price, self.price, self.price]
            self.high = self.price
            self.low = self.price
        if self.price > self.high:
            self.high = self.price
        if self.price < self.low:
            self.low = self.price
        self.data.iloc[-1, 1:4] = [self.high, self.low, self.price]
        self.prev_delta = self.delta_x

    def refresh_plot(self, autoscale=False):
        # self.data = self.get_binance_df()
        self.update_candle()
        self.ax1.collections.clear()
        self.ax3.clear()
        mpf.plot(self.data, ax=self.ax1, volume=self.ax3, type='candle',
                 style="binance")
        if autoscale:
            self.ax1.autoscale()
            self.ax3.autoscale()
