import yfinance as yf
import re
from ta.volume import money_flow_index as MFI
from ta.trend import MACD
from ta.momentum import rsi as RSI
from ta.trend import cci as CCI
from ta.momentum import StochasticOscillator as SR
from ta.trend import EMAIndicator
from ta.trend import SMAIndicator

class History:
    def __init__(self, timeframe='1d'):
        self.timeframe = timeframe

    def get(self, coin_name, period="max"):
        return yf.Ticker(ticker=coin_name).history(period=period, interval=self.timeframe)


class Indicators:
    def __init__(self, price_data):
        self.price_data = price_data

    def mfi(self):
        return MFI(
            self.price_data['High'],
            self.price_data['Low'],
            self.price_data['Close'],
            self.price_data['Volume']
        )

    def macd(self, key='Close', slow=26, fast=12, sign=9):
        return MACD(self.price_data[key], window_slow=slow, window_fast=fast, window_sign=sign)

    def cci(self):
        return CCI(
            self.price_data['High'],
            self.price_data['Low'],
            self.price_data['Close']
        )

    def rsi(self, key='Close', length=14):
        return RSI(self.price_data[key], window=length)

    def sr(self):
        return SR(
            self.price_data['High'],
            self.price_data['Low'],
            self.price_data['Close']
        )

    def ema(self, key='Close', length=14):
        return EMAIndicator(self.price_data[key], window=length)

    def sma(self, key='Close', length=14):
        return SMAIndicator(self.price_data[key], window=length)


class Analyzer:
    def __init__(self, indicators, codes):
        """
        :param indicators: Indicators Object
        """
        self.variables = {
            'high': list(indicators.price_data['High']),
            'low': list(indicators.price_data['Low']),
            'open': list(indicators.price_data['Open']),
            'close': list(indicators.price_data['Close']),
            'vol': list(indicators.price_data['Volume']),
            'macd_macd': list(indicators.macd().macd()),
            'macd_signal': list(indicators.macd().macd_signal()),
            'macd_diff': list(indicators.macd().macd_diff()),
            'mfi': list(indicators.mfi()),
            'rsi': list(indicators.rsi()),
            'cci': list(indicators.cci()),
            'stoch_stoch': list(indicators.sr().stoch()),
            'stoch_signal': list(indicators.sr().stoch_signal()),
            'ema20': list(indicators.ema(length=20).ema_indicator()),
            'ema25': list(indicators.ema(length=25).ema_indicator()),
            'ema30': list(indicators.ema(length=30).ema_indicator()),
            'ema35': list(indicators.ema(length=35).ema_indicator()),
            'ema40': list(indicators.ema(length=40).ema_indicator()),
            'ema45': list(indicators.ema(length=45).ema_indicator()),
            'ema50': list(indicators.ema(length=50).ema_indicator()),
            'ema55': list(indicators.ema(length=55).ema_indicator())
        }
        self.codes = codes
        self.results = []

    def __get_names(self, names):
        result = ''
        for name in names:
            result += name + '|'
        return result[:-1]

    def interpret_code(self):
        for code in self.codes:
            result = eval(code, self.variables)
            self.results.append(result)
        if False in self.results:
            return False
        return True


class OrderList:
    def __init__(self):
        self.order = []
        self.coins = []

    def get_user_orders(self):
        with open('main.we', 'r') as reader:
            orders = reader.read().split('\n')
        return orders

    def get_user_coins(self):
        with open('markets.we', 'r') as reader:
            coins = reader.read().split('\n')
        return coins

    def __str__(self):
        return self.order

orderlist = OrderList()
orders = orderlist.get_user_orders()
coins = orderlist.get_user_coins()

history = History()

for coin in coins:
    price_data = history.get(coin_name=coin)
    indicators = Indicators(price_data)

    analyzer = Analyzer(indicators, orders)
    if analyzer.interpret_code():
        print(coin)
