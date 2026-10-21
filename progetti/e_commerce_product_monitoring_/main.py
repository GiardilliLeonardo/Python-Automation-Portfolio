# Task: E-commerce Product Monitoring System

import requests
from bs4 import BeautifulSoup
import time
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EcommerceMonitor:
    def __init__(self, url, target_price):
        self.url = url
        self.target_price
