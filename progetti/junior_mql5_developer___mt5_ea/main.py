# Task: Junior MQL5 Developer / MT5 EA Tester — Existing Gold Trading Bot

import MetaTrader5 as mt5
import pandas as pd
import logging
from datetime import datetime, timedelta

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class GoldEATester:
    def __init__(self, symbol="XAUUSD", magic=123456):
        self.symbol = symbol
        self.magic = magic
        
        if not mt5.initialize():
            logging.error("MetaTrader5 initialization failed")
        else:
            logging.info("MetaTrader5 initialized successfully")
