import requests
from typing import Dict, Optional
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)

class FREDBase:
    BASE_URL = "https://api.stlouisfed.org/fred"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
