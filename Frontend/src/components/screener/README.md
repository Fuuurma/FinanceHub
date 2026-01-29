# FinanceHub Screener Module

**Last Updated:** January 29, 2026
**Status:** Production Ready ✅

## Overview

The FinanceHub Stock Screener is a comprehensive filtering tool that allows users to screen and discover stocks based on various financial criteria. Built with Next.js 16, React 19, TypeScript, and shadcn/ui, it follows modern best practices for accessibility, performance, and maintainability.

## Features

### Core Functionality
- ✅ **Multi-criteria filtering** - Filter by market data, valuation, financials, risk metrics, and classification
- ✅ **Quick presets** - Pre-built filter combinations (Undervalued, Growth, Dividend, Momentum, Small Cap, Tech Leaders)
- ✅ **Real-time screening** - Instant results with pagination
- ✅ **Export functionality** - Export results to CSV or JSON format
- ✅ **Persistent state** - User preferences saved to localStorage

### User Experience
- ✅ **Responsive design** - Works on desktop, tablet, and mobile
- ✅ **Loading states** - Clear visual feedback during operations
- ✅ **Error handling** - Graceful error display with retry options
- ✅ **Empty states** - Helpful guidance when no results found
- ✅ **Keyboard shortcuts** - Ctrl/Cmd + Enter to run screener

### Accessibility (WCAG 2.1 AA)
- ✅ **Screen reader support** - ARIA labels and roles throughout
- ✅ **Keyboard navigation** - Full keyboard accessibility
- ✅ **Focus management** - Visible focus indicators
- ✅ **Color contrast** - Meets WCAG contrast requirements
- ✅ **Semantic HTML** - Proper heading hierarchy and landmarks

## Architecture

### Component Structure

```
components/screener/
├── index.ts                 # Barrel export
├── FilterRow.tsx           # Individual filter row (input, operator, value)
├── FilterPanel.tsx         # Filter management and presets
├── ResultsPanel.tsx        # Results display with pagination and export
└── __tests__/
    └── screener.test.tsx   # Component tests
```

### State Management

**Zustand Store:** `stores/screenerStore.ts`
- Manages all screener state
- Persists user preferences (sort, limit, order)
- Provides actions for filter manipulation

### API Integration

**API Client:** `lib/api/screener.ts`
- `getFilters()` - Get available filters
- `getPresets()` - Get preset configurations
- `screenAssets()` - Run screener with filters
- `applyPreset()` - Apply preset configuration
- `clearFilters()` - Reset all filters

### Type Definitions

**Types:** `lib/types/screener.ts`
- `ScreenerFilter` - Filter configuration
- `ScreenerResult` - Individual result item
- `ScreenerResponse` - API response structure
- `ScreenerPreset` - Preset configuration

## Performance Optimizations

### React Hooks
- `useMemo` - Memoize filtered/sorted results
- `useCallback` - Memoize event handlers
- `useEffect` - Efficient side effect management

### Code Splitting
- Components loaded on demand
- No unnecessary bundle bloat
- Fast initial page load

### Rendering Optimization
- Virtualized list support (ready for large datasets)
- Efficient re-renders with proper dependency arrays
- Minimized DOM operations

## Usage

### Basic Usage

```typescript
'use client'

import { FilterPanel } from '@/components/screener'
import { ResultsPanel } from '@/components/screener'

export default function ScreenerPage() {
  return (
    <div className="grid lg:grid-cols-4 gap-6">
      <div className="lg:col-span-1">
        <FilterPanel />
      </div>
      <div className="lg:col-span-3">
        <ResultsPanel />
      </div>
    </div>
  )
}
```

### Using the Store

```typescript
import { useScreenerStore } from '@/stores/screenerStore'

function MyComponent() {
  const {
    results,
    loading,
    runScreener,
    addFilter,
    clearFilters,
  } = useScreenerStore()

  const handleCustomFilter = () => {
    addFilter({
      key: 'pe_ratio',
      operator: '<',
      value: 15
    })
    runScreener()
  }

  // ...
}
```

