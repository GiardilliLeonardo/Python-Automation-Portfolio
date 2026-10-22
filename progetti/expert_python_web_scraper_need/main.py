# Task: Expert Python Web Scraper Needed – 10,000 US Amateur Baseball Team Leads

import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dataclasses import dataclass, asdict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)

@dataclass
class TeamLead:
    team_name: str
    contact_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    website: Optional[str]
    city: Optional[str]
    state: Optional[str]

def create_session() -> requests.Session:
    session = requests.Session()
    retry_strategy = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    })
    return session

def scrape_team_data(url: str, session: requests.Session) -> Optional[TeamLead]:
    try:
        time.sleep(random.uniform(0.5, 2.0))
        response = session.get(url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        team_name_elem = soup.select_one('h1.team-name')
        email_elem = soup.select_one('a[href^="mailto:"]')
        phone_elem = soup.select_one('.contact-phone')
        
        return TeamLead(
            team_name=team_name_elem.text.strip() if team_name_elem else "Unknown",
            contact_name=None, 
            email=email_elem['href'].replace('mailto:', '').strip() if email_elem else None,
            phone=phone_elem.text.strip() if phone_elem else None,
            website=url,
            city=None, 
            state=None  
        )
    except Exception as e:
        logging.error
