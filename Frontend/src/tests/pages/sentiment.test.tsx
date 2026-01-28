import { describe, it, expect, beforeEach } from '@jest/globals'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import SentimentPage from '@/app/(dashboard)/sentiment/page'
import { newsSentimentApi } from '@/lib/api/news-sentiment'

jest.mock('@/lib/api/news-sentiment', () => ({
  newsSentimentApi: {
    getSentiment: jest.fn(),
  },
}))

describe('SentimentPage', () => {
  const mockGetSentiment = newsSentimentApi.getSentiment as jest.Mock

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders page title and description', () => {
    render(<SentimentPage />)
    expect(screen.getByText('News Sentiment')).toBeInTheDocument()
    expect(screen.getByText('Market sentiment analysis from news')).toBeInTheDocument()
  })

  it('renders symbol search form', () => {
    render(<SentimentPage />)
    expect(screen.getByPlaceholderText('Enter symbol (e.g., AAPL, BTC, TSLA)')).toBeInTheDocument()
    expect(screen.getByText('Analyze')).toBeInTheDocument()
  })

  it('renders day filter selector', () => {
    render(<SentimentPage />)
    expect(screen.getByText('1 Day')).toBeInTheDocument()
    expect(screen.getByText('7 Days')).toBeInTheDocument()
    expect(screen.getByText('14 Days')).toBeInTheDocument()
    expect(screen.getByText('30 Days')).toBeInTheDocument()
  })

  it('calls API when symbol is submitted', async () => {
    const mockResponse = {
      symbol: 'AAPL',
      overall_sentiment: 'positive',
      sentiment_score: 0.65,
      article_count: 25,
      positive_count: 15,
      negative_count: 5,
      neutral_count: 5,
      average_sentiment_7d: 0.58,
      articles: [],
      sentiment_trend: null,
      key_topics: ['earnings', 'iPhone', 'AI'],
      analyzed_at: '2026-01-28T12:00:00Z',
    }
    mockGetSentiment.mockResolvedValue(mockResponse as any)

    render(<SentimentPage />)
    
    const input = screen.getByPlaceholderText('Enter symbol (e.g., AAPL, BTC, TSLA)')
    fireEvent.change(input, { target: { value: 'aapl' } })
    
    const analyzeButton = screen.getByText('Analyze')
    const form = analyzeButton.closest('form')
    fireEvent.submit(form!)

    await waitFor(() => {
      expect(mockGetSentiment).toHaveBeenCalledWith('AAPL', { days: 7 })
    })
  })

  it('converts symbol to uppercase', async () => {
    const mockResponse = {
      symbol: 'AAPL',
      overall_sentiment: 'neutral',
      sentiment_score: 0,
      article_count: 0,
      positive_count: 0,
      negative_count: 0,
      neutral_count: 0,
      average_sentiment_7d: null,
      articles: [],
      sentiment_trend: null,
      key_topics: [],
      analyzed_at: '2026-01-28T12:00:00Z',
    }
    mockGetSentiment.mockResolvedValue(mockResponse as any)

    render(<SentimentPage />)
    
    const input = screen.getByPlaceholderText('Enter symbol (e.g., AAPL, BTC, TSLA)')
    fireEvent.change(input, { target: { value: 'aapl' } })
    fireEvent.keyPress(input, { key: 'Enter', code: 'Enter' })

    await waitFor(() => {
      expect(mockGetSentiment).toHaveBeenCalledWith('AAPL', { days: 7 })
    })
  })

  it('displays sentiment data when loaded', async () => {
    const mockResponse = {
      symbol: 'AAPL',
      overall_sentiment: 'positive',
      sentiment_score: 0.65,
      article_count: 25,
      positive_count: 15,
      negative_count: 5,
      neutral_count: 5,
      average_sentiment_7d: 0.58,
      articles: [],
      sentiment_trend: null,
      key_topics: ['earnings', 'iPhone', 'AI'],
      analyzed_at: '2026-01-28T12:00:00Z',
    }
    mockGetSentiment.mockResolvedValue(mockResponse as any)

    render(<SentimentPage />)
    
    const input = screen.getByPlaceholderText('Enter symbol (e.g., AAPL, BTC, TSLA)')
    fireEvent.change(input, { target: { value: 'AAPL' } })
    fireEvent.keyPress(input, { key: 'Enter', code: 'Enter' })

    await waitFor(() => {
      expect(screen.getByText('Positive')).toBeInTheDocument()
      expect(screen.getByText('0.65')).toBeInTheDocument()
      expect(screen.getByText('25')).toBeInTheDocument()
      expect(screen.getByText('15')).toBeInTheDocument()
      expect(screen.getByText('5')).toBeInTheDocument()
      expect(screen.getByText('5')).toBeInTheDocument()
      expect(screen.getByText('earnings')).toBeInTheDocument()
      expect(screen.getByText('iPhone')).toBeInTheDocument()
      expect(screen.getByText('AI')).toBeInTheDocument()
    })
  })

  it('changes day filter when selected', async () => {
    const mockResponse = {
      symbol: 'AAPL',
      overall_sentiment: 'neutral',
      sentiment_score: 0,
      article_count: 0,
      positive_count: 0,
      negative_count: 0,
      neutral_count: 0,
      average_sentiment_7d: null,
      articles: [],
      sentiment_trend: null,
      key_topics: [],
      analyzed_at: '2026-01-28T12:00:00Z',
    }
    mockGetSentiment.mockResolvedValue(mockResponse as any)

    render(<SentimentPage />)
    
    const input = screen.getByPlaceholderText('Enter symbol (e.g., AAPL, BTC, TSLA)')
    fireEvent.change(input, { target: { value: 'AAPL' } })
    fireEvent.keyPress(input, { key: 'Enter', code: 'Enter' })

    await waitFor(() => {
      expect(mockGetSentiment).toHaveBeenCalledWith('AAPL', { days: 7 })
    })

    const select = screen.getByDisplayValue('7 Days')
    fireEvent.change(select, { target: { value: '14' } })

    await waitFor(() => {
      expect(mockGetSentiment).toHaveBeenCalledWith('AAPL', { days: 14 })
    })
  })

  it('displays error when API fails', async () => {
    mockGetSentiment.mockRejectedValue(new Error('Failed to fetch sentiment'))

    render(<SentimentPage />)
    
    const input = screen.getByPlaceholderText('Enter symbol (e.g., AAPL, BTC, TSLA)')
    fireEvent.change(input, { target: { value: 'AAPL' } })
    fireEvent.keyPress(input, { key: 'Enter', code: 'Enter' })

    await waitFor(() => {
      expect(screen.getByText('Error')).toBeInTheDocument()
      expect(screen.getByText('Failed to fetch sentiment')).toBeInTheDocument()
    })
  })

  it('shows loading state during API call', () => {
    mockGetSentiment.mockImplementation(() => new Promise(() => {}))

    render(<SentimentPage />)
    
    const input = screen.getByPlaceholderText('Enter symbol (e.g., AAPL, BTC, TSLA)')
    fireEvent.change(input, { target: { value: 'AAPL' } })
    fireEvent.keyPress(input, { key: 'Enter', code: 'Enter' })

    expect(screen.getByText('Analyzing...')).toBeInTheDocument()
  })
})
