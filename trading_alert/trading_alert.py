import time
from threading import Thread

from trading_alert.candle_plotting import PricePlot, mpf
from datetime import datetime
import calendar

from trading_alert.util.time_tool import get_before_time


class TradingAlert:
    def __init__(self, start_str, **kwargs):
        self.start_str = start_str
        self.interval = kwargs["interval"]
        self.pp = PricePlot(start_str, **kwargs)
        self.event_loop()
        self.start_time = datetime.now()

    def event_loop(self):
        def _th():
            while True:
                if self.pp.ld.has_alert():
                    self.pp.refresh_plot()
                    self.pp.fig.canvas.draw()
                    symbols = self.pp.client.get_symbol_ticker()
                    for symbol in symbols:
                        if symbol["symbol"] == self.pp.symbol:
                            price = float(symbol["price"])
                            self.pp.ld.when_alert_triggered(price, self.test_cb)
                time.sleep(1)

        Thread(target=_th).start()

    def test_cb(self):
        print("執行觸發時回呼函數")

    def calc_headless_delta(self):
        now = datetime.now()
        time_by_unit = now.hour

        # Check current kindle bar
        if self.interval[-1] == "m":
            time_by_unit = (now - self.start_time).seconds // 60
        elif self.interval[-1] == "h":
            time_by_unit = (now - self.start_time).seconds // 60 // 60
        elif self.interval[-1] == "d":
            time_by_unit = (now - self.start_time).days
        elif self.interval[-1] == "M":
            month_days = calendar.monthrange(now.year, now.month)[1]
            time_by_unit = (now - self.start_time).days // month_days
        delta = time_by_unit // int(self.interval[:-1])
        return delta


if __name__ == '__main__':
    # ta = TradingAlert(get_before_time(hours=24), interval="15m")
    ta = TradingAlert(get_before_time(hours=24), symbol="FTMUSDT", interval="15m")
    mpf.show()
