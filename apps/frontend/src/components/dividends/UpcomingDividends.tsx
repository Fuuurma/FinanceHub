'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { cn } from '@/lib/utils';
import { 
  Calendar, 
  Bell, 
  BellOff,
  DollarSign,
  Clock,
  AlertTriangle,
  RefreshCw
} from 'lucide-react';
import { DividendPayment, DividendProjection } from './types';

interface UpcomingDividendsProps {
  portfolioId: string;
  days?: number;
  className?: string;
}

const formatCurrency = (value: number) => 
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
};

const getDaysUntil = (dateStr: string) => {
  const diff = new Date(dateStr).getTime() - Date.now();
  return Math.ceil(diff / (1000 * 60 * 60 * 24));
};

const FrequencyBadge = ({ frequency }: { frequency: string }) => {
  const colors: Record<string, string> = {
    monthly: 'bg-blue-100 text-blue-700',
    quarterly: 'bg-green-100 text-green-700',
    'semi-annual': 'bg-purple-100 text-purple-700',
    annual: 'bg-orange-100 text-orange-700',
    irregular: 'bg-gray-100 text-gray-700',
  };

  return (
    <Badge variant="outline" className={cn('text-xs', colors[frequency] || colors.irregular)}>
      {frequency}
    </Badge>
  );
};

const ProbabilityBadge = ({ probability }: { probability: string }) => {
  const colors: Record<string, string> = {
    confirmed: 'bg-green-500 text-white',
    estimated: 'bg-yellow-500 text-white',
    projected: 'bg-gray-500 text-white',
  };

  return (
    <Badge className={cn('text-xs', colors[probability] || colors.projected)}>
      {probability}
    </Badge>
  );
};

export function UpcomingDividends({ 
  portfolioId, 
  days = 30,
  className 
}: UpcomingDividendsProps) {
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'upcoming' | 'projected'>('upcoming');
  const [payments, setPayments] = useState<DividendPayment[]>([]);
  const [projections, setProjections] = useState<DividendProjection[]>([]);
  const [alerts, setAlerts] = useState<Set<string>>(new Set());

  const fetchData = async () => {
    setLoading(true);
    try {
      const { dividendApi } = await import('./api');
      const [paymentsRes, projectionsRes] = await Promise.all([
        dividendApi.getUpcoming(days),
        dividendApi.getProjections(3),
      ]);
      setPayments(paymentsRes);
      setProjections(projectionsRes);
    } catch {
      setPayments(mockPayments);
      setProjections(mockProjections);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [portfolioId, days]);

  const toggleAlert = (id: string) => {
    setAlerts(prev => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const renderPaymentList = (
    items: Array<DividendPayment | DividendProjection>,
    isProjection: boolean
  ) => {
    if (items.length === 0) {
      return (
        <div className="text-center py-12 text-muted-foreground">
          <Calendar className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p>No {isProjection ? 'projected' : ''} dividends</p>
        </div>
      );
    }

    return (
      <div className="space-y-3">
        {items.map((item, idx) => {
          const payment = item as DividendPayment;
          const projection = item as DividendProjection;
          const date = isProjection ? projection.expectedPaymentDate : payment.paymentDate;
          const daysUntil = getDaysUntil(date);

          return (
            <div
              key={isProjection ? projection.id : payment.id}
              className={cn(
                'p-4 border rounded-lg hover:bg-muted/50 transition-colors',
                daysUntil <= 7 && 'border-yellow-500/50 bg-yellow-500/5'
              )}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                    <DollarSign className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold">{payment.symbol}</span>
                      {isProjection ? (
                        <ProbabilityBadge probability={projection.probability} />
                      ) : (
                        <FrequencyBadge frequency={payment.frequency} />
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {payment.companyName || payment.symbol}
                    </p>
                  </div>
                </div>

                <div className="text-right">
                  <p className="font-semibold">{formatCurrency(
                    isProjection ? projection.projectedAmount : payment.amount
                  )}</p>
                  <p className="text-sm text-muted-foreground flex items-center gap-1 justify-end">
                    <Clock className="h-3 w-3" />
                    {formatDate(date)}
                    {daysUntil > 0 && (
                      <span className={cn(
                        'text-xs',
                        daysUntil <= 3 ? 'text-red-600' : daysUntil <= 7 ? 'text-yellow-600' : ''
                      )}>
                        ({daysUntil}d)
                      </span>
                    )}
                  </p>
                </div>
              </div>

              <div className="flex items-center justify-between mt-3 pt-3 border-t">
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <span>Ex-date: {formatDate(
                    isProjection ? projection.expectedExDate : payment.exDividendDate
                  )}</span>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => toggleAlert(isProjection ? projection.id : payment.id)}
                  className="h-8 px-2"
                >
                  {alerts.has(isProjection ? projection.id : payment.id) ? (
                    <>
                      <Bell className="h-4 w-4 mr-1 text-primary" />
                      Alerts on
                    </>
                  ) : (
                    <>
                      <BellOff className="h-4 w-4 mr-1" />
                      Alert
                    </>
                  )}
                </Button>
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <Card className={cn('w-full', className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Upcoming Dividends
            </CardTitle>
            <CardDescription>Next {days} days</CardDescription>
          </div>
          <Button variant="outline" size="sm" onClick={fetchData}>
            <RefreshCw className="h-4 w-4 mr-1" />
            Refresh
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3].map(i => (
              <Skeleton key={i} className="h-24 w-full" />
            ))}
          </div>
        ) : (
          <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as any)}>
            <TabsList className="w-full">
              <TabsTrigger value="upcoming" className="flex-1">
                Confirmed ({payments.length})
              </TabsTrigger>
              <TabsTrigger value="projected" className="flex-1">
                Projected ({projections.length})
              </TabsTrigger>
            </TabsList>

            <TabsContent value="upcoming" className="mt-4">
              {renderPaymentList(payments, false)}
            </TabsContent>

            <TabsContent value="projected" className="mt-4">
              {renderPaymentList(projections, true)}
            </TabsContent>
          </Tabs>
        )}
      </CardContent>
    </Card>
  );
}

const mockPayments: DividendPayment[] = [
  {
    id: '1', symbol: 'AAPL', companyName: 'Apple Inc.', amount: 0.24, currency: 'USD',
    exDividendDate: '2026-02-10', recordDate: '2026-02-12', paymentDate: '2026-02-14',
    frequency: 'quarterly', positionId: 'pos-1',
  },
  {
    id: '2', symbol: 'MSFT', companyName: 'Microsoft Corporation', amount: 0.75, currency: 'USD',
    exDividendDate: '2026-02-18', recordDate: '2026-02-20', paymentDate: '2026-02-25',
    frequency: 'quarterly', positionId: 'pos-2',
  },
];

const mockProjections: DividendProjection[] = [
  {
    id: 'p1', symbol: 'VZ', companyName: 'Verizon', projectedAmount: 0.677,
    expectedExDate: '2026-02-28', expectedPaymentDate: '2026-03-05',
    probability: 'confirmed', positionId: 'pos-4',
  },
];
