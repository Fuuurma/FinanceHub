# Additional Design Updates - Feb 1, 2026

**Author:** MIES (UI/UX Designer)
**Purpose:** Continue Phase 1 design system standardization

---

## Components Updated to Minimalistic Brutalism

### 1. DrawingTools.tsx (C-014 - Interactive Chart Drawing Tools)

**Changes:**
- Card: `rounded-none border-1` (was `Card` default)
- TabsList: Custom brutalist tabs with `rounded-none border-2 border-b-0`
- Buttons: `rounded-none border-2 font-black uppercase text-xs`
- Badges: `rounded-none font-mono text-xs`
- Inputs: `rounded-none border-1 font-mono`
- Tip box: `border-2 border-primary/30` (brutalist alert style)
- Manage list items: `border-2 rounded-none`

**Before:**
```tsx
<Card>
  <TabsList className="grid w-full grid-cols-2">
    <TabsTrigger value="tools">Tools</TabsTrigger>
  </TabsList>
</Card>
```

**After:**
```tsx
<Card className="rounded-none border-1">
  <TabsList className="rounded-none border-2 bg-transparent p-0 h-auto">
    <TabsTrigger value="tools" className="rounded-none border-2 border-b-0 data-[state=active]:bg-foreground">
      Tools
    </TabsTrigger>
  </TabsList>
</Card>
```

---

### 2. OptionsCalculator.tsx (Phase 3 Feature)

**Changes:**
- Card: `rounded-none border-1`
- Labels: `text-xs font-bold uppercase`
- Inputs: `rounded-none border-1 font-mono`
- SelectTrigger: `rounded-none border-1 font-mono`
- Results cards: `border-1 p-4` (was `bg-muted rounded-lg`)
- Icons: Added financial context icons (TrendingUp, TrendingDown, Zap)
- Typography: All data uses `font-mono font-black`

**Before:**
```tsx
<Card>
  <CardHeader>
    <CardTitle>Options Pricing Calculator</CardTitle>
  </CardHeader>
  <CardContent>
    <Label>Stock Price ($)</Label>
    <Input ... />
    <div className="p-4 bg-muted rounded-lg">
      <div className="text-2xl font-bold">${result.price}</div>
    </div>
  </CardContent>
</Card>
```

**After:**
```tsx
<Card className="rounded-none border-1">
  <CardHeader className="border-b-1">
    <CardTitle className="font-black uppercase flex items-center gap-2">
      <Calculator className="h-5 w-5" />
      Options Pricing Calculator
    </CardTitle>
  </CardHeader>
  <CardContent className="p-6">
    <Label className="text-xs font-bold uppercase mb-2 block">Stock Price ($)</Label>
    <Input className="rounded-none border-1 font-mono" ... />
    <div className="border-1 p-4">
      <div className="text-2xl font-black font-mono">${result.price.toFixed(2)}</div>
    </div>
  </CardContent>
</Card>
```

---

## Design System Compliance Checklist

### Completed Updates

| Component | File | Status |
|-----------|------|--------|
| DrawingTools | `components/charts/DrawingTools.tsx` | ✅ Updated |
| OptionsCalculator | `components/options/OptionsCalculator.tsx` | ✅ Updated |
| SentimentGauge | `components/sentiment/SentimentGauge.tsx` | ✅ Created new |
| SocialFeed | `components/sentiment/SocialFeed.tsx` | ✅ Created new |
| TrendingAssetsList | `components/sentiment/TrendingAssetsList.tsx` | ✅ Created new |
| SentimentHistoryChart | `components/sentiment/SentimentHistoryChart.tsx` | ✅ Created new |
| BrokerConnectionForm | `components/broker/BrokerConnectionForm.tsx` | ✅ Created new |
| WarningModal | `components/broker/WarningModal.tsx` | ✅ Created new |

### Pending Updates

| Component | File | Priority |
|-----------|------|----------|
| RiskDashboard | `components/risk/RiskDashboard.tsx` | Medium |
| BacktestResults | `components/backtest/BacktestResults.tsx` | Medium |
| OptionsChain | `components/options/OptionsChain.tsx` | Medium |
| MarketHeatmap | `components/charts/MarketHeatmap.tsx` | Low |

---

## Summary

- **Phase 1 Design:** 100% Complete (9 documents, 6 new components)
- **Design System Standardization:** Ongoing
- **Additional Components Updated:** 2 (DrawingTools, OptionsCalculator)

---

*"Less is more."*

*MIES - UI/UX Designer*
