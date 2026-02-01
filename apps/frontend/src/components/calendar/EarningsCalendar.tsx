import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useApi } from '@/hooks/useApi';

interface EarningsEvent {
  id: number;
  asset_id: number;
  symbol: string;
  company_name: string;
  date: string;
  time: string;
  quarter: string;
  estimated_eps: number | null;
}

interface EarningsCalendarProps {
  daysAhead?: number;
  portfolioOnly?: boolean;
}

export function EarningsCalendar({ daysAhead = 30, portfolioOnly = false }: EarningsCalendarProps) {
  const [events, setEvents] = useState<EarningsEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDays, setSelectedDays] = useState(daysAhead);
  const api = useApi();

  const fetchEvents = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/calendar/earnings?days_ahead=${selectedDays}&portfolio_only=${portfolioOnly}`);
      const data = await response.json();
      setEvents(data as EarningsEvent[]);
    } catch (error) {
      console.error('Error fetching earnings calendar:', error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchEvents();
  }, [selectedDays, portfolioOnly]);

  const getTimeBadge = (time: string) => {
    switch (time.toLowerCase()) {
      case 'pre-market':
        return <Badge variant="secondary">Pre-Market</Badge>;
      case 'after-market':
        return <Badge variant="destructive">After Market</Badge>;
      default:
        return <Badge>During Market</Badge>;
    }
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Earnings Calendar</span>
            <div className="flex gap-2">
              {[7, 14, 30, 60, 90].map((days) => (
                <button
                  key={days}
                  onClick={() => setSelectedDays(days)}
                  className={`px-3 py-1 text-sm rounded ${
                    selectedDays === days
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted hover:bg-muted/80'
                  }`}
                >
                  {days}d
                </button>
              ))}
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-3">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="h-16 bg-muted animate-pulse rounded" />
              ))}
            </div>
          ) : events.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No earnings events in the next {selectedDays} days
            </div>
          ) : (
            <div className="space-y-3">
              {events.map((event) => (
                <div
                  key={event.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                      <span className="text-lg font-bold">{event.symbol.charAt(0)}</span>
                    </div>
                    <div>
                      <div className="font-medium">{event.symbol}</div>
                      <div className="text-sm text-muted-foreground">{event.company_name}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <div className="font-medium">{event.quarter}</div>
                      <div className="text-sm text-muted-foreground">
                        {new Date(event.date).toLocaleDateString()}
                      </div>
                    </div>
                    {getTimeBadge(event.time)}
                    {event.estimated_eps && (
                      <div className="text-right w-24">
                        <div className="text-sm text-muted-foreground">Est. EPS</div>
                        <div className="font-medium">${event.estimated_eps.toFixed(2)}</div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
