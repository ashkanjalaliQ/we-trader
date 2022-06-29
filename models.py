from indicators import MACD, RSI, SMA, MFI, CCI
from utils import sum_two_dicts
import requests

class Coin:
    def __init__(self, symbol:str, timeframe:str):
        self.symbol = symbol
        self.timeframe = timeframe
        self.history = {
            'open': [],
            'high': [],
            'low': [],
            'close': [],
            'vol': [],
            'is_field': False
        }
        self.api_url = 'https://api3.binance.com'
        self.session = requests.session()

    def get_property_index(self, property:str):
        if property == 'open':
            return 1
        elif property == 'high':
            return 2
        elif property == 'low':
            return 3
        elif property == 'close':
            return 4
        elif property == 'vol':
            return 5
        
        return None

    def get_history(self, limit:int=500):
        response = self.session.get(self.api_url + "/api/v3/klines", params={'symbol': self.symbol, 'interval': self.timeframe, 'limit': limit})
        
        if response.status_code == 200:
            data = response.json()
            for i in range(len(data)):
                for key in self.history:
                    if key == 'is_field':
                        continue
                    self.history[key].append(float(data[i][self.get_property_index(key)]))
            self.history['is_field'] = True
        else:
            return None
    
        return self.history

    @property
    def all_symbols(self):
        response = requests.get(self.api_url + '/api/v3/exchangeInfo')
        if response.status_code == 200:
            data = response.json()
            return [coin['symbol'] for coin in data['symbols']]
        return None
        

class Interpreter:
    def __init__(self, coin:Coin) -> None:
        self.coin = coin
        self.builtin_functions = {
            'mfi': MFI(coin).mfi,
            'macd': MACD(coin).macd,
            'rsi': RSI(coin).rsi,
            'sma': SMA(coin).sma,
            'cci': CCI(coin).cci,
            'alert': print,
        }
        self.builtin_variables = {
            'symbol': coin.symbol,
            'timeframe': coin.timeframe,
            'close': coin.history['close'],
            'high': coin.history['high'],
            'low': coin.history['low'],
            'open': coin.history['open'],
            'vol': coin.history['vol']
        }
        self.variables = {}
    
    def __define_variable(self, line:str, variable_type:str) -> bool:
        line = line.strip()[len(variable_type):]
        line = line.split('=')
        line = [i.strip() for i in line]
        if len(line) == 2 and line[0] not in (list(self.builtin_functions.keys()) + list(self.builtin_variables.keys())):
            try:
                self.variables[line[0]] = eval(f'{variable_type}({line[1]})')
            except:
                return False
            return True
        return False

    def interpret(self, line:str):
        if line.startswith('int') or line.startswith('str') or line.startswith('float') or line.startswith('bool'):
            return self.__define_variable(line, line.split(' ')[0])
        elif line.startswith('if'):
            # the "if" character is used for conditional statements
            # if symbol == 'BTC' ? alert('BTC is here') : alert('BTC is not here')
            line = line.strip()[2:]
            line = line.split('?')
            condition = line[0]
            command = line[1].split(':')
            if eval(condition, sum_two_dicts(sum_two_dicts(self.builtin_functions, self.builtin_variables), self.variables)):
                self.interpret(command[0])
            elif ":" in line[1]:
                self.interpret(command[1])
        else:
            try:
                return eval(line, sum_two_dicts(sum_two_dicts(self.builtin_functions, self.builtin_variables), self.variables))
            except:
                return None
