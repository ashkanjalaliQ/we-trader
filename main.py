import os
from pathlib import Path
import requests
import matplotlib.pyplot as plt
import pandas as pd
from ta.trend import MACD
from ta.utils import dropna
from ta.volume import money_flow_index
from ta.trend import cci

MARKET_LIST_FILE_NAME = 'markets'

class URL:
    def __init__(self):
        self.urls = {
            "market_list": "https://api.coinex.com/v1/market/list",
            "price": "https://api.coinex.com/v1/market/kline"
        }

    def get(self, key):
        return self.urls.get(key, None)


class Dir:
    def __init__(self):
        pass

    def base_dir(self, directory):
        directory = directory.split('/')
        directory = directory[:-1]
        result = ''

        for pos in directory:
            result += pos + '/'

        return result

dir = Dir()
BASE_DIR = dir.base_dir(__file__)

class Update:
    def __init__(self):
        self.url = URL()
        self.dir = Dir()
        self.clear = False

    def reset(self):
        self.clear = False

    def update(self, key):
        url = self.url.get(key)
        markets = self.requests_to(url)['data']

        for market in markets:
            if 'USDT' in market:
                self.__write(market)

    def __try_requests(self, url, params=None):
        if params != None:
            result = requests.get(url, params=params)
            while result.status_code != 200:
                result = requests.get(url, params=params)
            return result

        result = requests.get(url)
        while result.status_code != 200:
            result = requests.get(url)
        return result

    def requests_to(self, url, is_json=True, params=None):
        if is_json:
            if params != None:
                result = self.__try_requests(url, params)
                return result.json()
            result = self.__try_requests(url)
            return result.json()
        result = self.__try_requests(url)
        return result

    def __write(self, txt_append=None):
        file_address = BASE_DIR + MARKET_LIST_FILE_NAME + '.txt'
        if not self.clear:
            self.__clear_content(file_address)
            self.clear = True
        if txt_append != None:
            with open(file_address, 'a') as market_file:
                self.__append_line(market_file, [txt_append, '\n'])

    def __clear_content(self, file):
        with open(file, 'w'): pass

    def __append_line(self, file, texts):
        for text in texts:
            file.write(text)


class Price(Update):
    def __init__(self, market, type, limit=100):
        super().__init__()
        self.url = URL()
        self.dir = Dir()
        self.params = {
            "market": market,
            "type": type,
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
        self.full_data = False

    '''def __try_requests(self, url, params=None):
        if params != None:
            result = requests.get(url, params=params)
            while result.status_code != 200:
                result = requests.get(url, params=params)
            return result

        result = requests.get(url)
        while result.status_code != 200:
            result = requests.get(url)
        return result

    def requests_to(self, url, is_json=True, params=None):
        if is_json:
            if params != None:
                result = self.__try_requests(url, params)
                return result.json()
            result = self.__try_requests(url)
            return result.json()
        result = self.__try_requests(url)
        return result'''

    def __get_price(self):
        url = self.url.get('price')
        result = self.requests_to(url=url, params=self.params)['data']

        return self.__fill_data(result)

    def __fill_data(self, result):
        for info in result:
            for i, key in enumerate(self.prices_data.keys()):
                try:
                    self.prices_data[key].append(float(info[i]))
                except:
                    self.prices_data[key].append(info[i])
        return self.prices_data

    def __find_index(self, key):
        result = list(self.prices_data.keys())
        for i in range(len(result)):
            if result[i] == key:
                return i

    def get_by(self, key):
        if not self.full_data:
            self.prices_data = self.__get_price()
            self.full_data = True
        self.__save_csv()
        return self.prices_data.get(key)

    def __save_csv(self):
        df = pd.DataFrame(self.prices_data)
        try:
            os.mkdir(f"{DATA_DIR}/{self.params['market']}")
        except FileExistsError:
            pass
        #df.to_csv(BASE_DIR + DATA_DIR + '/' + self.params['market'] + '/' + self.prices_data['market'][0] + '-' + self.params['type'] + '.csv', index=False)
        df.to_csv(BASE_DIR + DATA_DIR + '/' + FILE_PATTERN_SAVE.format(self.params['market'], self.prices_data['market'][0], self.params['type']), index=False)


class Indicators:
    def __init__(self, file_name):
        self.file_name = file_name
        self.prices_data = self.__open_file(file_name)

    def __open_file(self, file_name):
        df = pd.read_csv(file_name)
        df = dropna(df)
        return df

    def mfi(self):
        return money_flow_index(self.prices_data['high'],
                                self.prices_data['low'],
                                self.prices_data['close'],
                                self.prices_data['vol']
        )


    def macd(self, type=None, key='close'):
        #obj = MACD(self.__to_list(key))
        obj = MACD(self.prices_data['close'])
        return obj

    def cci(self):
        return cci(
            self.prices_data['high'],
            self.prices_data['low'],
            self.prices_data['close']
        )

    def rsi(self):
        pass

class Signals:
    def __init__(self, file_name):
        self.file_name = file_name
        self.indicators = Indicators(file_name)
        self.indicators_guide = {
            'mfi': self.__mfi_signal,
            'macd': self.__macd_signal,
            'cci': self.__cci_signal
        }

    def __mfi_signal(self):
        mfi = self.indicators.mfi()
        mfi = list(mfi)
        if mfi[-1] <= 30:
            return True
        return False

    def __macd_signal(self):
        #if list(self.indicators.macd('macd'))[-1] < list(self.indicators.macd('signal'))[-1]:
            #if list(self.indicators.macd('macd'))[-1] < 0 and list(self.indicators.macd('signal'))[-1] < 0:
        #if list(self.indicators.macd('histo'))[-1] > 0:
        if list(self.indicators.macd().macd_diff())[-1] > 0:
            return True
        return False

    def __cci_signal(self):
        print(self.indicators.cci().iloc[-1])
        if 80 <= self.indicators.cci().iloc[-1] <= 100:
            return True
        return False

    def get_signal(self):
        result = []
        for indicator in self.indicators_guide:
            if self.indicators_guide.get(indicator, False):
                result.append(self.indicators_guide[indicator]())

        return result

update = Update()
update.update('market_list')

COINS = []

with open(BASE_DIR + MARKET_LIST_FILE_NAME + '.txt') as markets:
    markets_list = markets.readlines()

for market in markets_list:
    COINS.append(market.split(':')[-1][:-1])

"""COINS = [
    'BNBUSDT',
    'ADAUSDT',
    'BTCUSDT',
    'XRPUSDT',
    'BCHUSDT',
    'DOGEUSDT',
    'LTCUSDT',
    'TRXUSDT',
    'XMRUSDT',
    'XRPUSDT',
    'DOTUSDT',
    'UNIUSDT',
    'LINKUSDT',
    'SOLUSDT',
    'VETUSDT',
    'XLMUSDT',
    'NEOUSDT',
    'DASHUSDT',
    'NANOUSDT'
]"""
print(COINS)

TYPES = [
    '1hour',
    '2hour',
    '1day'
]

DATA_DIR = "market-data/"

FILE_PATTERN_SAVE = '{}/{}-{}.csv'

data_dir = Path("./market-data")
if not data_dir.is_dir():
    os.mkdir(DATA_DIR)


while True:
    for coin in COINS:
        for type in TYPES:
            price = Price(coin, type)
            p = price.get_by('close')

            signal = Signals(DATA_DIR + FILE_PATTERN_SAVE.format(coin, coin, type))
            if signal.get_signal()[2] == True:

                plt.plot(p)
                plt.title(coin + '-' + type)
                plt.show()

            print(f'{coin} in {type}: Checked.')