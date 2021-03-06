import time
import tkinter as tk
from threading import Thread
from tkinter import font

import matplotlib.pyplot as plt
from requests import ReadTimeout

from trading_alert.base.main_window import MainWindow
from trading_alert.binance_plot import PricePlot, mpf
from datetime import datetime

from trading_alert.trade.account import BinanceAccount
from trading_alert.util.email_notifier import send_notify_email


# TODO 210910: Use thread workers to spawn multiple PricePlot in one TradingAlert
class TradingAlert:
    def __init__(self, start_str, default_symbol="BTCUSDT", theme="white", **kwargs):
        self.symbol_prices = {}
        self.theme = theme
        self._init_style()
        self.start_str = start_str
        self.kwargs = kwargs
        self.interval = kwargs["interval"]
        self.client = BinanceAccount()
        self.start_time = datetime.now()
        self._update_symbol_prices()
        self.pp_collection = {
            default_symbol: PricePlot(self, symbol=default_symbol, **kwargs)
        }
        self.main_pp = list(self.pp_collection.values())[0]
        self.main_window = MainWindow(self)
        self._alert_event_loop()

    def _init_style(self):
        if self.theme == "black":
            self.style = mpf.make_mpf_style(base_mpf_style='binance', base_mpl_style="dark_background",
                                            rc={'font.family': 'Segoe UI Emoji'})
        else:
            self.style = mpf.make_mpf_style(base_mpf_style='binance', rc={'font.family': 'Segoe UI Emoji'})

    def restore(self):
        self._init_style()
        self._update_symbol_prices()
        self.main_window = MainWindow(self)
        # It's a bug workaround to keep reloaded figsize
        plt.close(plt.figure())
        for pp in self.pp_collection.values():
            pp.restore()
        self._alert_event_loop()

    def _update_symbol_prices(self):
        def _th():
            while True:
                try:
                    symbols_ticker = self.client.get_symbol_ticker()
                    for item in symbols_ticker:
                        self.symbol_prices[item["symbol"]] = float(item["price"])
                except (ReadTimeout, ConnectionError) as e:
                    print(e)
                    continue
                time.sleep(1)
        Thread(target=_th).start()

    def _alert_event_loop(self):
        def _th():
            while True:
                # TODO 210910: Use thread workers to detect alert per symbol
                try:
                    for symbol, pp in self.pp_collection.items():
                        pp.price = self.symbol_prices[symbol]
                        pp.update_data()
                        if pp is self.main_pp and pp.is_auto_update:
                            pp.refresh_plot()
                        if pp.ld.has_alert():
                            self.when_alert_triggered(pp, self.test_cb)
                    time.sleep(1)
                except RuntimeError:
                    continue

        Thread(target=_th).start()

    def when_alert_triggered(self, pp, cb_alert):
        # TODO 210910: Use thread workers to detect alert per line
        for line in pp.ld.lines:
            # TODO 210909: Change method of getting x index to headless method
            if line.alert_equation and line.alert_equation.is_alert_triggered():
                self._do_after_alert(cb_alert, line)

    def _do_after_alert(self, cb_alert, line, send_email=True):
        Thread(target=cb_alert).start()

        def _th():
            line.alert_annotation.set_color("grey")
            if not line.is_debug:
                line.win10_toast.notify()
            if send_email:
                send_notify_email(line)

        Thread(target=_th).start()

    def test_cb(self):
        print("???????????????????????????")
