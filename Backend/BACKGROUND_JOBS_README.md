# FinanceHub Background Jobs System

## 🚀 Overview

Automated background data collection system that populates your FinanceHub database using free API tiers without requiring API keys.

## 📊 Data Sources

### Free Tier Providers (No API Key Required)

1. **Yahoo Finance (yfinance)** 
   - ✅ Unlimited free calls
   - ✅ Real-time stock prices
   - ✅ Historical data
   - ✅ No rate limits

2. **CoinGecko**
   - ✅ 30 calls/minute (250K/month free tier)
   - ✅ Crypto prices
   - ✅ Market data
   - ✅ Trading volume
   - ✅ Market cap rankings

3. **Alpha Vantage**
   - ✅ 25 calls/day free tier
   - ✅ Stock fundamentals
   - ✅ Technical indicators
   - ✅ Forex data

## 🎯 Assets Being Monitored

### Stocks (42 Assets)
Top S&P 500 companies by market cap:
- **Tech**: AAPL, MSFT, GOOGL, AMZN, TSLA, META, NVDA, ADBE, CRM, INTC, AMD, QCOM, AVGO, CSCO, IBM, ORCL
- **Finance**: JPM, BAC, V, MA
- **Healthcare**: JNJ, UNH, PFE
- **Consumer**: WMT, PG, KO, PEP, COST, DIS, NFLX
- **Industrial**: CAT, DE, GE, HON, MMM, BA, NOC, RTX, GD, LMT
- **Energy**: XOM, CVX, COP, HES, SLB
- **Other**: TXN, NOW, INTU, ACN

### Cryptocurrencies (23 Assets)
Top cryptos by market cap:
- **Major**: BTC, ETH, BNB, XRP, ADA, DOGE, SOL, DOT
- **Layer 1**: MATIC, LTC, AVAX, ATOM, XLM, ETC, XMR, ALGO
- **DeFi**: LINK, UNI, AAVE
- **Storage**: FIL, VET
- **Other**: NEAR, XTZ

## ⏰ Task Schedule

### High Frequency (Every 1-5 minutes)
- **Crypto prices** - Every 2 minutes (30 cryptos)
- **Stock prices** - Every 5 minutes (10 stocks)
- **Health checks** - Every 1 minute

### Medium Frequency (Every 10-30 minutes)
- **Data validation** - Every 10 minutes
- **Trending cryptos** - Every 15 minutes
- **Top cryptos ranking** - Every 30 minutes
- **Market aggregation** - Every 30 minutes

### Low Frequency (Daily)
- **Historical data updates** - Daily
- **Old data cleanup** - Daily at midnight (keeps 365 days)

## 🛠️ Management Commands

### Start Background Jobs
```bash
cd /Users/sergi/Desktop/Projects/FinanceHub/Backend
./venv/bin/python start_background_jobs.py
```

### Check Redis Status
```bash
redis-cli ping
# Should return: PONG
```

### View Redis Queues
```bash
redis-cli
> KEYS dramatiq:*
> LLEN dramatiq:default
```

### Stop Background Jobs
Press `Ctrl+C` in the terminal running the background jobs

## 📈 Monitoring

### Check Logs
```bash
tail -f Backend/src/logs/django.log
```

### View Active Tasks
In Python shell:
```python
from tasks.scheduler_tasks import health_check_task
result = health_check_task.send()
print(result)
```

### Monitor Database Growth
```sql
-- Count total price records
SELECT COUNT(*) FROM assets_assetpriceshistoric;

-- Latest prices by symbol
SELECT symbol, MAX(timestamp) as latest_update
FROM assets_assetpriceshistoric
GROUP BY symbol
ORDER BY latest_update DESC;
```

## 🔧 Configuration

### Adjust Update Frequency

Edit `start_background_jobs.py`:
```python
# Change from every 2 minutes to every 5 minutes
fetch_crypto_batch.send_with_options(
    delay=1000 * 60 * 5,  # Change this value
    repeat=True
)
```

### Add More Assets

Edit `start_background_jobs.py`:
```python
POPULAR_STOCKS = [
    "AAPL", "MSFT", "GOOGL",
    # Add your symbols here
]

POPULAR_CRYPTOS = [
    "BTC", "ETH",
    # Add your symbols here
]
```

### Adjust Rate Limits

Edit `Backend/src/utils/services/call_planner.py`:
```python
# CoinGecko limits
'coingecko': {
    'max_calls': 50000,
    'window_seconds': 60,
    'calls_per_window': 30,  # Adjust this
    'reset_period_seconds': 60,
    'batch_delay_seconds': 2
}
```

## 🎨 Features

### ✅ Data Quality
- **Cross-validation**: Compares data from multiple sources
- **Anomaly detection**: Identifies price outliers
- **Health monitoring**: Checks provider availability
- **Automatic retries**: Handles failed requests

### ✅ Performance
- **Batch processing**: Fetches multiple assets efficiently
- **Rate limiting**: Respects API provider limits
- **Caching**: Reduces redundant API calls
- **Async operations**: Non-blocking data fetching

### ✅ Reliability
- **Error handling**: Graceful failure recovery
- **Logging**: Comprehensive activity tracking
- **Automatic cleanup**: Removes old data
- **Health checks**: Continuous monitoring

## 📊 Data Collection Stats

### Expected Daily Volume
- **Stock price updates**: ~2,880 updates/day (10 stocks × 288 5-min intervals)
- **Crypto price updates**: ~21,600 updates/day (30 cryptos × 720 2-min intervals)
- **Historical records**: ~65/day (assuming 1 history fetch per asset)
- **Total**: ~24,545 records/day

### Database Growth
- **Daily**: ~24,545 new records
- **Monthly**: ~736,350 new records
- **Yearly**: ~8,858,925 new records (with 365-day retention)

## 🚨 Troubleshooting

### Redis Not Running
```bash
brew services start redis
```

### Jobs Not Starting
Check if Django is configured:
```bash
cd Backend/src
./venv/bin/python manage.py check
```

### Rate Limit Errors
- Reduce frequency in task schedule
- Reduce batch sizes
- Check provider status: `get_provider_health.send()`

### Database Errors
```bash
cd Backend/src
./venv/bin/python manage.py migrate
```

### High Memory Usage
- Reduce retention period in `clean_old_data`
- Reduce number of assets monitored
- Increase cleanup frequency

## 🔒 Security

### API Keys
- System uses **FREE TIER ONLY**
- No API keys required
- No credentials needed

### Data Privacy
- All data is public market data
- No personal information collected
- Safe to run in production

## 📝 Notes

- **System runs indefinitely** until stopped
- **All tasks are scheduled** automatically
- **Redis persists queues** across restarts
- **Automatic retry** on failures
- **Graceful shutdown** with Ctrl+C

## 🎓 Best Practices

1. **Monitor Redis memory**: `redis-cli INFO memory`
2. **Check database size**: Monitor growth weekly
3. **Review logs**: Check for errors daily
4. **Update assets**: Add/remove as needed
5. **Tune frequency**: Adjust based on needs
6. **Backup database**: Regular backups recommended

## 🚀 Next Steps

1. ✅ Background jobs running
2. 📊 Monitor data collection
3. 🎯 Adjust assets/frequency as needed
4. 📈 Query database for insights
5. 🔔 Set up alerts for failures

---

**Status**: ✅ Active and Running  
**Started**: 2026-01-30 03:51:55  
**Version**: 1.0.0
