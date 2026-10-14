# Task: Build interactive sales territory map from CRM data (Leaflet.js + Python automation pipeline)

import io
import json
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import folium
from folium.plugins import MarkerCluster
import numpy as np
import pandas as pd

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(
