import requests
from typing import Dict
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)

class StockTwitsAPI:
    BASE_URL = "https://api.stocktwits.com/api/2"
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {access_token}'
        })
    
    def get_symbol_sentiment(self, symbol: str) -> Dict:
        response = self.session.get(f"{self.BASE_URL}/streams/symbol/{symbol}.json")
        
        try:
            data = response.json()
            total = len(data['messages'])
            bullish = sum(1 for m in data['messages'] 
                         if m.get('entities', {}).get('sentiment', {}).get('basic') == 'Bullish')
            bearish = sum(1 for m in data['messages'] 
                        if m.get('entities', {}).get('sentiment', {}).get('basic') == 'Bearish')
            
            return {
                'symbol': symbol,
                'total_messages': total,
                'bullish': bullish,
                'bearish': bearish,
                'bullish_ratio': bullish / total if total > 0 else 0
            }
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            logger.error(f"Error fetching StockTwits data: {str(e)}")
            return {}
