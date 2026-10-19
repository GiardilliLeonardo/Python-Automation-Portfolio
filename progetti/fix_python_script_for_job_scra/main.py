# Task: Fix Python Script for Job Scraping

import requests
from bs4 import BeautifulSoup
import csv
import logging
import time
import random
from typing import List, Dict, Optional
from requests.exceptions import RequestException

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
