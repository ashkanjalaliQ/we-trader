import requests
import yfinance as yf
import re
import pandas as pd
from ta.volume import money_flow_index as MFI
from ta.trend import MACD
from ta.momentum import rsi as RSI
from ta.trend import cci as CCI
from ta.momentum import StochasticOscillator as SR
from ta.trend import EMAIndicator
from ta.trend import SMAIndicator
import matplotlib.pyplot as plt


class History:
    def __init__(self, limit=100):
        self.params = {
            "limit": limit
        }
        self.prices_data = {
            'time': [],
            'open': [],
            'close': [],
            'high': [],
            'low': [],
            'vol': [],
            'amount': [],
            'market': [],
        }
        self._base_url = 'https://api.coinex.com/v1/market/kline'

    def __to_pandas_series(self, prices_data):
        return pd.DataFrame(prices_data)

    def __try_requests(self, url):
        try:
            while (result := requests.get(url, params=self.params)).status_code != 200:
                pass
        except ConnectionError:
            raise print('ALARM: Your Net is lost. Please Check the Connection!')

        return result

    def __requests_to(self, url, is_json=True):
        result = self.__try_requests(url)
        if is_json:
            return result.json()
        return result

    def __get_price(self):
        result = self.__requests_to(url=self._base_url)['data']

        return self.__fill_data(result)

    def __fill_data(self, result):
        for info in result:
            for i, key in enumerate(self.prices_data.keys()):
                try:
                    self.prices_data[key].append(float(info[i]))
                except:
                    self.prices_data[key].append(info[i])
        return self.prices_data

    def get_by(self, coin_name, timeframe):
        self.params.update({'market': coin_name, 'type': timeframe})
        self.prices_data = self.__get_price()
        return self.__to_pandas_series(self.prices_data)


class Indicators:
    def __init__(self, price_data):
        self.price_data = price_data

    def mfi(self):
        return MFI(
            self.price_data['high'],
            self.price_data['low'],
            self.price_data['close'],
            self.price_data['vol']
        )

    def macd(self, key='close', slow=26, fast=12, sign=9):
        return MACD(self.price_data[key], window_slow=slow, window_fast=fast, window_sign=sign)

    def cci(self, length=14):
        return CCI(
            self.price_data['high'],
            self.price_data['low'],
            self.price_data['close'],
            window=length
        )

    def rsi(self, key='close', length=14):
        return RSI(self.price_data[key], window=length)

    def sr(self, length=21, length_smooth=8):
        return SR(
            self.price_data['high'],
            self.price_data['low'],
            self.price_data['close'],
            window=length,
            smooth_window=length_smooth
        )
        '''data = {}
        data['14-high'] = self.price_data['high'].rolling(21).max()
        data['14-low'] = self.price_data['low'].rolling(21).min()
        data['stoch_stoch'] = (self.price_data['close'] - data['14-low']) * 100 / (data['14-high'] - data['14-low'])
        data['stoch_signal'] = data['stoch_stoch'].rolling(8).mean()
        print(data['stoch_signal'].values[-1], data['stoch_stoch'].values[-1])
        return data
'''
    def ema(self, key='close', length=14):
        return EMAIndicator(self.price_data[key], window=length)

    def sma(self, key='close', length=14):
        return SMAIndicator(self.price_data[key], window=length)


class Analyzer:
    def __init__(self, indicators, codes):
        """
        :param indicators: Indicators Object
        """
        self.variables = {
            'high': list(indicators.price_data['high']),
            'low': list(indicators.price_data['low']),
            'open': list(indicators.price_data['open']),
            'close': list(indicators.price_data['close']),
            'vol': list(indicators.price_data['vol']),
            'macd_macd': list(indicators.macd().macd()),
            'macd_signal': list(indicators.macd().macd_signal()),
            'macd_diff': list(indicators.macd().macd_diff()),
            'mfi': list(indicators.mfi()),
            'rsi': list(indicators.rsi()),
            'cci': list(indicators.cci()),
            #'stoch_stoch': list(indicators.sr()['stoch_stoch'])[-1],
            #'stoch_signal': list(indicators.sr()['stoch_signal'])[-1],
            'stoch_stoch': list(indicators.sr().stoch()),
            'stoch_signal': list(indicators.sr().stoch_signal()),
            'ema7': list(indicators.ema(length=7).ema_indicator()),
            'ema20': list(indicators.ema(length=20).ema_indicator()),
            'ema25': list(indicators.ema(length=25).ema_indicator()),
            'ema30': list(indicators.ema(length=30).ema_indicator()),
            'ema35': list(indicators.ema(length=35).ema_indicator()),
            'ema40': list(indicators.ema(length=40).ema_indicator()),
            'ema45': list(indicators.ema(length=45).ema_indicator()),
            'ema50': list(indicators.ema(length=50).ema_indicator()),
            'ema55': list(indicators.ema(length=55).ema_indicator()),
            'ema233': list(indicators.ema(length=233).ema_indicator()),
            'sma100': list(indicators.sma(length=100).sma_indicator())
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

    def _cleaner(self, ls):
        ls_cleaned = []
        for i in range(len(ls)):
            if ls[i] != '':
                ls_cleaned.append(ls[i])
        return ls_cleaned

    def get_user_orders(self):
        with open('main.txt', 'r') as reader:
            orders = reader.read().split('\n')
        return self._cleaner(orders)

    def get_user_coins(self):
        with open('markets.txt', 'r') as reader:
            coins = reader.read().split('\n')
        return self._cleaner(coins)

    def get_user_timeframes(self):
        with open('timeframes.txt') as reader:
            timeframes = reader.read().split('\n')
        return self._cleaner(timeframes)

    def __str__(self):
        return self.order

orderlist = OrderList()
orders = orderlist.get_user_orders()
coins = orderlist.get_user_coins()
timeframes = orderlist.get_user_timeframes()

history = History()

for coin in coins:
    for timeframe in timeframes:
        price_data = history.get_by(coin_name=coin, timeframe=timeframe)

        indicators = Indicators(price_data)

        analyzer = Analyzer(indicators, orders)
        if analyzer.interpret_code():
            print(f'{coin}: timeframe {timeframe} => Found')
        #else:
            #print(f'{coin}: timeframe: {timeframe} => Checked.')