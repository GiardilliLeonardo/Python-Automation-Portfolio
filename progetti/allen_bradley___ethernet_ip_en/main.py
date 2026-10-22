# Task: Allen-Bradley / EtherNet/IP engineer to review, test and validate an AI-assisted PLC-to-MQTT gateway

import time
import json
import logging
from typing import Dict, Any

from pycomm3 import LogixDriver
from pycomm3.exceptions import CommError
import paho.mqtt.client as mqtt

CONFIG = {
    "plc_ip": "192.168.1.10",
    "mqtt_broker": "127.0.0.1",
    "mqtt_port": 1883,
    "mqtt_topic": "factory/plc/data",
    "poll_interval": 1.0,
    "tags": [
        "Machine_Status",
        "Production_Count",
        "Motor_Speed"
    ]
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
