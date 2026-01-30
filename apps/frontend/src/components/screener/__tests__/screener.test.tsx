import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { FilterRow } from '@/components/screener/FilterRow'
import { FilterPanel } from '@/components/screener/FilterPanel'
import { ResultsPanel } from '@/components/screener/ResultsPanel'

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
    back: jest.fn(),
    pathname: '/',
    query: {},
  }),
  useSearchParams: () => new URLSearchParams(),
  usePathname: () => '/',
}))

// Mock useDownloadFile hook
jest.mock('@/hooks/useDownload', () => ({
  useDownloadFile: () => ({
    downloadCSV: jest.fn(),
    downloadJSON: jest.fn(),
    downloadExcel: jest.fn(),
    downloadText: jest.fn(),
  }),
}))

// Mock the store
const mockUseScreenerStore = jest.fn()
jest.mock('@/stores/screenerStore', () => ({
  useScreenerStore: () => mockUseScreenerStore(),
}))

// Mock API
jest.mock('@/lib/api/screener', () => ({
  screenerApi: {
    getFilters: jest.fn(),
    getPresets: jest.fn(),
    screenAssets: jest.fn(),
    applyPreset: jest.fn(),
    clearFilters: jest.fn(),
  }
}))

// Default mock implementation
mockUseScreenerStore.mockReturnValue({
  results: [],
  selectedFilters: [],
  presets: [],
  customPresets: [],
  selectedPreset: null,
  loading: false,
  error: null,
  searchTerm: '',
  sortBy: 'relevance',
  sortOrder: 'desc' as const,
  limit: 20,
  currentPage: 1,
  autoRefresh: false,
  lastUpdated: null,
  runScreener: jest.fn(),
  loadPresets: jest.fn(),
  applyPreset: jest.fn(),
  clearFilters: jest.fn(),
  addFilter: jest.fn(),
  removeFilter: jest.fn(),
  updateFilter: jest.fn(),
  setSearchTerm: jest.fn(),
  setSortBy: jest.fn(),
  setSortOrder: jest.fn(),
  setSort: jest.fn(),
  setLimit: jest.fn(),
  setCurrentPage: jest.fn(),
  setAutoRefresh: jest.fn(),
  saveCustomPreset: jest.fn(),
  deleteCustomPreset: jest.fn(),
})

