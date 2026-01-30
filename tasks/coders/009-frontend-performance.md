# Task: C-009 - Frontend Performance Optimization

**Task ID:** C-009
**Assigned To:** Frontend Coder (1 Coder)
**Priority:** P1 (HIGH)
**Status:** ⏳ PENDING
**Deadline:** February 12, 2026
**Estimated Time:** 10-14 hours

---

## 📋 OBJECTIVE

Optimize frontend performance through code splitting, lazy loading, and bundle size reduction.

---

## 🎯 ACCEPTANCE CRITERIA

- [ ] Implement route-based code splitting
- [ ] Add lazy loading for heavy components
- [ ] Optimize bundle size (<500KB gzipped)
- [ ] Add loading skeletons for all pages
- [ ] Implement image optimization
- [ ] Debounce search inputs
- [ ] Virtualize long lists
- [ ] Lighthouse score >90

---

## 📝 CONTEXT

### Current Issues Found:

1. **No Code Splitting** (P1)
   - 8,472 frontend files
   - All loaded in main bundle
   - Initial load >2MB

2. **No Lazy Loading** (P1)
   - Heavy components loaded immediately
   - Charts, analytics, screener all load at startup

3. **Large Bundle Size** (P0)
   - Likely >1MB uncompressed
   - Slow on mobile connections

4. **No Loading States** (P2)
   - Poor UX during data fetch
   - No skeleton screens

---

## ✅ ACTIONS TO COMPLETE

### Action 1: Route-Based Code Splitting

**File:** `apps/frontend/src/app/layout.tsx`

```typescript
import dynamic from 'next/dynamic'

// Lazy load heavy routes
const Analytics = dynamic(() => import('./(dashboard)/analytics/page'), {
  loading: () => <LoadingSkeleton />,
  ssr: false  // Client-side only for heavy pages
})

const Screener = dynamic(() => import('./(dashboard)/screener/page'), {
  loading: () => <LoadingSkeleton />,
  ssr: false
})

const Settings = dynamic(() => import('./(dashboard)/settings/page'), {
  loading: () => <LoadingSkeleton />
})
```

---

### Action 2: Lazy Load Components

**File:** `apps/frontend/src/components/analytics/PerformanceChart.tsx`

```typescript
import dynamic from 'next/dynamic'

// Lazy load chart library (400KB reduction!)
const ReactECharts = dynamic(() => import('echarts-for-react'), {
  loading: () => <ChartSkeleton />,
  ssr: false
})

export function PerformanceChart({ data }) {
  return (
    <div>
      <ReactECharts option={chartOptions} />
    </div>
  )
}
```

---

### Action 3: Optimize Images

**File:** `apps/frontend/src/app/(dashboard)/assets/[assetId]/page.tsx`

```typescript
import Image from 'next/image'

// ❌ BAD: Regular img tag
// <img src="/logo.png" alt="Logo" />

// ✅ GOOD: Next.js Image optimization
<Image
  src="/logo.png"
  alt="Logo"
  width={200}
  height={200}
  priority={false}  // Lazy load
  placeholder="blur"  // Show blur placeholder
/>
```

---

### Action 4: Debounce Search Inputs

**File:** `apps/frontend/src/components/search/SearchBar.tsx`

```typescript
import { useDebouncedCallback } from 'use-debounce'

export function SearchBar() {
  const debouncedSearch = useDebouncedCallback(
    (value) => {
      // Perform search
      searchAssets(value)
    },
    500  // 500ms delay
  )

  return (
    <input
      type="text"
      onChange={(e) => debouncedSearch(e.target.value)}
      placeholder="Search assets..."
    />
  )
}
```

---

### Action 5: Virtualize Long Lists

**File:** `apps/frontend/src/components/assets/AssetList.tsx`

