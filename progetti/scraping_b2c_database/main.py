# Task: Scraping B2C Database

import requests
from bs4 import BeautifulSoup
import time
import csv

def scrape_b2c_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    extracted_data = []

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        items = soup.find_all('div', class_='product-item')
        
        for item in items:
            name_tag = item.find('h2', class_='product-name')
            price_tag = item.find('span', class_='product-price')
