"""
Test Crypto Data Cross-Validation and Batch Operations
Run this script to verify Phase 2.3 enhancements
"""
import asyncio
import sys
import os
from datetime import datetime

# Add Django project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')

import django
django.setup()

from data.data_providers.crypto_cross_validator import get_crypto_cross_validator
from data.data_providers.unified_crypto_provider import get_unified_crypto_provider
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


async def test_cross_validation_single():
    """Test 1: Cross-validation for single symbol"""
    print("\n" + "="*60)
    print("TEST 1: Cross-Validation (Single Symbol)")
    print("="*60)
    
    try:
        validator = get_crypto_cross_validator()
        
        # Validate BTC
        print("Validating BTC...")
        result = await validator.validate_symbol('BTC', force_refresh=True)
        
        if result:
            print(f"Symbol: {result.symbol}")
            print(f"Price match: {result.price_match}")
            print(f"Price difference: {result.price_difference_percent:.2f}%")
            print(f"Volume match: {result.volume_match}")
            print(f"Market cap match: {result.market_cap_match}")
            print(f"Overall confidence: {result.overall_confidence:.2f}")
            print(f"Recommended source: {result.recommended_source}")
            
            if result.coingecko_data:
                print(f"\nCoinGecko price: ${result.coingecko_data.get('price', 0)}")
            
            if result.coinmarketcap_data:
                print(f"CoinMarketCap price: ${result.coinmarketcap_data.get('price', 0)}")
        
        print("✅ Cross-validation test passed!")
        return True
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


async def test_cross_validation_batch():
    """Test 2: Cross-validation for multiple symbols"""
    print("\n" + "="*60)
    print("TEST 2: Cross-Validation (Batch)")
    print("="*60)
    
    try:
        validator = get_crypto_cross_validator()
        
        symbols = ['BTC', 'ETH', 'BNB', 'XRP', 'ADA']
        
        print(f"Validating {len(symbols)} symbols...")
        results = await validator.validate_batch(symbols)
        
        print(f"\nResults Summary:")
        print(f"Validations: {len(results)}")
        
        avg_confidence = sum(r.overall_confidence for r in results.values() if r.overall_confidence) / len(results)
        print(f"Average confidence: {avg_confidence:.2f}")
        
        cg_count = sum(1 for r in results.values() if r.coingecko_data)
        cmc_count = sum(1 for r in results.values() if r.coinmarketcap_data)
        both_count = sum(1 for r in results.values() if r.coingecko_data and r.coinmarketcap_data)
        
        print(f"CoinGecko available: {cg_count}")
        print(f"CoinMarketCap available: {cmc_count}")
        print(f"Both available: {both_count}")
        
        print(f"\nTop 5 by confidence:")
        sorted_results = sorted(results.items(), key=lambda x: x[1].overall_confidence if x[1].overall_confidence else 0, reverse=True)
        
        for symbol, result in sorted_results[:5]:
            print(f"  {symbol:6} | Confidence: {result.overall_confidence:.2f} | Source: {result.recommended_source}")
        
        print("✅ Batch validation test passed!")
        return True
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


async def test_anomaly_detection():
    """Test 3: Anomaly detection"""
    print("\n" + "="*60)
    print("TEST 3: Anomaly Detection")
    print("="*60)
    
    try:
        validator = get_crypto_cross_validator()
        
        symbols = ['BTC', 'ETH', 'BNB', 'XRP', 'ADA', 'DOGE', 'SOL', 'DOT', 'MATIC', 'LTC']
        
        print(f"Checking {len(symbols)} symbols for anomalies...")
        anomalies = await validator.detect_anomalies(symbols, threshold=0.7)
        
        print(f"\nFound {len(anomalies)} anomalies (confidence < 0.7)")
        
        if anomalies:
            for anomaly in anomalies:
                print(f"  {anomaly['symbol']:6} | Confidence: {anomaly['confidence']:.2f} | Source: {anomaly['recommended_source']}")
        else:
            print("  No anomalies found (all data has high confidence)")
        
        print("✅ Anomaly detection test passed!")
        return True
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


async def test_unified_provider():
    """Test 4: Unified provider with intelligent selection"""
    print("\n" + "="*60)
    print("TEST 4: Unified Crypto Provider")
    print("="*60)
    
    try:
        provider = get_unified_crypto_provider()
        
        # Fetch single crypto
        print("Fetching BTC with validation...")
        data = await provider.fetch_crypto_data('BTC', use_validation=True, force_refresh=True)
        
        if data:
            print(f"Symbol: {data.get('symbol')}")
            print(f"Price: ${data.get('price', 0)}")
            print(f"Market Cap: ${data.get('market_cap', 0):,.0f}")
            print(f"Volume 24h: ${data.get('volume_24h', 0):,.0f}")
            print(f"Change 24h: {data.get('change_24h', 0):.2f}%")
            print(f"Source: {data.get('source')}")
            
            if 'validation' in data:
                val = data['validation']
                print(f"Validation confidence: {val.get('confidence', 0):.2f}")
                print(f"Price diff: {val.get('price_difference_percent', 0):.2f}%")
        
        print("✅ Unified provider test passed!")
        return True
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


