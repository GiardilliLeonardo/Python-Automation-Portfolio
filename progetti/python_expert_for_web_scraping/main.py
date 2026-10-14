# Task: Python Expert for Web Scraping

import csv
import logging
import random
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Generator, List, Optional, Tuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)


@dataclass
class ScrapedItem:
    title: str
    price: Optional[str]
    availability: Optional[str]
    url: str


class RobustWebScraper:
