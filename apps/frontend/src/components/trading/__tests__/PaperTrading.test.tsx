/**
 * Paper Trading Component Tests - C-036
 * 
 * Frontend tests for paper trading UI components
 * 
 * Created by: GRACE (QA Engineer)
 * Date: February 1, 2026
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { PaperTradingDashboard } from '../PaperTradingDashboard';
import { OrderForm } from '../OrderForm';
import { PortfolioSummary } from '../PortfolioSummary';
import { PositionList } from '../PositionList';

// Mock API calls
jest.mock('../../lib/api/paperTrading', () => ({
  getPortfolio: jest.fn(),
  createPortfolio: jest.fn(),
  executeOrder: jest.fn(),
  getPositions: jest.fn(),
  getOrders: jest.fn(),
}));

jest.mock('../../lib/api/sentiment', () => ({
  getSentiment: jest.fn(),
}));

describe('PaperTradingDashboard', () => {
  const mockPortfolio = {
    id: 'portfolio-123',
    virtual_cash: 100000.00,
    portfolio_value: 100000.00,
    total_return_percent: 0.0,
  };

  const mockPositions = [
    { symbol: 'AAPL', quantity: 10, avg_price: 150.00, current_price: 160.00 },
    { symbol: 'TSLA', quantity: 5, avg_price: 200.00, current_price: 190.00 },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('TC-PT-001: Displays initial portfolio value of $100,000', async () => {
    const { getPortfolio } = require('../../lib/api/paperTrading');
    getPortfolio.mockResolvedValue(mockPortfolio);

    render(<PaperTradingDashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('$100,000.00')).toBeInTheDocument();
    });
  });

  test('TC-PT-002: Shows all portfolio fields correctly', async () => {
    const { getPortfolio } = require('../../lib/api/paperTrading');
    getPortfolio.mockResolvedValue(mockPortfolio);

    render(<PaperTradingDashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('Cash:')).toBeInTheDocument();
      expect(screen.getByText('Portfolio Value:')).toBeInTheDocument();
      expect(screen.getByText('Total Return:')).toBeInTheDocument();
    });
  });
});

describe('OrderForm', () => {
  const mockOnOrderSubmit = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('TC-PT-003: Market buy order with sufficient funds', async () => {
    render(
      <OrderForm
        portfolioCash={100000}
        onSubmit={mockOnOrderSubmit}
      />
    );

    const symbolInput = screen.getByLabelText(/symbol/i);
    const quantityInput = screen.getByLabelText(/quantity/i);
    const buyButton = screen.getByRole('button', { name: /buy/i });

    await userEvent.type(symbolInput, 'AAPL');
    await userEvent.type(quantityInput, '10');
    fireEvent.click(buyButton);

    expect(mockOnOrderSubmit).toHaveBeenCalledWith({
      symbol: 'AAPL',
      quantity: 10,
      orderType: 'market',
      side: 'buy',
    });
  });

  test('TC-PT-004: Shows error for insufficient funds', async () => {
    render(
      <OrderForm
        portfolioCash={1000}
        onSubmit={mockOnOrderSubmit}
      />
    );

    const quantityInput = screen.getByLabelText(/quantity/i);
    const buyButton = screen.getByRole('button', { name: /buy/i });

    await userEvent.type(quantityInput, '20');
    fireEvent.click(buyButton);

    expect(screen.getByText(/insufficient funds/i)).toBeInTheDocument();
  });

  test('TC-PT-005: Validates negative quantity', async () => {
    render(
      <OrderForm
        portfolioCash={100000}
        onSubmit={mockOnOrderSubmit}
      />
    );

    const quantityInput = screen.getByLabelText(/quantity/i);
    
    await userEvent.type(quantityInput, '-5');
    
    expect(quantityInput).toHaveValue(-5);
  });

  test('TC-PT-008: Creates limit order with correct parameters', async () => {
    render(
      <OrderForm
        portfolioCash={100000}
        onSubmit={mockOnOrderSubmit}
      />
    );

    const orderTypeSelect = screen.getByLabelText(/order type/i);
    const limitPriceInput = screen.getByLabelText(/limit price/i);
    const buyButton = screen.getByRole('button', { name: /buy/i });

    fireEvent.change(orderTypeSelect, { target: { value: 'limit' } });
    await userEvent.type(limitPriceInput, '140');
    fireEvent.click(buyButton);

    expect(mockOnOrderSubmit).toHaveBeenCalledWith({
      symbol: expect.any(String),
      quantity: expect.any(Number),
      orderType: 'limit',
      side: 'buy',
      limitPrice: 140,
    });
  });
});

describe('PortfolioSummary', () => {
  test('TC-PT-012: Calculates portfolio value correctly', () => {
    const portfolio = {
      virtual_cash: 50000,
      positions_value: 2500,
    };

    render(<PortfolioSummary portfolio={portfolio} />);
    
    expect(screen.getByText('$52,500.00')).toBeInTheDocument();
  });
});

describe('PositionList', () => {
  const mockPositions = [
    { 
      symbol: 'AAPL', 
      quantity: 10, 
      avg_price: 150.00, 
      current_price: 160.00,
      pl: 100.00,
      pl_percent: 6.67,
    },
  ];

  test('TC-PT-013: Displays P/L correctly', () => {
    render(<PositionList positions={mockPositions} />);
    
    expect(screen.getByText('+$100.00')).toBeInTheDocument();
    expect(screen.getByText('+6.67%')).toBeInTheDocument();
  });
});
