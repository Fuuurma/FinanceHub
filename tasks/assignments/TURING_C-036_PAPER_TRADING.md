# 📋 Task Assignment: C-036 Paper Trading System

**Date:** February 1, 2026
**From:** GAUDÍ (Architect)
**To:** Turing (Frontend Coder)
**Priority:** HIGH - Phase 1 Core Feature
**Estimated Effort:** 6-8 hours frontend
**Timeline:** Start immediately, quality-driven (no deadline)

---

## 🎯 OVERVIEW

You are assigned to **C-036: Paper Trading System** - frontend development.

**Collaborators:**
- **Linus (Backend Coder):** Building paper trading engine, API endpoints
- **GRACE (QA):** Creating test cases, validating functionality
- **Charo (Security):** Security audit, exploit prevention
- **MIES (UI/UX):** Design mockups for paper trading interface
- **HADI (Accessibility):** WCAG 2.1 Level AA compliance

**Backend Lead:** Linus is building the paper trading engine first. You'll integrate once backend is ready.

---

## 📋 YOUR TASKS

### Task 1: Paper Trading Page (2h)
**File:** `apps/frontend/src/app/(dashboard)/paper-trading/page.tsx`

**Requirements:**
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
- [ ] Create page layout with brutalist design (unified minimalistic)
- [ ] Add navigation to dashboard menu
- [ ] Add loading states
- [ ] Add error handling
- [ ] Integrate with API endpoints (wait for Linus)

**Design:** Contact MIES for mockups and design specifications

---

### Task 2: Portfolio Summary Component (1.5h)
**File:** `apps/frontend/src/components/trading/PortfolioSummary.tsx`

**Requirements:**
```tsx
// Display: Virtual cash, portfolio value, total return, day change
export function PortfolioSummary() {
  const { portfolio, isLoading } = usePaperTrading()

  return (
    <Card>
      <CardHeader>Portfolio Value</CardHeader>
      <CardContent>
        <Metric label="Cash" value={portfolio.virtual_cash} format="currency" />
        <Metric label="Value" value={portfolio.portfolio_value} format="currency" />
        <Metric label="Return" value={portfolio.total_return} format="percent" />
        <Metric label="Day Change" value={portfolio.day_change} format="percent" />
      </CardContent>
    </Card>
  )
}
```

**Tasks:**
- [ ] Create component with brutalist base (`rounded-none`)
- [ ] Display all portfolio metrics
- [ ] Add color coding (green for positive, red for negative)
- [ ] Add real-time updates via WebSocket (subscribe to portfolio updates)
- [ ] Add loading and error states
- [ ] Test with WebSocket connection

**API Integration:**
- Endpoint: `GET /api/paper-trading/portfolio/`
- WebSocket: Subscribe to `portfolio_updates` channel

---

### Task 3: Order Form Component (2h)
**File:** `apps/frontend/src/components/trading/OrderForm.tsx`

**Requirements:**
```tsx
// Form: Symbol, Side (Buy/Sell), Order Type (Market/Limit), Quantity, Price
export function OrderForm() {
  const [order, setOrder] = useState({
    symbol: '',
    side: 'buy',
    type: 'market',
    quantity: 0,
    price: 0
  })
  const { executeOrder, isExecuting } = usePaperTrading()

  const handleSubmit = () => {
    executeOrder(order)
  }

  return (
    <Card>
      <CardHeader>Place Order</CardHeader>
      <CardContent>
        <SymbolSearch onSelect={(symbol) => setOrder({...order, symbol})} />
        <SideToggle value={order.side} onChange={(side) => setOrder({...order, side})} />
        <OrderTypeSelect value={order.type} onChange={(type) => setOrder({...order, type})} />
        <QuantityInput value={order.quantity} onChange={(quantity) => setOrder({...order, quantity})} />
        {order.type === 'limit' && (
          <PriceInput value={order.price} onChange={(price) => setOrder({...order, price})} />
        )}
        <Button onClick={handleSubmit} disabled={isExecuting}>
          {isExecuting ? 'Executing...' : `Execute ${order.side.toUpperCase()} Order`}
        </Button>
      </CardContent>
    </Card>
  )
}
```

