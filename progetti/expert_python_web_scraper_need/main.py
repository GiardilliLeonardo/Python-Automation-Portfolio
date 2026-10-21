# Task: Expert Python Web Scraper Needed – 10,000 US Amateur Baseball Team Leads

import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
import time
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import List, Dict, Optional
import concurrent.futures

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)

TARGET_DIRECTORY_URL = "https://example-baseball-directory.com/teams?page={}"
BASE_DOMAIN = "https://example-baseball-directory.com"
MAX_PAGES = 500
OUTPUT_FILE = "us_amateur_baseball_leads.csv"
MAX_WORKERS = 5

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36
