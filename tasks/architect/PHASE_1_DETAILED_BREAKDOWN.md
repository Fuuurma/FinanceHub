# 📋 Phase 1 Detailed Task Breakdown

**Date:** February 1, 2026
**Created By:** GAUDÍ (Architect)
**Status:** ✅ Ready for Execution
**Phase Duration:** 4-6 weeks (quality-driven, not deadline-driven)

---

## 🎯 Phase 1 Overview

**Strategic Priority:** Transform FinanceHub from analytics platform → full trading platform

**Core Features (Priority Order):**
1. **C-036: Paper Trading System** (16-20h) - Build first, users first
2. **C-037: Social Sentiment Analysis** (18-24h) - Engagement driver
3. **C-030: Broker API Integration** (14-18h) - Live trading (most complex)

**Total Estimated Effort:** 48-62 hours across 3 features

---

## 📊 FEATURE 1: C-036 Paper Trading System (16-20h)

**Strategic Why:** Build user base first, reduce barrier to entry, enable strategy testing without risk

**Team Assignment:**
- **Lead:** Turing (Frontend Coder) - UI components, real-time updates
- **Support:** Linus (Backend Coder) - API endpoints, virtual portfolio logic
- **QA:** GRACE - Test strategies, edge cases, performance
- **Security:** Charo - Audit for exploits, virtual money security
- **Design:** MIES - Paper trading UI/UX
- **Accessibility:** HADI - WCAG compliance for trading interface

### Backend Tasks (Linus) - 8-10h

#### 1.1 Virtual Portfolio Model (2h)
**File:** `apps/backend/src/trading/models/paper_portfolio.py`
```python
class PaperTradingPortfolio(models.Model):
    user = OneToOneField(User)
    virtual_cash = DecimalField(max_digits=12, decimal_places=2)
    initial_cash = DecimalField(max_digits=12, decimal_places=2)
    portfolio_value = DecimalField(max_digits=12, decimal_places=2)
    total_return = PercentField()
    created_at = DateTimeField(auto_now_add=True)
    is_active = BooleanField(default=True)
```

**Tasks:**
- [ ] Create model with virtual cash tracking
- [ ] Implement portfolio value calculation
- [ ] Add total return tracking
- [ ] Create database migration

#### 1.2 Virtual Order Model (2h)
**File:** `apps/backend/src/trading/models/paper_order.py`
```python
class PaperTradingOrder(models.Model):
    ORDER_TYPES = [('market', 'Market'), ('limit', 'Limit'), ('stop', 'Stop')]
    SIDES = [('buy', 'Buy'), ('sell', 'Sell')]
    
    portfolio = ForeignKey(PaperTradingPortfolio)
    asset = ForeignKey(Asset)
    order_type = CharField(choices=ORDER_TYPES)
    side = CharField(choices=SIDES)
    quantity = DecimalField(max_digits=10, decimal_places=4)
    price = DecimalField(max_digits=12, decimal_places=2)  # Limit price
    filled_price = DecimalField(null=True)
    filled_at = DateTimeField(null=True)
    status = CharField()  # pending, filled, cancelled, rejected
    created_at = DateTimeField(auto_now_add=True)
```

**Tasks:**
- [ ] Create order model with paper trading fields
- [ ] Implement order status tracking
- [ ] Add order validation (sufficient funds, valid quantity)
- [ ] Create database migration

#### 1.3 Paper Trading Engine (3h)
**File:** `apps/backend/src/trading/services/paper_trading_engine.py`
```python
class PaperTradingEngine:
    def execute_market_order(self, portfolio, asset, side, quantity):
        """Execute market order instantly at current price"""
        # 1. Get current price from data provider
        # 2. Validate user has sufficient cash/position
        # 3. Create order record
        # 4. Update portfolio cash
        # 5. Create position or update existing
        # 6. Calculate portfolio value
        # 7. Return order confirmation
    
    def execute_limit_order(self, portfolio, asset, side, quantity, price):
        """Create limit order to be filled when price matches"""
        # 1. Create pending order
        # 2. Add to limit order queue
        # 3. Background task to monitor price
        # 4. Fill when price condition met
    
    def cancel_order(self, order_id):
        """Cancel pending order"""
        # 1. Validate order is pending
        # 2. Update status to cancelled
        # 3. Release reserved funds
```

**Tasks:**
- [ ] Implement market order execution
- [ ] Implement limit order execution
- [ ] Add order cancellation logic
- [ ] Implement portfolio value calculation
- [ ] Add position tracking (long/short)
- [ ] Create background task for limit order monitoring

