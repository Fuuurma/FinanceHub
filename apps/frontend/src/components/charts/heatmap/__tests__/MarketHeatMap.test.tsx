import React from 'react';
import { render, screen } from '@testing-library/react';
import { MarketHeatMap } from '../MarketHeatMap';
import { HeatMapNode, HeatMapLayoutNode } from '../types';

const mockData: HeatMapNode[] = [
  {
    id: 'technology',
    name: 'Technology',
    value: 15000000000,
    change: 2.5,
    changeAmount: 375000000,
    type: 'sector',
    children: [
      { id: 'AAPL', name: 'Apple', symbol: 'AAPL', value: 3000000000, change: 1.8, changeAmount: 54000000, type: 'stock' },
      { id: 'MSFT', name: 'Microsoft', symbol: 'MSFT', value: 2800000000, change: 2.1, changeAmount: 58800000, type: 'stock' },
    ]
  },
  {
    id: 'healthcare',
    name: 'Healthcare',
    value: 8000000000,
    change: 1.2,
    changeAmount: 96000000,
    type: 'sector',
    children: [
      { id: 'JNJ', name: 'Johnson & Johnson', symbol: 'JNJ', value: 1200000000, change: -0.5, changeAmount: -6000000, type: 'stock' },
    ]
  },
  {
    id: 'energy',
    name: 'Energy',
    value: 3500000000,
    change: -1.5,
    changeAmount: -52500000,
    type: 'sector',
    children: [],
  },
];

const largeMockData: HeatMapNode[] = [
  { id: 'gainers', name: 'Gainers Sector', value: 50000000000, change: 5, changeAmount: 2500000000, type: 'sector' },
  { id: 'losers', name: 'Losers Sector', value: 40000000000, change: -3, changeAmount: -1200000000, type: 'sector' },
];

const simpleData: HeatMapNode[] = [
  { id: 'big', name: 'Big Box', value: 750000000000, change: 5, changeAmount: 37500000000, type: 'sector' },
  { id: 'small', name: 'Small Box', value: 250000000000, change: -2, changeAmount: -5000000000, type: 'sector' },
];

describe('MarketHeatMap', () => {
  it('renders without crashing', () => {
    render(<MarketHeatMap data={mockData} />);
    expect(screen.getByText('Market Heat Map')).toBeInTheDocument();
  });

  it('renders SVG rects for large data', () => {
    render(<MarketHeatMap data={largeMockData} />);
    const svg = document.querySelector('svg');
    expect(svg).toBeInTheDocument();
    const rects = svg?.querySelectorAll('rect');
    expect(rects?.length).toBeGreaterThan(0);
  });

  it('renders with simple large data (2 items)', () => {
    render(<MarketHeatMap data={simpleData} />);
    const svg = document.querySelector('svg');
    expect(svg).toBeInTheDocument();
    const rects = svg?.querySelectorAll('rect');
    expect(rects?.length).toBe(2);
  });

  it('shows "No data available" when data is empty', () => {
    render(<MarketHeatMap data={[]} />);
    expect(screen.getByText('No data available')).toBeInTheDocument();
  });

  it('renders all sector nodes from mockData', () => {
    render(<MarketHeatMap data={mockData} />);
    const svg = document.querySelector('svg');
    expect(svg).toBeInTheDocument();
    const rects = svg?.querySelectorAll('rect');
    expect(rects?.length).toBe(3);
  });
});
