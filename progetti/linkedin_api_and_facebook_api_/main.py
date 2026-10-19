# Task: Linkedin API and Facebook API Expert

import csv
import json
import logging
import os
import time
from typing import Dict, Any

import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

FB_PAGE_ID = os.getenv('FB_PAGE_ID', '
