# 🎉 FinanceHub Background Jobs - Quick Start Guide

## ✅ Your Background Jobs Are NOW RUNNING!

The system is actively collecting data and populating your database with:
- **42 stocks** (S&P 500 leaders)
- **23 cryptos** (Top market cap)
- **Updates every 2-5 minutes**
- **100% free** - No API keys needed!

---

## 📊 Monitor Your Data Collection

### Option 1: Check Status (Quick)
```bash
cd Backend
./manage_jobs.sh status
```

### Option 2: Live Dashboard (Real-time)
```bash
cd Backend
./manage_jobs.sh monitor
```
Press `Ctrl+C` to exit monitoring

### Option 3: View Logs
```bash
cd Backend
./manage_jobs.sh logs
```

---

## 🛠️ Management Commands

All commands run from the `Backend` directory:

```bash
# Start jobs (already running)
./manage_jobs.sh start

# Stop jobs
./manage_jobs.sh stop

# Restart jobs
./manage_jobs.sh restart

# Check status
./manage_jobs.sh status

# Monitor dashboard
./manage_jobs.sh monitor

# View logs
./manage_jobs.sh logs

# Test with quick job
./manage_jobs.sh test
```

---

## 📈 What's Happening Right Now?

### Active Tasks
✅ **Every 2 minutes**: Fetching 30 crypto prices  
✅ **Every 5 minutes**: Fetching 10 stock prices  
✅ **Every 10 minutes**: Validating data quality  
✅ **Every 15 minutes**: Fetching trending cryptos  
✅ **Every 30 minutes**: Updating market rankings  
✅ **Daily**: Cleaning old data  

### Expected Data Volume
- **~24,545 records/day**
- **~736K records/month**
- **All stored in your database**
- **Automatically cleaned after 365 days**

---

## 💾 Access Your Data

### Check Database Growth
```sql
-- Total records collected
SELECT COUNT(*) FROM assets_assetpriceshistoric;

-- Latest prices by asset
SELECT symbol, MAX(timestamp) as latest
FROM assets_assetpriceshistoric
GROUP BY symbol
ORDER BY latest DESC;

-- Records in last hour
SELECT COUNT(*) FROM assets_assetpriceshistoric
WHERE timestamp >= NOW() - INTERVAL '1 hour';
```

### Example Queries
```python
# In Django shell
from assets.models.historic.prices import AssetPricesHistoric
from assets.models.asset import Asset

# Get latest BTC price
btc = Asset.objects.get(symbol='BTC')
latest = btc.prices.order_by('-timestamp').first()
print(f"BTC: ${latest.close}")

# Get price history
history = AssetPricesHistoric.objects.filter(
    asset__symbol='AAPL'
).order_by('-timestamp')[:100]
```

---

## 🔧 Customize Your Setup

### Change Update Frequency
Edit `Backend/start_background_jobs.py`:
```python
# Line ~180: Change crypto updates from 2 min to 5 min
fetch_crypto_batch.send_with_options(
    delay=1000 * 60 * 5,  # Change to 5 minutes
    repeat=True
)
```

### Add More Assets
Edit `Backend/start_background_jobs.py`:
```python
# Line ~72: Add more stocks
POPULAR_STOCKS = [
    "AAPL", "MSFT", "GOOGL",
    "YOUR_STOCK_1", "YOUR_STOCK_2",  # Add here
]

# Line ~84: Add more cryptos
POPULAR_CRYPTOS = [
    "BTC", "ETH", "BNB",
    "YOUR_CRYPTO_1", "YOUR_CRYPTO_2",  # Add here
]
```

### Adjust Rate Limits
Edit `Backend/src/utils/services/call_planner.py`:
```python
# Line ~100: Adjust CoinGecko limits
'coingecko': {
    'calls_per_window': 30,  # Adjust this
    'batch_delay_seconds': 2,  # And this
}
```

---

## 🚨 Troubleshooting

### Jobs Not Running?
```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG

# If not, start Redis
brew services start redis

# Restart jobs
cd Backend
./manage_jobs.sh restart
```

### High Memory Usage?
```bash
# Reduce retention period
# Edit start_background_jobs.py line ~215
clean_old_data.send_with_options(
    args=[180],  # Change from 365 to 180 days
    ...
)
```

### Rate Limit Errors?
```bash
# Check provider health
cd Backend
./venv/bin/python -c "
import os, sys, django
sys.path.insert(0, '/Users/sergi/Desktop/Projects/FinanceHub/Backend/src')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from tasks.crypto_data_tasks import get_provider_health
health = get_provider_health.send()
print(health)
"
```

---

## 📚 Documentation

- **Full Documentation**: `Backend/BACKGROUND_JOBS_README.md`
- **Configuration**: `Backend/start_background_jobs.py`
- **Tasks**: `Backend/src/tasks/`
- **Data Providers**: `Backend/src/data/data_providers/`

---

## 🎓 Key Features

✅ **Fully Automated** - Set and forget  
✅ **Rate Limited** - Respects API limits  
✅ **Error Resilient** - Auto-retry on failures  
✅ **Data Validated** - Cross-checks sources  
✅ **Production Ready** - Logging and monitoring  
✅ **100% Free** - No API costs  

---

## 🚀 Next Steps

1. ✅ Jobs are running
2. 📊 **Monitor**: `./manage_jobs.sh monitor`
3. ⏰ **Wait**: Data will accumulate over time
4. 💾 **Query**: Check your database for insights
5. 🎯 **Customize**: Adjust assets/frequency as needed

---

**📞 Need Help?**
- Check logs: `./manage_jobs.sh logs`
- Check status: `./manage_jobs.sh status`
- Read docs: `BACKGROUND_JOBS_README.md`

**Status**: ✅ RUNNING  
**Started**: 2026-01-30 03:51:55  
**Location**: Backend/start_background_jobs.py  

🎊 **Congratulations! Your FinanceHub database is now being populated automatically!**
