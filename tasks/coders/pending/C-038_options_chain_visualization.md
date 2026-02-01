# #️⃣ TASK: C-038 - Options Chain Visualization

**Task ID:** C-038
**Created:** February 1, 2026
**Assigned To:** Frontend Coder (Turing)
**Status:** ✅ COMPLETED
**Priority:** P1 HIGH
**Estimated Time:** 16-20 hours
**Deadline:** March 8, 2026 5:00 PM

---

## 🎯 OBJECTIVE

Create a comprehensive options chain visualization that displays:
- Options chain table (calls and puts)
- Greeks values (delta, gamma, theta, vega, rho)
- Implied volatility skew chart
- Open interest and volume
- Strike price filtering
- Expiration date selection

---

## 📋 REQUIREMENTS

### 1. Backend API Enhancements

**Note:** Options pricing API already exists (from C-023)
```python
# apps/backend/src/options/api.py (enhance existing)
@router.get("/options/chain")
def get_options_chain(request, symbol: str, expiry: date):
    """
    Get full options chain for symbol and expiration
    Returns calls and puts with Greeks
    """
    chain = OptionsChainService().get_chain(symbol, expiry)
    return {
        'symbol': symbol,
        'expiry': expiry,
        'calls': chain['calls'],
        'puts': chain['puts'],
        'spot_price': chain['spot_price'],
        'implied_volatility': chain['iv']
    }

@router.get("/options/greeks")
def get_greeks(request, symbol: str, strike: float, expiry: date):
    """Get Greeks for specific option contract"""
    pass

@router.get("/options/skew")
def get_volatility_skew(request, symbol: str, expiry: date):
    """
    Get implied volatility skew
    Returns IV by strike price
    """
    pass
```

### 2. Options Chain Table Component

```typescript
// apps/frontend/src/components/options/OptionsChainTable.tsx
interface OptionContract {
  strike: number;
  expiry: string;
  type: 'call' | 'put';
  bid: number;
  ask: number;
  last: number;
  change: number;
  changePercent: number;
  volume: number;
  openInterest: number;
  iv: number;  // Implied volatility
  delta: number;
  gamma: number;
  theta: number;
  vega: number;
  rho: number;
  intrinsicValue: number;
  timeValue: number;
  inTheMoney: boolean;
}

export function OptionsChainTable({ symbol, expiry }: Props) {
  // State:
  const [chain, setChain] = useState<{calls: OptionContract[], puts: OptionContract[]}>();
  const [selectedStrike, setSelectedStrike] = useState<number | null>(null);
  const [filter, setFilter] = useState<'all' | 'itm' | 'otm'>('all');

  // Features:
  // - Side-by-side calls and puts table
  // - Sortable columns (strike, bid, ask, iv, volume, OI)
  // - Color code ITM/OTM
  // - Highlight selected strike
  // - Show spot price row
  // - Filter by ITM/OTM/near-the-money
  // - Greeks display (delta, gamma, theta, vega)
  // - IV column with color scale
  // - Volume and open interest bars
  // - Click on row to view details
}
```

### 3. Options Detail Panel

```typescript
// apps/frontend/src/components/options/OptionDetailPanel.tsx
export function OptionDetailPanel({ contract }: Props) {
  // Show selected option details:
  // - Strike, expiry, type
  // - Bid/ask spread
  // - Greeks table
  // - IV chart over time
  // - Volume and OI chart
  // - Profit/loss calculator at expiration
  // - Breakeven price
}
```

### 4. Implied Volatility Skew Chart

```typescript
// apps/frontend/src/components/options/IVSkewChart.tsx
export function IVSkewChart({ symbol, expiry }: Props) {
  // Line chart: Strike Price vs Implied Volatility
  // Separate lines for calls and puts
  // Show smile/smirk shape
  // Compare to historical skew
  - Hover tooltips with details
}
```

### 5. Options Strategy Builder (Bonus)

```typescript
// apps/frontend/src/components/options/OptionsStrategyBuilder.tsx
export function OptionsStrategyBuilder({ symbol }: Props) {
  // Build multi-leg options strategies:
  // - Straddle, strangle
  // - Spread (vertical, calendar, diagonal)
  // - Iron condor, butterfly
  // - Visual P/L diagram
  // - Breakeven points
  // - Max profit/loss
  // - Greeks for entire strategy
}
```

### 6. Options Filter/Sort Controls

```typescript
// apps/frontend/src/components/options/OptionsFilters.tsx
export function OptionsFilters() {
  // Expiration date selector
  // Strike price range slider
  // ITM/OTM filter
  // Volume threshold
  - OI threshold
  - IV range filter
  - Sort selector (strike, iv, volume, delta, etc.)
}
```

