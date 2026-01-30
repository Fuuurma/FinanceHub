#!/bin/bash

# Enhanced Background Jobs Manager
# Manages the comprehensive data population system

ACTION=$1

case "$ACTION" in
  start)
    echo "🚀 Starting Enhanced Background Jobs..."
    cd /Users/sergi/Desktop/Projects/FinanceHub/Backend
    nohup ./venv/bin/python enhanced_data_population.py > logs/enhanced_jobs.log 2>&1 &
    echo $! > enhanced_jobs.pid
    echo "✅ Enhanced jobs started (PID: $(cat enhanced_jobs.pid))"
    echo "📝 Logs: Backend/logs/enhanced_jobs.log"
    echo ""
    echo "📊 Assets being tracked:"
    echo "  - 100+ stocks (S&P 500 + more)"
    echo "  - 50+ cryptos (Top market cap)"
    echo "  - 30+ ETFs (Popular ETFs)"
    echo "  - 10+ indices (Major markets)"
    echo "  - 10 forex pairs (Major currencies)"
    ;;
    
  stop)
    echo "🛑 Stopping Enhanced Background Jobs..."
    if [ -f enhanced_jobs.pid ]; then
      pid=$(cat enhanced_jobs.pid)
      kill $pid 2>/dev/null
      rm enhanced_jobs.pid
      echo "✅ Enhanced jobs stopped"
    else
      echo "⚠️  No PID file found. Jobs may not be running."
    fi
    
    # Also stop original jobs if running
    ./manage_jobs.sh stop 2>/dev/null
    ;;
    
  restart)
    echo "🔄 Restarting Enhanced Background Jobs..."
    $0 stop
    sleep 2
    $0 start
    ;;
    
  status)
    echo "📊 Enhanced Background Jobs Status"
    echo "================================"
    
    if [ -f enhanced_jobs.pid ]; then
      pid=$(cat enhanced_jobs.pid)
      if ps -p $pid > /dev/null; then
        echo "  Status: ✅ Running"
        echo "  PID: $pid"
        echo "  Started: $(ps -p $pid -o lstart= 2>/dev/null || echo 'Unknown')"
        echo "  Memory: $(ps -p $pid -o rss= 2>/dev/null | awk '{printf \"%.1f MB\", $1/1024}')"
      else
        echo "  Status: ❌ Not running (stale PID file)"
        rm enhanced_jobs.pid
      fi
    else
      echo "  Status: ⏸️  Not running"
    fi
    
    echo ""
    echo "📬 Queue Status:"
    redis-cli -h localhost -p 6379 PING 2>/dev/null || echo "  ⚠️  Redis not responding"
    redis-cli -h localhost -p 6379 LLEN dramatiq:default 2>/dev/null | xargs -I {} echo "  Default queue: {} messages" || echo "  Queue: Empty"
    ;;
    
  monitor)
    echo "📈 Starting Enhanced Monitoring Dashboard..."
    cd /Users/sergi/Desktop/Projects/FinanceHub/Backend
    ./venv/bin/python monitor_background_jobs.py
    ;;
    
  logs)
    echo "📝 Showing enhanced jobs log (Ctrl+C to exit)..."
    if [ -f logs/enhanced_jobs.log ]; then
      tail -f logs/enhanced_jobs.log
    else
      echo "⚠️  Log file not found: Backend/logs/enhanced_jobs.log"
    fi
    ;;
  
  test)
    echo "🧪 Testing enhanced data collection..."
    cd /Users/sergi/Desktop/Projects/FinanceHub/Backend
    ./venv/bin/python -c "
import os, sys, django
sys.path.insert(0, '/Users/sergi/Desktop/Projects/FinanceHub/Backend/src')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

print('Testing Yahoo Finance fetch...')
from enhanced_data_population import fetch_yahoo_stocks_batch
result = fetch_yovsky_stocks_batch(['AAPL', 'MSFT', 'GOOGL'])
print(f'Result: {result}')
"
    ;;
    
  populate)
    echo "🔄 Running one-time comprehensive population..."
    cd /Users/sergi/Desktop/Projects/FinanceHub/Backend
    ./venv/bin/python -c "
import os, sys, django, asyncio
sys.path.insert(0, '/Users/sergi/Desktop/Projects/FinanceHub/Backend/src')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from enhanced_data_population import daily_data_fresh
import dramatiq
from dramatiq.brokers.redis import RedisBroker

# Configure broker
broker = RedisBroker(url='redis://localhost:6379')
dramatiq.set_broker(broker)

# Send task
daily_data_fresh.send()
print('✅ Comprehensive population task sent!')
print('This will take a few minutes to complete...')
print('Monitor progress: tail -f Backend/logs/enhanced_jobs.log')
"
    ;;
    
  *)
    echo "FinanceHub Enhanced Background Jobs Manager"
    echo "===================================="
    echo ""
    echo "Usage: ./enhanced_manage.sh {start|stop|restart|status|monitor|logs|test|populate}"
    echo ""
    echo "Commands:"
    echo "  start      - Start enhanced background jobs (stocks + cryptos + ETFs + indices + forex)"
    echo "  stop       - Stop enhanced background jobs"
    echo "  restart    - Restart enhanced background jobs"
    echo "  status     - Show running status and statistics"
    echo "  monitor    - Start real-time monitoring dashboard"
    echo "  logs       - Show enhanced jobs log (tail -f)"
    echo "  test       - Test data collection with quick fetch"
    echo "  populate   - Run one-time comprehensive population of all data"
    echo ""
    echo "Examples:"
    echo "  ./enhanced_manage.sh start     # Start jobs"
    echo "  ./enhanced_manage.sh status    # Check status"
    echo "  ./enhanced_manage.sh monitor   # View dashboard"
    echo "  ./enhanced_manage.sh populate  # Full database population"
    echo ""
    exit 1
    ;;
esac

exit 0
