"""
Performance Benchmarks for FinanceHub Data Fetchers
Tests key rotation, API performance, and data processing speed
"""
import asyncio
import time
from typing import Dict, List, Any
import orjson
import polars as pl
from datetime import datetime

from data.data_providers.alphaVantage.scraper import AlphaVantageScraper
from data.data_providers.coingecko.scraper import CoinGeckoScraper
from data.data_providers.coinmarketcap.scraper import CoinMarketCapScraper
from investments.services.api_key_manager import APIKeyManager
from investments.models.api_key import APIKey
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


class PerformanceBenchmark:
    """Performance benchmark suite for data fetchers"""
    
    def __init__(self):
        self.results = {}
    
    def benchmark_json_parsing(self, data_size: int = 1000) -> Dict[str, Any]:
        """Benchmark JSON parsing performance (orjson vs python json)"""
        import json
        
        # Generate test data
        test_data = {'symbol': 'BTC', 'price': 50000.0, 'volume': 1000000, 'data': [{'test': i} for i in range(data_size)]}
        json_str = json.dumps(test_data)
        
        # Benchmark orjson
        orjson_times = []
        for _ in range(100):
            start = time.perf_counter()
            orjson.loads(json_str)
            orjson_times.append(time.perf_counter() - start)
        
        # Benchmark python json
        python_times = []
        for _ in range(100):
            start = time.perf_counter()
            json.loads(json_str)
            python_times.append(time.perf_counter() - start)
        
        orjson_avg = sum(orjson_times) / len(orjson_times) * 1000  # Convert to ms
        python_avg = sum(python_times) / len(python_times) * 1000  # Convert to ms
        speedup = python_avg / orjson_avg if orjson_avg > 0 else 1
        
        result = {
            'data_size': len(json_str),
            'orjson_avg_ms': orjson_avg,
            'python_json_avg_ms': python_avg,
            'speedup_x': speedup,
            'passes': speedup > 2  # Pass if orjson is 2x faster
        }
        
        self.results['json_parsing'] = result
        logger.info(f"JSON parsing benchmark: orjson {orjson_avg:.2f}ms vs python {python_avg:.2f}ms ({speedup:.1f}x speedup)")
        
        return result
    
    def benchmark_data_processing(self, num_rows: int = 10000) -> Dict[str, Any]:
        """Benchmark data processing (polars vs pandas)"""
        try:
            import pandas as pd
        except ImportError:
            logger.warning("pandas not installed, skipping comparison")
            return {}
        
        # Generate test data
        test_data = {
            'symbol': ['BTC'] * num_rows + ['ETH'] * num_rows,
            'price': [50000.0 + i for i in range(num_rows)] + [3000.0 + i for i in range(num_rows)],
            'volume': [1000000 + i for i in range(num_rows)] + [500000 + i for i in range(num_rows)],
            'timestamp': [datetime.now() for _ in range(num_rows * 2)]
        }
        
        # Benchmark polars
        polars_times = []
        for _ in range(50):
            start = time.perf_counter()
            df = pl.DataFrame(test_data)
            _ = df.group_by('symbol').agg(
                pl.col('price').mean(),
                pl.col('volume').sum()
            )
            polars_times.append(time.perf_counter() - start)
        
        # Benchmark pandas
        pandas_times = []
        for _ in range(50):
            start = time.perf_counter()
            df = pd.DataFrame(test_data)
            _ = df.groupby('symbol').agg({'price': 'mean', 'volume': 'sum'})
            pandas_times.append(time.perf_counter() - start)
        
        polars_avg = sum(polars_times) / len(polars_times) * 1000  # Convert to ms
        pandas_avg = sum(pandas_times) / len(pandas_times) * 1000  # Convert to ms
        speedup = pandas_avg / polars_avg if polars_avg > 0 else 1
        
        result = {
            'num_rows': num_rows * 2,
            'polars_avg_ms': polars_avg,
            'pandas_avg_ms': pandas_avg,
            'speedup_x': speedup,
            'passes': speedup > 5  # Pass if polars is 5x faster
        }
        
        self.results['data_processing'] = result
        logger.info(f"Data processing benchmark: polars {polars_avg:.2f}ms vs pandas {pandas_avg:.2f}ms ({speedup:.1f}x speedup)")
        
        return result
    
    async def benchmark_api_key_rotation(self, provider: str = "alpha_vantage") -> Dict[str, Any]:
        """Benchmark API key rotation performance"""
        try:
            manager = APIKeyManager(provider)
            
            # Benchmark key selection
            selection_times = []
            for _ in range(100):
                start = time.perf_counter()
                key = manager.get_best_key()
                selection_times.append(time.perf_counter() - start)
                
                if not key:
                    logger.warning(f"No available keys for {provider}")
                    break
            
            avg_selection_time = (sum(selection_times) / len(selection_times)) * 1000 if selection_times else 0
            
            # Benchmark health report
            report_times = []
            for _ in range(10):
                start = time.perf_counter()
                report = manager.get_key_health_report()
                report_times.append(time.perf_counter() - start)
            
            avg_report_time = (sum(report_times) / len(report_times)) * 1000 if report_times else 0
            
            result = {
                'provider': provider,
                'avg_key_selection_ms': avg_selection_time,
                'avg_health_report_ms': avg_report_time,
                'selection_samples': len(selection_times),
                'report_samples': len(report_times),
                'passes': avg_selection_time < 10  # Pass if selection is under 10ms
            }
            
            self.results['key_rotation'] = result
            logger.info(f"Key rotation benchmark: selection {avg_selection_time:.2f}ms, report {avg_report_time:.2f}ms")
            
            return result
            
        except Exception as e:
            logger.error(f"Error benchmarking key rotation: {str(e)}")
            return {'error': str(e), 'passes': False}
    
    async def benchmark_fetch_performance(self, scraper_class, symbols: List[str], provider_name: str) -> Dict[str, Any]:
        """Benchmark API fetch performance"""
        try:
            scraper = scraper_class()
            
            fetch_times = []
            success_count = 0
            
            for symbol in symbols[:10]:  # Limit to 10 symbols
                try:
                    start = time.perf_counter()
                    
                    if provider_name == "alpha_vantage":
                        # Alpha Vantage is async
                        async with scraper:
                            await scraper.get_quote(symbol)
                    else:
                        # Others are also async
                        async with scraper:
                            if provider_name == "coingecko":
                                await scraper.get_coin(symbol.lower())
                            elif provider_name == "coinmarketcap":
                                await scraper.get_cryptocurrency_info(symbol)
                    
                    elapsed = time.perf_counter() - start
                    fetch_times.append(elapsed)
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"Error fetching {symbol}: {str(e)}")
                    continue
            
            avg_fetch_time = (sum(fetch_times) / len(fetch_times) * 1000) if fetch_times else 0
            success_rate = success_count / len(symbols[:10]) if symbols else 0
            
            result = {
                'provider': provider_name,
                'num_symbols': len(symbols[:10]),
                'success_rate': success_rate,
                'avg_fetch_time_ms': avg_fetch_time,
                'total_time_sec': sum(fetch_times),
                'passes': success_rate > 0.8 and avg_fetch_time < 5000  # Pass if >80% success and <5s average
            }
            
            self.results[f'fetch_{provider_name}'] = result
            logger.info(f"{provider_name} fetch benchmark: {success_count}/10 success, avg {avg_fetch_time:.2f}ms")
            
            return result
            
        except Exception as e:
            logger.error(f"Error benchmarking {provider_name} fetch: {str(e)}")
            return {'error': str(e), 'passes': False}
    
    async def run_all_benchmarks(self) -> Dict[str, Any]:
        """Run all performance benchmarks"""
        logger.info("Starting performance benchmarks...")
        
        # JSON parsing benchmark
        json_result = self.benchmark_json_parsing()
        
        # Data processing benchmark
        data_result = self.benchmark_data_processing()
        
        # Key rotation benchmark
        key_result = await self.benchmark_api_key_rotation("alpha_vantage")
        
        # API fetch benchmarks (only test with symbols, don't save to DB)
        test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'BTC', 'ETH', 'BNB', 'XRP', 'ADA']
        
        alpha_result = await self.benchmark_fetch_performance(AlphaVantageScraper, test_symbols, "alpha_vantage")
        coingecko_result = await self.benchmark_fetch_performance(CoinGeckoScraper, test_symbols, "coingecko")
        coinmarketcap_result = await self.benchmark_fetch_performance(CoinMarketCapScraper, test_symbols, "coinmarketcap")
        
        # Compile results
        all_results = {
            'timestamp': datetime.now().isoformat(),
            'benchmarks': {
                'json_parsing': json_result,
                'data_processing': data_result,
                'key_rotation': key_result,
                'api_fetches': {
                    'alpha_vantage': alpha_result,
                    'coingecko': coingecko_result,
                    'coinmarketcap': coinmarketcap_result
                }
            },
            'summary': self._generate_summary()
        }
        
        logger.info(f"Benchmarks completed: {all_results['summary']}")
        return all_results
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate benchmark summary"""
        passes = 0
        total = 0
        
        for key, result in self.results.items():
            if isinstance(result, dict) and 'passes' in result:
                total += 1
                if result['passes']:
                    passes += 1
        
        pass_rate = (passes / total * 100) if total > 0 else 0
        
        return {
            'total_benchmarks': total,
            'passed_benchmarks': passes,
            'pass_rate_percent': pass_rate,
            'status': 'PASS' if pass_rate >= 80 else 'FAIL'
        }


async def main():
    """Run all performance benchmarks"""
    benchmark = PerformanceBenchmark()
    results = await benchmark.run_all_benchmarks()
    
    # Save results to file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"benchmark_results_{timestamp}.json"
    
    with open(filename, 'w') as f:
        f.write(orjson.dumps(results, option=orjson.OPT_INDENT_2))
    
    print(f"\n{'='*60}")
    print("PERFORMANCE BENCHMARK RESULTS")
    print(f"{'='*60}")
    
    # Print summary
    summary = results['summary']
    print(f"\nSummary: {summary['passed_benchmarks']}/{summary['total_benchmarks']} passed ({summary['pass_rate_percent']:.1f}%)")
    print(f"Status: {summary['status']}")
    
    # Print individual benchmarks
    for name, result in results['benchmarks'].items():
        print(f"\n{name.upper()}:")
        if isinstance(result, dict) and 'passes' in result:
            status = "✓ PASS" if result['passes'] else "✗ FAIL"
            print(f"  {status}")
            for key, value in result.items():
                if key != 'passes':
                    print(f"  {key}: {value}")
        elif name == 'api_fetches':
            for provider, fetch_result in result.items():
                print(f"\n  {provider.upper()}:")
                if isinstance(fetch_result, dict) and 'passes' in fetch_result:
                    status = "✓ PASS" if fetch_result['passes'] else "✗ FAIL"
                    print(f"    {status}")
                    for key, value in fetch_result.items():
                        if key != 'passes':
                            print(f"    {key}: {value}")
    
    print(f"\n{'='*60}")
    print(f"Results saved to: {filename}")
    print(f"{'='*60}\n")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())
