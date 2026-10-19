# Task: Need Working Quotex OTC M1 Candle Data Feed – Python

import os
import csv
import time
import json
import logging
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

QUOTEX_URL = "https://qxbroker.com/en/trade"
ASSET_TARGET = "EURUSD"
