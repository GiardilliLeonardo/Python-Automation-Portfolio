# Task: Python Script assistance

import requests
from bs4 import BeautifulSoup
import csv
import logging
import time
from typing import List, Dict, Optional

# Configurazione del logging professionale per il debug e il monitoraggio
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

class RobustWebScraper:
    """
    Web Scraper professionale e corretto (Fixed Web Scraper).
    Risolve problemi comuni come:
    - Blocchi IP (tramite User-Agent e Sessioni)
    - Timeout infiniti (tramite parametro timeout)
    - Errori di parsing (tramite try/except e controlli None)
    - Gestione della paginazione
    """

    def __init__(self, base_url: str, output_file: str = 'scraped_data.csv'):
        self.base_url = base_url
        self.output_file = output_file
        self.scraped_data: List[Dict[str, str]] = []
        
        # Utilizzo di requests.Session() per mantenere i cookie e riutilizzare le connessioni TCP
        self.session = requests.Session()
        
        # Aggiunta di headers standard per evitare l'errore 403 Forbidden
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        })

    def fetch_page(self, url: str) -> Optional[str]:
        """Effettua la richiesta HTTP con gestione degli errori e timeout."""
        try:
            logging.info(f"Fetching URL: {url}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()  # Solleva un'eccezione per codici HTTP 4xx/5xx
            return response.text
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err}")
        except requests.exceptions.ConnectionError as conn_err:
            logging.
