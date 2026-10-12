# Task: Product scraping

import csv
import logging
import re
import sys
from dataclasses import asdict, dataclass
from typing import Generator, List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


@dataclass
class Product:
    title: str
    price: float
    availability: str
    rating: str
    url: str


class ProductScraper:
    BASE_URL = "https://books.toscrape.com/"

    def __init__(self, output_file: str = "products.csv"):
        self.output_file = output_file
        self.session = self._init_session()

    def _init_session(self) -> requests.Session:
        session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "en-US,en;q=0.9",
            }
        )
        return session

    def fetch_page(self, url: str) -> Optional[str]:
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None

    def parse_product_card(self, article: BeautifulSoup, base_page_url: str) -> Optional[Product]:
        try:
            title_tag = article.select_one("h3 a")
            title = "N/A"
            relative_url = ""
            if title_tag:
                title = title_tag.attrs.get("title") or title_tag.get_text(strip=True)
                relative_url = title_tag.attrs.get("href", "")
            product_url = urljoin(base_page_url, relative_url)

            price_tag = article.select_one("p.price_color")
            raw_price = price_tag.get_text() if price_tag else "0"
            price_match = re.search(r"\d+(?:\.\d+)?", raw_price)
            price = float(price_match.group(0)) if price_match else 0.0

            avail_tag = article.select_one("p.instock.availability")
            availability = " ".join(avail_tag.get_text().split()) if avail_tag else "Unknown"

            rating_tag = article.select_one("p.star-rating")
            rating = "None"
            if rating_tag:
                classes = rating_tag.get("class", [])
                rating = next((c for c in classes if c != "star-rating"), "None")

            return Product(
                title=title,
                price=price,
                availability=availability,
                rating=rating,
                url=product_url,
            )
        except (ValueError, AttributeError) as e:
            logger.warning(f"Error parsing product item: {e}")
            return None

    def scrape(self, max_pages: int = 5) -> Generator[Product, None, None]:
        current_url = urljoin(self.BASE_URL, "catalogue/page-1.html")
        pages_scraped = 0

        while current_url and pages_scraped < max_pages:
            logger.info(f"Scraping: {current_url}")
            html = self.fetch_page(current_url)
            if not html:
                break

            soup = BeautifulSoup(html, "html.parser")
            articles = soup.select("article.product_pod")

            for article in articles:
                product = self.parse_product_card(article, current_url)
                if product:
                    yield product

            pages_scraped += 1
            next_button = soup.select_one("li.next a")
            if next_button:
                next_rel_url = next_button.attrs.get("href", "")
                current_url = urljoin(current_url, next_rel_url)
            else:
                current_url = None

    def save_to_csv(self, products: List[Product]) -> None:
        if not products:
            logger.warning("No products found to save.")
            return

        keys = asdict(products[0]).keys()
        with open(self.output_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for product in products:
                writer.writerow(asdict(product))
        logger.info(f"Saved {len(products)} products to {self.output_file}")


def main():
    scraper = ProductScraper(output_file="extracted_products.csv")
    products = list(scraper.scrape(max_pages=2))
    scraper.save_to_csv(products)


if __name__ == "__main__":
    main()
