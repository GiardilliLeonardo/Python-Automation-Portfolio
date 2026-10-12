# Task: Expert Python Developer to build TikTok Ads Automation Bot (.exe GUI)

import csv
import logging
import os
import queue
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class QueueHandler(logging.Handler):
    """Redirige i log di logging verso una coda thread-safe per la GUI."""
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(self.format(record))


class TikTokAdsScraper:
    """Gestore del web scraping e dell'automazione di TikTok Ads."""
    def __init__(self, headless=True, logger=None):
        self.headless = headless
        self.logger = logger or logging.getLogger(__name__)
        self.driver = None
        self._stop_requested = False

    def init_driver(self):
        options = Options()
        if self.headless:
            options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

    def scrape_creative_center(self, target_keyword="", max_results=20):
        self._stop_requested = False
        scraped_data = []
        url = "https://ads.tiktok.com/business/creativecenter/inspiration/topads/pc/en"
        
        try:
            self.logger.info("Inizializzazione del browser Chrome...")
            self.init_driver()
            
            self.logger.info(f"Navigazione verso: {url}")
            self.driver.get(url)
            wait = WebDriverWait(self.driver, 15)

            time.sleep(3)
            
            self.logger.info("Ricerca annunci in corso...")
            cards_selector = "div[class*='CardWrapper'], div[class*='adCard']"
            
            retries = 0
            while len(scraped_data) < max_results and not self._stop_requested:
                cards = self.driver.find_elements(By.CSS_SELECTOR, cards_selector)
                
                if not cards:
                    cards = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'card')]")

                for card in cards[len(scraped_data):]:
                    if self._stop_requested or len(scraped_data) >= max_results:
                        break
                    try:
                        text_content = [line.strip() for line in card.text.split("\n") if line.strip()]
                        title = text_content[0] if len(text_content) > 0 else "N/A"
                        brand = text_content[1] if len(text_content) > 1 else "N/A"
                        
                        data_item = {
                            "Index": len(scraped_data) + 1,
                            "Title": title,
                            "Brand": brand,
                            "Raw_Data": " | ".join(text_content[:4]),
                            "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                        }
                        scraped_data.append(data_item)
                        self.logger.info(f"Estratto [{len(scraped_data)}/{max_results}]: {title[:30]}")
                    except Exception as err:
                        self.logger.debug(f"Errore parsing card: {err}")
                        continue

                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                retries += 1
                if retries > 10 and len(scraped_data) == 0:
                    self.logger.warning("Nessun annuncio intercettato con i selettori predefiniti.")
                    break

            return scraped_data

        except Exception as e:
            self.logger.error(f"Errore critico durante l'automazione: {e}")
            return scraped_data
        finally:
            self.close()

    def request_stop(self):
        self._stop_requested = True

    def close(self):
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("Browser chiuso correttamente.")
            except Exception:
                pass
            self.driver = None


class TikTokAdsBotGUI(tk.Tk):
    """Interfaccia Grafica Utente basata su Tkinter pronta per compilazione EXE."""
    def __init__(self):
        super().__init__()
        self.title("TikTok Ads Automation Bot v1.0")
        self.geometry("800x600")
        self.minsize(700, 500)
        
        self.log_queue = queue.Queue()
        self.scraper = None
        self.worker_thread = None

        self._setup_logging()
        self._create_widgets()
        self._poll_log_queue
