from typing import List, Dict, Optional, Any
from datetime import datetime
from .base import SECEDGARBase
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class SECEDGARScraper(SECEDGARBase):
    def get_company_filings(self, ticker: str, filing_type: str = "10-K") -> List[Dict]:
        cik = self.get_cik(ticker)
        if not cik:
            return []

        url = f"{self.API_URL}/CIK{cik.zfill(10)}.json"
        self._rate_limit()

        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()

            filings = data.get("filings", {}).get("recent", {})

            results = []
            for i, form in enumerate(filings.get("form", [])):
                if form == filing_type:
                    results.append(
                        {
                            "accession_number": filings["accessionNumber"][i],
                            "filing_date": filings["filingDate"][i],
                            "form": filings["form"][i],
                            "primary_doc": filings["primaryDocument"][i],
                            "url": f"https://www.sec.gov/Archives/edgar/data/{cik}/{filings['accessionNumber'][i].replace('-', '')}",
                        }
                    )

            return results[:10]
        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            logger.error(f"Error fetching SEC filings for {ticker}: {str(e)}")
            return []

    def get_cik(self, ticker: str) -> Optional[str]:
        ticker_to_cik = {
            "AAPL": "0000320193",
            "MSFT": "0000789019",
            "GOOGL": "0001652044",
            "AMZN": "0001018724",
            "TSLA": "0001318605",
            "META": "0001326801",
            "NVDA": "0001045810",
            "JPM": "0000019617",
            "V": "0000950509",
            "JNJ": "0000200406",
            "WMT": "0000104169",
            "PG": "0000080855",
            "XOM": "0000034088",
            "BAC": "0000070858",
            "KO": "0000021344",
            "PEP": "0000077476",
            "COST": "0000902563",
            "DIS": "0001001039",
            "NFLX": "0001065280",
            "ADBE": "0000796343",
            "INTC": "0000050863",
            "AMD": "0000002488",
            "CRM": "0001108524",
            "QCOM": "0000804328",
            "AVGO": "0001609388",
            "CSCO": "0000888487",
            "IBM": "0000051143",
            "ORCL": "0001341439",
            "ACN": "0001467373",
            "TXN": "0000094645",
            "NOW": "00000155528",
            "INTU": "0000946739",
            "LMT": "0000080046",
            "BA": "0000012927",
            "NOC": "0000020855",
            "RTX": "0000097745",
            "GD": "0000037996",
            "HON": "0000024387",
            "MMM": "0000066740",
            "CAT": "0000058749",
            "DE": "0000031584",
            "GE": "0000040545",
        }
        return ticker_to_cik.get(ticker.upper())

    def get_filing_document(self, url: str) -> str:
        self._rate_limit()

        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.text
        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            logger.error(f"Error downloading filing: {str(e)}")
            return ""

    def get_company_info(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get company information from SEC filings"""
        cik = self.get_cik(ticker)
        if not cik:
            return None

        url = f"{self.API_URL}/CIK{cik.zfill(10)}.json"
        self._rate_limit()

        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()

            name = data.get("name", "")
            sic = data.get("sic", "")
            sic_desc = data.get("sicDescription", "")
            filings = data.get("filings", {}).get("recent", {})

            return {
                "cik": cik,
                "name": name,
                "ticker": ticker,
                "sic": sic,
                "sic_description": sic_desc,
                "state_of_incorporation": data.get("stateOfIncorporation", ""),
                "state_of_location": data.get("stateOfLocation", ""),
                "fiscal_year_end": data.get("fiscalYearEnd", ""),
                "last_filing_date": filings.get("filingDate", [""])[0]
                if filings
                else "",
                "number_of_filings": len(filings.get("form", [])),
            }
        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            logger.error(f"Error fetching company info for {ticker}: {str(e)}")
            return None

    def search_company_filings(
        self,
        ticker: str,
        forms: List[str] = None,
        start_date: str = None,
        end_date: str = None,
        count: int = 100,
    ) -> List[Dict]:
        """Search for company filings with filters"""
        cik = self.get_cik(ticker)
        if not cik:
            return []

        url = f"{self.API_URL}/CIK{cik.zfill(10)}.json"
        self._rate_limit()

        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()

            filings = data.get("filings", {}).get("recent", {})
            forms_set = set(f or "" for f in (forms or ["10-K", "10-Q", "8-K", "4"]))

            results = []
            for i, form in enumerate(filings.get("form", [])):
                if form in forms_set:
                    filing_date = filings["filingDate"][i]

                    if start_date and filing_date < start_date:
                        continue
                    if end_date and filing_date > end_date:
                        continue

                    results.append(
                        {
                            "accession_number": filings["accessionNumber"][i],
                            "filing_date": filing_date,
                            "report_date": filings.get("reportDate", [""])[i],
                            "form": form,
                            "primary_doc": filings["primaryDocument"][i],
                            "size": filings.get("size", [0])[i],
                            "is_amendment": filings.get("isAmendment", [False])[i],
                            "url": f"https://www.sec.gov/Archives/edgar/data/{cik}/{filings['accessionNumber'][i].replace('-', '')}",
                        }
                    )

                    if len(results) >= count:
                        break

            return results
        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            logger.error(f"Error searching filings for {ticker}: {str(e)}")
            return []

    def get_insider_transactions(self, ticker: str, count: int = 50) -> List[Dict]:
        """Get insider transactions (Form 4 filings)"""
        return self.search_company_filings(ticker, forms=["4"], count=count)

    def get_annual_reports(self, ticker: str, count: int = 5) -> List[Dict]:
        """Get annual reports (10-K filings)"""
        return self.search_company_filings(
            ticker, forms=["10-K", "20-F", "40-F"], count=count
        )

    def get_quarterly_reports(self, ticker: str, count: int = 10) -> List[Dict]:
        """Get quarterly reports (10-Q filings)"""
        return self.search_company_filings(ticker, forms=["10-Q"], count=count)

    def get_current_reports(self, ticker: str, count: int = 10) -> List[Dict]:
        """Get current reports (8-K filings)"""
        return self.search_company_filings(ticker, forms=["8-K"], count=count)

    def get_8k_filings(self, ticker: str, count: int = 20) -> List[Dict]:
        """Get 8-K filings (material events)"""
        return self.search_company_filings(ticker, forms=["8-K"], count=count)

    def get_proxy_statements(self, ticker: str, count: int = 5) -> List[Dict]:
        """Get proxy statements (DEF 14A filings)"""
        return self.search_company_filings(ticker, forms=["DEF 14A"], count=count)

    def get_registration_statements(self, ticker: str, count: int = 10) -> List[Dict]:
        """Get registration statements (S-1, S-3, S-8 filings)"""
        return self.search_company_filings(
            ticker, forms=["S-1", "S-3", "S-8", "S-4"], count=count
        )

    def get_filings_summary(self, ticker: str) -> Dict[str, int]:
        """Get summary of filing types for a company"""
        cik = self.get_cik(ticker)
        if not cik:
            return {}

        url = f"{self.API_URL}/CIK{cik.zfill(10)}.json"
        self._rate_limit()

        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()

            filings = data.get("filings", {}).get("recent", {})
            forms = filings.get("form", [])

            summary = {}
            for form in forms:
                summary[form] = summary.get(form, 0) + 1

            return summary
        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            logger.error(f"Error getting filings summary for {ticker}: {str(e)}")
            return {}

    def get_recent_filings_all(self, ticker: str, count: int = 20) -> List[Dict]:
        """Get most recent filings regardless of type"""
        cik = self.get_cik(ticker)
        if not cik:
            return []

        url = f"{self.API_URL}/CIK{cik.zfill(10)}.json"
        self._rate_limit()

        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()

            filings = data.get("filings", {}).get("recent", {})

            if not filings:
                return []

            results = []
            num_filings = min(len(filings.get("form", [])), count)

            for i in range(num_filings):
                try:
                    accession_number = (
                        filings["accessionNumber"][i]
                        if filings.get("accessionNumber")
                        else ""
                    )
                    results.append(
                        {
                            "accession_number": accession_number,
                            "filing_date": filings["filingDate"][i]
                            if filings.get("filingDate")
                            else "",
                            "report_date": filings.get("reportDate", [""])[i]
                            if filings.get("reportDate")
                            else "",
                            "form": filings["form"][i] if filings.get("form") else "",
                            "primary_doc": filings["primaryDocument"][i]
                            if filings.get("primaryDocument")
                            else "",
                            "size": filings.get("size", [0])[i]
                            if filings.get("size")
                            else 0,
                            "is_amendment": filings.get("isAmendment", [False])[i]
                            if filings.get("isAmendment")
                            else False,
                            "url": f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number.replace('-', '')}"
                            if accession_number
                            else "",
                        }
                    )
                except (KeyError, IndexError) as e:
                    logger.warning(f"Error processing filing at index {i}: {e}")
                    continue

            return results
        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            logger.error(f"Error getting recent filings for {ticker}: {str(e)}")
            return []

        url = f"{self.API_URL}/CIK{cik.zfill(10)}.json"
        self._rate_limit()

        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()

            filings = data.get("filings", {}).get("recent", {})

            results = []
            num_filings = min(len(filings.get("form", [])), count)

            for i in range(num_filings):
                results.append(
                    {
                        "accession_number": filings["accessionNumber"][i],
                        "filing_date": filings["filingDate"][i],
                        "report_date": filings.get("reportDate", [""])[i],
                        "form": filings["form"][i],
                        "primary_doc": filings["primaryDocument"][i],
                        "size": filings.get("size", [0])[i],
                        "is_amendment": filings.get("isAmendment", [False])[i],
                        "url": f"https://www.sec.gov/Archives/edgar/data/{cik}/{filings['accessionNumber'][i].replace('-', '')}",
                    }
                )

            return results
        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            logger.error(f"Error getting recent filings for {ticker}: {str(e)}")
            return []
