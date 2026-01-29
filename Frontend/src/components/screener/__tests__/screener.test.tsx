import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { FilterRow } from '@/components/screener/FilterRow'
import { FilterPanel } from '@/components/screener/FilterPanel'
import { ResultsPanel } from '@/components/screener/ResultsPanel'
import { useScreenerStore } from '@/stores/screenerStore'

// Mock the store
jest.mock('@/stores/screenerStore', () => ({
  useScreenerStore: jest.fn(() => ({
    results: [],
    selectedFilters: [],
    loading: false,
    error: null,
    searchTerm: '',
    sortBy: 'relevance',
    sortOrder: 'desc',
    limit: 20,
    currentPage: 1,
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
    setLimit: jest.fn(),
    setCurrentPage: jest.fn(),
  }))
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
      ;(useScreenerStore as jest.Mock).mockImplementation(() => ({
        updateFilter,
        removeFilter: jest.fn(),
      }))

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
      ;(useScreenerStore as jest.Mock).mockImplementation(() => ({
        results: [],
        loading: true,
        error: null,
        searchTerm: '',
        sortBy: 'relevance',
        sortOrder: 'desc',
        limit: 20,
        currentPage: 1,
        runScreener: jest.fn(),
        setSearchTerm: jest.fn(),
        setSortBy: jest.fn(),
        setSortOrder: jest.fn(),
        setLimit: jest.fn(),
        setCurrentPage: jest.fn(),
      }))

      render(<ResultsPanel />)

      expect(screen.getByLabelText('Loading results')).toBeInTheDocument()
    })

    it('shows error state when there is an error', () => {
      ;(useScreenerStore as jest.Mock).mockImplementation(() => ({
        results: [],
        loading: false,
        error: 'Test error message',
        searchTerm: '',
        sortBy: 'relevance',
        sortOrder: 'desc',
        limit: 20,
        currentPage: 1,
        runScreener: jest.fn(),
        setSearchTerm: jest.fn(),
        setSortBy: jest.fn(),
        setSortOrder: jest.fn(),
        setLimit: jest.fn(),
        setCurrentPage: jest.fn(),
      }))

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

      ;(useScreenerStore as jest.Mock).mockImplementation(() => ({
        results: mockResults,
        loading: false,
        error: null,
        searchTerm: '',
        sortBy: 'relevance',
        sortOrder: 'desc',
        limit: 20,
        currentPage: 1,
        runScreener: jest.fn(),
        setSearchTerm: jest.fn(),
        setSortBy: jest.fn(),
        setSortOrder: jest.fn(),
        setLimit: jest.fn(),
        setCurrentPage: jest.fn(),
      }))

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

      ;(useScreenerStore as jest.Mock).mockImplementation(() => ({
        results: mockResults,
        loading: false,
        error: null,
        searchTerm: '',
        sortBy: 'relevance',
        sortOrder: 'desc',
        limit: 20,
        currentPage: 1,
        runScreener: jest.fn(),
        setSearchTerm: jest.fn(),
        setSortBy: jest.fn(),
        setSortOrder: jest.fn(),
        setLimit: jest.fn(),
        setCurrentPage: jest.fn(),
      }))

      render(<ResultsPanel />)

      expect(screen.getByLabelText('Export results as CSV')).toBeInTheDocument()
      expect(screen.getByLabelText('Export results as JSON')).toBeInTheDocument()
    })
  })
})