---

## ✅ ACCEPTANCE CRITERIA

- [ ] Options chain table with calls and puts
- [ ] Side-by-side view (standard format)
- [ ] Greeks display (delta, gamma, theta, vega, rho)
- [ ] Implied volatility column
- [ ] Open interest and volume
- [ ] Color coding for ITM/OTM
- [ ] Spot price row highlighted
- [ ] Sort by any column
- [ ] Filter by strike range
- [ ] Filter by ITM/OTM/ATM
- [ ] Multiple expiration dates
- [ ] IV skew chart
- [ ] Option detail panel
- [ ] Responsive design
- [ ] Real-time data updates
- [ ] Export options chain to CSV

---

## 📁 FILES TO CREATE/MODIFY

### Create:
- `apps/frontend/src/components/options/OptionsChainTable.tsx`
- `apps/frontend/src/components/options/OptionDetailPanel.tsx`
- `apps/frontend/src/components/options/IVSkewChart.tsx`
- `apps/frontend/src/components/options/OptionsFilters.tsx`
- `apps/frontend/src/components/options/OptionsStrategyBuilder.tsx` (bonus)

### Modify:
- `apps/backend/src/options/api.py` (enhance if needed)
- `apps/frontend/src/app/(dashboard)/options/[symbol]/page.tsx`

---

## 🔗 DEPENDENCIES

**Prerequisites:**
- Options pricing API (C-023 already implemented)
- Greeks calculation service (C-023 already implemented)
- Real-time market data

**Related Tasks:**
- C-023: Options Greeks Calculator (already exists)

---

## 📊 OPTIONS CHAIN TABLE LAYOUT

**Standard Format:**

| Calls | | | | | | | Puts | | | | |
|-------|---|---|---|---|---|---|-------|---|---|---|---|
| Strike | Last | Change | Bid | Ask | Vol | OI | IV | OI | Vol | Ask | Bid | Change | Last | Strike |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 180 | 5.20 | +0.30 | 5.10 | 5.30 | 125 | 1500 | 0.25 | 1800 | 95 | 0.15 | 0.17 | -0.05 | 0.12 | 180 |
| **185** | **2.10** | **+0.15** | **2.05** | **2.15** | **250** | **3000** | **0.22** | **2500** | **180** | **0.40** | **0.42** | **-0.10** | **0.35** | **185** ← Spot |
| 190 | 0.50 | +0.05 | 0.45 | 0.55 | 500 | 5000 | 0.20 | 3500 | 300 | 1.20 | 1.25 | -0.15 | 1.10 | 190 |

**Color Coding:**
- ITM calls: Green background
- ITM puts: Red background
- Spot price row: Yellow highlight
- High IV: Darker color

---

## 📊 DELIVERABLES

1. **Options Chain Table:** Full chain with calls and puts
2. **Greeks Display:** All 5 Greeks in columns
3. **IV Skew Chart:** Strike vs implied volatility
4. **Option Detail Panel:** Selected option details
5. **Filters:** Expiration, strike range, ITM/OTM
6. **Sorting:** Sortable columns
7. **Real-time Updates:** WebSocket or polling
8. **Export:** CSV export functionality
9. **Responsive:** Mobile-friendly layout
10. **Tests:** Component tests

---

## 💬 NOTES

**Data Refresh:**
- Real-time: WebSocket if available
- Fallback: Poll every 5 seconds
- Show last update timestamp
- Allow manual refresh

**Performance:**
- Virtual scrolling for large chains
- Lazy load Greeks if expensive to calculate
- Cache options chain data
- Debounce sort/filter operations

**User Experience:**
- Hover tooltips for Greeks explanations
- Click row to view strategy suggestions
- Compare current IV to historical IV
- Show earnings date on expiry
- Calculate probability of ITM

**Visual Design:**
- Use heat map colors for volume/OI
- Show ITM/OTM with background colors
- Highlight spot price row
- Color delta (green for positive, red for negative)
- Show smile/smirk pattern in IV chart

**Libraries:**
- Frontend: `recharts` for IV skew chart
- Frontend: `react-table` or custom table for chain
- Frontend: `date-fns` for date handling

---

**Status:** ⏳ READY TO START
**Assigned To:** Frontend Coder (Turing)
**User Value:** HIGH - options traders need detailed chain data

---

#️⃣ *C-038: Options Chain Visualization*
*Display options chains with Greeks, IV skew, volume, OI - professional trading tools*
