# Task: Brazilian Business Data Scraper — USA (10,000+ records, CSV format)

import csv
import time
import requests
from bs4 import BeautifulSoup

TARGET_URL = "https://example.com/brazilian-businesses-usa?page={}"
OUTPUT_FILE = "brazilian_businesses_usa.csv"
MAX_RECORDS = 10000

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
}

def scrape_directory():
    records_
