# Advanced Chart Component

**Component:** `AdvancedChart`
**Location:** `Frontend/src/components/charts/AdvancedChart.tsx`
**Library:** lightweight-charts (TradingView library)
**Status:** Production Ready ✅

---

## Features

### Chart Types
- ✅ **Candlestick** - Traditional OHLCV candlestick charts
- ✅ **Line** - Simple price line chart
- ✅ **Area** - Filled area chart
- ✅ **Bar** - OHLC bar chart

### Timeframes
- **Intraday:** 1m, 5m, 15m, 30m, 1h, 4h
- **Daily+:** 1d, 1w, 1M, 3m, 6m, 1y

### Technical Indicators
- **Trend:** SMA, EMA, WMA, Bollinger Bands, Ichimoku, Parabolic SAR
- **Momentum:** RSI, MACD, Stochastic, CCI, Williams %R
- **Volume:** OBV, MFI, A/D Line, ATR

### Interactions
- ✅ Zoom in/out (scroll or buttons)
- ✅ Pan (drag or scroll)
- ✅ Crosshair on hover
- ✅ Timeframe selection
- ✅ Chart type selection
- ✅ Fullscreen mode
- ✅ Reset zoom

### Accessibility
- ✅ ARIA labels throughout
- ✅ Keyboard navigation support
- ✅ Screen reader announcements
- ✅ Focus management
- ✅ High contrast colors

---

## Usage

### Basic Usage

```typescript
import { AdvancedChart } from '@/components/charts'

<AdvancedChart
  symbol="AAPL"
  timeframe="1h"
  chartType="candlestick"
  showVolume={true}
  height={500}
/>
```

### With Indicators

```typescript
import { AdvancedChart } from '@/components/charts'
import { DEFAULT_INDICATORS } from '@/lib/types/indicators'

<AdvancedChart
  symbol="AAPL"
  timeframe="1h"
  indicators={[
    { ...DEFAULT_INDICATORS.sma, visible: true },
    { ...DEFAULT_INDICATORS.ema, visible: true },
  ]}
  onIndicatorsChange={(indicators) => console.log(indicators)}
  showIndicators={true}
/>
```

### With Callbacks

```typescript
<AdvancedChart
  symbol="AAPL"
  onTimeframeChange={(tf) => console.log('Timeframe:', tf)}
  onChartTypeChange={(ct) => console.log('Chart type:', ct)}
  onIndicatorsChange={(indicators) => console.log('Indicators:', indicators)}
/>
```

### Full Example

```typescript
'use client'

import { useState } from 'react'
import { AdvancedChart } from '@/components/charts/AdvancedChart'
import { TechnicalIndicators } from '@/components/charts/TechnicalIndicators'
import type { IndicatorConfig } from '@/lib/types/indicators'

export default function ChartPage() {
  const [indicators, setIndicators] = useState<IndicatorConfig[]>([])

  return (
    <div className="grid lg:grid-cols-4 gap-6">
      <div className="lg:col-span-3">
        <AdvancedChart
          symbol="AAPL"
          timeframe="1h"
          indicators={indicators}
          showVolume={true}
          height={600}
          onIndicatorsChange={setIndicators}
        />
      </div>
      <div className="lg:col-span-1">
        <TechnicalIndicators
          symbol="AAPL"
          selectedIndicators={indicators}
          onIndicatorsChange={setIndicators}
        />
      </div>
    </div>
  )
}
```

---

## Props Interface

```typescript
export type ChartType = 'candlestick' | 'line' | 'area' | 'bar'

export interface AdvancedChartProps {
  symbol: string                    // Asset symbol (required)
  initialData?: ChartDataPoint[]     // Pre-loaded OHLCV data
  chartType?: ChartType              // Default: 'candlestick'
  timeframe?: TimeFrame             // Default: '1h'
  indicators?: IndicatorConfig[]     // Active indicators
  showVolume?: boolean              // Default: true
  showIndicators?: boolean          // Default: false
  height?: number                  // Default: 500
  className?: string               // Additional CSS classes
  onTimeframeChange?: (tf: TimeFrame) => void
  onChartTypeChange?: (ct: ChartType) => void
  onIndicatorsChange?: (indicators: IndicatorConfig[]) => void
}
```

---

## Data Format

### ChartDataPoint Interface

```typescript
interface ChartDataPoint {
  timestamp: string  // ISO 8601 format
  open: number       // Opening price
  high: number       // High price
  low: number        // Low price
  close: number      // Closing price
  volume: number     // Trading volume
}
```

### Example Data

