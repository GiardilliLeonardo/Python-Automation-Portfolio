# Task: Extract data from PDF doc to excel/sheets. Create timeline from key dates of data extracted.

import os
import re
import pandas as pd
import pdfplumber
from dateutil import parser

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                extracted_text
