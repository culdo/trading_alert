import tkinter

import mplfinance as mpf

from trading_alert.base.main_window import MainWindow
from trading_alert.trading_alert import TradingAlert
from trading_alert.util.time_tool import get_before_time

from trading_alert.util.util import load_ta

if __name__ == '__main__':
    # _ = TradingAlert(get_before_time(hours=1), interval="1m")
    load_ta()
    tkinter.mainloop()
