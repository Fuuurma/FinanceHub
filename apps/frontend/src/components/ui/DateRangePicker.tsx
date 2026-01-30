'use client'

import { useState, useCallback } from 'react'
import { Calendar, ChevronLeft, ChevronRight, Clock } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Popover,
  PopoverContent,
  PopoverTrigger
} from '@/components/ui/popover'
import { cn, formatDate } from '@/lib/utils'

export type DateRangeValue = {
  from: Date | undefined
  to: Date | undefined
}

export type PresetRange = {
  label: string
  value: 'today' | 'yesterday' | 'last7days' | 'last30days' | 'last90days' | 'thisMonth' | 'lastMonth' | 'thisYear' | 'lastYear'
}

export const PRESET_RANGES: PresetRange[] = [
  { label: 'Today', value: 'today' },
  { label: 'Yesterday', value: 'yesterday' },
  { label: 'Last 7 days', value: 'last7days' },
  { label: 'Last 30 days', value: 'last30days' },
  { label: 'Last 90 days', value: 'last90days' },
  { label: 'This month', value: 'thisMonth' },
  { label: 'Last month', value: 'lastMonth' },
  { label: 'This year', value: 'thisYear' },
  { label: 'Last year', value: 'lastYear' }
]

interface DateRangePickerProps {
  value?: DateRangeValue
  onChange?: (value: DateRangeValue) => void
  className?: string
  placeholder?: string
  disabled?: boolean
  showTimePicker?: boolean
  minDate?: Date
  maxDate?: Date
}

function getPresetRange(preset: PresetRange['value']): DateRangeValue {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000)

  switch (preset) {
    case 'today':
      return { from: today, to: now }
    case 'yesterday':
      return { from: yesterday, to: today }
    case 'last7days':
      return { from: new Date(today.getTime() - 6 * 24 * 60 * 60 * 1000), to: now }
    case 'last30days':
      return { from: new Date(today.getTime() - 29 * 24 * 60 * 60 * 1000), to: now }
    case 'last90days':
      return { from: new Date(today.getTime() - 89 * 24 * 60 * 60 * 1000), to: now }
    case 'thisMonth':
      return { from: new Date(now.getFullYear(), now.getMonth(), 1), to: now }
    case 'lastMonth':
      return {
        from: new Date(now.getFullYear(), now.getMonth() - 1, 1),
        to: new Date(now.getFullYear(), now.getMonth(), 0)
      }
    case 'thisYear':
      return { from: new Date(now.getFullYear(), 0, 1), to: now }
    case 'lastYear':
      return { from: new Date(now.getFullYear() - 1, 0, 1), to: new Date(now.getFullYear() - 1, 11, 31) }
    default:
      return { from: undefined, to: undefined }
  }
}

function getCalendarDays(year: number, month: number): (number | null)[] {
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  const daysInMonth = lastDay.getDate()
  const startingDay = firstDay.getDay()

  const days: (number | null)[] = []

  for (let i = 0; i < startingDay; i++) {
    days.push(null)
  }

  for (let i = 1; i <= daysInMonth; i++) {
    days.push(i)
  }

  return days
}

