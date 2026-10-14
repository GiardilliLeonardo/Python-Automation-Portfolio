# Task: Product Data Scraping, Shopify & B2B Uploads, and Automated Competitor Price Monitoring

import csv
import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class Product:
    sku: str
    title: str
    base_price: float
    current_price: float
    competitor_url: str
    competitor_price: Optional[float] = None
    shopify_product_id: Optional[int] = None
    shopify_variant_id: Optional[int] = None


class CompetitorScraper:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            raise_on_status=False
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        })

    def scrape_price(self, url: str, selector: str) -> Optional[float]:
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            price_element = soup.select_one(selector)

            if not price_element:
                logger.warning(f"Price selector '{selector}' not found at {url}")
                return None

            raw_price = price_element.get_text(strip=True)
            match = re.search(r"[\d.,]+", raw_price)
            if not match:
                logger.warning(f"No numeric price found in '{raw_price}' at {url}")
                return None

            cleaned_price = match.group(0)

            if "." in cleaned_price and "," in cleaned_price:
                if cleaned_price.rfind(".") > cleaned_price.rfind(","):
                    cleaned_price = cleaned_price.replace(",", "")
                else:
                    cleaned_price = cleaned_price.replace(".", "").replace(",", ".")
            elif "," in cleaned_price:
                cleaned_price = cleaned_price.replace(",", ".")
            elif cleaned_price.count(".") > 1:
                parts = cleaned_price.split(".")
                cleaned_price = "".join(parts[:-1]) + "." + parts[-1]

            return float(cleaned_price)
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None


class ShopifyManager:
    def __init__(self, store
