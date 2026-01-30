import requests
import time
from typing import List, Dict, Optional
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)

class SECEDGARBase:
    BASE_URL = "https://www.sec.gov/cgi-bin/browse-edgar"
    API_URL = "https://data.sec.gov/submissions"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'FinanceHub/1.0 (your-email@example.com)',
            'Accept': 'application/json'
        })
        self.last_request = 0
        self.rate_limit = 0.1
    
    def _rate_limit(self):
        elapsed = time.time() - self.last_request
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self.last_request = time.time()
