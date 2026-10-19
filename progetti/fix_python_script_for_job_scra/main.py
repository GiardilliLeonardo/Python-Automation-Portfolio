# Task: Fix Python Script for Job Scraping

import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
import time
import random
from typing import List, Optional
from dataclasses import dataclass, asdict
from requests.exceptions import RequestException

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)
