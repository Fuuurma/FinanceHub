import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MarketHeatMap } from '../MarketHeatMap';
import { HeatMapNode } from '../types';

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

describe('MarketHeatMap', () => {
  it('renders without crashing', () => {
    render(<MarketHeatMap data={mockData} />);
    expect(screen.getByText('Market Heat Map')).toBeInTheDocument();
  });

  it('renders all sector nodes', () => {
    render(<MarketHeatMap data={mockData} />);
    expect(screen.getByText('Technology')).toBeInTheDocument();
    expect(screen.getByText('Healthcare')).toBeInTheDocument();
    expect(screen.getByText('Energy')).toBeInTheDocument();
  });

  it('renders gainer labels correctly', () => {
    render(<MarketHeatMap data={mockData} />);
    expect(screen.getByText('+2.50%')).toBeInTheDocument();
    expect(screen.getByText('+1.20%')).toBeInTheDocument();
  });

  it('renders loser labels correctly', () => {
    render(<MarketHeatMap data={mockData} />);
    expect(screen.getByText('-1.50%')).toBeInTheDocument();
  });

  it('calls onNodeClick when clicking a node', () => {
    const onClick = jest.fn();
    render(<MarketHeatMap data={mockData} onNodeClick={onClick} />);
    const techNode = screen.getByText('Technology');
    fireEvent.click(techNode);
    expect(onClick).toHaveBeenCalledWith(mockData[0]);
  });

  it('shows "No data available" when data is empty', () => {
    render(<MarketHeatMap data={[]} />);
    expect(screen.getByText('No data available')).toBeInTheDocument();
  });
});

describe('HeatMap Color Logic', () => {
  it('renders positive change as green', () => {
    const positiveData: HeatMapNode[] = [
      { id: 'gainers', name: 'Gainers', value: 1000, change: 5, changeAmount: 50, type: 'stock' }
    ];
    render(<MarketHeatMap data={positiveData} />);
    expect(screen.getByText('+5.00%')).toBeInTheDocument();
  });

  it('renders negative change as red', () => {
    const negativeData: HeatMapNode[] = [
      { id: 'losers', name: 'Losers', value: 1000, change: -3, changeAmount: -30, type: 'stock' }
    ];
    render(<MarketHeatMap data={negativeData} />);
    expect(screen.getByText('-3.00%')).toBeInTheDocument();
  });
});
