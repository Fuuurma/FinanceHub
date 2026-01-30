#!/bin/bash

# Background Jobs Control Script
# Start, stop, and manage FinanceHub background data collection

ACTION=$1

case "$ACTION" in
  start)
    echo "🚀 Starting FinanceHub background jobs..."
    cd /Users/sergi/Desktop/Projects/FinanceHub/Backend
    nohup ./venv/bin/python start_background_jobs.py > logs/background_jobs.log 2>&1 &
    echo $! > background_jobs.pid
    echo "✅ Background jobs started (PID: $(cat background_jobs.pid))"
    echo "📝 Logs: Backend/logs/background_jobs.log"
    ;;
    
  stop)
    echo "🛑 Stopping FinanceHub background jobs..."
    if [ -f background_jobs.pid ]; then
      pid=$(cat background_jobs.pid)
      kill $pid 2>/dev/null
      rm background_jobs.pid
      echo "✅ Background jobs stopped"
    else
      echo "⚠️  No PID file found. Jobs may not be running."
    fi
    ;;
    
  restart)
    echo "🔄 Restarting FinanceHub background jobs..."
    $0 stop
    sleep 2
    $0 start
    ;;
    
  status)
    echo "📊 FinanceHub Background Jobs Status"
    echo "===================================="
    if [ -f background_jobs.pid ]; then
      pid=$(cat background_jobs.pid)
      if ps -p $pid > /dev/null; then
        echo "✅ Status: Running"
        echo "📌 PID: $pid"
        echo "⏰ Started: $(ps -p $pid -o lstart=)"
        echo "💾 Memory: $(ps -p $pid -o rss= | awk '{printf "%.1f MB", $1/1024}')"
      else
        echo "❌ Status: Not running (stale PID file)"
        rm background_jobs.pid
      fi
    else
      echo "⏸️  Status: Not running"
    fi
    
    echo ""
    echo "📬 Queue Status:"
    redis-cli -h localhost -p 6379 LLEN dramatiq:default 2>/dev/null | xargs -I {} echo "  Default queue: {} messages"
    redis-cli -h localhost -p 6379 PING 2>/dev/null || echo "  ⚠️  Redis not responding"
    ;;
    
  monitor)
    echo "📈 Starting monitoring dashboard..."
    cd /Users/sergi/Desktop/Projects/FinanceHub/Backend
    ./venv/bin/python monitor_background_jobs.py
    ;;
    
  logs)
    echo "📝 Showing recent logs (Ctrl+C to exit)..."
    if [ -f logs/background_jobs.log ]; then
      tail -f logs/background_jobs.log
    else
      echo "⚠️  Log file not found: Backend/logs/background_jobs.log"
    fi
    ;;
  
  test)
    echo "🧪 Testing background jobs..."
    cd /Users/sergi/Desktop/Projects/FinanceHub/Backend
    ./venv/bin/python -c "
import os, sys, django
sys.path.insert(0, '/Users/sergi/Desktop/Projects/FinanceHub/Backend/src')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from tasks.crypto_data_tasks import fetch_crypto_batch
print('Testing crypto batch fetch...')
result = fetch_crypto_batch(['BTC', 'ETH'])
print(f'Result: {result}')
"
    ;;
    
  *)
    echo "FinanceHub Background Jobs Manager"
    echo "=================================="
    echo ""
    echo "Usage: ./manage_jobs.sh {start|stop|restart|status|monitor|logs|test}"
    echo ""
    echo "Commands:"
    echo "  start    - Start background jobs in background"
    echo "  stop     - Stop background jobs"
    echo "  restart  - Restart background jobs"
    echo "  status   - Show running status and statistics"
    echo "  monitor  - Start real-time monitoring dashboard"
    echo "  logs     - Show background jobs log (tail -f)"
    echo "  test     - Run a quick test job"
    echo ""
    echo "Examples:"
    echo "  ./manage_jobs.sh start     # Start jobs"
    echo "  ./manage_jobs.sh status    # Check status"
    echo "  ./manage_jobs.sh monitor   # View dashboard"
    echo ""
    exit 1
    ;;
esac

exit 0