#### 1.4 API Endpoints (2h)
**File:** `apps/backend/src/trading/api/paper_trading.py`
```python
# GET /api/paper-trading/portfolio/
# POST /api/paper-trading/orders/
# GET /api/paper-trading/orders/
# DELETE /api/paper-trading/orders/{id}/
# POST /api/paper-trading/reset/  # Reset portfolio
# GET /api/paper-trading/performance/
```

**Tasks:**
- [ ] Create portfolio API endpoint
- [ ] Create order creation endpoint
- [ ] Create order listing endpoint
- [ ] Create order cancellation endpoint
- [ ] Create portfolio reset endpoint
- [ ] Create performance metrics endpoint
- [ ] Add permission classes (user can only access their own portfolio)

#### 1.5 WebSocket Integration (1h)
**File:** `apps/backend/src/trading/consumers/paper_trading.py`
```python
class PaperTradingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Subscribe to user's portfolio updates"""
    
    async def portfolio_update(self, event):
        """Broadcast portfolio value changes"""
    
    async def order_update(self, event):
        """Broadcast order status updates"""
```

**Tasks:**
- [ ] Create WebSocket consumer for portfolio updates
- [ ] Broadcast portfolio value changes (every 30s or on trade)
- [ ] Broadcast order status updates
- [ ] Add authentication

### Frontend Tasks (Turing) - 6-8h

#### 1.6 Paper Trading Page (2h)
**File:** `apps/frontend/src/app/(dashboard)/paper-trading/page.tsx`
```tsx
// Layout: Portfolio summary + Order form + Position list + Performance chart
export default function PaperTradingPage() {
  return (
    <div className="grid grid-cols-12 gap-6">
      <PortfolioSummary className="col-span-4" />
      <OrderForm className="col-span-4" />
      <PerformanceChart className="col-span-4" />
      <PositionList className="col-span-12" />
    </div>
  )
}
```

**Tasks:**
- [ ] Create page layout
- [ ] Add navigation to dashboard
- [ ] Integrate with API endpoints

#### 1.7 Portfolio Summary Component (1.5h)
**File:** `apps/frontend/src/components/trading/PortfolioSummary.tsx`
```tsx
// Display: Virtual cash, portfolio value, total return, day change
export function PortfolioSummary() {
  const { portfolio } = usePaperTrading()
  
  return (
    <Card>
      <CardHeader>Portfolio Value</CardHeader>
      <CardContent>
        <Metric label="Cash" value={portfolio.virtual_cash} />
        <Metric label="Value" value={portfolio.portfolio_value} />
        <Metric label="Return" value={portfolio.total_return} format="percent" />
      </CardContent>
    </Card>
  )
}
```

**Tasks:**
- [ ] Create component
- [ ] Display portfolio metrics
- [ ] Add real-time updates via WebSocket
- [ ] Add loading states

#### 1.8 Order Form Component (2h)
**File:** `apps/frontend/src/components/trading/OrderForm.tsx`
```tsx
// Form: Symbol, Side (Buy/Sell), Order Type (Market/Limit), Quantity, Price
export function OrderForm() {
  const [order, setOrder] = useState({ symbol: '', side: 'buy', type: 'market', quantity: 0, price: 0 })
  const { executeOrder } = usePaperTrading()
  
  return (
    <Card>
      <CardHeader>Place Order</CardHeader>
      <CardContent>
        <SymbolSearch />
        <SideToggle />
        <OrderTypeSelect />
        <QuantityInput />
        {order.type === 'limit' && <PriceInput />}
        <Button onClick={() => executeOrder(order)}>Execute Trade</Button>
      </CardContent>
    </Card>
  )
}
```

**Tasks:**
- [ ] Create order form component
- [ ] Add symbol search (use existing universal search)
- [ ] Add buy/sell toggle
- [ ] Add order type selector (market/limit)
- [ ] Add quantity input with validation
- [ ] Add price input (show only for limit orders)
- [ ] Add form validation (sufficient funds, valid quantity)
- [ ] Add order confirmation modal