```typescript
import { useVirtualizer } from '@tanstack/react-virtual'

export function AssetList({ assets }) {
  const parentRef = useRef()

  const virtualizer = useVirtualizer({
    count: assets.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,  // Estimated row height
    overscan: 5  // Render 5 extra rows above/below viewport
  })

  return (
    <div ref={parentRef} style={{ height: '600px', overflow: 'auto' }}>
      <div style={{ height: `${virtualizer.getTotalSize()}px` }}>
        {virtualizer.getVirtualItems().map((virtualItem) => (
          <AssetRow
            key={virtualItem.key}
            asset={assets[virtualItem.index]}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualItem.size}px`,
              transform: `translateY(${virtualItem.start}px)`
            }}
          />
        ))}
      </div>
    </div>
  )
}
```

---

### Action 6: Add Loading Skeletons

**File:** `apps/frontend/src/components/ui/loading-skeleton.tsx`

```typescript
export function TableSkeleton() {
  return (
    <div className="space-y-3">
      {Array.from({ length: 10 }).map((_, i) => (
        <div key={i} className="animate-pulse flex space-x-4">
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
        </div>
      ))}
    </div>
  )
}

export function ChartSkeleton() {
  return (
    <div className="animate-pulse">
      <div className="h-64 bg-gray-200 rounded"></div>
    </div>
  )
}
```

---

### Action 7: Update next.config.js

**File:** `apps/frontend/src/next.config.js`

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable SWC minification (faster than Terser)
  swcMinification: true,

  // Production optimizations
  productionBrowserSourceMaps: false,
  compress: true,

  // Image optimization
  images: {
    domains: ['api.financehub.com'],
    formats: ['image/webp', 'image/avif'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920],
    imageSizes: [16, 32, 48, 64, 96, 128, 256],
  },

  // Bundle analysis
  webpack: (config, { dev, isServer }) => {
    if (!dev && !isServer) {
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          default: false,
          vendors: false,
          commons: {
            name: 'commons',
            chunks: 'all',
            minChunks: 2,
          },
          // Vendor chunks for heavy libraries
          echarts: {
            test: /[\\/]node_modules[\\/](echarts|echarts-for-react)[\\/]/,
            name: 'echarts',
            chunks: 'all',
          },
          recharts: {
            test: /[\\/]node_modules[\\/]recharts[\\/]/,
            name: 'recharts',
            chunks: 'all',
          },
        },
      }
    }

    return config
  },
}

module.exports = nextConfig
```

---

### Action 8: Run Lighthouse Audit

```bash
# Install Lighthouse CI
npm install -D @lhci/cli

# Create lighthouserc.json
cat > lighthouserc.json << 'EOF'
{
  "ci": {
    "collect": {
      "staticDistDir": "./out",
      "url": ["http://localhost:3000"],
      "numberOfRuns": 3
    },
    "assert": {
      "assertions": {
        "categories:performance": ["error", { "minScore": 0.9 }],
        "categories:accessibility": ["error", { "minScore": 0.9 }],
        "categories:best-practices": ["error", { "minScore": 0.9 }],
        "categories:seo": ["error", { "minScore": 0.9 }]
      }
    }
  }
}
EOF

# Run Lighthouse
npx lhci autorun
```

---

## 🎯 SUCCESS CRITERIA

- ✅ Bundle size <500KB gzipped
- ✅ Code splitting implemented
- ✅ Lazy loading active
- ✅ Lighthouse score >90
- ✅ All pages have loading states
- ✅ Images optimized
- ✅ Search debounced
- ✅ Lists virtualized

---

## 📊 DELIVERABLES

1. Updated route components with lazy loading
2. Loading skeleton components
3. Optimized next.config.js
4. Debounced search inputs
5. Virtualized list components
6. Lighthouse audit report (>90 score)
7. Bundle analysis report

---

## ⏱️ ESTIMATED TIME

- Code splitting: 3-4 hours
- Lazy loading: 2-3 hours
- Image optimization: 1-2 hours
- Virtualization: 2-3 hours
- Lighthouse audit: 1-2 hours
- Fixes and iterations: 1-2 hours

**Total:** 10-16 hours

---

## 🔗 DEPENDENCIES

- None

---

**Task Status:** ⏳ PENDING
**Priority:** P1 HIGH (User experience)
