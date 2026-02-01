'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { cn } from '@/lib/utils';
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon, DollarSign } from 'lucide-react';
import { DividendCalendarEvent } from './types';

interface DividendCalendarProps {
  portfolioId: string;
  startDate?: string;
  endDate?: string;
  className?: string;
}

const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const MONTHS = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

const formatCurrency = (value: number) =>
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value);

export function DividendCalendar({
  portfolioId,
  startDate: initialStart,
  endDate: initialEnd,
  className,
}: DividendCalendarProps) {
  const [loading, setLoading] = useState(true);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [events, setEvents] = useState<DividendCalendarEvent[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<DividendCalendarEvent | null>(null);
  const [viewYear, setViewYear] = useState(true);

  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  const fetchEvents = async () => {
    setLoading(true);
    try {
      const start = new Date(year, month, 1).toISOString();
      const end = new Date(year, month + 1, 0).toISOString();
      
      const response = await fetch(
        `/api/dividends/calendar?portfolio_id=${portfolioId}&start_date=${start}&end_date=${end}`
      );
      
      if (response.ok) {
        setEvents(await response.json());
      } else {
        setEvents(mockEvents);
      }
    } catch {
      setEvents(mockEvents);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, [portfolioId, year, month]);

  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const firstDayOfMonth = new Date(year, month, 1).getDay();

  const prevMonth = () => {
    setCurrentDate(new Date(year, month - 1, 1));
  };

  const nextMonth = () => {
    setCurrentDate(new Date(year, month + 1, 1));
  };

  const goToToday = () => {
    setCurrentDate(new Date());
  };

  const getEventsForDay = (day: number) => {
    const dateStr = new Date(year, month, day).toISOString().split('T')[0];
    return events.filter(e => e.date === dateStr);
  };

  const calendarDays = useMemo(() => {
    const days: (number | null)[] = [];
    
    for (let i = 0; i < firstDayOfMonth; i++) {
      days.push(null);
    }
    
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(day);
    }
    
    while (days.length % 7 !== 0) {
      days.push(null);
    }
    
    return days;
  }, [firstDayOfMonth, daysInMonth]);

  const today = new Date();
  const isToday = (day: number | null) => {
    if (!day) return false;
    return (
      year === today.getFullYear() &&
      month === today.getMonth() &&
      day === today.getDate()
    );
  };

  const monthlyTotal = useMemo(() => {
    return events.reduce((sum, e) => sum + e.amount, 0);
  }, [events]);

  const yearlyData = useMemo(() => {
    const byMonth: Record<number, number> = {};
    events.forEach(e => {
      const eventMonth = new Date(e.date).getMonth();
      byMonth[eventMonth] = (byMonth[eventMonth] || 0) + e.amount;
    });
    return byMonth;
  }, [events]);

  if (loading) {
    return (
      <Card className={cn('w-full', className)}>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-[400px] w-full" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={cn('w-full', className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg flex items-center gap-2">
              <CalendarIcon className="h-5 w-5" />
              Dividend Calendar
            </CardTitle>
            <CardDescription>
              {monthlyTotal > 0 && (
                <span className="text-primary font-semibold">
                  {formatCurrency(monthlyTotal)} this month
                </span>
              )}
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={goToToday}>
              Today
            </Button>
            <div className="flex items-center gap-1">
              <Button variant="ghost" size="icon" onClick={prevMonth}>
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <span className="w-32 text-center font-semibold">
                {MONTHS[month]} {year}
              </span>
              <Button variant="ghost" size="icon" onClick={nextMonth}>
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-7 gap-1">
          {DAYS.map(day => (
            <div
              key={day}
              className="text-center text-xs font-medium text-muted-foreground py-2"
            >
              {day}
            </div>
          ))}

          {calendarDays.map((day, idx) => {
            const dayEvents = day ? getEventsForDay(day) : [];
            const hasEvents = dayEvents.length > 0;
            const isTodayDate = isToday(day);

            return (
              <div
                key={idx}
                className={cn(
                  'min-h-[80px] p-1 border rounded-lg relative',
                  day ? 'bg-background' : 'bg-muted/20',
                  isTodayDate && 'ring-2 ring-primary',
                  hasEvents && 'hover:bg-muted/50 transition-colors cursor-pointer',
                  !day && 'pointer-events-none'
                )}
                onClick={() => day && dayEvents.length > 0 && setSelectedEvent(dayEvents[0])}
              >
                {day && (
                  <>
                    <span
                      className={cn(
                        'text-xs font-medium',
                        isTodayDate && 'bg-primary text-primary-foreground px-1.5 py-0.5 rounded-full'
                      )}
                    >
                      {day}
                    </span>
                    {hasEvents && (
                      <div className="mt-1 space-y-0.5">
                        {dayEvents.slice(0, 2).map((event, eIdx) => (
                          <div
                            key={eIdx}
                            className={cn(
                              'text-[10px] px-1 py-0.5 rounded truncate',
                              event.type === 'ex-dividend' && 'bg-yellow-100 text-yellow-800',
                              event.type === 'record' && 'bg-blue-100 text-blue-800',
                              event.type === 'payment' && 'bg-green-100 text-green-800'
                            )}
                          >
                            {event.symbol} {formatCurrency(event.amount)}
                          </div>
                        ))}
                        {dayEvents.length > 2 && (
                          <div className="text-[10px] text-muted-foreground text-center">
                            +{dayEvents.length - 2} more
                          </div>
                        )}
                      </div>
                    )}
                  </>
                )}
              </div>
            );
          })}
        </div>

        {selectedEvent && (
          <div className="mt-4 p-4 border rounded-lg bg-muted/30">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-semibold">{selectedEvent.companyName}</h4>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSelectedEvent(null)}
              >
                ×
              </Button>
            </div>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <p className="text-muted-foreground">Symbol</p>
                <p className="font-medium">{selectedEvent.symbol}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Amount</p>
                <p className="font-medium">{formatCurrency(selectedEvent.amount)}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Date</p>
                <p className="font-medium">
                  {new Date(selectedEvent.date).toLocaleDateString()}
                </p>
              </div>
              <div>
                <p className="text-muted-foreground">Type</p>
                <Badge variant="outline" className="mt-1">
                  {selectedEvent.type.replace('-', ' ')}
                </Badge>
              </div>
            </div>
          </div>
        )}

        <div className="mt-4 flex items-center justify-between text-xs text-muted-foreground">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded bg-yellow-100" />
              <span>Ex-Dividend</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded bg-blue-100" />
              <span>Record Date</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 rounded bg-green-100" />
              <span>Payment</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span>Monthly Total:</span>
            <span className="font-semibold text-primary">{formatCurrency(monthlyTotal)}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

const mockEvents: DividendCalendarEvent[] = [
  { date: '2026-02-14', type: 'payment', symbol: 'AAPL', companyName: 'Apple Inc.', amount: 0.24, currency: 'USD' },
  { date: '2026-02-10', type: 'ex-dividend', symbol: 'AAPL', companyName: 'Apple Inc.', amount: 0.24, currency: 'USD' },
  { date: '2026-02-25', type: 'payment', symbol: 'MSFT', companyName: 'Microsoft', amount: 0.75, currency: 'USD' },
  { date: '2026-02-14', type: 'payment', symbol: 'JNJ', companyName: 'Johnson & Johnson', amount: 1.24, currency: 'USD' },
  { date: '2026-03-01', type: 'payment', symbol: 'VZ', companyName: 'Verizon', amount: 0.677, currency: 'USD' },
  { date: '2026-02-28', type: 'ex-dividend', symbol: 'VZ', companyName: 'Verizon', amount: 0.677, currency: 'USD' },
];
