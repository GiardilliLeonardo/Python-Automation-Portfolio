# Task: Python Script assistance

import os
import shutil
import argparse
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

FILE_CATEGORIES = {
    "Images": ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.tiff'],
    "Documents": ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.xls', '.xlsx', '.ppt', '.pptx', '.csv', '.md'],
    "Audio": ['.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a'],
    "Video": ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
    "Archives": ['.zip', '.rar', '.tar', '.gz', '.7z', '.bz2'],
    "Scripts_and_Code": ['.py', '.sh', '.bat', '.js', '.html', '.css', '.json', '.xml', '.cpp', '.c', '.java'],
    "Executables": ['.exe', '.msi', '.apk', '.dmg', '.deb', '.rpm']
}

def get_category(extension: str) -> str:
    for category, extensions in FILE_CATEGORIES.items():
        if extension.lower() in extensions:
            return category
    return "Others"

def organize_directory(target_dir: str) -> None:
    base_dir = Path(target_dir)

    if not base_dir.exists() or not base_dir.is_dir():
        logging.error(f"The directory '{target_dir}' does not exist or is not a valid directory.")
        return

    logging.info(f"Starting automation: Organizing directory '{base_dir.resolve()}'")

    moved_count = 0
    error_count = 0

    for file_path in base_dir.iterdir():
        if file_path.is_file():
            if file_path.name.startswith('.') or file_path.name == Path(__file__).name:
                continue

            category = get_category(file_path.suffix)
            category_dir = base_dir / category

            try:
                category_dir.mkdir(exist_ok=True)
                target_path = category_dir / file_path.name

                counter = 1
