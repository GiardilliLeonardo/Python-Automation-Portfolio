# Task: Python Script assistance

import requests
from bs4 import BeautifulSoup
import csv
import logging
import time
from typing import List, Dict, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ProfessionalScraper:
    """
    A professional and robust web
