# Task: Build a Python Tool to Identify UK Business Websites Using PublicWWW API

#!/usr/bin/env python3
"""
UK Business Website Identifier using PublicWWW API
Category: Python CSV Automation
"""

import argparse
import csv
import io
import logging
import sys
import time
from typing import Generator, Optional
from urllib.parse import quote_plus
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


class PublicWWWClient:
    BASE_URL = "https://publicwww.com/websites"

    def __init__(self, api_key: str, request_timeout: int = 60):
        self.api_key = api_key
        self.timeout = request_timeout
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "UKBusinessIdentifier/1.0 (+https://publicwww.com)"}
        )

    def search_csv(self, query: str) -> Generator[str, None, None]:
        """
        Executes a query against PublicWWW API and yields domains from CSV output.
        PublicWWW endpoint: https://publicwww.com/websites/{query}/?export=csv&key={api_key}
        """
        encoded_query = quote_plus(query)
        url = f"{self.BASE_URL}/{encoded_query}/?export=csv&key={self.api_key}"

        try:
            logger.info("Executing API request to PublicWWW...")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            # Handle rate limits or quota messages returned as plain text
            content_type = response.headers.get("Content-Type", "")
            if "text/csv" not in content_type and "text/plain" not in content_type:
                logger.warning(
                    f"Unexpected Content-Type: {content_type}. Validating response..."
                )

            csv_stream = io.StringIO(response.text)
            reader = csv.reader(csv_stream, delimiter=";")

            for row in reader:
                if not row:
                    continue
                domain = row[0].strip()
                if domain and not domain.startswith("#"):
                    yield domain

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response is not None else None
            if status_code == 401:
                logger.error("Authentication failed: Invalid API key.")
            elif status_code == 429:
                logger.error("Rate limit or query quota exceeded.")
            else:
                logger.error(f"HTTP Error: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error communicating with PublicWWW: {e}")
            raise


class UKBusinessAutomation:
    DEFAULT_QUERIES = [
        '"Registered in England and Wales"',
        '"Companies House" "Company No"',
        '"Registered Office:" "UK"',
        '"VAT Registration No" "GB"',
    ]

    UK_TLDS = (".co.uk", ".org.uk", ".uk", ".ltd.uk", ".plc.uk", ".me.uk")

    def __init__(self, api_key: str, output_file: str):
        self.client = PublicWWWClient(api_key=api_key)
        self.output_file = output_file
        self.discovered_domains: set = set()

    def is_uk_affinity(self, domain: str) -> bool:
        """Determines likelihood of UK-specific business."""
        domain = domain.lower()
        return any(domain.endswith(tld) for tld in self.UK_TLDS)

    def run(self, custom_query: Optional[str] = None, max_results: int = 1000):
        queries = [custom_query] if custom_query else self.DEFAULT_QUERIES
        logger.info(f"Target output file: {self.output_file}")

        fieldnames = ["domain", "is_uk_tld", "source_query", "timestamp"]

        with open(self.output_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            total_written = 0

            for query in queries:
                if total_written >= max_results:
                    logger.info(f"Reached threshold limit of {max_results} domains.")
                    break

                logger.info(f"Processing query: {query}")
                try:
                    for domain in self.client.search_csv(query):
                        if domain not in self.discovered_domains:
                            self.discovered_domains.add(domain)

                            record = {
                                "domain": domain,
                                "is_uk_tld": self.is_uk_affinity(domain),
                                "source_query": query,
                                "timestamp": int(time.time()),
                            }
                            writer.writerow(record)
                            total_written += 1

                            if total_written >= max_results:
                                break

                    # Cooldown to respect API resource constraints
                    time.sleep(1)

                except Exception as e:
                    logger.error(f"Skipping query '{query}' due to error: {e}")
                    continue

        logger.info(
            f"Extraction completed successfully. {total_written} unique business websites saved to {self.output_file}"
        )


def main():
    parser = argparse.ArgumentParser(
        description="PublicWWW Automation: Identify UK Business Websites"
    )
    parser.add_argument(
