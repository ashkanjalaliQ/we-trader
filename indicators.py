from ta.trend import MACD as moving_average_convergence_divergence
from ta.momentum import rsi as relative_strength_index
from ta.trend import cci as commodity_channel_index
from ta.volume import money_flow_index
from ta.trend import SMAIndicator
import pandas as pd


class History:
    def __init__(self, history) -> None:
        self.history = history
    
    def to_dataframe(self):
        return pd.DataFrame(self.history)


class MFI(History):
    def __init__(self, coin) -> None:
        super().__init__(coin.history)
    
    def mfi(self, length:int=14) -> pd.Series:
        history = self.to_dataframe()
        return money_flow_index(high=history['high'], low=history['low'], close=history['close'], volume=history['vol'], window=length)


class MACD(History):
    def __init__(self, coin) -> None:
        super().__init__(coin.history)
    
    def macd(self, fast:int=12, slow:int=26) -> pd.Series:
        history = self.to_dataframe()
        return moving_average_convergence_divergence(history['close'], window_fast=fast, window_slow=slow)


class RSI(History):
    def __init__(self, coin):
        super().__init__(coin.history)
    
    def rsi(self, length:int=14) -> pd.Series:
        history = self.to_dataframe()
        return relative_strength_index(history['close'], window=length)


class SMA(History):
    def __init__(self, coin):
        super().__init__(coin.history)
    
    def sma(self, length:int=9) -> float:
        history = self.to_dataframe()
        return SMAIndicator(history['close'], window=length).sma_indicator()


class CCI(History):
    def __init__(self, coin):
        super().__init__(coin.history)
    
    def cci(self, length:int=20) -> pd.Series:
        history = self.to_dataframe()
        return commodity_channel_index(high=history['high'], low=history['low'], close=history['close'], window=length)