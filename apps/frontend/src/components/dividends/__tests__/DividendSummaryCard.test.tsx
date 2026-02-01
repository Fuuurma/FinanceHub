import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { DividendSummaryCard } from '../DividendSummaryCard';

jest.mock('../api', () => ({
  dividendApi: {
    getSummary: jest.fn(() => Promise.resolve({
      totalDividendsYTD: 1247.50,
      totalDividendsLast12m: 3842.30,
      projectedAnnualDividends: 4120.00,
      dividendYield: 0.0325,
      monthlyDividendIncome: 343.33,
      averageYield: 0.0452,
      ytdGrowth: 0.085,
      lastUpdated: '2026-02-01',
    })),
  },
}));

describe('DividendSummaryCard', () => {
  it('renders card structure', async () => {
    render(<DividendSummaryCard portfolioId="1" />);
    
    await waitFor(() => {
      expect(screen.getByText('Dividend Summary')).toBeInTheDocument();
    });
  });

  it('displays YTD Dividends metric', async () => {
    render(<DividendSummaryCard portfolioId="1" />);
    
    await waitFor(() => {
      expect(screen.getByText('YTD Dividends')).toBeInTheDocument();
      expect(screen.getByText('$1,247.50')).toBeInTheDocument();
    });
  });

  it('displays projected annual dividends', async () => {
    render(<DividendSummaryCard portfolioId="1" />);
    
    await waitFor(() => {
      expect(screen.getByText('Projected Annual')).toBeInTheDocument();
    });
  });
});
