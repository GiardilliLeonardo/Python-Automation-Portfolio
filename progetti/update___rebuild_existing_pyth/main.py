# Task: Update & Rebuild Existing Python Luma Event Attendee Scraper (Scrapy / Playwright)

import argparse
import asyncio
import csv
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional, Set
from playwright.async_api import BrowserContext, Locator, Page, async_playwright

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@dataclass
class Attendee:
    name: str
    username: Optional[str] = None
    profile_url: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None


class LumaAttendeeScraper:
    def __init__(self, event_url: str, output_csv: Path, headless: bool = True):
        self.event_url = event_url
        self.output_csv = Path(output_csv)
        self.headless = headless
        self.attendees: List[Attendee] = []
        self._seen_profiles: Set[str] = set()

    async def _scroll_element_to_bottom(
        self, page: Page, container_locator: Optional[Locator] = None, max_idle_retries: int = 5
    ) -> None:
        retries = 0
        last_count = 0

        while retries < max_idle_retries:
            current_elements = await page.locator("a[href*='/usr/']").count()
            if current_elements > last_count:
                last_count = current_elements
                retries = 0
                logger.info(f"Loaded {current_elements} attendee profiles so far...")
            else:
                retries += 1

            if container_locator and await container_locator.is_visible():
                await container_locator.evaluate("(el) => { el.scrollTop = el.scrollHeight; }")
            else:
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

            await asyncio.sleep(1.2)

    async def _open_guest_list_modal(self, page: Page) -> Optional[Locator]:
        guest_triggers = [
            "button:has-text('Going')",
            "button:has-text('Guests')",
            "div:has-text('Going') button",
            "a:has-text('Going')",
            "[aria-label*='guests' i]",
            "[aria-label*='attendees' i]",
            "div[class*='guest']",
            "div:text-matches('Going|Guests', 'i')",
        ]

        for trigger in guest_triggers:
            button = page.locator(trigger).first
            if await button.count() > 0 and await button.is_visible():
                try:
                    await button.click()
                    await page.wait_for_timeout(1500)
                    modal = page.locator("[role='dialog'], .content-card, div[class*='modal']").first
                    if await modal.is_visible():
                        logger.info("Attendee modal detected and opened.")
                        return modal
                except Exception as e:
                    logger.debug(f"Click attempt failed for {trigger}: {e}")

        logger.info("No separate modal opened; scanning main page context.")
        return None

    async def _extract_attendee_card(self, element: Locator) -> Optional[Attendee]:
        try:
            profile_link = await element.get_attribute("href")
            if not profile_link:
                return None

            if not profile_link.startswith("http"):
                profile_link = f"https://lu.ma{profile_link}"

            username = profile_link.rstrip("/").split("/")[-1].split("?")[0]
            if username in self._seen_profiles:
                return None

            name_elem = element.locator("div[class*='name'], h4, p, span").first
            if await name_elem.count() > 0 and await name_elem.is_visible():
                name = (await name_elem.inner_text()).strip()
            else:
                name = username

            img_elem = element.locator("img").first
            avatar_url = None
            if await img_elem.count() > 0 and await img_elem.is_visible():
                avatar_url = await img_elem.get_attribute("src")

            bio_elem = element.locator("div[class*='bio'], div[class*='title'], p[class*='sub'], div[class*='desc']").first
            bio = None
            if await bio_elem.count() > 0 and await bio_elem.is_visible():
                bio = (await bio_elem.inner_text()).strip()

            self._seen_profiles.add(username)
            return Attendee(
                name=name,
                username=username,
                profile_url=profile_link,
                avatar_url=avatar_url,
                bio=bio,
            )
        except Exception as e:
            logger.debug(f"Error extracting attendee card: {e}")
            return None

    def _save_to_csv(self) -> None:
        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_csv, mode="w", newline="", encoding="utf-8") as f:
            if not self.attendees:
                writer = csv.writer(f)
                writer.writerow(["name", "username", "profile_url", "avatar_url", "bio"])
                return

            fieldnames = list(asdict(self.attendees[0]).keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for attendee in self.attendees:
                writer.writerow(asdict(attendee))
        logger.info(f"Saved {len(self.attendees)} attendees to {self.output_csv}")

    async def scrape(self) -> List[Attendee]:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=self.headless,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            )
            context: BrowserContext = await browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                ),
            )

            page: Page = await context.new_page()

            try:
                logger.info(f"Navigating to {self.event_url}...")
                await page.goto(self.event_url, wait_until="networkidle", timeout=60000)
                await page.wait_for_timeout(2000)

                modal_container = await self._open_guest_list_modal(page)
                await self._scroll_element_to_bottom(page, container_locator=modal_container)

                cards = page.locator
