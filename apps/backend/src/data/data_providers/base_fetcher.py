import asyncio
import aiohttp
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
from django.utils import timezone

from investments.models.api_key import APIKey
from investments.models.api_call_log import APIKeyUsageLog
from investments.services.api_key_manager import APIKeyManager
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)

class BaseAPIFetcher(ABC):
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self.key_manager = APIKeyManager(provider_name)
        self.session: Optional[aiohttp.ClientSession] = None
        self.current_key: Optional[APIKey] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @abstractmethod
    def get_base_url(self) -> str:
        pass
    
    @abstractmethod
    def extract_rate_limit_error(self, response: dict) -> Optional[str]:
        pass
    
    async def request(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        method: str = "GET",
        max_retries: int = 3
    ) -> Dict[str, Any]:
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            api_key = self.key_manager.get_best_key()
            
            if not api_key:
                raise Exception(f"No available API keys for {self.provider_name}")
            
            self.current_key = api_key
            start_time = timezone.now()
            
            try:
                api_key.increment_usage()
                
                response_data = await self._make_request(endpoint, params, method, api_key)
                
                response_time = (timezone.now() - start_time).total_seconds() * 1000
                
                rate_limit_error = self.extract_rate_limit_error(response_data)
                if rate_limit_error:
                    logger.warning(f"Rate limit hit: {rate_limit_error}")
                    
                    await self._log_api_call(
                        api_key, endpoint, method, success=False,
                        status_code=429, response_time_ms=int(response_time),
                        error_type="rate_limit", error_message=rate_limit_error,
                        request_params=params
                    )
                    
                    self.current_key = self.key_manager.rotate_on_rate_limit(api_key)
                    retry_count += 1
                    continue
                
                await self._log_api_call(
                    api_key, endpoint, method, success=True,
                    status_code=200, response_time_ms=int(response_time),
                    request_params=params
                )
                
                api_key.record_success()
                return response_data
                
            except Exception as e:
                response_time = (timezone.now() - start_time).total_seconds() * 1000
                last_error = e
                
                await self._log_api_call(
                    api_key, endpoint, method, success=False,
                    status_code=500, response_time_ms=int(response_time),
                    error_type=str(type(e).__name__), error_message=str(e),
                    request_params=params
                )
                
                api_key.record_failure(str(type(e).__name__))
                
                if isinstance(e, (ValueError, KeyError)):
                    raise
                
                retry_count += 1
                await asyncio.sleep(1 * retry_count)
        
        raise Exception(f"Max retries exceeded. Last error: {last_error}")
    
    async def _make_request(self, endpoint: str, params: Optional[Dict], method: str, api_key: APIKey) -> Dict:
        url = f"{self.get_base_url()}/{endpoint}"
        headers = self._get_headers(api_key)
        
        async with self.session.request(method, url, params=params, headers=headers) as response:
            response.raise_for_status()
            return await response.json()
    
    def _get_headers(self, api_key: APIKey) -> Dict:
        return {}
    
    async def _log_api_call(self, api_key: APIKey, endpoint: str, method: str, success: bool, status_code: int, response_time_ms: int, error_type: str = "", error_message: str = "", request_params: Dict = None):
        try:
            APIKeyUsageLog.objects.create(
                api_key=api_key,
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                success=success,
                response_time_ms=response_time_ms,
                error_type=error_type,
                error_message=error_message[:1000],
                request_params=request_params or {}
            )
        except Exception as e:
            logger.error(f"Failed to log API call: {str(e)}")
