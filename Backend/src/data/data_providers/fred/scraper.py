from typing import Dict, Optional
from .base import FREDBase
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)

class FREDScraper(FREDBase):
    SERIES = {
        'treasury_10y': 'DGS10',
        'treasury_2y': 'DGS2',
        'fed_funds': 'DFF',
        'gdp': 'GDP',
        'cpi': 'CPIAUCSL',
        'unemployment': 'UNRATE'
    }
    
    def get_series_data(self, series_id: str, start_date: Optional[str] = None) -> Dict:
        params = {
            'api_key': self.api_key,
            'series_id': series_id,
            'file_type': 'json'
        }
        
        if start_date:
            params['observation_start'] = start_date
        
        try:
            response = self.session.get(f"{self.BASE_URL}/series/observations", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching FRED data: {str(e)}")
            return {}
    
    def get_treasury_yields(self) -> Dict:
        data = {}
        for name, series_id in [('10y', 'DGS10'), ('2y', 'DGS2'), ('30y', 'DGS30')]:
            series_data = self.get_series_data(series_id)
            if series_data and 'observations' in series_data:
                latest = series_data['observations'][-1]
                data[name] = float(latest['value']) if latest['value'] else None
        return data
