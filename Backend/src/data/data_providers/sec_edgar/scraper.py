from typing import List, Dict, Optional
from .base import SECEDGARBase
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)

class SECEDGARScraper(SECEDGARBase):
    def get_company_filings(self, ticker: str, filing_type: str = '10-K') -> List[Dict]:
        cik = self.get_cik(ticker)
        if not cik:
            return []
        
        url = f"{self.API_URL}/CIK{cik.zfill(10)}.json"
        self._rate_limit()
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            
            filings = data.get('filings', {}).get('recent', {})
            
            results = []
            for i, form in enumerate(filings.get('form', [])):
                if form == filing_type:
                    results.append({
                        'accession_number': filings['accessionNumber'][i],
                        'filing_date': filings['filingDate'][i],
                        'form': filings['form'][i],
                        'primary_doc': filings['primaryDocument'][i],
                        'url': f"https://www.sec.gov/Archives/edgar/data/{cik}/{filings['accessionNumber'][i].replace('-', '')}"
                    })
            
            return results[:10]
        except Exception as e:
            logger.error(f"Error fetching SEC filings for {ticker}: {str(e)}")
            return []
    
    def get_cik(self, ticker: str) -> Optional[str]:
        ticker_to_cik = {
            'AAPL': '0000320193',
            'MSFT': '0000789019',
            'GOOGL': '0001652044',
            'AMZN': '0001018724',
            'TSLA': '0001318605',
            'META': '0001326801',
            'NVDA': '0001045810',
            'JPM': '0000019617',
            'V': '0000950509',
            'JNJ': '0000200406',
            'WMT': '0000104169',
            'PG': '0000080855',
            'XOM': '0000034088',
            'BAC': '0000070858',
            'KO': '0000021344',
            'PEP': '0000077476',
            'COST': '0000902563',
            'DIS': '0001001039',
            'NFLX': '0001065280',
            'ADBE': '0000796343',
            'INTC': '0000050863',
            'AMD': '0000002488',
            'CRM': '0001108524',
            'QCOM': '0000804328',
            'AVGO': '0001609388',
            'CSCO': '0000888487',
            'IBM': '0000051143',
            'ORCL': '0001341439',
            'ACN': '0001467373',
            'TXN': '0000094645',
            'NOW': '00000155528',
            'INTU': '0000946739',
            'LMT': '0000080046',
            'BA': '0000012927',
            'NOC': '0000020855',
            'RTX': '0000097745',
            'GD': '0000037996',
            'HON': '0000024387',
            'MMM': '0000066740',
            'CAT': '0000058749',
            'DE': '0000031584',
            'GE': '0000040545'
        }
        return ticker_to_cik.get(ticker.upper())
    
    def get_filing_document(self, url: str) -> str:
        self._rate_limit()
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Error downloading filing: {str(e)}")
            return ""
