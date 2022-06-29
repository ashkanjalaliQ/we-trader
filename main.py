from models import Coin, Interpreter
from concurrent.futures import ThreadPoolExecutor
import argparse
import json


with open('config.json') as file:
    config = json.load(file)


timeframes = config['timeframes']
symbols = config['symbols']


#argparser = argparse.ArgumentParser()
#argparser.add_argument('-c', '--code', help='The code to interpret', required=True)

#code_file = argparser.parse_args().code
code_file = './main.we'

with open(code_file) as file:
    code = file.read().split('\n')
code = [i for i in code if i != ""]

coins = []

with ThreadPoolExecutor(max_workers=10) as executor:
    for symbol in symbols:
        for timeframe in timeframes:
            coins.append(Coin(symbol, timeframe))
            executor.submit(coins[-1].get_history)


for coin in coins:
    interpreter = Interpreter(coin)
    for line in code:
        interpreter.interpret(line)