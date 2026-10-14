# Task: Python Expert for Web Scraping

from dataclasses import asdict, dataclass
import re
from typing import List, Optional
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import requests


@dataclass
class ScrapedItem:
    raw_title: Optional[str]
    raw_price: Optional[str]
    raw_rating: Optional[str