```typescript
const data: ChartDataPoint[] = [
  {
    timestamp: '2026-01-29T10:00:00Z',
    open: 150.25,
    high: 152.30,
    low: 149.75,
    close: 151.80,
    volume: 2500000,
  },
  // ... more data points
]
```

---

## Integration with TechnicalIndicators

```typescript
import { AdvancedChart } from '@/components/charts/AdvancedChart'
import { TechnicalIndicators } from '@/components/charts/TechnicalIndicators'

function ChartWithIndicators() {
  const [indicators, setIndicators] = useState<IndicatorConfig[]>([])

  return (
    <div className="grid lg:grid-cols-4 gap-6">
      <div className="lg:col-span-3">
        <AdvancedChart
          symbol="AAPL"
          indicators={indicators}
          onIndicatorsChange={setIndicators}
        />
      </div>
      <div className="lg:col-span-1">
        <TechnicalIndicators
          symbol="AAPL"
          selectedIndicators={indicators}
          onIndicatorsChange={setIndicators}
        />
      </div>
    </div>
  )
}
```

---

## Performance Considerations

### Memoization
The component uses React's `useMemo` and `useCallback` to optimize:
- Filtering and sorting operations
- Event handlers
- Derived calculations

### Chart Lifecycle
- Chart is created once on mount
- Data updates don't recreate the chart
- Resize observer handles window changes
- Proper cleanup on unmount

### Large Datasets
For datasets with >1000 candles:
```typescript
// Consider reducing initial data
<AdvancedChart
  symbol="AAPL"
  initialData={data.slice(-500)} // Last 500 candles only
/>
```

---

## Accessibility Features

### ARIA Attributes
- `role="img"` on chart container
- `aria-label` on all interactive elements
- `aria-pressed` on timeframe buttons
- `aria-label` on zoom controls
- `role="toolbar"` for chart controls

### Keyboard Navigation
- Tab through all controls
- Enter/Space to activate buttons
- Arrow keys for navigation
- Escape to close dropdowns

### Screen Reader Support
- Announces chart type and timeframe
- Describes active indicators
- Provides context for data updates

---

## Customization

### Styling
The component uses Tailwind CSS classes. Customize with:
- `className` prop for additional styles
- CSS variables for theme colors
- Override chart colors in `CHART_CONFIG`

### Theme Colors
```typescript
const CHART_CONFIG = {
  CANDLE_UP_COLOR: '#22c55e',  // Green candles
  CANDLE_DOWN_COLOR: '#ef4444', // Red candles
  GRID_COLOR: '#e1e1e1',
  TEXT_COLOR: '#666666',
  BACKGROUND_COLOR: '#ffffff',
}
```

---

## Browser Support

- ✅ Chrome 80+
- ✅ Firefox 75+
- ✅ Safari 13+
- ✅ Edge 80+
- ✅ Mobile browsers (touch support)

---

## Dependencies

```json
{
  "lightweight-charts": "latest"
}
```

---

## Examples

### Static Data

```typescript
<AdvancedChart
  symbol="AAPL"
  initialData={[
    {
      timestamp: '2026-01-29T10:00:00Z',
      open: 150,
      high: 152,
      low: 149,
      close: 151,
      volume: 2500000,
    },
    // ... more data
  ]}
/>
```

### Real-time Updates

```typescript
function RealTimeChart({ symbol }) {
  const [data, setData] = useState([])

  useEffect(() => {
    // Subscribe to WebSocket updates
    const subscription = subscribeToPrice(symbol, (candle) => {
      setData(prev => [...prev, candle].slice(-100))
    })

    return () => subscription.unsubscribe()
  }, [symbol])

  return <AdvancedChart symbol={symbol} initialData={data} />
}
```

### Comparison Mode

```typescript
<AdvancedChart
  symbol="SPY"
  chartType="line"
  showVolume={false}
  height={400}
/>
```

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Scroll | Pan chart |
| Ctrl + Scroll | Zoom in/out |
| Double-click | Reset zoom |
| Right-click | Context menu |

---

## Troubleshooting

### Chart not rendering
- Ensure container has defined height
- Check browser console for errors
- Verify data format is correct

### Poor performance
- Reduce initial data size
- Disable unnecessary features
- Use `useMemo` for data transforms

### Indicators not showing
- Verify indicator config is correct
- Check indicator is marked as visible
- Ensure data has required fields

---

## Related Components

- [TechnicalIndicators](./TechnicalIndicators.md) - Indicator configuration panel
- [DrawingTools](./DrawingTools.md) - Chart drawing tools
- [ComparisonChart](./ComparisonChart.md) - Multi-symbol comparison

---

**Last Updated:** January 29, 2026
**Version:** 1.0.0
