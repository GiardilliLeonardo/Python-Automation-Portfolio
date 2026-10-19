# Task: AI Workflow & API Integration Assistant

import os
import sys
import json
import logging
import requests
from typing import List, Dict, Any, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("AI_Workflow_Integration")

class AIWorkflowIntegration:
    def __init__(self):
        self.source_api_url = os.getenv("SOURCE_API_URL", "https://api.example.com/v1/data")
        self.source_api_key = os.getenv("SOURCE_API_KEY", "your_source_api_key")
        
        self.ai_api_url = os.getenv("AI_API_URL", "https://api.openai.com/v1/chat/completions")
        self.ai_api_key = os.getenv("AI_API_KEY", "your_openai_api_key")
        self.ai_model = os.getenv("AI_MODEL", "gpt-4")
        
        self.dest_api_url = os.getenv("DEST_API_URL", "https://api.destination.com/v1/webhook")
        self.dest_api_key = os.getenv("DEST_API_KEY", "your_destination_api_key")

        self.session = self._create_robust_session()

    @staticmethod
    def _create_robust_session() -> requests.Session:
        session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def fetch_source_data(self) -> List[Dict[str, Any]]:
