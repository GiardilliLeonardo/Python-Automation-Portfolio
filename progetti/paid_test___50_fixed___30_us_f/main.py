# Task: Paid test ($50 fixed): 30 US fractional CFO firm owners + 3-message LinkedIn sequence

import csv
import re
import sys
import time
import urllib.parse
from dataclasses import asdict, dataclass
from typing import List, Optional

import requests
from bs4 import BeautifulSoup


@dataclass
class CFOLead:
    full_name: str
    title: str
    company: str
    location: str
    linkedin_url: str
    message_1_connect: str
    message_2_followup: str
    message_3_breakup: str


class LeadScraperSequence:
    def __init__(self, target_count: int = 30):
        self.target_count = target_count
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def generate_sequences(self, first_name: str, company: str) -> tuple:
        f_name = first_name if first_name else "there"
        comp = company if company else "your firm"

        msg_1 = (
            f"Hi {f_name}, noticed your focus on fractional CFO services at {comp}. "
            "Always looking to connect with finance leaders driving strategic SME growth. Let's connect!"
        )

        msg_2 = (
            f"Hi {f_name}, quick follow-up. Many fractional CFOs I speak with mention capacity bottlenecks "
            "when onboarding multiple mid-market clients simultaneously. "
            "We recently developed a workflow framework to streamline financial modeling and reporting setup. "
            f"Would you be open to a 5-minute chat next week to see if it could benefit {comp}?"
        )

        msg_3 = (
            f"Hi {f_name}, I realize you're likely flat out advising clients at {comp}. "
            "I won't clutter your inbox further. If optimizing client onboarding and analytical bandwidth "
            "becomes a priority down the line, feel free to reach back out. Wishing you continued success!"
        )

        return msg_1, msg_2, msg_3

    def clean_text(self, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    def parse_snippet(self, raw_title: str) -> tuple:
        title_cleaned = re.sub(r"\s*\|\s*LinkedIn.*$", "", raw_title, flags=re.IGNORECASE)
        parts = [p.strip() for p in re.split(r"[-–—]", title_cleaned) if p.strip()]

        full_name = "N/A"
        job
