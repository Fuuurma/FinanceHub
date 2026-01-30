# 🎯 TASK C-017: Market Heat Map Visualization

**Created:** January 30, 2026
**Assigned To:** Frontend Coder
**Priority:** P1 - HIGH
**Estimated Time:** 10-14 hours
**Status:** ⏳ PENDING

---

## 📋 OVERVIEW

Implement an interactive market heat map visualization showing:
- Sector performance (color-coded by % change)
- Market cap sizing (larger boxes = larger companies)
- Treemap-style layout
- Drill-down functionality (click sector → see individual stocks)
- Real-time updates
- Multiple views (S&P 500, NASDAQ, user's portfolio, watchlist)

**User Value:** High - Excellent visual overview of market movements
**Complexity:** High - Requires custom visualization
**Dependencies:** Market data APIs exist, need frontend visualization

---

## 🎯 SUCCESS CRITERIA

- [x] Treemap-style heat map of market sectors
- [x] Color coding (green for gains, red for losses)
- [x] Box size proportional to market cap
- [x] Click to drill down (sector → individual stocks)
- [x] Hover tooltips with details
- [x] Real-time data updates
- [x] Multiple market views (S&P 500, NASDAQ, etc.)
- [x] Portfolio heat map view
- [x] Watchlist heat map view
- [x] Responsive design
- [x] Performance: 60fps with 100+ boxes

---

## 📁 FILES TO CREATE/MODIFY

### Frontend Files:

**1. Create Heat Map Types**
```typescript
// apps/frontend/src/types/heatmap.ts

export interface HeatMapNode {
  id: string;
  name: string;
  value: number; // Market cap or allocation %
  change: number; // % change
  changeAmount: number; // Dollar change
  children?: HeatMapNode[]; // For drill-down
  type: 'sector' | 'stock' | 'asset';
  symbol?: string;
}

export interface HeatMapView {
  id: string;
  name: string;
  type: 'market' | 'portfolio' | 'watchlist';
  data: HeatMapNode[];
}

export interface HeatMapConfig {
  colorScheme: 'green-red' | 'blue-orange' | 'custom';
  sizeMetric: 'market_cap' | 'allocation' | 'equal';
  showLabels: boolean;
  showValues: boolean;
  groupBy: 'sector' | 'industry' | 'asset_class';
}
```

**2. Create Heat Map Data Hook**
```typescript
// apps/frontend/src/hooks/useHeatMapData.ts

import { useState, useEffect } from 'react';
import { HeatMapNode } from '@/types/heatmap';

export const useHeatMapData = (view: string) => {
  const [data, setData] = useState<HeatMapNode[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await fetch(`/api/analytics/heatmap/${view}`);
        if (!response.ok) throw new Error('Failed to fetch heat map data');
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 60000); // Update every minute

    return () => clearInterval(interval);
  }, [view]);

  return { data, loading, error };
};
```

**3. Create Heat Map Component**
```typescript
// apps/frontend/src/components/charts/MarketHeatMap.tsx

'use client';

import React, { useState, useMemo } from 'react';
import { HeatMapNode } from '@/types/heatmap';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

interface MarketHeatMapProps {
  data: HeatMapNode[];
  config?: Partial<HeatMapConfig>;
  onNodeClick?: (node: HeatMapNode) => void;
}

export const MarketHeatMap: React.FC<MarketHeatMapProps> = ({
  data,
  config = {},
  onNodeClick
}) => {
  const [viewMode, setViewMode] = useState<'sectors' | 'stocks'>('sectors');
  const [hoveredNode, setHoveredNode] = useState<HeatMapNode | null>(null);

  // Calculate total value for sizing
  const totalValue = useMemo(() => 
    data.reduce((sum, node) => sum + node.value, 0), 
    [data]
  );

  // Calculate color based on change
  const getColor = (change: number) => {
    const intensity = Math.min(Math.abs(change) / 5, 1); // Cap at 5% for full color
    if (change >= 0) {
      return `rgba(34, 197, 94, ${0.3 + intensity * 0.7})`; // Green
    } else {
      return `rgba(239, 68, 68, ${0.3 + intensity * 0.7})`; // Red
    }
  };

  // Squarified treemap algorithm (simplified)
  const layoutNodes = useMemo(() => {
    const nodes = [...data].sort((a, b) => b.value - a.value);
    const layout: Array<{ node: HeatMapNode; x: number; y: number; width: number; height: number }> = [];
    
    // Simple layout (for production, use proper treemap algorithm)
    let currentX = 0;
    let currentY = 0;
    let rowHeight = 0;
    const containerWidth = 1000;
    const containerHeight = 600;
    
    nodes.forEach(node => {
      const valueRatio = node.value / totalValue;
      const area = valueRatio * containerWidth * containerHeight;
      
      // Determine if we should start a new row
      if (currentX + area / rowHeight > containerWidth) {
        currentX = 0;
        currentY += rowHeight;
        rowHeight = 0;
      }
      
      const boxWidth = area / (containerHeight - currentY);
      const boxHeight = containerHeight - currentY;
      
      layout.push({
        node,
        x: currentX,
        y: currentY,
        width: boxWidth,
        height: boxHeight
      });
      
      currentX += boxWidth;
      rowHeight = Math.max(rowHeight, boxHeight);
    });
    
    return layout;
  }, [data, totalValue]);

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Market Heat Map</CardTitle>
        <div className="flex gap-2">
          <Badge variant={viewMode === 'sectors' ? 'default' : 'outline'}>
            Sectors
          </Badge>
          <Badge variant={viewMode === 'stocks' ? 'default' : 'outline'}>
            Stocks
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <TooltipProvider>
          <div className="relative" style={{ width: '100%', height: '600px' }}>
            <svg width="100%" height="100%" viewBox="0 0 1000 600">
              {layoutNodes.map(({ node, x, y, width, height }, index) => (
                <Tooltip key={node.id}>
                  <TooltipTrigger asChild>
                    <g
                      onClick={() => onNodeClick?.(node)}
                      className="cursor-pointer transition-opacity hover:opacity-80"
                      onMouseEnter={() => setHoveredNode(node)}
                      onMouseLeave={() => setHoveredNode(null)}
                    >
                      <rect
                        x={x}
                        y={y}
                        width={width}
                        height={height}
                        fill={getColor(node.change)}
                        stroke="#fff"
                        strokeWidth={2}
                      />
                      <text
                        x={x + width / 2}
                        y={y + height / 2}
                        textAnchor="middle"
                        dominantBaseline="middle"
                        fill="#fff"
                        fontSize={Math.min(width, height) / 10}
                        fontWeight="bold"
                      >
                        {node.name}
                      </text>
                      <text
                        x={x + width / 2}
                        y={y + height / 2 + 20}
                        textAnchor="middle"
                        dominantBaseline="middle"
                        fill="#fff"
                        fontSize={Math.min(width, height) / 12}
                      >
                        {node.change.toFixed(2)}%
                      </text>
                    </g>
                  </TooltipTrigger>
                  <TooltipContent>
                    <div className="space-y-1">
                      <p className="font-bold">{node.name}</p>
                      <p>Change: {node.change.toFixed(2)}%</p>
                      <p>Value: ${node.value.toLocaleString()}</p>
                      {node.symbol && <p>Symbol: {node.symbol}</p>}
                    </div>
                  </TooltipContent>
                </Tooltip>
              ))}
            </svg>
          </div>
        </TooltipProvider>
      </CardContent>
    </Card>
  );
};
```

**4. Create Heat Map Page**
```typescript
// apps/frontend/src/app/(dashboard)/market/heatmap/page.tsx

'use client';

import React, { useState } from 'react';
import { MarketHeatMap } from '@/components/charts/MarketHeatMap';
import { useHeatMapData } from '@/hooks/useHeatMapData';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function MarketHeatMapPage() {
  const [view, setView] = useState('sp500');
  const { data, loading, error } = useHeatMapData(view);
  const router = useRouter();

  const handleNodeClick = (node: any) => {
    if (node.type === 'sector') {
      // Drill down to stocks in this sector
      router.push(`/market/heatmap?sector=${node.id}`);
    } else if (node.type === 'stock') {
      // Navigate to stock details
      router.push(`/assets/${node.symbol}`);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <Button variant="ghost" onClick={() => router.back()}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back
        </Button>
      </div>
      
      <div className="flex gap-2 mb-6">
        <Button onClick={() => setView('sp500')}>S&P 500</Button>
        <Button onClick={() => setView('nasdaq')}>NASDAQ</Button>
        <Button onClick={() => setView('dow')}>DOW JONES</Button>
        <Button onClick={() => setView('portfolio')}>My Portfolio</Button>
        <Button onClick={() => setView('watchlist')}>Watchlist</Button>
      </div>

      <MarketHeatMap data={data} onNodeClick={handleNodeClick} />
    </div>
  );
}
```

### Backend Files:

**5. Create Heat Map API**
```python
# apps/backend/src/api/analytics.py (extend existing)

from ninja import Router
from django.db.models import Q, Sum, F
from ...investments.models import Asset, AssetPricesHistoric, Portfolio

router = Router(tags=['analytics'])

@router.get("/heatmap/{view}")
def get_heatmap_data(request, view: str):
    """Get heat map data for different views"""
    
    user = request.auth
    
    if view == 'sp500':
        return get_sp500_heatmap()
    elif view == 'nasdaq':
        return get_nasdaq_heatmap()
    elif view == 'dow':
        return get_dow_heatmap()
    elif view == 'portfolio':
        return get_portfolio_heatmap(user)
    elif view == 'watchlist':
        return get_watchlist_heatmap(user)
    else:
        return []

def get_sp500_heatmap():
    """Get S&P 500 sector heat map"""
    # Group assets by sector and calculate performance
    from django.db.models import Count
    
    sectors = Asset.objects.filter(
        asset_type='stock',
        exchange__code='NYSE'
    ).values('sector').annotate(
        total_market_cap=Sum('market_cap'),
        avg_change=Sum(F('current_price') * F('market_cap')) / Sum('market_cap')
    ).order_by('-total_market_cap')
    
    data = []
    for sector in sectors:
        change_percent = 0
        if sector['total_market_cap']:
            # Calculate sector change (simplified)
            prices = AssetPricesHistoric.objects.filter(
                asset__sector=sector['sector']
            ).order_by('-timestamp')[:2]
            if len(prices) >= 2:
                change_percent = ((prices[0].close_price - prices[1].close_price) / 
                               prices[1].close_price) * 100
        
        data.append({
            'id': sector['sector'] or 'Unknown',
            'name': sector['sector'] or 'Unknown',
            'value': sector['total_market_cap'] or 0,
            'change': change_percent,
            'changeAmount': 0,
            'type': 'sector'
        })
    
    return data

def get_portfolio_heatmap(user):
    """Get user's portfolio heat map"""
    portfolios = Portfolio.objects.filter(user=user)
    
    data = []
    for portfolio in portfolios:
        for position in portfolio.positions.all():
            change_percent = 0
            if position.asset.current_price and position.average_cost:
                change_percent = ((position.asset.current_price - position.average_cost) / 
                                position.average_cost) * 100
            
            data.append({
                'id': f"{portfolio.id}-{position.asset.id}",
                'name': position.asset.symbol,
                'symbol': position.asset.symbol,
                'value': position.market_value,
                'change': change_percent,
                'changeAmount': position.unrealized_gain_loss,
                'type': 'stock'
            })
    
    return data

def get_watchlist_heatmap(user):
    """Get user's watchlist heat map"""
    # Similar to portfolio but from watchlist
    # ...
    pass
```

---

## 🔧 IMPLEMENTATION STEPS

### Phase 1: Backend API (2-3 hours)
1. Extend analytics API with heat map endpoints
2. Implement sector aggregation logic
3. Implement portfolio heat map logic
4. Implement watchlist heat map logic
5. Test with real data

### Phase 2: Frontend Components (4-5 hours)
1. Create HeatMap types
2. Create useHeatMapData hook
3. Create MarketHeatMap component
4. Implement treemap layout algorithm
5. Add color coding
6. Add tooltips
7. Add click handlers

### Phase 3: Page Integration (2-3 hours)
1. Create heat map page
2. Add view selector (S&P 500, NASDAQ, etc.)
3. Add navigation (back button, drill-down)
4. Add loading states
5. Add error handling

### Phase 4: Polish & Optimization (2-3 hours)
1. Optimize rendering performance
2. Add animations
3. Improve responsive design
4. Add accessibility (ARIA labels)
5. Test with 100+ nodes
6. Test real-time updates

---

## 🧪 TESTING CHECKLIST

### Backend Tests:
- [ ] S&P 500 heat map returns correct sectors
- [ ] Sector performance calculations accurate
- [ ] Portfolio heat map returns user's positions
- [ ] Watchlist heat map returns user's watchlist
- [ ] Data updates correctly (60s interval)
- [ ] Large datasets handled efficiently

### Frontend Tests:
- [ ] Heat map renders correctly
- [ ] Colors match performance (green/red)
- [ ] Box sizes proportional to value
- [ ] Tooltips show correct information
- [ ] Click handlers navigate correctly
- [ ] View switcher works
- [ ] Responsive design works on mobile
- [ ] Performance smooth with 100+ boxes

### E2E Tests:
- [ ] User opens heat map page
- [ ] User switches between views
- [ ] User clicks sector → sees stocks
- [ ] User clicks stock → goes to asset page
- [ ] Data updates in real-time

---

## 📊 API SPECIFICATION

### GET /api/analytics/heatmap/{view}
**Parameters:**
- `view`: sp500 | nasdaq | dow | portfolio | watchlist

**Response:**
```json
[
  {
    "id": "Technology",
    "name": "Technology",
    "value": 15000000000,
    "change": 2.5,
    "changeAmount": 375000000,
    "type": "sector"
  },
  {
    "id": "AAPL",
    "name": "Apple Inc.",
    "symbol": "AAPL",
    "value": 2500000000,
    "change": 1.8,
    "changeAmount": 45000000,
    "type": "stock"
  }
]
```

---

## 🎨 UI DESIGN

```
┌─────────────────────────────────────────────┐
│ Market Heat Map                      [Back] │
├─────────────────────────────────────────────┤
│ [S&P 500] [NASDAQ] [DOW] [Portfolio] [WL] │
├─────────────────────────────────────────────┤
│ ┌───────────────────────────────────────┐   │
│ │ ┌──────┐ ┌──────────┐ ┌───┐          │   │
│ │ │ Tech │ │Healthcare│ │Fin │          │   │
│ │ │+2.5% │ │  +1.2%   │ │-0.8│          │   │
│ │ └──────┘ └──────────┘ └───┘          │   │
│ │ ┌───────────────────────────────┐    │   │
│ │ │        Energy                 │    │   │
│ │ │        +3.8%                  │    │   │
│ │ └───────────────────────────────┘    │   │
│ │ ┌────┐ ┌────┐ ┌────┐ ┌───┐          │   │
│ │ │Util│ │Cons│ │Mat │ │Ind │          │   │
│ │ │-1.2│ │+0.5│ │+1.1│ │+0.3│          │   │
│ │ └────┘ └────┘ └────┘ └───┘          │   │
│ └───────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

---

## 📦 DEPENDENCIES

### Frontend:
- D3.js or similar for treemap layout (optional, can implement own)
- Recharts for fallback (optional)

### Backend:
- None (uses existing models)

---

## 🚀 FUTURE ENHANCEMENTS

**Phase 2:**
- Historical heat map (show performance over time)
- Custom date ranges
- Heat map animation (show changes over time)
- Compare multiple time periods
- Export heat map as image

---

## 🎯 PRIORITY RATIONALE

**Why P1 (HIGH):**
- High visual impact (impressive feature)
- High user value (excellent market overview)
- Builds on existing APIs
- Moderate implementation complexity
- Reusable across multiple views

**User Impact:** 9/10 - Users love heat maps
**Dev Effort:** 7/10 - Complex visualization
**Risk:** 4/10 - Performance could be issue with many nodes

---

**Task created by GAUDÍ (Architect)**
**Ready for assignment to Frontend Coder**
**Part of Visualization Suite**