#### 1.9 Position List Component (1.5h)
**File:** `apps/frontend/src/components/trading/PositionList.tsx`
```tsx
// Table: Symbol, Quantity, Avg Price, Current Price, P/L, Market Value
export function PositionList() {
  const { positions } = usePaperTrading()
  
  return (
    <Card>
      <CardHeader>Positions</CardHeader>
      <Table>
        <TableHeader>
          <TableRow>Symbol, Quantity, Avg Price, Current Price, P/L, Market Value, Actions</TableRow>
        </TableHeader>
        <TableBody>
          {positions.map(p => (
            <TableRow key={p.id}>
              <TableCell>{p.symbol}</TableCell>
              <TableCell>{p.quantity}</TableCell>
              <TableCell>{p.avg_price}</TableCell>
              <TableCell>{p.current_price}</TableCell>
              <TableCell className={p.pl >= 0 ? 'text-green-500' : 'text-red-500'}>
                {p.pl} ({p.pl_percent}%)
              </TableCell>
              <TableCell>{p.market_value}</TableCell>
              <TableCell><Button onClick={() => closePosition(p.id)}>Close</Button></TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Card>
  )
}
```

**Tasks:**
- [ ] Create position list table
- [ ] Display position details
- [ ] Calculate P/L for each position
- [ ] Add close position button
- [ ] Add real-time price updates

#### 1.10 Performance Chart Component (1h)
**File:** `apps/frontend/src/components/trading/PerformanceChart.tsx`
```tsx
// Line chart: Portfolio value over time
export function PerformanceChart() {
  const { performanceHistory } = usePaperTrading()
  
  return (
    <Card>
      <CardHeader>Performance</CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={performanceHistory}>
            <XAxis dataKey="timestamp" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="portfolio_value" stroke="#8884d8" />
            <Line type="monotone" dataKey="benchmark" stroke="#82ca9d" />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
```

**Tasks:**
- [ ] Create performance chart component
- [ ] Fetch historical performance data
- [ ] Display portfolio value over time
- [ ] Add benchmark comparison (S&P 500)

### Testing Tasks (GRACE) - 2h

#### 1.11 Test Cases

**Paper Trading Test Scenarios:**
- [ ] Create paper trading portfolio with initial cash
- [ ] Execute market buy order (sufficient funds)
- [ ] Execute market buy order (insufficient funds) → should fail
- [ ] Execute market sell order (sufficient position)
- [ ] Execute market sell order (insufficient position) → should fail
- [ ] Create limit order
- [ ] Fill limit order when price matches
- [ ] Cancel pending limit order
- [ ] Close position (sell all shares)
- [ ] Reset portfolio
- [ ] Calculate portfolio value correctly
- [ ] Calculate P/L correctly
- [ ] WebSocket updates work correctly
- [ ] Concurrent orders (race conditions)
- [ ] Performance: 1000+ concurrent users

---

## 📊 FEATURE 2: C-037 Social Sentiment Analysis (18-24h)

**Strategic Why:** Social features drive engagement, competitive differentiator, modern feature

**Team Assignment:**
- **Lead:** Guido (Backend Coder) - API integrations, NLP processing
- **Support:** Turing (Frontend Coder) - Sentiment visualization, social feed
- **QA:** GRACE - Validate sentiment accuracy
- **Security:** Charo - Social data privacy, rate limiting
- **Design:** MIES - Social feed UI/UX
- **Accessibility:** HADI - WCAG compliance for social features

### Backend Tasks (Guido) - 10-14h

#### 2.1 Sentiment Data Model (2h)
**File:** `apps/backend/src/social/models/sentiment.py`
```python
class SentimentData(models.Model):
    asset = ForeignKey(Asset)
    source = CharField()  # twitter, reddit, news
    sentiment_score = DecimalField(max_digits=5, decimal_places=4)  # -1 to 1
    sentiment_label = CharField()  # bullish, bearish, neutral
    mention_count = IntegerField()
    volume_change = PercentField()  # vs previous period
    timestamp = DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['asset', '-timestamp']),
            models.Index(fields=['source', '-timestamp']),
        ]
```

**Tasks:**
- [ ] Create sentiment data model
- [ ] Add indexes for fast queries
- [ ] Create database migration

#### 2.2 Twitter Sentiment Integration (3h)
**File:** `apps/backend/src/social/services/twitter_sentiment.py`
```python
class TwitterSentimentAnalyzer:
    def __init__(self):
        self.api_key = settings.TWITTER_API_KEY
        self.client = TwitterClient(self.api_key)
    
    def fetch_tweets(self, symbol, count=100):
        """Fetch recent tweets mentioning symbol"""
        # Use Twitter API v2
        # Filter by cashtags (e.g., $AAPL)
        # Return tweet text, author, metrics
    
    def analyze_sentiment(self, tweets):
        """Analyze sentiment using NLP"""
        # Use FinBERT or VADER for financial sentiment
        # Calculate sentiment score (-1 to 1)
        # Classify as bullish/bearish/neutral
        # Aggregate scores across tweets
```

**Tasks:**
- [ ] Set up Twitter API integration
- [ ] Implement tweet fetching by cashtag
- [ ] Integrate FinBERT/VADER for sentiment analysis
- [ ] Calculate aggregate sentiment scores
- [ ] Handle rate limiting (Twitter API limits)

#### 2.3 Reddit Sentiment Integration (3h)
**File:** `apps/backend/src/social/services/reddit_sentiment.py`
```python
class RedditSentimentAnalyzer:
    def __init__(self):
        self.client = RedditClient(
            client_id=settings.REDDIT_CLIENT_ID,
            client_secret=settings.REDDIT_CLIENT_SECRET
        )
    
    def fetch_posts(self, symbol, subreddit='wallstreetbets'):
        """Fetch recent posts mentioning symbol"""
        # Use Reddit API
        # Search by ticker symbol
        # Return post text, comments, upvotes
    
    def analyze_sentiment(self, posts):
        """Analyze sentiment of posts and comments"""
        # Use FinBERT or VADER
        # Weight by upvotes
        # Calculate aggregate sentiment
```

**Tasks:**
- [ ] Set up Reddit API integration
- [ ] Implement post fetching by ticker
- [ ] Implement comment fetching
- [ ] Integrate sentiment analysis
- [ ] Weight sentiment by upvotes

#### 2.4 Sentiment Aggregation Service (2h)
**File:** `apps/backend/src/social/services/sentiment_aggregator.py`
```python
class SentimentAggregator:
    def aggregate_sentiment(self, asset, hours=24):
        """Aggregate sentiment from all sources"""
        # 1. Fetch Twitter sentiment
        # 2. Fetch Reddit sentiment
        # 3. Fetch news sentiment (if available)
        # 4. Weight by source reliability
        # 5. Calculate weighted average
        # 6. Return aggregated sentiment
    
    def calculate_trend(self, asset, hours=24):
        """Calculate sentiment trend (improving/worsening)"""
        # Compare current sentiment to previous period
        # Return trend direction and magnitude
```

**Tasks:**
- [ ] Implement sentiment aggregation across sources
- [ ] Add source weighting (Twitter: 40%, Reddit: 40%, News: 20%)
- [ ] Calculate sentiment trend
- [ ] Cache results (5-minute TTL)

#### 2.5 API Endpoints (2h)
**File:** `apps/backend/src/social/api/sentiment.py`
```python
# GET /api/sentiment/{symbol}/
# GET /api/sentiment/{symbol}/history/
# GET /api/sentiment/trending/  # Most mentioned assets
# GET /api/sentiment/feed/  # Social feed (tweets, posts)
```

**Tasks:**
- [ ] Create current sentiment endpoint
- [ ] Create historical sentiment endpoint
- [ ] Create trending assets endpoint
- [ ] Create social feed endpoint
- [ ] Add caching

#### 2.6 Background Tasks (2h)
**File:** `apps/backend/src/social/tasks/sentiment_tasks.py`
```python
@celery_app.task
def update_sentiment_data():
    """Update sentiment data for all tracked assets"""
    # Run every 5 minutes
    # Fetch latest tweets/posts
    # Analyze sentiment
    # Store in database

@celery_app.task
def calculate_trending_assets():
    """Calculate most mentioned assets"""
    # Run every 15 minutes
    # Aggregate mention counts
    # Calculate sentiment
    # Cache results
```

**Tasks:**
- [ ] Create Celery task for sentiment updates
- [ ] Create task for trending assets calculation
- [ ] Set up periodic tasks (Celery Beat)
- [ ] Add error handling and retry logic

### Frontend Tasks (Turing) - 6-8h

#### 2.7 Sentiment Overview Page (1.5h)
**File:** `apps/frontend/src/app/(dashboard)/sentiment/page.tsx`
```tsx
// Layout: Sentiment gauge, sentiment chart, trending assets, social feed
export default function SentimentPage() {
  return (
    <div className="grid grid-cols-12 gap-6">
      <SentimentGauge className="col-span-4" symbol={symbol} />
      <SentimentChart className="col-span-8" symbol={symbol} />
      <TrendingAssets className="col-span-6" />
      <SocialFeed className="col-span-6" symbol={symbol} />
    </div>
  )
}
```

**Tasks:**
- [ ] Create page layout
- [ ] Add symbol selector
- [ ] Integrate with API endpoints

#### 2.8 Sentiment Gauge Component (1.5h)
**File:** `apps/frontend/src/components/social/SentimentGauge.tsx`
```tsx
// Display: Gauge showing sentiment score (-1 to 1), label (bullish/bearish/neutral)
export function SentimentGauge({ symbol }: { symbol: string }) {
  const { sentiment } = useSentiment(symbol)
  
  return (
    <Card>
      <CardHeader>Sentiment for {symbol}</CardHeader>
      <CardContent>
        <GaugeChart value={sentiment.score} min={-1} max={1} />
        <Badge color={sentiment.score > 0.3 ? 'green' : sentiment.score < -0.3 ? 'red' : 'gray'}>
          {sentiment.label}
        </Badge>
        <Metric label="Mentions" value={sentiment.mention_count} />
        <Metric label="Volume Change" value={sentiment.volume_change} format="percent" />
      </CardContent>
    </Card>
  )
}
```

**Tasks:**
- [ ] Create gauge component
- [ ] Display sentiment score
- [ ] Display sentiment label
- [ ] Add color coding (green=bullish, red=bearish, gray=neutral)

#### 2.9 Sentiment Chart Component (2h)
**File:** `apps/frontend/src/components/social/SentimentChart.tsx`
```tsx
// Line chart: Sentiment over time (last 24h, 7d, 30d)
export function SentimentChart({ symbol }: { symbol: string }) {
  const { sentimentHistory } = useSentiment(symbol)
  
  return (
    <Card>
      <CardHeader>Sentiment History</CardHeader>
      <CardContent>
        <Tabs defaultValue="24h">
          <TabsList>
            <TabsTrigger value="24h">24 Hours</TabsTrigger>
            <TabsTrigger value="7d">7 Days</TabsTrigger>
            <TabsTrigger value="30d">30 Days</TabsTrigger>
          </TabsList>
          <TabsContent value="24h">
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={sentimentHistory['24h']}>
                <XAxis dataKey="timestamp" />
                <YAxis domain={[-1, 1]} />
                <Tooltip />
                <Area type="monotone" dataKey="sentiment" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
              </AreaChart>
            </ResponsiveContainer>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}
```

**Tasks:**
- [ ] Create sentiment chart component
- [ ] Add time period selector (24h, 7d, 30d)
- [ ] Display sentiment trend
- [ ] Add zero line reference

#### 2.10 Trending Assets Component (1h)
**File:** `apps/frontend/src/components/social/TrendingAssets.tsx`
```tsx
// List: Most mentioned assets with sentiment
export function TrendingAssets() {
  const { trendingAssets } = useSocialSentiment()
  
  return (
    <Card>
      <CardHeader>Trending Assets</CardHeader>
      <CardContent>
        <ul>
          {trendingAssets.map(asset => (
            <li key={asset.symbol}>
              <Link href={`/sentiment/${asset.symbol}`}>
                {asset.symbol} ({asset.mention_count} mentions)
                <Badge color={asset.sentiment > 0 ? 'green' : 'red'}>
                  {asset.sentiment > 0 ? 'Bullish' : 'Bearish'}
                </Badge>
              </Link>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  )
}
```

**Tasks:**
- [ ] Create trending assets list
- [ ] Display mention counts
- [ ] Display sentiment label
- [ ] Add click to navigate to asset sentiment page

#### 2.11 Social Feed Component (2h)
**File:** `apps/frontend/src/components/social/SocialFeed.tsx`
```tsx
// Feed: Recent tweets and Reddit posts about asset
export function SocialFeed({ symbol }: { symbol: string }) {
  const { feed } = useSentiment(symbol)
  
  return (
    <Card>
      <CardHeader>Social Feed</CardHeader>
      <CardContent>
        <Tabs defaultValue="all">
          <TabsList>
            <TabsTrigger value="all">All</TabsTrigger>
            <TabsTrigger value="twitter">Twitter</TabsTrigger>
            <TabsTrigger value="reddit">Reddit</TabsTrigger>
          </TabsList>
          <TabsContent value="all">
            {feed.map(item => (
              <FeedItem
                key={item.id}
                source={item.source}
                author={item.author}
                content={item.content}
                timestamp={item.timestamp}
                sentiment={item.sentiment}
              />
            ))}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}
```

**Tasks:**
- [ ] Create social feed component
- [ ] Display tweets and Reddit posts
- [ ] Add source filtering (Twitter/Reddit/All)
- [ ] Display sentiment indicator for each post
- [ ] Add link to original post

### Testing Tasks (GRACE) - 2h

#### 2.12 Test Cases

**Sentiment Analysis Test Scenarios:**
- [ ] Fetch and analyze Twitter sentiment for stock
- [ ] Fetch and analyze Reddit sentiment for stock
- [ ] Aggregate sentiment from multiple sources
- [ ] Calculate sentiment trend (improving/worsening)
- [ ] Identify trending assets
- [ ] Display social feed correctly
- [ ] Handle rate limiting gracefully
- [ ] Validate sentiment accuracy (compare to manual analysis)
- [ ] Performance: Sentiment queries < 500ms

---

## 📊 FEATURE 3: C-030 Broker API Integration (14-18h)

**Strategic Why:** Transform into full trading platform, most complex (user acknowledged difficulty), do LAST

**Team Assignment:**
- **Lead:** Linus (Backend Coder) - API integrations, authentication, order execution
- **Support:** Turing (Frontend Coder) - Trading UI, order confirmation
- **QA:** GRACE - Test broker integration with test accounts
- **Security:** Charo - Broker API security, live trading hardening
- **Design:** MIES - Trading UI/UX
- **Accessibility:** HADI - WCAG compliance for trading interface

### Backend Tasks (Linus) - 8-10h

#### 3.1 Broker Connection Model (1.5h)
**File:** `apps/backend/src/broker/models/broker_connection.py`
```python
class BrokerConnection(models.Model):
    BROKER_CHOICES = [
        ('alpaca', 'Alpaca'),
        ('interactive_brokers', 'Interactive Brokers'),
        ('td_ameritrade', 'TD Ameritrade'),
    ]
    
    user = ForeignKey(User)
    broker = CharField(choices=BROKER_CHOICES)
    api_key = EncryptedCharField()  # Encrypted at rest
    api_secret = EncryptedCharField()
    account_id = CharField()
    is_active = BooleanField(default=True)
    is_test_account = BooleanField(default=True)  # Use test accounts first
    connected_at = DateTimeField(auto_now_add=True)
    last_sync = DateTimeField()
```

**Tasks:**
- [ ] Create broker connection model
- [ ] Implement encrypted fields for API keys
- [ ] Add test account flag
- [ ] Create database migration

#### 3.2 Alpaca API Integration (2.5h)
**File:** `apps/backend/src/broker/services/alpaca_client.py`
```python
class AlpacaBrokerClient:
    def __init__(self, api_key, api_secret, is_test=True):
        self.base_url = 'https://paper-api.alpaca.markets' if is_test else 'https://api.alpaca.markets'
        self.client = AlpacaClient(api_key, api_secret, self.base_url)
    
    def get_account(self):
        """Get account information"""
        return self.client.get_account()
    
    def place_order(self, symbol, side, quantity, order_type, price=None):
        """Place order"""
        return self.client.submit_order(
            symbol=symbol,
            side=side,
            qty=quantity,
            type=order_type,
            limit_price=price
        )
    
    def get_positions(self):
        """Get open positions"""
        return self.client.list_positions()
    
    def cancel_order(self, order_id):
        """Cancel order"""
        return self.client.cancel_order(order_id)
```

**Tasks:**
- [ ] Set up Alpaca API client
- [ ] Implement account retrieval
- [ ] Implement order placement
- [ ] Implement position retrieval
- [ ] Implement order cancellation
- [ ] Handle test vs live accounts

#### 3.3 Interactive Brokers Integration (2.5h)
**File:** `apps/backend/src/broker/services/ib_client.py`
```python
class IBrokerClient:
    def __init__(self, api_key, api_secret, is_test=True):
        # IB API setup
        self.client = IBClient(api_key, api_secret)
    
    def get_account(self):
        """Get account information"""
        return self.client.get_account()
    
    def place_order(self, symbol, side, quantity, order_type, price=None):
        """Place order"""
        return self.client.place_order(...)
    
    # Similar methods to Alpaca
```

**Tasks:**
- [ ] Set up Interactive Brokers API client
- [ ] Implement same methods as Alpaca
- [ ] Handle IB-specific quirks

#### 3.4 Unified Broker Service (2h)
**File:** `apps/backend/src/broker/services/broker_factory.py`
```python
class BrokerFactory:
    @staticmethod
    def create_client(broker_type, api_key, api_secret, is_test=True):
        """Create broker client based on type"""
        if broker_type == 'alpaca':
            return AlpacaBrokerClient(api_key, api_secret, is_test)
        elif broker_type == 'interactive_brokers':
            return IBrokerClient(api_key, api_secret, is_test)
        # Add more brokers as needed

class BrokerService:
    def __init__(self, user_broker_connection):
        self.client = BrokerFactory.create_client(
            user_broker_connection.broker,
            user_broker_connection.api_key,
            user_broker_connection.api_secret,
            user_broker_connection.is_test_account
        )
    
    def execute_order(self, symbol, side, quantity, order_type, price=None):
        """Execute order through broker"""
        return self.client.place_order(symbol, side, quantity, order_type, price)
    
    def get_positions(self):
        """Get positions from broker"""
        return self.client.get_positions()
    
    # Wrapper methods for all broker operations
```

**Tasks:**
- [ ] Create broker factory
- [ ] Implement unified broker service
- [ ] Handle broker-specific differences
- [ ] Add error handling and retry logic

#### 3.5 API Endpoints (2h)
**File:** `apps/backend/src/broker/api/trading.py`
```python
# POST /api/broker/connect/  # Connect broker account
# GET /api/broker/accounts/  # List connected accounts
# DELETE /api/broker/accounts/{id}/  # Disconnect account
# GET /api/broker/positions/  # Get positions from broker
# POST /api/broker/orders/  # Place order
# GET /api/broker/orders/  # List orders
# DELETE /api/broker/orders/{id}/  # Cancel order
# GET /api/broker/account/{id}/  # Get account info
```

**Tasks:**
- [ ] Create broker connection endpoint
- [ ] Create order placement endpoint
- [ ] Create position listing endpoint
- [ ] Create order cancellation endpoint
- [ ] Add permission classes (user can only access their own accounts)
- [ ] Add validation (test account required before live)

### Frontend Tasks (Turing) - 4-6h

#### 3.6 Broker Connection Page (1.5h)
**File:** `apps/frontend/src/app/(dashboard)/broker-connection/page.tsx`
```tsx
// Form: Broker selection, API key, API secret, test mode toggle
export default function BrokerConnectionPage() {
  const [connection, setConnection] = useState({ broker: 'alpaca', api_key: '', api_secret: '', is_test: true })
  const { connectBroker } = useBroker()
  
  return (
    <Card>
      <CardHeader>Connect Broker Account</CardHeader>
      <CardContent>
        <BrokerSelector />
        <APIKeyInput />
        <APISecretInput />
        <TestModeToggle />
        <Button onClick={() => connectBroker(connection)}>Connect</Button>
      </CardContent>
    </Card>
  )
}
```

**Tasks:**
- [ ] Create connection page
- [ ] Add broker selector (Alpaca, IB, TD Ameritrade)
- [ ] Add API key/secret inputs
- [ ] Add test mode toggle (default: checked)
- [ ] Add connection validation

#### 3.7 Trading Interface (2.5h)
**File:** `apps/frontend/src/components/trading/LiveTradingInterface.tsx`
```tsx
// Similar to paper trading, but connects to broker API
export function LiveTradingInterface() {
  const { brokerAccounts, executeOrder } = useBroker()
  
  return (
    <div className="grid grid-cols-12 gap-6">
      <BrokerAccountSelector className="col-span-4" />
      <LiveOrderForm className="col-span-4" />
      <BrokerPositions className="col-span-12" />
      <BrokerOrders className="col-span-12" />
    </div>
  )
}
```

**Tasks:**
- [ ] Create live trading interface
- [ ] Reuse paper trading components (with broker API integration)
- [ ] Add broker account selector (for multiple accounts)
- [ ] Add order confirmation modal (critical for live trading)

### Testing Tasks (GRACE) - 2h

#### 3.8 Test Cases

**Broker Integration Test Scenarios:**
- [ ] Connect Alpaca test account
- [ ] Connect Interactive Brokers test account
- [ ] Validate API credentials
- [ ] Place test order (buy)
- [ ] Place test order (sell)
- [ ] Cancel pending order
- [ ] Get positions from broker
- [ ] Get account information
- [ ] Handle API errors gracefully
- [ ] Test with multiple broker accounts
- [ ] Security: API keys encrypted at rest
- [ ] Security: User can only access their own accounts

---

## 📋 COORDINATION & DEPENDENCIES

### Feature Dependencies

```
C-036 (Paper Trading) - NO DEPENDENCIES (can start immediately)
    ↓
C-037 (Social Sentiment) - NO DEPENDENCIES (can start immediately)
    ↓
C-030 (Broker Integration) - DEPENDS ON NOTHING, but should be LAST
```

**Parallel Execution:**
- C-036 and C-037 can be developed in parallel (different coders)
- C-030 should start AFTER C-036 is complete (reuse code)

### Resource Allocation

| Week | Turing (Frontend) | Guido (Backend) | Linus (Backend) | GRACE (QA) | Charo (Security) |
|------|------------------|-----------------|-----------------|------------|------------------|
| 1 | C-036 Paper Trading UI | C-037 Twitter/Reddit APIs | C-036 Paper Trading Engine | Test planning | C-036 security audit |
| 2 | C-036 complete | C-037 sentiment aggregation | Support C-036, start C-030 | C-036 testing | C-037 data privacy review |
| 3 | C-037 Social Feed UI | C-037 complete | C-030 broker integration | C-037 testing | C-030 security hardening |
| 4 | C-030 trading UI | Support C-030 | C-030 complete | C-030 testing | C-030 live trading audit |

### Cross-Team Coordination

**MIES (UI/UX Designer):**
- Week 1: Design paper trading interface
- Week 2: Design social feed UI
- Week 3: Design live trading interface

**HADI (Accessibility):**
- Week 1: Audit paper trading UI
- Week 2: Audit social feed UI
- Week 3: Audit live trading UI

**Karen (DevOps):**
- Week 1: Set up staging environment for testing
- Week 2: Monitor performance of social sentiment APIs
- Week 3: Prepare for live trading deployment

---

## ✅ ACCEPTANCE CRITERIA

### C-036: Paper Trading System
- [ ] Users can create paper trading portfolio with $100,000 virtual cash
- [ ] Users can execute market orders (buy/sell) instantly
- [ ] Users can create limit orders
- [ ] Portfolio value updates in real-time
- [ ] Performance chart tracks portfolio value over time
- [ ] WebSocket updates work correctly
- [ ] Supports 1000+ concurrent users
- [ ] Zero security vulnerabilities
- [ ] WCAG 2.1 Level AA compliant

### C-037: Social Sentiment Analysis
- [ ] Fetches Twitter sentiment for stocks
- [ ] Fetches Reddit sentiment for stocks
- [ ] Aggregates sentiment from multiple sources
- [ ] Displays sentiment gauge (-1 to 1)
- [ ] Displays sentiment history chart (24h, 7d, 30d)
- [ ] Shows trending assets by mention count
- [ ] Displays social feed (tweets, Reddit posts)
- [ ] Sentiment accuracy > 75%
- [ ] Updates every 5 minutes
- [ ] WCAG 2.1 Level AA compliant

### C-030: Broker API Integration
- [ ] Users can connect Alpaca test account
- [ ] Users can connect Interactive Brokers test account
- [ ] API keys encrypted at rest
- [ ] Users can place live orders through broker
- [ ] Users can view broker positions
- [ ] Users can cancel pending orders
- [ ] Order execution < 1 second
- [ ] Zero security vulnerabilities
- [ ] Requires test account before live trading
- [ ] WCAG 2.1 Level AA compliant

---

## 📊 SUCCESS METRICS

### Phase 1 Success Criteria
- [ ] All 3 features complete and deployed
- [ ] User retention increases by 30%
- [ ] Paper trading handles 1000+ concurrent users
- [ ] Social sentiment accuracy > 75%
- [ ] Broker integration executes orders in < 1 second
- [ ] Zero security vulnerabilities in live trading
- [ ] All features WCAG 2.1 Level AA compliant

---

## 🚀 NEXT STEPS

### Immediate (This Week)
1. **Assign C-036 to Turing and Linus** - Start paper trading development
2. **Assign C-037 to Guido** - Start social sentiment API integration
3. **GRACE creates test plans** - Prepare for testing
4. **Charo reviews security** - Audit paper trading architecture
5. **MIES designs UI** - Create paper trading mockups

### Next Week
1. **Complete C-036 backend** - Paper trading engine ready
2. **Begin C-036 frontend** - Paper trading UI
3. **Complete C-037 API integration** - Twitter/Reddit sentiment working
4. **Prepare for C-030** - Review broker APIs

---

**Status:** ✅ Phase 1 Detailed Breakdown Complete
**Ready for:** Task Assignment & Execution
**Timeline:** Quality-driven, not deadline-driven (4-6 weeks)

---

🎨 *GAUDÍ - Architect*

📋 *Execution: C-036 → C-037 → C-030*

*"Quality over speed. God is in the details." - Mies van der Rohe*
