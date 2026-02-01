import { OptionContract, OptionsChainData } from '@/components/options/OptionsChainTable';

export interface IVSkewDataPoint {
  strike: number;
  callIV: number | null;
  putIV: number | null;
  midIV: number | null;
}

const SPOT_PRICE = 185;

const generateCalls = (): OptionContract[] => {
  const strikes = [160, 165, 170, 175, 180, 182, 184, 185, 186, 188, 190, 195, 200, 205, 210];
  return strikes.map((strike, idx) => {
    const itm = strike < SPOT_PRICE;
    const intrinsic = itm ? SPOT_PRICE - strike : 0;
    const timeValue = Math.max(0.5, (SPOT_PRICE - strike) * 0.1 + 2);
    const basePrice = intrinsic + timeValue;
    const iv = 0.15 + (strike - SPOT_PRICE) * 0.002 + Math.random() * 0.05;

    return {
      symbol: `AAPL${new Date().toISOString().slice(0, 10).replace(/-/g, '')}${strike}${strike < SPOT_PRICE ? 'C' : 'C'}`,
      strike,
      expiry: '2026-02-21',
      type: 'call' as const,
      bid: basePrice * 0.95 + Math.random() * 0.5,
      ask: basePrice * 1.05 + Math.random() * 0.5,
      last: basePrice + Math.random() * 0.3 - 0.15,
      change: (Math.random() - 0.5) * 2,
      changePercent: (Math.random() - 0.5) * 0.1,
      volume: Math.floor(Math.random() * 5000) + 100,
      openInterest: Math.floor(Math.random() * 10000) + 500,
      iv: Math.min(0.8, Math.max(0.1, iv)),
      delta: itm ? 0.7 + (SPOT_PRICE - strike) * 0.03 : Math.max(0.05, 0.5 - (strike - SPOT_PRICE) * 0.05),
      gamma: 0.02 + Math.random() * 0.02,
      theta: -0.05 - Math.random() * 0.03,
      vega: 0.1 + Math.random() * 0.05,
      rho: 0.02 + Math.random() * 0.02,
      intrinsicValue: intrinsic,
      timeValue: timeValue,
      inTheMoney: itm,
    };
  });
};

const generatePuts = (): OptionContract[] => {
  const strikes = [160, 165, 170, 175, 180, 182, 184, 185, 186, 188, 190, 195, 200, 205, 210];
  return strikes.map((strike) => {
    const itm = strike > SPOT_PRICE;
    const intrinsic = itm ? strike - SPOT_PRICE : 0;
    const timeValue = Math.max(0.5, (strike - SPOT_PRICE) * 0.1 + 2);
    const basePrice = intrinsic + timeValue;
    const iv = 0.18 + (SPOT_PRICE - strike) * 0.003 + Math.random() * 0.05;

    return {
      symbol: `AAPL${new Date().toISOString().slice(0, 10).replace(/-/g, '')}${strike}P`,
      strike,
      expiry: '2026-02-21',
      type: 'put' as const,
      bid: basePrice * 0.95 + Math.random() * 0.5,
      ask: basePrice * 1.05 + Math.random() * 0.5,
      last: basePrice + Math.random() * 0.3 - 0.15,
      change: (Math.random() - 0.5) * 2,
      changePercent: (Math.random() - 0.5) * 0.1,
      volume: Math.floor(Math.random() * 5000) + 100,
      openInterest: Math.floor(Math.random() * 10000) + 500,
      iv: Math.min(0.8, Math.max(0.1, iv)),
      delta: itm ? -(0.7 + (strike - SPOT_PRICE) * 0.03) : Math.max(-0.05, -0.5 + (strike - SPOT_PRICE) * 0.05),
      gamma: 0.02 + Math.random() * 0.02,
      theta: -0.05 - Math.random() * 0.03,
      vega: 0.1 + Math.random() * 0.05,
      rho: -0.02 - Math.random() * 0.02,
      intrinsicValue: intrinsic,
      timeValue: timeValue,
      inTheMoney: itm,
    };
  });
};

export const mockOptionsChainData: OptionsChainData = {
  symbol: 'AAPL',
  spotPrice: SPOT_PRICE,
  calls: generateCalls(),
  puts: generatePuts(),
  lastUpdated: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
};

export const mockIVSkewData: IVSkewDataPoint[] = (() => {
  const strikes = [160, 165, 170, 175, 180, 182, 184, 185, 186, 188, 190, 195, 200, 205, 210];
  return strikes.map(strike => {
    const distanceFromSpot = (strike - SPOT_PRICE) / SPOT_PRICE;
    const callIV = 0.20 + distanceFromSpot * 0.5 + (Math.random() - 0.5) * 0.03;
    const putIV = 0.25 - distanceFromSpot * 0.3 + (Math.random() - 0.5) * 0.03;

    return {
      strike,
      callIV: Math.min(0.6, Math.max(0.1, callIV)),
      putIV: Math.min(0.6, Math.max(0.1, putIV)),
      midIV: (Math.min(0.6, Math.max(0.1, callIV)) + Math.min(0.6, Math.max(0.1, putIV))) / 2,
    };
  });
})();

export const mockExpiryDates = [
  { date: '2026-02-07', label: 'Feb 7, 2026', daysToExpiry: 6 },
  { date: '2026-02-14', label: 'Feb 14, 2026', daysToExpiry: 13 },
  { date: '2026-02-21', label: 'Feb 21, 2026', daysToExpiry: 20 },
  { date: '2026-02-28', label: 'Feb 28, 2026', daysToExpiry: 27 },
  { date: '2026-03-07', label: 'Mar 7, 2026', daysToExpiry: 34 },
  { date: '2026-03-21', label: 'Mar 21, 2026', daysToExpiry: 48 },
  { date: '2026-04-18', label: 'Apr 18, 2026', daysToExpiry: 76 },
  { date: '2026-06-20', label: 'Jun 20, 2026', daysToExpiry: 139 },
  { date: '2026-12-19', label: 'Dec 19, 2026', daysToExpiry: 321 },
];
