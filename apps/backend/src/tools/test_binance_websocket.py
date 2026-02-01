"""
Test Binance WebSocket Streaming and Data Processing
Run this script to verify Binance WebSocket functionality
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

from data.data_providers.binance.websocket_client import get_binance_ws_client
from data.data_providers.binance.order_book_service import get_binance_order_book_service
from data.data_providers.binance.trade_service import get_binance_trade_service
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)


async def test_websocket_connection():
    """Test 1: WebSocket connection"""
    print("\n" + "="*60)
    print("TEST 1: WebSocket Connection")
    print("="*60)
    
    try:
        ws_client = get_binance_ws_client()
        
        # Connect to WebSocket
        print("Connecting to Binance WebSocket...")
        success = await ws_client.connect()
        
        if success:
            print("✅ Connected successfully!")
            stats = ws_client.get_stats()
            print(f"Connection time: {stats['connection_time']}")
            print(f"Is connected: {stats['is_connected']}")
        else:
            print("❌ Failed to connect")
            return False
        
        await ws_client.disconnect()
        return True
    
    except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
        print(f"❌ Error: {str(e)}")
        return False


async def test_mini_ticker_stream(symbol: str = 'BTCUSDT', duration: int = 30):
    """Test 2: Mini ticker streaming"""
    print("\n" + "="*60)
    print(f"TEST 2: Mini Ticker Stream ({symbol})")
    print("="*60)
    
    try:
        ws_client = get_binance_ws_client()
        
        # Counter for updates
        update_count = {'count': 0}
        
        async def on_ticker_update(data):
            update_count['count'] += 1
            
            if update_count['count'] == 1:
                print(f"First update received:")
                print(f"  Price: {data.get('c')}")
                print(f"  Change: {data.get('p')} ({data.get('P')}%)")
                print(f"  Volume: {data.get('v')}")
            elif update_count['count'] % 10 == 0:
                print(f"  Updates received: {update_count['count']}")
        
        # Connect
        print("Connecting to WebSocket...")
        await ws_client.connect()
        
        # Subscribe
        print(f"Subscribing to mini ticker for {symbol}...")
        await ws_client.subscribe_mini_ticker(symbol, on_ticker_update)
        
        # Listen for specified duration
        print(f"Listening for {duration} seconds...")
        print("Waiting for updates...")
        
        start_time = datetime.now()
        while (datetime.now() - start_time).total_seconds() < duration:
            try:
                await asyncio.sleep(1)
            except KeyboardInterrupt:
                break
        
        # Get stats
        stats = ws_client.get_stats()
        print(f"\n✅ Test completed!")
        print(f"Total messages received: {stats['messages_received']}")
        print(f"Ticker updates: {update_count['count']}")
        
        await ws_client.disconnect()
        return True
    
    except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
        print(f"❌ Error: {str(e)}")
        return False


async def test_trade_stream(symbol: str = 'BTCUSDT', duration: int = 30):
    """Test 3: Trade execution stream"""
    print("\n" + "="*60)
    print(f"TEST 3: Trade Execution Stream ({symbol})")
    print("="*60)
    
    try:
        trade_service = get_binance_trade_service()
        
        # Connect WebSocket
        ws_client = get_binance_ws_client()
        await ws_client.connect()
        
        # Subscribe to trades
        print(f"Subscribing to aggregated trades for {symbol}...")
        await trade_service.subscribe_agg_trades(symbol)
        
        # Listen
        print(f"Listening for trades for {duration} seconds...")
        
        start_time = datetime.now()
        while (datetime.now() - start_time).total_seconds() < duration:
            await asyncio.sleep(1)
            
            # Get recent trades
            recent_trades = await trade_service.get_recent_trades(symbol, limit=5)
            
            if recent_trades:
                print(f"Recent trades: {len(recent_trades)}")
                for trade in recent_trades[:3]:
                    print(f"  {trade['side']:4} {trade['quantity']:10.4f} @ ${trade['price']:10.2f}")
                break
        
        # Get trade stats
        stats = await trade_service.get_trade_stats(symbol)
        if stats:
            print(f"\nTrade Statistics:")
            print(f"  Total trades: {stats['total_trades']}")
            print(f"  Buy ratio: {stats['buy_ratio']:.2%}")
            print(f"  VWAP: ${stats['vwap_all']:.2f}")
        
        await ws_client.disconnect()
        return True
    
    except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
        print(f"❌ Error: {str(e)}")
        return False


async def test_order_book(symbol: str = 'BTCUSDT', duration: int = 30):
    """Test 4: Order book depth"""
    print("\n" + "="*60)
    print(f"TEST 4: Order Book Depth ({symbol})")
    print("="*60)
    
    try:
        order_book_service = get_binance_order_book_service()
        
        # Initialize order book
        print(f"Initializing order book for {symbol}...")
        await order_book_service.initialize_depth(symbol, level=20)
        
        # Wait a bit for updates
        print("Waiting for order book updates...")
        await asyncio.sleep(5)
        
        # Get order book
        order_book = await order_book_service.get_order_book(symbol, levels=10)
        
        if order_book:
            print(f"\nOrder Book Snapshot:")
            print(f"Best bid: ${order_book['best_bid']['price']:.2f} ({order_book['best_bid']['quantity']:.4f})")
            print(f"Best ask: ${order_book['best_ask']['price']:.2f} ({order_book['best_ask']['quantity']:.4f})")
            print(f"Spread: ${order_book['spread']:.2f} ({order_book['spread_percent']:.4f}%)")
            print(f"Imbalance: {order_book['imbalance']:.2f}")
            
            print(f"\nTop Bids:")
            for bid in order_book['bids'][:5]:
                print(f"  ${bid['price']:10.2f} | {bid['quantity']:10.4f}")
            
            print(f"\nTop Asks:")
            for ask in order_book['asks'][:5]:
                print(f"  ${ask['price']:10.2f} | {ask['quantity']:10.4f}")
        
        # Get depth summary
        summary = await order_book_service.get_depth_summary(symbol)
        if summary:
            print(f"\nDepth Summary:")
            print(f"  Total bids: {summary['total_bids']}")
            print(f"  Total asks: {summary['total_asks']}")
            print(f"  Bid volume: {summary['bid_volume']:.2f}")
            print(f"  Ask volume: {summary['ask_volume']:.2f}")
            print(f"  Liquidity score: {summary['liquidity_score']:.2f}/100")
        
        # Get price impact analysis
        impact = await order_book_service.get_price_impact_analysis(
            symbol,
            trade_sizes=[0.1, 0.5, 1.0, 5.0]
        )
        
        if impact:
            print(f"\nPrice Impact Analysis:")
            for size, data in impact.items():
                if data['avg_impact_percent']:
                    print(f"  ${size} BTC: {data['avg_impact_percent']:.4f}% slippage")
        
        # Stop service
        await order_book_service.stop()
        return True
    
    except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
        print(f"❌ Error: {str(e)}")
        return False


async def test_trade_flow(symbol: str = 'BTCUSDT', duration: int = 60):
    """Test 5: Trade flow analysis"""
    print("\n" + "="*60)
    print(f"TEST 5: Trade Flow Analysis ({symbol})")
    print("="*60)
    
    try:
        trade_service = get_binance_trade_service()
        
        # Connect and subscribe
        ws_client = get_binance_ws_client()
        await ws_client.connect()
        await trade_service.subscribe_agg_trades(symbol)
        
        # Wait for trades to accumulate
        print(f"Collecting trades for {duration} seconds...")
        start_time = datetime.now()
        
        while (datetime.now() - start_time).total_seconds() < duration:
            await asyncio.sleep(10)
            
            # Get trade flow
            flow = await trade_service.get_trade_flow(symbol, window=50)
            
            if flow and flow['trade_count'] >= 10:
                print(f"\nTrade Flow (last 50 trades):")
                print(f"  Total trades: {flow['trade_count']}")
                print(f"  Buy trades: {flow['buy_count']}")
                print(f"  Sell trades: {flow['sell_count']}")
                print(f"  Buy ratio (volume): {flow['buy_ratio_volume']:.2%}")
                print(f"  Direction: {flow['direction']}")
                print(f"  Total volume: {flow['total_volume']:.2f}")
        
        # Find large trades
        large_trades = await trade_service.get_large_trades(symbol, threshold_multiplier=10.0)
        
        if large_trades:
            print(f"\nLarge Trades (whales):")
            for trade in large_trades[:5]:
                print(f"  ${trade['value']:,.2f} | {trade['quantity']:.4f} @ ${trade['price']:.2f}")
        
        # Get volume profile
        profile = await trade_service.get_volume_profile(symbol, bins=20)
        
        if profile:
            print(f"\nVolume Profile:")
            print(f"  Price range: ${profile['min_price']:.2f} - ${profile['max_price']:.2f}")
            print(f"  Total trades: {profile['total_trades']}")
        
        await ws_client.disconnect()
        return True
    
    except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
        print(f"❌ Error: {str(e)}")
        return False


async def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("BINANCE WEBSOCKET TEST SUITE")
    print("="*60)
    print("This script tests Binance WebSocket streaming functionality")
    print("Press Ctrl+C at any time to stop\n")
    
    results = {}
    
    # Test 1: Connection
    results['connection'] = await test_websocket_connection()
    
    # Test 2: Mini ticker
    results['ticker'] = await test_mini_ticker_stream('BTCUSDT', duration=15)
    
    # Test 3: Trade stream
    results['trade'] = await test_trade_stream('BTCUSDT', duration=20)
    
    # Test 4: Order book
    results['order_book'] = await test_order_book('BTCUSDT', duration=10)
    
    # Test 5: Trade flow
    results['trade_flow'] = await test_trade_flow('BTCUSDT', duration=30)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} | {status}")
    
    total_tests = len(results)
    passed = sum(1 for r in results.values() if r)
    print(f"\nTotal: {passed}/{total_tests} tests passed")
    
    if passed == total_tests:
        print("\n🎉 All tests passed! Binance WebSocket is working correctly.")
    else:
        print(f"\n⚠️  {total_tests - passed} test(s) failed. Please check the errors above.")


if __name__ == "__main__":
    try:
        asyncio.run(run_all_tests())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
        print(f"\n\nFatal error: {str(e)}")
        import traceback
        traceback.print_exc()