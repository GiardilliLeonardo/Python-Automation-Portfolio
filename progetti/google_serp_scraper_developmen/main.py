# Task: Google SERP Scraper Development- (Build a Fast, High-Success-Rate, Requests-Based, No Browser)

import requests
from bs4 import BeautifulSoup
import time
import random
import urllib.parse
import logging
import json
from typing import List, Dict, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s -
