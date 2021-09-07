import json

from binance import Client


class BinanceAccount(Client):
    def __init__(self):
        with open("../api_key.json") as f:
            api_keys = json.load(f)
        super(BinanceAccount, self).__init__(**api_keys)

    def get_margin_balance(self, symbol):
        account = self.get_margin_account()
        for asset in account["userAssets"]:
            if asset["asset"] == symbol:
                return asset