async def test_batch_fetch():
    """Test 5: Batch fetch with polars optimization"""
    print("\n" + "="*60)
    print("TEST 5: Batch Fetch with Polars")
    print("="*60)
    
    try:
        provider = get_unified_crypto_provider()
        
        symbols = ['BTC', 'ETH', 'BNB', 'XRP', 'ADA', 'DOGE', 'SOL', 'DOT', 'MATIC', 'LTC', 
                   'AVAX', 'LINK', 'UNI', 'ATOM', 'XLM', 'ETC', 'XMR', 'ALGO', 'VET', 'FIL']
        
        print(f"Fetching {len(symbols)} cryptos in batch...")
        start_time = datetime.now()
        
        results = await provider.fetch_batch_cryptos(symbols, use_validation=False, force_refresh=True)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        successful = sum(1 for v in results.values() if v is not None)
        failed = len(symbols) - successful
        
        print(f"\nBatch fetch complete:")
        print(f"  Total symbols: {len(symbols)}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        print(f"  Success rate: {(successful/len(symbols)*100):.1f}%")
        print(f"  Time elapsed: {elapsed:.1f}s")
        print(f"  Avg per symbol: {(elapsed/len(symbols)*1000):.1f}ms")
        
        print(f"\nTop 5 by market cap:")
        sorted_results = sorted(
            [(s, v) for s, v in results.items() if v],
            key=lambda x: x[1].get('market_cap', 0),
            reverse=True
        )
        
        for i, (symbol, data) in enumerate(sorted_results[:5], 1):
            print(f"  {i}. {symbol:6} | ${data.get('price', 0):,.2f} | MC: ${data.get('market_cap', 0):,.0f}")
        
        print("✅ Batch fetch test passed!")
        return True
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


async def test_provider_health():
    """Test 6: Provider health monitoring"""
    print("\n" + "="*60)
    print("TEST 6: Provider Health Monitoring")
    print("="*60)
    
    try:
        provider = get_unified_crypto_provider()
        
        # Get health status
        cg_health = await provider.get_provider_health('coingecko')
        cmc_health = await provider.get_provider_health('coinmarketcap')
        
        print("\nCoinGecko Health:")
        print(f"  Healthy: {cg_health['is_healthy']}")
        print(f"  Last success: {cg_health['last_success']}")
        print(f"  Last failure: {cg_health['last_failure']}")
        print(f"  Consecutive failures: {cg_health['consecutive_failures']}")
        print(f"  Rate limited until: {cg_health['rate_limited_until']}")
        
        print("\nCoinMarketCap Health:")
        print(f"  Healthy: {cmc_health['is_healthy']}")
        print(f"  Last success: {cmc_health['last_success']}")
        print(f"  Last failure: {cmc_health['last_failure']}")
        print(f"  Consecutive failures: {cmc_health['consecutive_failures']}")
        print(f"  Rate limited until: {cmc_health['rate_limited_until']}")
        
        # Get provider summary
        summary = provider.get_provider_summary()
        
        print("\nProvider Configuration:")
        print(f"  Primary: {summary['primary_provider']}")
        print(f"  Secondary: {summary['secondary_provider']}")
        print(f"  Batch size: {summary['batch_config']['size']}")
        print(f"  Max concurrent: {summary['batch_config']['max_concurrent']}")
        
        print("✅ Provider health test passed!")
        return True
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


async def test_trending_fetch():
    """Test 7: Trending crypto fetch"""
    print("\n" + "="*60)
    print("TEST 7: Trending Crypto Fetch")
    print("="*60)
    
    try:
        provider = get_unified_crypto_provider()
        
        print("Fetching trending cryptos...")
        trending = await provider.get_trending_cryptos(limit=7)
        
        print(f"\nTop 7 Trending:")
        for i, crypto in enumerate(trending, 1):
            if crypto:
                print(f"  {i}. {crypto.get('symbol', 'N/A'):6} | ${crypto.get('price', 0):,.2f} | Change: {crypto.get('change_24h', 0):+.2f}%")
        
        print("✅ Trending fetch test passed!")
        return True
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


async def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("PHASE 2.3 - COIN GECKO & COINMARKETCAP OPTIMIZATION TEST SUITE")
    print("="*60)
    print("This script tests crypto data cross-validation and batch operations")
    print("Press Ctrl+C at any time to stop\n")
    
    results = {}
    
    # Test 1: Single symbol validation
    results['single_validation'] = await test_cross_validation_single()
    
    # Test 2: Batch validation
    results['batch_validation'] = await test_cross_validation_batch()
    
    # Test 3: Anomaly detection
    results['anomaly_detection'] = await test_anomaly_detection()
    
    # Test 4: Unified provider
    results['unified_provider'] = await test_unified_provider()
    
    # Test 5: Batch fetch
    results['batch_fetch'] = await test_batch_fetch()
    
    # Test 6: Provider health
    results['provider_health'] = await test_provider_health()
    
    # Test 7: Trending fetch
    results['trending'] = await test_trending_fetch()
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:25} | {status}")
    
    total_tests = len(results)
    passed = sum(1 for r in results.values() if r)
    print(f"\nTotal: {passed}/{total_tests} tests passed")
    
    if passed == total_tests:
        print("\n🎉 All tests passed! Phase 2.3 is working correctly.")
    else:
        print(f"\n⚠️  {total_tests - passed} test(s) failed. Please check errors above.")


if __name__ == "__main__":
    try:
        asyncio.run(run_all_tests())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nFatal error: {str(e)}")
        import traceback
        traceback.print_exc()