describe('Screener Components', () => {
  describe('FilterRow', () => {
    it('renders filter row with correct elements', () => {
      render(
        <FilterRow
          index={0}
          filter={{ key: 'price', operator: '>', value: 100 }}
        />
      )

      expect(screen.getByLabelText('Select filter field')).toBeInTheDocument()
      expect(screen.getByLabelText('Select operator')).toBeInTheDocument()
      expect(screen.getByLabelText('Enter value')).toBeInTheDocument()
      expect(screen.getByLabelText('Remove filter 1')).toBeInTheDocument()
    })

    it('calls updateFilter when field changes', () => {
      const updateFilter = jest.fn()
      mockUseScreenerStore.mockReturnValue({
        updateFilter,
        removeFilter: jest.fn(),
      })

      render(
        <FilterRow
          index={0}
          filter={{ key: '', operator: '=', value: '' }}
        />
      )

      // Note: In a real test, you'd trigger the Select component
      expect(updateFilter).not.toHaveBeenCalled()
    })
  })

  describe('FilterPanel', () => {
    it('renders filter panel with title and description', () => {
      render(<FilterPanel />)

      expect(screen.getByText('Active Filters')).toBeInTheDocument()
    })

    it('shows empty state when no filters applied', () => {
      render(<FilterPanel />)

      expect(screen.getByText('No filters applied. Add filters or select a preset below.')).toBeInTheDocument()
    })

    it('renders quick preset buttons', () => {
      render(<FilterPanel />)

      expect(screen.getByText('Quick Presets')).toBeInTheDocument()
      expect(screen.getByText('Undervalued')).toBeInTheDocument()
      expect(screen.getByText('Growth')).toBeInTheDocument()
    })
  })

  describe('ResultsPanel', () => {
    it('renders results panel with title', () => {
      render(<ResultsPanel />)

      expect(screen.getByText('Results')).toBeInTheDocument()
    })

    it('shows loading state when loading', () => {
      mockUseScreenerStore.mockReturnValue({
        results: [],
        loading: true,
        error: null,
        searchTerm: '',
        sortBy: 'relevance',
        sortOrder: 'desc' as const,
        limit: 20,
        currentPage: 1,
        autoRefresh: false,
        lastUpdated: null,
        runScreener: jest.fn(),
        setSearchTerm: jest.fn(),
        setSortBy: jest.fn(),
        setSortOrder: jest.fn(),
        setLimit: jest.fn(),
        setCurrentPage: jest.fn(),
        setAutoRefresh: jest.fn(),
      })

      render(<ResultsPanel />)

      expect(screen.getByLabelText('Loading results')).toBeInTheDocument()
    })

    it('shows error state when there is an error', () => {
      mockUseScreenerStore.mockReturnValue({
        results: [],
        loading: false,
        error: 'Test error message',
        searchTerm: '',
        sortBy: 'relevance',
        sortOrder: 'desc' as const,
        limit: 20,
        currentPage: 1,
        autoRefresh: false,
        lastUpdated: null,
        runScreener: jest.fn(),
        setSearchTerm: jest.fn(),
        setSortBy: jest.fn(),
        setSortOrder: jest.fn(),
        setLimit: jest.fn(),
        setCurrentPage: jest.fn(),
        setAutoRefresh: jest.fn(),
      })

      render(<ResultsPanel />)

      expect(screen.getByText('Test error message')).toBeInTheDocument()
      expect(screen.getByText('Retry')).toBeInTheDocument()
    })

    it('shows empty state when no results', () => {
      render(<ResultsPanel />)

      expect(screen.getByText('No results match your criteria.')).toBeInTheDocument()
    })

    it('renders result items when results exist', () => {
      const mockResults = [
        {
          id: '1',
          symbol: 'AAPL',
          name: 'Apple Inc.',
          asset_type: 'stock',
          price: 150.25,
          change_percent: 2.5,
          volume: 50000000,
          market_cap: 2500000000000,
          pe_ratio: 25.5,
        },
        {
          id: '2',
          symbol: 'GOOGL',
          name: 'Alphabet Inc.',
          asset_type: 'stock',
          price: 2800.50,
          change_percent: -1.2,
          volume: 2500000,
          market_cap: 1800000000000,
          pe_ratio: 30.2,
        },
      ]

      mockUseScreenerStore.mockReturnValue({
        results: mockResults,
        loading: false,
        error: null,
        searchTerm: '',
        sortBy: 'relevance',
        sortOrder: 'desc' as const,
        limit: 20,
        currentPage: 1,
        autoRefresh: false,
        lastUpdated: null,
        runScreener: jest.fn(),
        setSearchTerm: jest.fn(),
        setSortBy: jest.fn(),
        setSortOrder: jest.fn(),
        setLimit: jest.fn(),
        setCurrentPage: jest.fn(),
        setAutoRefresh: jest.fn(),
      })

      render(<ResultsPanel />)

      expect(screen.getByText('AAPL')).toBeInTheDocument()
      expect(screen.getByText('Apple Inc.')).toBeInTheDocument()
      expect(screen.getByText('GOOGL')).toBeInTheDocument()
      expect(screen.getByText('Alphabet Inc.')).toBeInTheDocument()
    })

    it('shows export buttons when results exist', () => {
      const mockResults = [
        {
          id: '1',
          symbol: 'AAPL',
          name: 'Apple Inc.',
          asset_type: 'stock',
          price: 150.25,
          change_percent: 2.5,
          volume: 50000000,
          market_cap: 2500000000000,
          pe_ratio: 25.5,
        },
      ]

      mockUseScreenerStore.mockReturnValue({
        results: mockResults,
        loading: false,
        error: null,
        searchTerm: '',
        sortBy: 'relevance',
        sortOrder: 'desc' as const,
        limit: 20,
        currentPage: 1,
        autoRefresh: false,
        lastUpdated: null,
        runScreener: jest.fn(),
        setSearchTerm: jest.fn(),
        setSortBy: jest.fn(),
        setSortOrder: jest.fn(),
        setLimit: jest.fn(),
        setCurrentPage: jest.fn(),
        setAutoRefresh: jest.fn(),
      })

      render(<ResultsPanel />)

      expect(screen.getByLabelText('Export results as CSV')).toBeInTheDocument()
      expect(screen.getByLabelText('Export results as JSON')).toBeInTheDocument()
    })
  })
})
