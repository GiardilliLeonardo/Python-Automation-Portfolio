# Task: Brazilian Business Data Scraper — USA (10,000+ records, CSV format)

import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import logging
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def scrape_page(
