# Task: Junior MQL5 Developer / MT5 EA Tester — Existing Gold Trading Bot

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import pytz
import sys

def initialize_mt5():
    if not mt5.initialize():
        sys.exit(1)

def fetch_gold_data(symbol: str = "XAUUSD", timeframe=mt5.TIMEFRAME_H1, num_bars: int = 10000) -> pd.DataFrame:
    if not mt5.symbol_select(symbol, True):
        mt5.shutdown()
        sys.exit(1)

    timezone = pytz.timezone("Etc/UTC")
    utc_from = datetime.now(timezone)
    
    rates = mt5.copy_rates_from(symbol, timeframe, utc_from, num_bars)
    
    if rates is None or len(rates) == 0:
        mt5.shutdown()
        sys.exit(1)
        
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    return df

def analyze_ea_conditions(df: pd.DataFrame) -> pd.DataFrame:
    df['volatility'] = df['high'] - df['low']
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['sma_50'] = df['close'].rolling(window=50).mean()
    df.dropna(inplace=True)
    return df

if __name__ == "__main__":
    initialize_mt5()
    
    df_gold = fetch_gold_data("XAUUSD", mt5.TIMEFRAME_H1, 10000)
    df_analyzed = analyze_ea_conditions(df_gold)
    
    print(df_analyzed.tail())
    
    mt5.shutdown()
