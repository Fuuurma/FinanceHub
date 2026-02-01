import React from 'react';
import { render, screen } from '@testing-library/react';
import { IVSkewChart, IVSkewDataPoint } from '../IVSkewChart';

const mockData: IVSkewDataPoint[] = [
  { strike: 170, callIV: 0.22, putIV: 0.28, midIV: 0.25 },
  { strike: 175, callIV: 0.20, putIV: 0.26, midIV: 0.23 },
  { strike: 180, callIV: 0.18, putIV: 0.24, midIV: 0.21 },
  { strike: 185, callIV: 0.17, putIV: 0.23, midIV: 0.20 },
  { strike: 190, callIV: 0.18, putIV: 0.24, midIV: 0.21 },
  { strike: 195, callIV: 0.20, putIV: 0.26, midIV: 0.23 },
  { strike: 200, callIV: 0.22, putIV: 0.28, midIV: 0.25 },
];

const renderWithSize = (ui: React.ReactElement) => {
  return render(
    <div style={{ width: '600px', height: '400px' }}>
      {ui}
    </div>
  );
};

describe('IVSkewChart', () => {
  it('renders without crashing', () => {
    renderWithSize(
      <IVSkewChart
        data={mockData}
        spotPrice={185}
        symbol="AAPL"
        expiry="2024-02-21"
      />
    );
    expect(screen.getByText('Implied Volatility Skew')).toBeInTheDocument();
  });

  it('displays symbol and expiry', () => {
    renderWithSize(
      <IVSkewChart
        data={mockData}
        spotPrice={185}
        symbol="AAPL"
        expiry="Feb 21, 2024"
      />
    );
    expect(screen.getByText('AAPL - Feb 21, 2024')).toBeInTheDocument();
  });

  it('shows legend badges', () => {
    renderWithSize(
      <IVSkewChart
        data={mockData}
        spotPrice={185}
        symbol="AAPL"
        expiry="2024-02-21"
      />
    );
    expect(screen.getByText('Calls')).toBeInTheDocument();
    expect(screen.getByText('Puts')).toBeInTheDocument();
  });

  it.skip('handles empty data', () => {
    renderWithSize(
      <IVSkewChart
        data={[]}
        spotPrice={185}
        symbol="AAPL"
        expiry="2024-02-21"
      />
    );
    expect(screen.getByText('Implied Volatility Skew')).toBeInTheDocument();
  });

  it.skip('handles null IV values', () => {
    const dataWithNulls: IVSkewDataPoint[] = [
      { strike: 170, callIV: 0.22, putIV: null, midIV: null },
      { strike: 175, callIV: null, putIV: 0.26, midIV: null },
      { strike: 180, callIV: 0.18, putIV: 0.24, midIV: 0.21 },
    ];
    renderWithSize(
      <IVSkewChart
        data={dataWithNulls}
        spotPrice={185}
        symbol="AAPL"
        expiry="2024-02-21"
      />
    );
    expect(screen.getByText('Implied Volatility Skew')).toBeInTheDocument();
  });
});
