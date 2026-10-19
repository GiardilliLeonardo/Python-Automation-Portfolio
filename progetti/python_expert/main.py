# Task: Python Expert

#!/usr/bin/env python3
"""
Professional Python Automation Script
Description: Automates the organization of files in a specified directory based on their extensions.
Features: Object-Oriented design, Type Hinting, Logging, CLI argument parsing, and Collision handling.
"""

import shutil
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Default configuration for file categories and their corresponding extensions
DEFAULT_CATEGORIES: Dict[str, List[str]] = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xlsx", ".csv", ".pptx"],
    "Archives": [".zip", ".tar", ".gz", ".rar", ".7z"],
    "Audio": [".mp3", ".wav", ".aac", ".flac", ".ogg"],
    "Video": [".mp4", ".avi", ".mkv", ".mov", ".wmv"],
    "Scripts": [".py", ".sh", ".bat", ".ps1", ".js", ".html", ".css"],
    "Executables": [".exe", ".msi", ".apk", ".dmg"]
}

class FileAutomator:
    """Handles the automation of file organization within a directory."""

    def __init__(self, target_directory: str, categories: Optional[Dict[str, List[str]]] = None):
        self.target_dir = Path(target_directory).resolve()
        self.categories = categories or DEFAULT_CATEGORIES
        self.logger = self._setup_logger()
        
        # Create a reverse mapping for O(1) extension lookups
        self.extension_map: Dict[str, str] = {
            ext.lower(): category 
            for category, extensions in self.categories.items() 
            for ext in extensions
        }

    def _setup_logger(self) -> logging.Logger:
        """Configures and returns a logger for the automation process."""
        logger = logging.getLogger("FileAutomator")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            console_handler = logging.StreamHandler()
            file_handler = logging.FileHandler(
                self.target_dir / f"automation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            )
            
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)
            
            logger.addHandler(console_handler)
            logger.addHandler(file_handler)
            
        return logger
