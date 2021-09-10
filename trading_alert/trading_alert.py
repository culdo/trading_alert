import time
import tkinter as tk
from threading import Thread
from tkinter import font

from mplfinance._styles import _apply_mpfstyle

from trading_alert.candle_plotting import PricePlot, mpf
from datetime import datetime

from trading_alert.trade.account import BinanceAccount
from trading_alert.util.email_notifier import send_notify_email
from trading_alert.util.time_tool import get_before_time


# TODO 210910: Use thread workers to spawn multiple PricePlot in one TradingAlert
class TradingAlert:
    def __init__(self, start_str, **kwargs):
        self.start_str = start_str
        self.interval = kwargs["interval"]
        self.client = BinanceAccount()
        self._init_tk()
        self.start_time = datetime.now()
        self.pp = PricePlot(start_str, self.client, self, **kwargs)
        self.pp_collection = {self.pp.symbol: self.pp}
        self.alert_event_loop()
        self.symbols_ticker = None
        self.price = None

    def restore(self):
        _apply_mpfstyle(self.pp.style)
        self.pp.restore_mpl_event()
        self.pp.ld.restore_notify()
        if self.pp.is_auto_update:
            self.pp.refresh_plot_th()
        self._init_tk()
        self.alert_event_loop()

    def alert_event_loop(self):
        def _th():
            while True:
                self.symbols_ticker = self.client.get_symbol_ticker()
                # TODO 210910: Use thread workers to detect alert per symbol
                for item in self.symbols_ticker:
                    if item["symbol"] in self.pp_collection.keys():
                        pp = self.pp_collection[item["symbol"]]
                        pp.price = float(item["price"])
                        if pp.ld.has_alert():
                            self.when_alert_triggered(self.test_cb)
                time.sleep(1)

        Thread(target=_th).start()

    def when_alert_triggered(self, cb_alert):
        # TODO 210910: Use thread workers to detect alert per line
        for line in self.pp.ld.lines:
            # TODO 210909: Change method of getting x index to headless method
            if line.alert_equation and line.alert_equation.is_alert_triggered(self.price):
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
        print("執行觸發時回呼函數")

    def _init_tk(self):
        root = tk.Tk()
        root.withdraw()
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family='Courier', size=20)
        root.option_add("*Font", default_font)


if __name__ == '__main__':
    # ta = TradingAlert(get_before_time(hours=24), interval="15m")
    ta = TradingAlert(get_before_time(hours=6), symbol="FTMUSDT", interval="15m")
    mpf.show()
