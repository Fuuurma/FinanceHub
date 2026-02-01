export interface DividendSummary {
  totalDividendsYTD: number;
  totalDividendsLast12m: number;
  projectedAnnualDividends: number;
  dividendYield: number;
  monthlyDividendIncome: number;
  averageYield: number;
  ytdGrowth: number;
  lastUpdated: string;
}

export interface DividendPayment {
  id: string;
  symbol: string;
  companyName: string;
  amount: number;
  currency: string;
  exDividendDate: string;
  recordDate: string;
  paymentDate: string;
  frequency: 'monthly' | 'quarterly' | 'semi-annual' | 'annual' | 'irregular';
  positionId: string;
}

export interface DividendProjection {
  id: string;
  symbol: string;
  companyName: string;
  projectedAmount: number;
  expectedExDate: string;
  expectedPaymentDate: string;
  probability: 'confirmed' | 'estimated' | 'projected';
  positionId: string;
}

export interface DividendCalendarEvent {
  date: string;
  type: 'ex-dividend' | 'record' | 'payment';
  symbol: string;
  companyName: string;
  amount: number;
  currency: string;
}

export interface DividendHistoryPoint {
  date: string;
  amount: number;
  symbol: string;
}

export interface DividendAlert {
  id: string;
  positionId: string;
  alertType: 'ex-date' | 'payment' | 'yield-threshold';
  daysBefore: number;
  enabled: boolean;
}
