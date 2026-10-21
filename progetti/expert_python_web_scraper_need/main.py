# Task: Expert Python Web Scraper Needed – 10,000 US Amateur Baseball Team Leads

import requests
from bs4 import BeautifulSoup
import pandas as pd
import concurrent.futures
import logging
import time
import random
import os
from typing import List, Dict, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def create_session() -> requests.Session:
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    })
    return session

def scrape_team_lead(url: str, session: requests.Session) -> Optional[Dict[str, str]]:
    try:
        time.sleep(random.uniform(0.5, 2.0))
        response = session.get(url, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        name_elem = soup.find('h1', class_='team-name')
        coach_elem = soup.find('div', class_='coach-name')
        email_elem = soup.find('a', href=lambda href: href and "mailto:" in href