**Tasks:**
- [ ] Create order form component
- [ ] Integrate with existing universal asset search (C-018)
- [ ] Add buy/sell toggle (green for buy, red for sell)
- [ ] Add order type selector (Market/Limit/Stop)
- [ ] Add quantity input with validation (must be > 0)
- [ ] Add price input (show only for limit/stop orders)
- [ ] Add form validation (sufficient funds, valid quantity)
- [ ] Add order confirmation modal (shows order details, requires confirmation)
- [ ] Add success/error notifications
- [ ] Disable form while order is executing

**Validation Rules:**
- Market orders: Check sufficient cash (buy) or sufficient position (sell)
- Limit orders: Check sufficient cash/position at limit price
- Quantity: Must be > 0, max 4 decimal places for stocks

**API Integration:**
- Endpoint: `POST /api/paper-trading/orders/`
- Request body: `{ symbol, side, type, quantity, price }`
- Response: `{ order_id, status, filled_price, filled_at }`

---

### Task 4: Position List Component (1.5h)
**File:** `apps/frontend/src/components/trading/PositionList.tsx`

**Requirements:**
```tsx
// Table: Symbol, Quantity, Avg Price, Current Price, P/L, Market Value, Actions
export function PositionList() {
  const { positions, isLoading } = usePaperTrading()

  return (
    <Card>
      <CardHeader>Positions</CardHeader>
      <CardContent>
        {isLoading ? (
          <Skeleton count={5} />
        ) : positions.length === 0 ? (
          <EmptyState message="No positions yet. Start trading!" />
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Symbol</TableHead>
                <TableHead>Quantity</TableHead>
                <TableHead>Avg Price</TableHead>
                <TableHead>Current Price</TableHead>
                <TableHead>P/L</TableHead>
                <TableHead>Market Value</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {positions.map(p => (
                <TableRow key={p.id}>
                  <TableCell className="font-medium">{p.symbol}</TableCell>
                  <TableCell>{p.quantity}</TableCell>
                  <TableCell>${p.avg_price.toFixed(2)}</TableCell>
                  <TableCell>${p.current_price.toFixed(2)}</TableCell>
                  <TableCell className={p.pl >= 0 ? 'text-green-500' : 'text-red-500'}>
                    {p.pl >= 0 ? '+' : ''}{p.pl.toFixed(2)} ({p.pl_percent >= 0 ? '+' : ''}{p.pl_percent.toFixed(2)}%)
                  </TableCell>
                  <TableCell>${p.market_value.toFixed(2)}</TableCell>
                  <TableCell>
                    <Button onClick={() => closePosition(p.id)}>Close Position</Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  )
}
```

**Tasks:**
- [ ] Create position list table component
- [ ] Display all position details
- [ ] Calculate and display P/L (unrealized)
- [ ] Add color coding for P/L (green=profit, red=loss)
- [ ] Add "Close Position" button for each position
- [ ] Add empty state when no positions
- [ ] Add loading skeleton while fetching
- [ ] Add real-time price updates via WebSocket
- [ ] Sort table by market value (highest first)

**API Integration:**
- Endpoint: `GET /api/paper-trading/positions/`
- WebSocket: Subscribe to `position_updates` channel

---

### Task 5: Performance Chart Component (1h)
**File:** `apps/frontend/src/components/trading/PerformanceChart.tsx`

**Requirements:**
```tsx
// Line chart: Portfolio value over time + S&P 500 benchmark
export function PerformanceChart() {
  const { performanceHistory, isLoading } = usePaperTrading()

  return (
    <Card>
      <CardHeader>Performance</CardHeader>
      <CardContent>
        {isLoading ? (
          <Skeleton height={200} />
        ) : (
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={performanceHistory}>
              <XAxis dataKey="timestamp" tickFormatter={(ts) => new Date(ts).toLocaleTimeString()} />
              <YAxis tickFormatter={(val) => `$${val.toFixed(0)}`} />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="portfolio_value"
                stroke="#8884d8"
                name="Portfolio"
                strokeWidth={2}
              />
              <Line
                type="monotone"
                dataKey="benchmark"
                stroke="#82ca9d"
                name="S&P 500"
                strokeWidth={2}
                strokeDasharray="5 5"
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  )
}
```

