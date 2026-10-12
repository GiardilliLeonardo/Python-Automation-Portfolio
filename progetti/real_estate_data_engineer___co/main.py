# Task: Real Estate Data Engineer – Commercial Mortgage & Loan Data APIs

import asyncio
import logging
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, List, Optional
import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field, field_validator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("CRELoanPipeline")


class CommercialLoanSchema(BaseModel):
    loan_id: str
    property_name: str
    property_type: str
    origination_date: str
    maturity_date: str
    original_balance: Decimal
    current_balance: Decimal
    interest_rate: float
    ltv_ratio: Optional[float] = Field(None, description="Loan-to-Value Ratio")
    dscr: Optional[float] = Field(None, description="Debt Service Coverage Ratio")
    city: str
    state: str
    source_url: str
    extracted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("original_balance", "current_balance", mode="before")
    def clean_currency(cls, value: Any) -> Decimal:
        if isinstance(value, str):
            cleaned = value.replace("$", "").replace(",", "").strip()
            return Decimal(cleaned)
        return Decimal(value)

    @field_validator("interest_rate", "ltv_ratio", "dscr", mode="before")
    def clean_numeric_fields(cls, value: Any) -> Optional[float]:
        if value is None:
            return None
        if isinstance(value, str):
            cleaned = value.replace("%", "").replace(",", "").strip()
            if not cleaned or cleaned.upper() in {"N/A", "NONE", "-"}:
                return None
            return float(cleaned)
        return float(value)


class SECMortgageScraper:
    def __init__(
        self,
        user_agent: str,
        concurrency_limit: int = 5,
        requests_per_second: float = 10.0
    ):
        self.headers = {
            "User-Agent": user_agent,
            "Accept-Encoding": "gzip, deflate"
        }
        self.semaphore = asyncio.Semaphore(concurrency_limit)
        self.rate_limit_delay = 1.0 / requests_per_second
        self.client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        limits = httpx.Limits(max_keepalive_connections=10, max_connections=20)
        timeout = httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=10.0)
        self.client = httpx.AsyncClient(
            headers=self.headers,
            limits=limits,
            timeout=timeout,
            follow_redirects=True
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
            self.client = None

    async def fetch_html(self, url: str, retries: int = 3) -> Optional[str]:
        if not self.client:
            raise RuntimeError("Client is not initialized. Use SECMortgageScraper within an 'async with' context.")

        async with self.semaphore:
            for attempt in range(1, retries + 1):
                try:
                    await asyncio.sleep(self.rate_limit_delay)
                    response = await self.client.get(url)

                    if response.status_code == 200:
                        return response.text
                    elif response.status_code == 429:
                        backoff = 2 ** attempt
                        logger.warning(f"Rate limited (429). Backing off for {backoff}s. URL: {url}")
                        await asyncio.sleep(backoff)
                    else:
                        logger.error(f"HTTP {response.status_code} fetching {url}")
                        await asyncio.sleep(2 ** attempt)
                except (httpx.RequestError, httpx.TimeoutException) as ex:
                    logger.warning(f"Attempt {attempt}/{retries} failed for {url}: {ex}")
                    await asyncio.sleep(2 ** attempt)
            return None

    def parse_loan_exhibits(self, html_content: str, source_url: str) -> List[CommercialLoanSchema]:
        soup = BeautifulSoup(html_content, "html.parser")
        extracted_records: List[CommercialLoanSchema] = []

        table = soup.find("table", {"class": "cmbs-loan-schedule"})
        if not table:
            return extracted_records

        rows = table.find_all("tr")[1:]
        for row in rows:
            cols = [td.get_text(strip=True) for td in row.find_all("td")]
            if len(cols) >= 11:
                try:
                    record = CommercialLoanSchema(
                        loan_id=cols[0],
                        property_name=
