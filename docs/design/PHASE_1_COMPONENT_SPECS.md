# Phase 1 Component Specifications

**Date:** February 1, 2026
**Author:** MIES (UI/UX Designer)
**Features:** C-036, C-037, C-030

---

## Paper Trading Components

### PortfolioSummaryCard

```tsx
<PortfolioSummaryCard
  totalValue="$152,450.00"
  totalReturn={{ value: 4450, percentage: 3.0, isPositive: true }}
  cash="$50,000"
  invested="$102,450"
  dayChange={{ value: 2100, percentage: 1.4, isPositive: true }}
/>
```

**Tailwind Classes:**
```
rounded-none border-1 p-4 space-y-4
```

### OrderForm

```tsx
<OrderForm
  onSubmit={handleOrder}
  availableCash="$50,000"
  defaultSymbol="AAPL"
/>
```

**Sub-components:**
- SymbolInput: `rounded-none border-1`
- SideToggle: Two buttons with `rounded-none`
- OrderTypeSelect: Native select with `rounded-none`
- QuantityInput: `rounded-none border-1 text-right font-mono`
- PriceInput: `rounded-none border-1 text-right font-mono`
- ExecuteButton: `rounded-none border-1 bg-success`

### PositionTable

```tsx
<PositionTable
  positions={positions}
  onClosePosition={handleClose}
/>
```

**Tailwind Classes:**
```
rounded-none border-1
table { w-full border-collapse }
th { border-b-1 p-3 text-left bg-muted font-semibold }
td { border-b-1 p-3 font-mono }
```

### PerformanceChart

```tsx
<PerformanceChart
  data={chartData}
  timeframe="24h"
  onTimeframeChange={setTimeframe}
/>
```

**Tailwind Classes:**
```
rounded-none border-1 p-4
```

---

## Sentiment Components

### SentimentGauge

```tsx
<SentimentGauge
  score={0.45}
  label="BULLISH"
  mentions={87}
  source="twitter"
/>
```

**Tailwind Classes:**
```
rounded-none border-1 p-6 text-center
score { font-bold text-4xl }
label { font-black uppercase tracking-widest }
mentions { font-mono text-sm }
```

### SentimentHistoryChart

```tsx
<SentimentHistoryChart
  data={sentimentHistory}
  timeframe="24h"
  onTimeframeChange={setTimeframe}
/>
```

### TrendingAssetsList

```tsx
<TrendingAssetsList
  assets={trendingAssets}
  onAssetClick={navigateToAsset}
/>
```

**Tailwind Classes:**
```
rounded-none border-1
item { border-b-1 p-3 flex justify-between items-center hover:bg-muted cursor-pointer }
```

### SocialFeed

```tsx
<SocialFeed
  posts={socialPosts}
  filter="all"
  onFilterChange={setFilter}
/>
```

**Tailwind Classes:**
```
rounded-none border-1
filter-tabs { flex border-b-1 }
post { border-b-1 p-4 }
post-header { flex gap-2 text-sm text-muted-foreground }
post-sentiment { inline-block rounded-none border-1 px-2 text-xs }
```

---

## Broker Integration Components

### BrokerConnectionForm

```tsx
<BrokerConnectionForm
  brokers={availableBrokers}
  onConnect={handleConnect}
/>
```

**Sub-components:**
- BrokerSelector: Grid of cards with `rounded-none border-2`
- ApiKeyInput: `rounded-none border-1`
- ApiSecretInput: `rounded-none border-1`
- AccountTypeToggle: Radio-like buttons with `rounded-none border-1`
- ConnectButton: `rounded-none border-2`

### WarningModal

```tsx
<WarningModal
  type="live-trading"
  onConfirm={handleLiveConnect}
  onCancel={handleCancel}
/>
```

**Tailwind Classes:**
```
modal-overlay { fixed inset-0 bg-black/50 flex items-center justify-center }
modal { rounded-none border-2 max-w-md p-6 space-y-4 }
warning-icon { text-4xl }
checkbox { flex items-center gap-2 }
confirm-button { rounded-none border-1 bg-destructive }
cancel-button { rounded-none border-1 }
```

---

## Brutalist Component Variants

### Button Variants

```tsx
const buttonVariants = cva("...", {
  variants: {
    variant: {
      brutalist: "rounded-none border-2 border-foreground bg-foreground text-background font-black uppercase shadow-[4px_4px_0px_0px_var(--foreground)] hover:translate-x-[-1px] hover:translate-y-[-1px] hover:shadow-[5px_5px_0px_0px_var(--foreground)] transition-all",
      brutalistOutline: "rounded-none border-2 border-foreground bg-transparent text-foreground font-black uppercase shadow-[3px_3px_0px_0px_var(--foreground)]",
      trading: "rounded-none border-1 bg-primary text-primary-foreground",
      tradingSuccess: "rounded-none border-1 bg-success text-success-foreground",
      tradingDanger: "rounded-none border-1 bg-destructive text-destructive-foreground",
    },
    size: {
      brutalist: "h-10 px-6 text-xs",
      trading: "h-9 px-4",
    }
  }
})
```

### Card Variants

```tsx
// Trading cards (data-dense)
.trading-card {
  @apply rounded-none border-1 p-4;
}

// Dashboard cards (standard)
.dashboard-card {
  @apply rounded-none border-2 p-6;
}

// Landing cards (bold)
.landing-card {
  @apply rounded-none border-4 p-8;
}
```

### Badge Variants

```tsx
const badgeVariants = cva("...", {
  variants: {
    variant: {
      brutalist: "rounded-none border-2 border-foreground bg-foreground text-background font-mono uppercase text-[10px]",
      trading: "rounded-none border-1 px-2 py-0.5 text-xs",
      sentimentBullish: "rounded-none border-1 bg-success/20 text-success",
      sentimentBearish: "rounded-none border-1 bg-destructive/20 text-destructive",
      sentimentNeutral: "rounded-none border-1 bg-muted text-muted-foreground",
    }
  }
})
```

---

## Spacing Scale

| Token | REM | Pixels | Usage |
|-------|-----|--------|-------|
| space-1 | 0.25rem | 4px | Tight spacing inside inputs |
| space-2 | 0.5rem | 8px | Standard gap |
| space-3 | 0.75rem | 12px | Medium gap |
| space-4 | 1rem | 16px | Component padding |
| space-6 | 1.5rem | 24px | Card padding |
| space-8 | 2rem | 32px | Section gap |

---

## Color Usage by Context

### Financial Data
- Gains: `text-success`
- Losses: `text-destructive`
- Neutral: `text-muted-foreground`

### Sentiment Data
- Bullish: `bg-success/20 border-success text-success`
- Bearish: `bg-destructive/20 border-destructive text-destructive`
- Neutral: `bg-muted border-muted text-muted-foreground`

### Interactive Elements
- Primary: `bg-primary text-primary-foreground`
- Secondary: `bg-secondary text-secondary-foreground`
- Destructive: `bg-destructive text-destructive-foreground`

---

**"Less is more."**

*MIES - UI/UX Designer*