**Tasks:**
- [ ] Create performance chart component using Recharts
- [ ] Display portfolio value over time
- [ ] Add S&P 500 benchmark comparison
- [ ] Add tooltip showing exact values
- [ ] Add legend
- [ ] Handle empty state (no data yet)
- [ ] Add loading state

**API Integration:**
- Endpoint: `GET /api/paper-trading/performance/`
- Response: `[{ timestamp, portfolio_value, benchmark }]`

---

## 🔄 COORDINATION

### Backend (Linus)
**Status:** Linus is building backend first (models, engine, API)

**What to wait for:**
1. Backend models: `PaperTradingPortfolio`, `PaperTradingOrder`
2. API endpoints: `/api/paper-trading/*`
3. WebSocket consumer: `PaperTradingConsumer`

**Coordination:**
- Check in with Linus daily for backend progress
- Create frontend mock data for testing until backend is ready
- Integrate with real API once Linus completes backend

### Design (MIES)
**Action:** Contact MIES for design mockups

**What to request:**
- Paper trading page layout
- Order form design
- Position list table design
- Performance chart design
- Color scheme (use unified minimalistic brutalism)

### QA (GRACE)
**Action:** Coordinate testing with GRACE

**What to provide:**
- Component access for testing
- Test cases from GRACE
- Bug fixes and iterations

### Accessibility (HADI)
**Action:** Ensure WCAG 2.1 Level AA compliance

**Requirements:**
- Keyboard navigation for order form
- Screen reader support for tables
- Color contrast meets WCAG standards
- Focus indicators on all interactive elements

---

## ✅ ACCEPTANCE CRITERIA

Your frontend work is complete when:

- [ ] Paper trading page renders correctly
- [ ] Portfolio summary displays all metrics
- [ ] Order form accepts valid orders
- [ ] Order form rejects invalid orders (insufficient funds, invalid quantity)
- [ ] Order confirmation modal works
- [ ] Position list displays all positions correctly
- [ ] Position list shows real-time P/L updates
- [ ] Performance chart displays portfolio history
- [ ] WebSocket updates work (portfolio value updates in real-time)
- [ ] All components use unified brutalist design
- [ ] All components pass WCAG 2.1 Level AA
- [ ] All components handle loading and error states
- [ ] All components are responsive (mobile, tablet, desktop)

---

## 📊 SUCCESS METRICS

- Page load time < 2 seconds
- WebSocket latency < 100ms
- Order execution < 500ms (frontend processing)
- Zero console errors
- 100% test coverage for components
- WCAG 2.1 Level AA compliant

---

## 🚀 NEXT STEPS

### Immediate (Today)
1. **Contact Linus:** Check backend progress, coordinate API integration
2. **Contact MIES:** Request design mockups for paper trading interface
3. **Create branch:** `feature/c-036-paper-trading-frontend`
4. **Set up:** Install dependencies (Recharts for charts)

### This Week
1. **Build components:** Start with PortfolioSummary, then OrderForm
2. **Integrate with backend:** Once Linus completes API
3. **Test with GRACE:** Coordinate testing
4. **Accessibility review:** Work with HADI

### Next Week
1. **Polish UI:** Refine animations, transitions
2. **Performance optimization:** Ensure smooth WebSocket updates
3. **Documentation:** Document component usage
4. **Handoff to QA:** GRACE will test thoroughly

---

## 📞 COMMUNICATION

**Daily Check-ins:**
- Linus: Backend progress, API availability
- MIES: Design mockups, UI feedback
- GRACE: Testing status, bug reports

**Weekly Updates:**
- Report progress to GAUDÍ (Architect)
- Flag blockers immediately

**Ask for help:**
- Stuck on API integration → Linus
- Design questions → MIES
- Testing failures → GRACE
- Accessibility issues → HADI

---

**Status:** ✅ Task Assigned
**Timeline:** Start immediately, quality-driven
**Collaborators:** Linus (BE), MIES (Design), GRACE (QA), HADI (A11y)

---

💻 *Turing - Frontend Coder*

⚡ *Focus: C-036 Paper Trading Frontend*

*"Quality over speed. The details matter."*
