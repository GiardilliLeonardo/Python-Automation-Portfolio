# Task: Expert Python Web Scraper Needed – 10,000 US Amateur Baseball Team Leads

import requests
from bs4 import BeautifulSoup
import csv
import time

def scrape_baseball_leads(target_url, output_file):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like
