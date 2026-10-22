# Task: Extract data from PDF doc to excel/sheets. Create timeline from key dates of data extracted.

import os
import re
import pandas as pd
import pdfplumber
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from dateutil import parser
import warnings

warnings.filterwarnings("ignore")

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfpl
