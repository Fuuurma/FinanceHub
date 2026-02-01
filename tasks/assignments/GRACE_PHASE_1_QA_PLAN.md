# 📋 Task Assignment: Phase 1 QA Planning (C-036, C-037, C-030)

**Date:** February 1, 2026
**From:** GAUDÍ (Architect)
**To:** GRACE (QA Engineer)
**Priority:** HIGH - Phase 1 Quality Assurance
**Estimated Effort:** 10-12 hours total
**Timeline:** Start immediately, parallel with development

---

## 🎯 OVERVIEW

You are assigned to **QA planning for Phase 1 features**:
- C-036: Paper Trading System
- C-037: Social Sentiment Analysis
- C-030: Broker API Integration

**Collaborators:**
- **Turing (Frontend):** Building UI components
- **Linus (Backend):** Building paper trading & broker integration
- **Guido (Backend):** Building social sentiment analysis
- **Charo (Security):** Security audits
- **MIES (Design):** UI/UX specifications

**Your Role:** Create comprehensive test plans, execute tests, validate functionality, measure success metrics.

---

## 📋 YOUR TASKS

### Task 1: C-036 Paper Trading Test Plan (3h)

**File to create:** `apps/frontend/src/components/trading/__tests__/paperTrading.test.tsx`

**Test Scenarios:**

#### 1.1 Paper Trading Portfolio Creation
- [ ] **TC-PT-001:** Create new paper trading portfolio with $100,000 initial cash
  - **Expected:** Portfolio created with virtual_cash=100000, portfolio_value=100000, total_return=0%
  - **Test Data:** New user with no existing portfolio
  - **Steps:**
    1. Login as new user
    2. Navigate to `/paper-trading`
    3. Verify portfolio summary displays $100,000

- [ ] **TC-PT-002:** Verify portfolio fields are correct
  - **Expected:** All fields populated (cash, value, return)
  - **Test Data:** Existing portfolio
  - **Steps:**
    1. Get portfolio via API
    2. Verify all fields present and valid

#### 1.2 Market Order Execution (Buy)
- [ ] **TC-PT-003:** Execute market buy order with sufficient funds
  - **Expected:** Order filled, cash decreased, position created
  - **Test Data:** Portfolio with $100,000, buy 10 shares AAPL at $150
  - **Steps:**
    1. Submit market buy order: AAPL, 10 shares
    2. Verify order status = "filled"
    3. Verify cash = $100,000 - $1,500 = $98,500
    4. Verify position created: 10 shares AAPL at $150
    5. Verify portfolio value = $98,500 (cash) + $1,500 (position) = $100,000

- [ ] **TC-PT-004:** Execute market buy order with insufficient funds
  - **Expected:** Order rejected, error message displayed
  - **Test Data:** Portfolio with $1,000, try to buy 10 shares at $150
  - **Steps:**
    1. Submit market buy order: AAPL, 10 shares ($1,500)
    2. Verify order status = "rejected"
    3. Verify rejection_reason = "Insufficient funds"
    4. Verify cash unchanged = $1,000

- [ ] **TC-PT-005:** Execute market buy order with invalid quantity
  - **Expected:** Form validation error
  - **Test Data:** Portfolio with $100,000, try to buy -5 shares
  - **Steps:**
    1. Enter quantity = -5
    2. Verify form validation prevents submission

#### 1.3 Market Order Execution (Sell)
- [ ] **TC-PT-006:** Execute market sell order with sufficient position
  - **Expected:** Order filled, cash increased, position closed
  - **Test Data:** Portfolio with 10 shares AAPL at $150
  - **Steps:**
    1. Submit market sell order: AAPL, 10 shares
    2. Verify order status = "filled"
    3. Verify cash increased by current price
    4. Verify position deleted (all shares sold)

- [ ] **TC-PT-007:** Execute market sell order with insufficient position
  - **Expected:** Order rejected, error message displayed
  - **Test Data:** Portfolio with 10 shares AAPL, try to sell 20 shares
  - **Steps:**
    1. Submit market sell order: AAPL, 20 shares
    2. Verify order status = "rejected"
    3. Verify rejection_reason = "Insufficient position"

#### 1.4 Limit Order Creation
- [ ] **TC-PT-008:** Create limit buy order with sufficient funds
  - **Expected:** Order created with status = "pending"
  - **Test Data:** Portfolio with $100,000, buy 10 AAPL at limit $140
  - **Steps:**
    1. Submit limit buy order: AAPL, 10 shares, limit $140
    2. Verify order status = "pending"
    3. Verify funds reserved

- [ ] **TC-PT-009:** Fill limit order when price matches
  - **Expected:** Order status changes to "filled"
  - **Test Data:** Pending limit order at $140, price drops to $139
  - **Steps:**
    1. Wait for price to drop below $140
    2. Verify order status = "filled"
    3. Verify position created

#### 1.5 Order Cancellation
- [ ] **TC-PT-010:** Cancel pending limit order
  - **Expected:** Order status = "cancelled", funds released
  - **Test Data:** Pending limit order
  - **Steps:**
    1. Submit cancel order request
    2. Verify order status = "cancelled"
    3. Verify funds released back to portfolio

- [ ] **TC-PT-011:** Attempt to cancel filled order
  - **Expected:** Error "Only pending orders can be cancelled"
  - **Test Data:** Filled order
  - **Steps:**
    1. Attempt to cancel filled order
    2. Verify error message

#### 1.6 Portfolio Value Calculation
- [ ] **TC-PT-012:** Calculate portfolio value correctly (cash + positions)
  - **Expected:** Portfolio value = cash + sum(positions × current_price)
  - **Test Data:**
    - Cash: $50,000
    - 10 shares AAPL at $150 = $1,500
    - 5 shares TSLA at $200 = $1,000
  - **Steps:**
    1. Calculate expected value = $50,000 + $1,500 + $1,000 = $52,500
    2. Get portfolio from API
    3. Verify portfolio_value = $52,500

#### 1.7 Position Tracking (P/L)
- [ ] **TC-PT-013:** Calculate unrealized P/L correctly
  - **Expected:** P/L = (current_price - avg_price) × quantity
  - **Test Data:** 10 shares AAPL avg_price=$150, current_price=$160
  - **Steps:**
    1. Calculate expected P/L = ($160 - $150) × 10 = $100
    2. Get position from API
    3. Verify pl = $100
    4. Verify pl_percent = 6.67%

#### 1.8 WebSocket Real-Time Updates
- [ ] **TC-PT-014:** Portfolio value updates via WebSocket
  - **Expected:** Portfolio value updates in real-time after order
  - **Test Data:** Execute order
  - **Steps:**
    1. Open WebSocket connection
    2. Execute market buy order
    3. Verify portfolio value update received within 100ms
    4. Verify UI updates automatically

#### 1.9 Performance Testing
- [ ] **TC-PT-015:** Handle 1000+ concurrent users
  - **Expected:** API response time < 200ms (p95)
  - **Test Data:** Simulate 1000 concurrent users
  - **Steps:**
    1. Use load testing tool (Locust/k6)
    2. Simulate 1000 users executing orders
    3. Measure p95 response time
    4. Verify < 200ms

---

### Task 2: C-037 Social Sentiment Test Plan (3h)

**File to create:** `apps/backend/src/social/tests/test_sentiment.py`

**Test Scenarios:**

#### 2.1 Twitter Sentiment Fetching
- [ ] **TC-SS-001:** Fetch Twitter sentiment for stock
  - **Expected:** Returns tweets with sentiment scores
  - **Test Data:** Fetch sentiment for AAPL
  - **Steps:**
    1. Call Twitter API for AAPL
    2. Verify tweets returned
    3. Verify sentiment scores calculated (-1 to 1)
    4. Verify sentiment label (bullish/bearish/neutral)

- [ ] **TC-SS-002:** Handle Twitter API rate limiting
  - **Expected:** Gracefully handle rate limit, wait and retry
  - **Test Data:** Exceed Twitter API rate limit
  - **Steps:**
    1. Make requests until rate limit exceeded
    2. Verify error handled gracefully
    3. Verify retry logic works

#### 2.2 Reddit Sentiment Fetching
- [ ] **TC-SS-003:** Fetch Reddit sentiment for stock
  - **Expected:** Returns posts with sentiment scores
  - **Test Data:** Fetch sentiment for TSLA
  - **Steps:**
    1. Call Reddit API for TSLA
    2. Verify posts returned from r/wallstreetbets, r/stocks
    3. Verify sentiment scores calculated
    4. Verify posts weighted by upvotes

#### 2.3 Sentiment Aggregation
- [ ] **TC-SS-004:** Aggregate sentiment from multiple sources
  - **Expected:** Returns weighted sentiment score
  - **Test Data:**
    - Twitter: score=0.5, count=100
    - Reddit: score=0.3, count=50
  - **Steps:**
    1. Call aggregator for stock
    2. Verify aggregated score calculated correctly (weighted)
    3. Verify source weights: Twitter 40%, Reddit 40%

#### 2.4 Sentiment Trend Detection
- [ ] **TC-SS-005:** Detect improving sentiment trend
  - **Expected:** Returns "improving" when sentiment increases
  - **Test Data:** Current score=0.4, previous score=0.2
  - **Steps:**
    1. Calculate sentiment for current period
    2. Compare to previous period
    3. Verify trend = "improving"

#### 2.5 Sentiment Accuracy Validation
- [ ] **TC-SS-006:** Validate sentiment accuracy
  - **Expected:** Sentiment accuracy > 75%
  - **Test Data:** Manually analyze 100 tweets/posts
  - **Steps:**
    1. Fetch 100 tweets/posts
    2. Manually label sentiment (bullish/bearish/neutral)
    3. Compare to NLP labels
    4. Calculate accuracy = (correct / total) × 100
    5. Verify accuracy > 75%

#### 2.6 Performance Testing
- [ ] **TC-SS-007:** Sentiment API response time < 500ms
  - **Expected:** p95 response time < 500ms
  - **Test Data:** 100 concurrent sentiment requests
  - **Steps:**
    1. Load test sentiment API
    2. Measure p95 response time
    3. Verify < 500ms

---

### Task 3: C-030 Broker Integration Test Plan (3h)

**File to create:** `apps/backend/src/broker/tests/test_broker_integration.py`

**Test Scenarios:**

#### 3.1 Broker Account Connection
- [ ] **TC-BI-001:** Connect Alpaca test account
  - **Expected:** Account connected successfully
  - **Test Data:** Valid Alpaca API keys (test account)
  - **Steps:**
    1. Submit connection request with API keys
    2. Verify API keys encrypted at rest
    3. Verify account information retrieved
    4. Verify connection status = "active"

- [ ] **TC-BI-002:** Connect with invalid API keys
  - **Expected:** Error "Invalid API credentials"
  - **Test Data:** Invalid API keys
  - **Steps:**
    1. Submit connection request with invalid keys
    2. Verify error returned
    3. Verify connection not created

#### 3.2 Order Execution
- [ ] **TC-BI-003:** Place test market buy order
  - **Expected:** Order executed via broker
  - **Test Data:** Alpaca test account, buy 1 share AAPL
  - **Steps:**
    1. Submit market buy order
    2. Verify order sent to broker
    3. Verify order status = "filled"
    4. Verify position updated

- [ ] **TC-BI-004:** Place test limit order
  - **Expected:** Limit order created via broker
  - **Test Data:** Alpaca test account, buy AAPL at limit $1
  - **Steps:**
    1. Submit limit buy order
    2. Verify order sent to broker
    3. Verify order status = "pending"

#### 3.3 Order Cancellation
- [ ] **TC-BI-005:** Cancel pending broker order
  - **Expected:** Order cancelled via broker
  - **Test Data:** Pending limit order
  - **Steps:**
    1. Cancel order
    2. Verify cancellation sent to broker
    3. Verify order status = "cancelled"

#### 3.4 Position Sync
- [ ] **TC-BI-006:** Sync positions from broker
  - **Expected:** Positions retrieved from broker
  - **Test Data:** Alpaca test account with positions
  - **Steps:**
    1. Request positions
    2. Verify positions match broker
    3. Verify quantities match

#### 3.5 Security Validation
- [ ] **TC-BI-007:** Verify API keys encrypted at rest
  - **Expected:** API keys stored encrypted
  - **Test Data:** Connected broker account
  - **Steps:**
    1. Query database for API keys
    2. Verify keys are encrypted (not plaintext)
    3. Verify decryption works

- [ ] **TC-BI-008:** Verify user isolation (cannot access other users' accounts)
  - **Expected:** User A cannot access User B's broker accounts
  - **Test Data:** Two users with broker connections
  - **Steps:**
    1. Login as User A
    2. Attempt to access User B's broker account
    3. Verify permission denied

#### 3.6 Order Execution Time
- [ ] **TC-BI-009:** Order execution < 1 second
  - **Expected:** Order executed and confirmed within 1 second
  - **Test Data:** Market order
  - **Steps:**
    1. Submit market order
    2. Measure time from submission to confirmation
    3. Verify < 1 second

---

### Task 4: Cross-Feature Integration Tests (2h)

**Test Scenarios:**

#### 4.1 Paper Trading → Social Sentiment Integration
- [ ] **TC-INT-001:** Display sentiment in paper trading interface
  - **Expected:** Sentiment gauge shown for assets in paper portfolio
  - **Test Data:** Paper portfolio with AAPL position
  - **Steps:**
    1. Open paper trading interface
    2. Verify sentiment gauge displayed for AAPL
    3. Verify sentiment score matches API

#### 4.2 Paper Trading → Broker Integration Handoff
- [ ] **TC-INT-002:** User transitions from paper trading to live trading
  - **Expected:** Similar UI/UX between paper and live trading
  - **Test Data:** User with paper portfolio and broker account
  - **Steps:**
    1. User practices with paper trading
    2. User connects broker account
    3. User switches to live trading
    4. Verify UI/UX is consistent
    5. Verify user understands the transition

---

## ✅ ACCEPTANCE CRITERIA

Your QA work is complete when:

### C-036 Paper Trading
- [ ] All 15 test scenarios documented
- [ ] All test scenarios executed
- [ ] Test results documented (pass/fail)
- [ ] Bugs reported and tracked
- [ ] Performance metrics collected (response times, concurrent users)
- [ ] 100% of acceptance criteria validated

### C-037 Social Sentiment
- [ ] All 7 test scenarios documented
- [ ] All test scenarios executed
- [ ] Sentiment accuracy validated (> 75%)
- [ ] Performance metrics collected
- [ ] Rate limiting tested

### C-030 Broker Integration
- [ ] All 9 test scenarios documented
- [ ] All test scenarios executed
- [ ] Security validation complete
- [ ] Test accounts used (no real money)
- [ ] Order execution time validated (< 1s)

### Cross-Feature Integration
- [ ] Integration test scenarios documented
- [ ] Integration tests executed
- [ ] User flow tested end-to-end

---

## 📊 SUCCESS METRICS

### Quality Metrics
- **Test Coverage:** > 95% of acceptance criteria covered
- **Bug Detection:** All critical bugs found before release
- **Test Execution Rate:** 100% of tests executed
- **Pass Rate:** > 95% of tests passing (before bug fixes)

### Performance Metrics
- **Paper Trading:** < 200ms p95 response time, 1000+ concurrent users
- **Social Sentiment:** < 500ms p95 response time
- **Broker Integration:** < 1s order execution time

### Accuracy Metrics
- **Sentiment Accuracy:** > 75% (vs manual analysis)
- **Portfolio Calculation:** 100% accuracy
- **P/L Calculation:** 100% accuracy

---

## 🚀 NEXT STEPS

### Immediate (Today)
1. **Create test plan documents** for all 3 features
2. **Set up test environment** (test database, test accounts)
3. **Coordinate with developers:** Get access to dev builds
4. **Request test data:** Paper trading test accounts, broker test accounts

### This Week
1. **Write test cases** for C-036 (Paper Trading)
2. **Write test cases** for C-037 (Social Sentiment)
3. **Write test cases** for C-030 (Broker Integration)
4. **Set up load testing** (Locust/k6)

### Next Week
1. **Execute tests** as developers complete features
2. **Document bugs** in issue tracker
3. **Validate fixes** from developers
4. **Measure performance** and accuracy
5. **Sign off** on features when acceptance criteria met

---

## 📞 COMMUNICATION

**Daily Check-ins:**
- Turing: Frontend testing status
- Linus: Backend testing status
- Guido: Social sentiment testing status

**Weekly Updates:**
- Report test progress to GAUDÍ (Architect)
- Report bug statistics (found, fixed, open)
- Flag blockers immediately

**Bug Reporting:**
- Create GitHub issues for all bugs
- Tag relevant developer
- Set priority (P0=critical, P1=high, P2=medium, P3=low)
- Provide steps to reproduce

---

## 🛠️ TEST TOOLS

### Frontend Testing
- **Jest:** Unit testing for React components
- **React Testing Library:** Component testing
- **Cypress:** End-to-end testing
- **MSW:** API mocking for tests

### Backend Testing
- **pytest:** Unit testing for Python
- **Factory Boy:** Test data generation
- **pytest-django:** Django integration
- **pytest-cov:** Coverage reporting

### Load Testing
- **Locust:** Python-based load testing
- **k6:** Modern load testing tool

### Test Data
- **Paper Trading:** Create test portfolios with various scenarios
- **Broker Accounts:** Request test accounts from Alpaca, Interactive Brokers
- **Social Sentiment:** Use sample tweets/posts for accuracy validation

---

**Status:** ✅ Task Assigned
**Timeline:** Start immediately, parallel with development
**Collaborators:** Turing, Linus, Guido, Charo, MIES

---

🧪 *GRACE - QA Engineer*

✅ *Focus: Phase 1 Quality Assurance*

*"Quality is never an accident; it is always the result of intelligent effort."*