export function DateRangePicker({
  value = { from: undefined, to: undefined },
  onChange,
  className,
  placeholder = 'Select date range',
  disabled = false,
  showTimePicker = false,
  minDate,
  maxDate
}: DateRangePickerProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [viewMonth, setViewMonth] = useState(new Date())
  const [selectingFrom, setSelectingFrom] = useState(true)
  const [tempFrom, setTempFrom] = useState<Date | undefined>(value.from)
  const [tempTo, setTempTo] = useState<Date | undefined>(value.to)

  const viewYear = viewMonth.getFullYear()
  const viewMonthNum = viewMonth.getMonth()
  const calendarDays = getCalendarDays(viewYear, viewMonthNum)
  const monthName = viewMonth.toLocaleString('default', { month: 'long' })

  const handleDateClick = useCallback((day: number | null) => {
    if (day === null) return

    const clickedDate = new Date(viewYear, viewMonthNum, day, 12, 0, 0)

    if (minDate && clickedDate < minDate) return
    if (maxDate && clickedDate > maxDate) return

    if (selectingFrom) {
      setTempFrom(clickedDate)
      setTempTo(undefined)
      setSelectingFrom(false)
    } else {
      if (tempFrom && clickedDate < tempFrom) {
        setTempFrom(clickedDate)
        setTempTo(clickedDate)
      } else {
        setTempTo(clickedDate)
        setSelectingFrom(true)
        onChange?.({ from: tempFrom, to: clickedDate })
        setIsOpen(false)
      }
    }
  }, [viewYear, viewMonthNum, selectingFrom, tempFrom, minDate, maxDate, onChange])

  const handlePresetSelect = useCallback((preset: PresetRange) => {
    const range = getPresetRange(preset.value)
    setTempFrom(range.from)
    setTempTo(range.to)
    onChange?.(range)
    setIsOpen(false)
  }, [onChange])

  const formatDateRange = () => {
    if (value.from && value.to) {
      const fromStr = formatDate(value.from)
      const toStr = formatDate(value.to)
      return `${fromStr} - ${toStr}`
    }
    if (value.from) {
      return `${formatDate(value.from)} - Select end date`
    }
    return placeholder
  }

  const isDateSelected = (day: number | null) => {
    if (day === null) return false
    const date = new Date(viewYear, viewMonthNum, day)
    const dateOnly = new Date(date.getFullYear(), date.getMonth(), date.getDate())

    if (tempFrom) {
      const fromOnly = new Date(tempFrom.getFullYear(), tempFrom.getMonth(), tempFrom.getDate())
      if (dateOnly.getTime() === fromOnly.getTime()) return true
    }

    if (tempTo) {
      const toOnly = new Date(tempTo.getFullYear(), tempTo.getMonth(), tempTo.getDate())
      if (dateOnly.getTime() === toOnly.getTime()) return true
    }

    if (tempFrom && tempTo) {
      const fromOnly = new Date(tempFrom.getFullYear(), tempFrom.getMonth(), tempFrom.getDate())
      const toOnly = new Date(tempTo.getFullYear(), tempTo.getMonth(), tempTo.getDate())
      return dateOnly > fromOnly && dateOnly < toOnly
    }

    return false
  }

  const isDateInRange = (day: number | null) => {
    if (day === null || !tempFrom || !tempTo) return false
    const date = new Date(viewYear, viewMonthNum, day)
    const dateOnly = new Date(date.getFullYear(), date.getMonth(), date.getDate())
    const fromOnly = new Date(tempFrom.getFullYear(), tempFrom.getMonth(), tempFrom.getDate())
    const toOnly = new Date(tempTo.getFullYear(), tempTo.getMonth(), tempTo.getDate())
    return dateOnly >= fromOnly && dateOnly <= toOnly
  }

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          disabled={disabled}
          className={cn(
            'w-full justify-start text-left font-normal gap-2',
            !value.from && !value.to && 'text-muted-foreground',
            className
          )}
        >
          <Calendar className="h-4 w-4" />
          {formatDateRange()}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-4" align="start">
        <div className="flex gap-4">
          <div>
            <div className="flex items-center justify-between mb-4">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setViewMonth(new Date(viewYear, viewMonthNum - 1, 1))}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <span className="font-medium">{monthName} {viewYear}</span>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setViewMonth(new Date(viewYear, viewMonthNum + 1, 1))}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>

            <div className="grid grid-cols-7 gap-1 text-center text-xs mb-2">
              {['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'].map(day => (
                <div key={day} className="p-1 text-muted-foreground">{day}</div>
              ))}
            </div>

            <div className="grid grid-cols-7 gap-1">
              {calendarDays.map((day, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => handleDateClick(day)}
                  disabled={day === null}
                  className={cn(
                    'w-8 h-8 rounded-md text-sm transition-colors',
                    day === null && 'invisible',
                    day !== null && isDateSelected(day) && 'bg-primary text-primary-foreground',
                    day !== null && !isDateSelected(day) && isDateInRange(day) && 'bg-primary/20',
                    day !== null && !isDateSelected(day) && !isDateInRange(day) && 'hover:bg-muted',
                    day !== null && (minDate || maxDate) && 'opacity-50'
                  )}
                >
                  {day}
                </button>
              ))}
            </div>
          </div>

          <div className="border-l pl-4 space-y-4">
            <div>
              <p className="text-sm font-medium mb-2">Quick select</p>
              <div className="space-y-1">
                {PRESET_RANGES.map(preset => (
                  <button
                    key={preset.value}
                    type="button"
                    onClick={() => handlePresetSelect(preset)}
                    className={cn(
                      'w-full text-left px-3 py-1.5 text-sm rounded-md transition-colors',
                      'hover:bg-muted'
                    )}
                  >
                    {preset.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  )
}

export default DateRangePicker
