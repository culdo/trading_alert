import mplfinance as mpf

from trading_alert.trading_alert import TradingAlert
from trading_alert.util.time_tool import get_before_time

if __name__ == '__main__':
    ta = TradingAlert(get_before_time(hours=6), symbol="FTMUSDT", interval="15m")
    mpf.show()
