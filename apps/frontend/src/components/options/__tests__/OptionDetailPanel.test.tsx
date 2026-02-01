import React from 'react';
import { render, screen } from '@testing-library/react';
import { OptionDetailPanel } from '../OptionDetailPanel';

const mockContract = {
  symbol: 'AAPL240217C00185000',
  strike: 185,
  expiry: '2024-02-17',
  type: 'call' as const,
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

describe('OptionDetailPanel', () => {
  it('renders without crashing', () => {
    render(
      <OptionDetailPanel
        contract={mockContract}
        spotPrice={187.50}
      />
    );
    expect(screen.getByText('AAPL240217C00185000')).toBeInTheDocument();
  });

  it('displays bid and ask prices', () => {
    render(
      <OptionDetailPanel
        contract={mockContract}
        spotPrice={187.50}
      />
    );
    expect(screen.getByText('Bid / Ask')).toBeInTheDocument();
  });

  it('shows put option correctly', () => {
    const putContract = {
      ...mockContract,
      type: 'put' as const,
      inTheMoney: false,
      delta: -0.45,
    };
    render(
      <OptionDetailPanel
        contract={putContract}
        spotPrice={187.50}
      />
    );
    expect(screen.getByText('PUT')).toBeInTheDocument();
  });

  it('shows probability analysis section', () => {
    render(
      <OptionDetailPanel
        contract={mockContract}
        spotPrice={187.50}
      />
    );
    expect(screen.getByText('Probability Analysis')).toBeInTheDocument();
  });

  it('displays all greeks labels', () => {
    render(
      <OptionDetailPanel
        contract={mockContract}
        spotPrice={187.50}
      />
    );
    expect(screen.getByText('Delta')).toBeInTheDocument();
    expect(screen.getByText('Gamma')).toBeInTheDocument();
    expect(screen.getByText('Theta')).toBeInTheDocument();
    expect(screen.getByText('Vega')).toBeInTheDocument();
    expect(screen.getByText('Rho')).toBeInTheDocument();
  });
});
