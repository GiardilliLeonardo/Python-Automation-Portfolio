# Task: Google SERP Scraper Development- (Build a Fast, High-Success-Rate, Requests-Based, No Browser)

import requests
from bs4 import BeautifulSoup
import re
import time
import random
import logging
import csv
import json
from typing import List, Dict, Optional
from urllib.parse import urlparse, parse_qs

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class GoogleSERPScraper:
    """
    A fast, requests-based Google SERP scraper with high-success-rate techniques
    (User-Agent rotation, retries, session management) and data cleaning capabilities.
    """
    
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    ]

    def __init__(self, proxies: Optional[Dict[str, str]] = None, max_retries: int = 3):
        self.proxies = proxies
        self.max_retries = max_retries
        self.session = requests.Session()
        if self.proxies:
            self.session.proxies.update(self.proxies)

    def _get_random_headers(self) -> Dict[str, str]:
        return {
            "User-Agent": random.choice(self.USER_AG
