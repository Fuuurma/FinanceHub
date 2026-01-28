import asyncio
import aiohttp
from typing import Dict, List, Optional
from datetime import datetime, date
from decimal import Decimal
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class DeFiLlamaFetcher:
    """
    DeFi Llama API Fetcher
    Completely free, no API key required

    API Docs: https://docs.llama.fi/api/
    """

    BASE_URL = "https://api.llama.fi"

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make API request"""
        try:
            url = f"{self.BASE_URL}/{endpoint}"
            async with self.session.get(url, params=params or {}) as response:
                response.raise_for_status()
                data = await response.json()

                await asyncio.sleep(0.3)
                return data

        except Exception as e:
            logger.error(f"DeFi Llama API error: {str(e)}")
            raise

    async def get_protocol_data(self, protocol: str) -> Dict:
        """Get comprehensive protocol data"""
        return await self._request(f"protocol/{protocol}")

    async def get_all_protocols(self) -> List[Dict]:
        """Get all protocols (no parameters, returns TVL for all)"""
        return await self._request("protocols")

    async def get_tvl(self, protocol: str) -> List[Dict]:
        """Get TVL history for a protocol"""
        return await self._request(f"protocol/{protocol}")

    async def get_tvl_by_date(self, protocol: str, date: str) -> Dict:
        """Get TVL for a protocol on a specific date (YYYY-MM-DD)"""
        return await self._request(f"protocol/{protocol}", {"date": date})

    async def get_tvl_by_chain(self, chain: str) -> Dict:
        """Get TVL data for a specific chain"""
        return await self._request(f"tvl/{chain}")

    async def get_all_chains(self) -> Dict:
        """Get TVL for all chains"""
        return await self._request("chains")

    async def get_protocols_by_chain(self, chain: str) -> List[Dict]:
        """Get all protocols on a specific chain"""
        return await self._request(f"chains/{chain}")

    async def get_historical_tvl(self, protocol: str) -> List[Dict]:
        """Get historical TVL for a protocol"""
        return await self._request(f"protocol/{protocol}")

    async def get_dex_volume(self, protocol: str) -> List[Dict]:
        """Get DEX volume for a protocol"""
        return await self._request(f"protocol/{protocol}")

    async def get_bridge_volume(self, protocol: str) -> List[Dict]:
        """Get bridge volume for a protocol"""
        return await self._request(f"protocol/{protocol}")

    async def get_stablecoins(self) -> List[Dict]:
        """Get stablecoin data"""
        return await self._request("stablecoins")

    async def get_stablecoin_tvl(self, stablecoin: str) -> List[Dict]:
        """Get stablecoin TVL history"""
        return await self._request(f"stablecoin/{stablecoin}")

    async def get_yields(self, protocol: Optional[str] = None) -> List[Dict]:
        """Get lending/yield data"""
        if protocol:
            return await self._request(f"yields/{protocol}")
        return await self._request("yields")

    async def get_fees(self, protocol: str) -> Dict:
        """Get protocol fees"""
        return await self._request(f"protocol/{protocol}")

    async def get_revenue(self, protocol: str) -> Dict:
        """Get protocol revenue"""
        return await self._request(f"protocol/{protocol}")

    async def get_dexs(self) -> List[Dict]:
        """Get all DEX protocols"""
        return await self._request("protocols/dex")

    async def get_lending(self) -> List[Dict]:
        """Get all lending protocols"""
        return await self._request("protocols/lending")

    async def get_yield_aggregators(self) -> List[Dict]:
        """Get all yield aggregator protocols"""
        return await self._request("protocols/yield")

    async def get_bridges(self) -> List[Dict]:
        """Get all bridge protocols"""
        return await self._request("protocols/bridge")

    async def get_chain_overview(self, chain: str) -> Dict:
        """Get overview of a chain's DeFi ecosystem"""
        return await self._request(f"chains/{chain}")


class CryptoProtocolMetrics:
    """Helper class to transform DeFi Llama data into structured format"""

    @staticmethod
    def extract_tvl_data(raw_data: Dict) -> Dict:
        """Extract key TVL metrics from raw DeFi Llama response"""
        return {
            "current_tvl": raw_data.get("tvl"),
            "tvl_change_24h": raw_data.get("tvlChange24h"),
            "tvl_change_7d": raw_data.get("tvlChange7d"),
            "tvl_change_30d": raw_data.get("tvlChange30d"),
            "chain": raw_data.get("chain"),
            "category": raw_data.get("category"),
        }

    @staticmethod
    def extract_revenue_data(raw_data: Dict) -> Dict:
        """Extract revenue metrics from raw DeFi Llama response"""
        return {
            "daily_revenue": raw_data.get("dailyRevenue"),
            "daily_fees": raw_data.get("dailyFees"),
            "total_revenue": raw_data.get("totalRevenue"),
            "total_fees": raw_data.get("totalFees"),
            "monthly_revenue": raw_data.get("monthlyRevenue"),
            "monthly_fees": raw_data.get("monthlyFees"),
        }

    @staticmethod
    def extract_dex_metrics(raw_data: Dict) -> Dict:
        """Extract DEX-specific metrics"""
        return {
            "volume_24h": raw_data.get("volume24h"),
            "volume_7d": raw_data.get("volume7d"),
            "volume_change_24h": raw_data.get("volumeChange24h"),
            "fees_24h": raw_data.get("fees24h"),
            "fees_7d": raw_data.get("fees7d"),
            "revenue_24h": raw_data.get("revenue24h"),
        }

    @staticmethod
    def extract_lending_metrics(raw_data: Dict) -> Dict:
        """Extract lending-specific metrics"""
        return {
            "total_borrowed": raw_data.get("totalBorrowed"),
            "total_deposits": raw_data.get("totalDeposits"),
            "borrow_rate": raw_data.get("borrowRate"),
            "supply_rate": raw_data.get("supplyRate"),
            "utilization_rate": raw_data.get("utilizationRate"),
        }

    @staticmethod
    def extract_stablecoin_metrics(raw_data: Dict) -> Dict:
        """Extract stablecoin metrics"""
        return {
            "circulating_supply": raw_data.get("circulatingSupply"),
            "total_supply": raw_data.get("totalSupply"),
            "pegged_usd": raw_data.get("peg"),
            "peg_change_24h": raw_data.get("pegChange24h"),
            "chain": raw_data.get("chain"),
        }

    @staticmethod
    def transform_protocol_list(protocols: List[Dict]) -> List[Dict]:
        """Transform protocol list for easier consumption"""
        return [
            {
                "name": p.get("name"),
                "slug": p.get("slug"),
                "tvl": p.get("tvl"),
                "tvl_change_24h": p.get("tvlChange24h"),
                "chain": p.get("chain"),
                "category": p.get("category"),
                "logo_url": p.get("logo"),
            }
            for p in protocols
        ]
