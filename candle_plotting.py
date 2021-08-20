import numpy as np
import pandas as pd
import mplfinance as mpf
from binance.client import Client
import json
from line_drawer import LineDrawer
import matplotlib.pyplot as plt
plt.ion()

class PricePlot:
    def __init__(self, symbol="ETHUSDT", interval='15m', start_str='20 August 2021 00:00 am +0800'):
        with open("api_key.json") as f:
            api_keys = json.load(f)
        self.client = Client(**api_keys)
        self.symbol = symbol
        self.interval = interval
        self.start_str = start_str

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

    def test(self):
        self.data = self.get_binance_df()
        fig, ax = self.creat_plot()
        ld = LineDrawer()
        ld.draw_line(fig, ax)
        mpf.show()

    def creat_plot(self):
        fig, axes = mpf.plot(self.data, returnfig=True, figratio=(10, 6), type="candle",
                 volume=True,
                 title=f"Price of {self.symbol}",
                 tight_layout=True, style="binance")

        # mpf.show()
        return fig, axes[0]


if __name__ == '__main__':
    PricePlot().test()
