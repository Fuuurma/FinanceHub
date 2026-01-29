"""
SEC Filings API Router
Exposes SEC Edgar endpoints for frontend integration - company filings, insider trading, annual/quarterly reports
"""

from ninja import Router
from ninja_jwt import authenticate
from investments.tasks.sec_edgar_tasks import (
    fetch_company_info_sec,
    fetch_company_filings_sec,
    fetch_all_filings_sec,
    fetch_insider_transactions_sec,
    fetch_annual_reports_sec,
    fetch_quarterly_reports_sec,
    fetch_current_reports_sec,
    fetch_filings_summary_sec,
)

router = Router(tags=["SEC Filings"])


@router.get("/company/{symbol}")
@authenticate
def get_company_info(request, symbol: str):
    """Get SEC company information (CIK, SIC, state of incorporation)"""
    result = fetch_company_info_sec.delay(symbol)
    return result.get(timeout=30)


@router.get("/filings/{symbol}")
@authenticate
def get_company_filings(request, symbol: str, filing_type: str = None, count: int = 10):
    """Get all SEC filings for a company"""
    result = fetch_company_filings_sec.delay(symbol, count)
    return result.get(timeout=30)


@router.get("/summary/{symbol}")
@authenticate
def get_filings_summary(request, symbol: str):
    """Get filing type summary for a company"""
    result = fetch_filings_summary_sec.delay(symbol)
    return result.get(timeout=30)


@router.get("/10k/{symbol}")
@authenticate
def get_annual_reports(request, symbol: str, count: int = 5):
    """Get annual reports (10-K, 20-F, 40-F)"""
    result = fetch_annual_reports_sec.delay(symbol, count)
    return result.get(timeout=30)


@router.get("/10q/{symbol}")
@authenticate
def get_quarterly_reports(request, symbol: str, count: int = 5):
    """Get quarterly reports (10-Q)"""
    result = fetch_quarterly_reports_sec.delay(symbol, count)
    return result.get(timeout=30)


@router.get("/8k/{symbol}")
@authenticate
def get_current_reports(request, symbol: str, count: int = 10):
    """Get current reports (8-K) - material events"""
    result = fetch_current_reports_sec.delay(symbol, count)
    return result.get(timeout=30)


@router.get("/insider/{symbol}")
@authenticate
def get_insider_transactions(request, symbol: str, count: int = 50):
    """Get Form 4 insider trading filings"""
    result = fetch_insider_transactions_sec.delay(symbol, count)
    return result.get(timeout=30)


@router.get("/proxy/{symbol}")
@authenticate
def get_proxy_statements(request, symbol: str, count: int = 5):
    """Get proxy statements (DEF 14A)"""
    result = fetch_company_filings_sec.delay(symbol)
    return result.get(timeout=30)
