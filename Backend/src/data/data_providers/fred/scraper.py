from typing import Dict, Optional, List
from .base import FREDBase
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)

class FREDScraper(FREDBase):
    SERIES = {
        'treasury_10y': 'DGS10',
        'treasury_2y': 'DGS2',
        'treasury_5y': 'DGS5',
        'treasury_30y': 'DGS30',
        'treasury_1y': 'DGS1',
        'treasury_3m': 'DGS3M',
        'fed_funds': 'DFF',
        'gdp': 'GDP',
        'cpi': 'CPIAUCSL',
        'unemployment': 'UNRATE',
        'mortgage_30y': 'MORTGAGE30US',
        'mortgage_15y': 'MORTGAGE15US',
    }

    BOND_CURVE_SERIES = {
        'treasury_1m': 'DTB1M',
        'treasury_3m': 'DTB3',
        'treasury_6m': 'DTB6',
        'treasury_1y': 'DTB1YR',
        'tresury_2y': 'DTB2YR',
        'treasury_3y': 'DTB3YR',
        'treasury_5y': 'DTB5YR',
        'treasury_7y': 'DTB7YR',
        'treasury_10y': 'DTB10YR',
        'treasury_20y': 'DTB20YR',
        'treasury_30y': 'DTB30YR',
    }

    CREDIT_SPREAD_SERIES = {
        'baa_aa': 'BAA10Y',
        'aaa_aa': 'AAA10Y',
        'high_yield_spread': 'BAMLH0A0HYM2',
        'ig_spread': 'BAMLH0A0HYM2',
    }

    INFLATION_SERIES = {
        'cpi': 'CPIAUCSL',
        'pce': 'PCEPI',
        'core_cpi': 'CPILFESL',
        'core_pce': 'PCEPILFE',
        'inflation_expectation': 'T5YIE',
        'breakeven_5y': 'T5YBE',
        'breakeven_10y': 'T10YIE',
    }

    def get_series_data(self, series_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict:
        params = {
            'api_key': self.api_key,
            'series_id': series_id,
            'file_type': 'json'
        }

        if start_date:
            params['observation_start'] = start_date
        if end_date:
            params['observation_end'] = end_date

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

    def get_full_treasury_curve(self) -> Dict:
        data = {}
        series_map = {
            '1m': 'DTB1M',
            '3m': 'DTB3M',
            '6m': 'DTB6M',
            '1y': 'DTB1YR',
            '2y': 'DTB2YR',
            '3y': 'DTB3YR',
            '5y': 'DTB5YR',
            '7y': 'DTB7YR',
            '10y': 'DTB10YR',
            '20y': 'DTB20YR',
            '30y': 'DTB30YR',
        }

        for name, series_id in series_map.items():
            series_data = self.get_series_data(series_id)
            if series_data and 'observations' in series_data:
                latest = series_data['observations'][-1]
                data[name] = float(latest['value']) if latest['value'] else None

        return data

    def get_mortgage_rates(self) -> Dict:
        data = {}
        for name, series_id in [('30y', 'MORTGAGE30US'), ('15y', 'MORTGAGE15US')]:
            series_data = self.get_series_data(series_id)
            if series_data and 'observations' in series_data:
                latest = series_data['observations'][-1]
                data[name] = float(latest['value']) if latest['value'] else None
        return data

    def get_credit_spreads(self) -> Dict:
        data = {}
        series_map = {
            'baa_aa_spread': 'BAA10Y',
            'aaa_aa_spread': 'AAA10Y',
        }

        for name, series_id in series_map.items():
            series_data = self.get_series_data(series_id)
            if series_data and 'observations' in series_data:
                latest = series_data['observations'][-1]
                data[name] = float(latest['value']) if latest['value'] else None

        return data

    def get_inflation_data(self) -> Dict:
        data = {}
        series_map = {
            'cpi': 'CPIAUCSL',
            'pce': 'PCEPI',
            'core_cpi': 'CPILFESL',
            'core_pce': 'PCEPILFE',
            'inflation_expectation_5y': 'T5YIE',
        }

        for name, series_id in series_map.items():
            series_data = self.get_series_data(series_id)
            if series_data and 'observations' in series_data:
                latest = series_data['observations'][-1]
                data[name] = float(latest['value']) if latest['value'] else None

        return data

    def get_bond_yield_history(self, maturity: str = '10y', days: int = 365) -> List[Dict]:
        series_map = {
            '10y': 'DGS10',
            '5y': 'DGS5',
            '2y': 'DGS2',
            '30y': 'DGS30',
        }

        series_id = series_map.get(maturity, 'DGS10')
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        series_data = self.get_series_data(
            series_id,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )

        if series_data and 'observations' in series_data:
            return [
                {
                    'date': obs['date'],
                    'value': float(obs['value']) if obs['value'] else None
                }
                for obs in series_data['observations']
            ]

        return []

    def get_yield_curve_spread(self) -> Dict:
        curve = self.get_full_treasury_curve()

        if curve.get('10y') and curve.get('2y'):
            curve['10y_2y_spread'] = curve['10y'] - curve['2y']
        if curve.get('10y') and curve.get('3m'):
            curve['10y_3m_spread'] = curve['10y'] - curve['3m']
        if curve.get('30y') and curve.get('5y'):
            curve['30y_5y_spread'] = curve['30y'] - curve['5y']

        return curve

    def get_macro_indicators(self) -> Dict:
        data = {}
        series_map = {
            'gdp': 'GDP',
            'cpi': 'CPIAUCSL',
            'unemployment': 'UNRATE',
            'fed_funds': 'DFF',
            'mortgage_30y': 'MORTGAGE30US',
        }

        for name, series_id in series_map.items():
            series_data = self.get_series_data(series_id)
            if series_data and 'observations' in series_data:
                latest = series_data['observations'][-1]
                data[name] = float(latest['value']) if latest['value'] else None

        return data
