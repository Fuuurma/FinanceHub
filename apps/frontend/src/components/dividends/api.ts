import { DividendPayment, DividendProjection, DividendSummary } from './types';

export const dividendApi = {
  getSummary: async (_portfolioId: string): Promise<DividendSummary> => {
    return {
      totalDividendsYTD: 1247.50,
      totalDividendsLast12m: 3842.30,
      projectedAnnualDividends: 4120.00,
      dividendYield: 0.0325,
      monthlyDividendIncome: 343.33,
      averageYield: 0.0452,
      ytdGrowth: 0.085,
      lastUpdated: new Date().toLocaleString(),
    };
  },
  
  getCalendar: async (_startDate: string, _endDate: string) => {
    return [] as Array<{ date: string; type: string; symbol: string; companyName: string; amount: number; currency: string }>;
  },
  
  getUpcoming: async (_days: number = 30): Promise<DividendPayment[]> => {
    return [
      {
        id: '1',
        symbol: 'AAPL',
        companyName: 'Apple Inc.',
        amount: 0.24,
        currency: 'USD',
        exDividendDate: '2026-02-10',
        recordDate: '2026-02-12',
        paymentDate: '2026-02-14',
        frequency: 'quarterly',
        positionId: 'pos-1',
      },
      {
        id: '2',
        symbol: 'MSFT',
        companyName: 'Microsoft Corporation',
        amount: 0.75,
        currency: 'USD',
        exDividendDate: '2026-02-18',
        recordDate: '2026-02-20',
        paymentDate: '2026-02-25',
        frequency: 'quarterly',
        positionId: 'pos-2',
      },
    ];
  },
  
  getProjections: async (_months: number = 12): Promise<DividendProjection[]> => {
    return [
      {
        id: 'p1',
        symbol: 'VZ',
        companyName: 'Verizon',
        projectedAmount: 0.677,
        expectedExDate: '2026-02-28',
        expectedPaymentDate: '2026-03-05',
        probability: 'confirmed',
        positionId: 'pos-4',
      },
    ];
  },
  
  getHistory: async (_years: number = 5): Promise<DividendHistoryPoint[]> => {
    return Array.from({ length: 60 }, (_, i) => {
      const date = new Date();
      date.setMonth(date.getMonth() - (59 - i));
      return {
        date: date.toISOString(),
        amount: 50 + Math.random() * 150 + Math.sin(i / 6) * 30,
        symbol: i % 3 === 0 ? 'AAPL' : i % 3 === 1 ? 'MSFT' : 'JNJ',
      };
    });
  },
  
  getPositionHistory: async (_positionId: string, _years: number = 5) => {
    return {
      data: Array.from({ length: 60 }, (_, i) => {
        const date = new Date();
        date.setMonth(date.getMonth() - (59 - i));
        return {
          date: date.toISOString(),
          amount: 50 + Math.random() * 150,
          symbol: 'AAPL',
        };
      }),
      summary: { totalReceived: 2450.00, averagePayment: 125.50, growthRate: 7.2, paymentCount: 60 },
    };
  },
};

interface DividendHistoryPoint {
  date: string;
  amount: number;
  symbol: string;
}
