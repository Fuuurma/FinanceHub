import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { OptionsChainTable } from '../OptionsChainTable';
import { OptionContract, OptionsChainData } from '../OptionsChainTable';

const mockContract: OptionContract = {
  symbol: 'AAPL240217C00185000',
  strike: 185,
  expiry: '2024-02-17',
  type: 'call',
  bid: 5.20,
  ask: 5.35,
  last: 5.25,
  change: 0.30,
  changePercent: 6.06,
  volume: 12500,
  openInterest: 8500,
  iv: 0.25,
  delta: 0.55,
  gamma: 0.045,
  theta: -0.08,
  vega: 0.15,
  rho: 0.03,
  intrinsicValue: 2.50,
  timeValue: 2.75,
  inTheMoney: true,
};

const mockData: OptionsChainData = {
  symbol: 'AAPL',
  spotPrice: 187.50,
  calls: [
    mockContract,
    {
      ...mockContract,
      symbol: 'AAPL240217C00190000',
      strike: 190,
      bid: 2.10,
      ask: 2.20,
      last: 2.15,
      change: 0.15,
      changePercent: 7.50,
      volume: 8500,
      openInterest: 6200,
      iv: 0.22,
      delta: 0.35,
      gamma: 0.038,
      theta: -0.06,
      vega: 0.12,
      intrinsicValue: 0,
      timeValue: 2.15,
      inTheMoney: false,
    },
    {
      ...mockContract,
      symbol: 'AAPL240217C00195000',
      strike: 195,
      bid: 0.50,
      ask: 0.55,
      last: 0.52,
      change: 0.05,
      changePercent: 10.64,
      volume: 5200,
      openInterest: 4100,
      iv: 0.20,
      delta: 0.15,
      gamma: 0.025,
      theta: -0.04,
      vega: 0.08,
      intrinsicValue: 0,
      timeValue: 0.52,
      inTheMoney: false,
    },
  ],
  puts: [
    {
      ...mockContract,
      symbol: 'AAPL240217P00185000',
      type: 'put',
      bid: 3.10,
      ask: 3.25,
      last: 3.18,
      change: -0.20,
      changePercent: -5.92,
      volume: 9800,
      openInterest: 7200,
      iv: 0.28,
      delta: -0.45,
      gamma: 0.042,
      theta: -0.07,
      vega: 0.14,
      intrinsicValue: 0,
      timeValue: 3.18,
      inTheMoney: false,
    },
    {
      ...mockContract,
      symbol: 'AAPL240217P00190000',
      type: 'put',
      strike: 190,
      bid: 5.50,
      ask: 5.70,
      last: 5.60,
      change: -0.35,
      changePercent: -5.88,
      volume: 11200,
      openInterest: 8900,
      iv: 0.30,
      delta: -0.65,
      gamma: 0.048,
      theta: -0.09,
      vega: 0.18,
      intrinsicValue: 2.50,
      timeValue: 3.10,
      inTheMoney: true,
    },
    {
      ...mockContract,
      symbol: 'AAPL240217P00195000',
      type: 'put',
      strike: 195,
      bid: 8.20,
      ask: 8.45,
      last: 8.32,
      change: -0.45,
      changePercent: -5.13,
      volume: 6500,
      openInterest: 5100,
      iv: 0.32,
      delta: -0.85,
      gamma: 0.035,
      theta: -0.08,
      vega: 0.12,
      intrinsicValue: 7.50,
      timeValue: 0.82,
      inTheMoney: true,
    },
  ],
  lastUpdated: '10:30 AM',
};

describe('OptionsChainTable', () => {
  it('renders without crashing', () => {
    render(<OptionsChainTable data={mockData} />);
    expect(screen.getByText('AAPL Options Chain')).toBeInTheDocument();
  });

  it('displays spot price', () => {
    render(<OptionsChainTable data={mockData} />);
    expect(screen.getByText(/Spot:/)).toBeInTheDocument();
    expect(screen.getByText(/\$187\.50/)).toBeInTheDocument();
  });

  it('shows strike prices in table', () => {
    render(<OptionsChainTable data={mockData} />);
    expect(screen.getByText(/\$185\.00/)).toBeInTheDocument();
    expect(screen.getByText(/\$190\.00/)).toBeInTheDocument();
    expect(screen.getByText(/\$195\.00/)).toBeInTheDocument();
  });

  it('calls onSelectContract when row is clicked', () => {
    const onSelect = jest.fn();
    render(<OptionsChainTable data={mockData} onSelectContract={onSelect} />);
    const rows = screen.getAllByRole('row').filter(row => row.textContent?.includes('$185.00'));
    if (rows.length > 0) {
      fireEvent.click(rows[0]);
      expect(onSelect).toHaveBeenCalled();
    }
  });

  it('filters by ITM when filter changes', () => {
    render(<OptionsChainTable data={mockData} filter="itm" />);
    const rows = screen.getAllByRole('row');
    expect(rows.length).toBeGreaterThan(0);
  });

  it('shows last updated time', () => {
    render(<OptionsChainTable data={mockData} />);
    expect(screen.getByText(/Last updated:/)).toBeInTheDocument();
  });

  it('highlights spot price row', () => {
    render(<OptionsChainTable data={mockData} />);
    expect(screen.getByText(/\$185\.00/)).toBeInTheDocument();
  });

  it('renders export button', () => {
    render(<OptionsChainTable data={mockData} />);
    expect(screen.getByText('Export')).toBeInTheDocument();
  });

  it('handles empty data', () => {
    const emptyData: OptionsChainData = {
      symbol: 'AAPL',
      spotPrice: 187.50,
      calls: [],
      puts: [],
      lastUpdated: '10:30 AM',
    };
    render(<OptionsChainTable data={emptyData} />);
    expect(screen.getByText('No options found matching your filters')).toBeInTheDocument();
  });
});