### Using the Hook

```typescript
import { useScreener } from '@/hooks/useScreener'

function MyComponent() {
  const {
    runScreener,
    applyPreset,
    clearFilters,
    loading,
    error,
    retryScreener,
  } = useScreener()

  // ...
}
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd + Enter` | Run screener |
| `Tab` | Navigate between elements |
| `Enter` | Activate button/select |
| `Escape` | Close dropdowns |

## Accessibility Features

### ARIA Labels
- All interactive elements have descriptive labels
- Screen readers announce filter changes
- Export buttons have clear descriptions

### Focus Management
- Visible focus indicators on all interactive elements
- Logical tab order
- Skip links for keyboard users

### Screen Reader Support
- Live regions for dynamic content updates
- Proper heading hierarchy
- Descriptive link text

## Testing

### Unit Tests

```bash
cd Frontend/src
npm test -- --testPathPattern="screener"
```

### Test Coverage
- FilterRow component
- FilterPanel component
- ResultsPanel component
- Store actions
- API integration

## Integration with Backend

### API Endpoints

**GET /api/screener/filters**
- Returns available filter categories and options
- Cached for performance

**GET /api/screener/presets**
- Returns predefined filter combinations

**POST /api/screener/screen**
- Accepts filter criteria
- Returns paginated results
- Supports sorting and limiting

**POST /api/screener/apply-preset**
- Applies predefined preset

**POST /api/screener/clear-filters**
- Resets all active filters

## Best Practices Implemented

### Code Quality
- ✅ TypeScript for type safety
- ✅ ESLint for code quality
- ✅ Prettier for consistent formatting
- ✅ Conventional commits

### Component Design
- ✅ Single responsibility principle
- ✅ Prop drilling minimized
- ✅ Composition over inheritance
- ✅ Reusable components

### Performance
- ✅ Memoization where needed
- ✅ Lazy loading
- ✅ Efficient re-renders
- ✅ Bundle optimization

### Maintainability
- ✅ Clear file structure
- ✅ Descriptive naming
- ✅ Comprehensive comments
- ✅ Documentation

## Future Enhancements

### Planned Features
- [ ] **Advanced filtering** - Support for more complex filter combinations
- [ ] **Saved screeners** - Save custom filter combinations
- [ ] **Real-time updates** - Auto-refresh results
- [ ] **Comparison mode** - Compare multiple results
- [ ] **Export formats** - Excel, PDF support
- [ ] **Sharing** - Share screener configurations
- [ ] **AI suggestions** - ML-powered filter recommendations
- [ ] **Chart integration** - Visualize results

### Performance Improvements
- [ ] Virtual scrolling for large result sets
- [ ] Server-side pagination
- [ ] Aggressive caching
- [ ] Web Worker for heavy computations

## Troubleshooting

### Common Issues

**Results not loading:**
- Check API connectivity
- Verify authentication
- Check filter criteria validity

**Slow performance:**
- Reduce number of filters
- Increase pagination limit
- Check network latency

**Export not working:**
- Check browser permissions
- Verify result count
- Try different format

### Debug Mode

Enable debug logging:
```typescript
localStorage.setItem('screener-debug', 'true')
```

## Contributing

### Code Style
- Follow AGENTS.md guidelines
- Use TypeScript strict mode
- Write tests for new features
- Update documentation

### Pull Request Process
1. Create feature branch
2. Implement changes
3. Add/update tests
4. Ensure build passes
5. Update documentation
6. Submit PR

## License

MIT License - See LICENSE file for details

## Support

- **Documentation:** See `/docs` folder
- **Issues:** GitHub Issues
- **Discussions:** GitHub Discussions

---

**Built with ❤️ using Next.js, React, TypeScript, and shadcn/ui**
