import mplfinance as mpf

from trading_alert.trading_alert import TradingAlert
from trading_alert.util.time_tool import get_before_time
import pickle as pk

if __name__ == '__main__':
    ta = TradingAlert(get_before_time(hours=1), symbol="FTMUSDT", interval="1m")
    # ta = pk.load(file=open('ta.pkl', 'rb'))
    # ta.restore()
    mpf.show()
