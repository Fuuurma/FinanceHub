/**
 * Formatters
 * Utility functions for formatting data
 */

export function formatPrice(value: number | string | undefined | null, currency: string = 'USD'): string {
  if (value === undefined || value === null) return '--'
  
  const numValue = typeof value === 'string' ? parseFloat(value) : value
  
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(numValue)
}

export function formatCurrency(value: number | string | undefined | null, decimals: number = 2): string {
  if (value === undefined || value === null) return '--'
  
  const numValue = typeof value === 'string' ? parseFloat(value) : value
  
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(numValue)
}

export function formatNumber(value: number | string | undefined | null): string {
  if (value === undefined || value === null) return '--'
  
  const numValue = typeof value === 'string' ? parseFloat(value) : value
  
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(numValue)
}

export function formatPercent(value: number | string | undefined | null, showSign: boolean = true): string {
  if (value === undefined || value === null) return '--'
  
  const numValue = typeof value === 'string' ? parseFloat(value) : value
  const sign = numValue > 0 && showSign ? '+' : ''
  
  return `${sign}${numValue.toFixed(2)}%`
}

export function formatVolume(value: number | string | undefined | null): string {
  if (value === undefined || value === null) return '--'
  
  const numValue = typeof value === 'string' ? parseFloat(value) : value
  
  if (numValue >= 1e9) {
    return `${(numValue / 1e9).toFixed(2)}B`
  }
  if (numValue >= 1e6) {
    return `${(numValue / 1e6).toFixed(2)}M`
  }
  if (numValue >= 1e3) {
    return `${(numValue / 1e3).toFixed(2)}K`
  }
  
  return numValue.toString()
}

export function formatMarketCap(value: number | string | undefined | null): string {
  if (value === undefined || value === null) return '--'
  
  const numValue = typeof value === 'string' ? parseFloat(value) : value
  
  if (numValue >= 1e12) {
    return `$${(numValue / 1e12).toFixed(2)}T`
  }
  if (numValue >= 1e9) {
    return `$${(numValue / 1e9).toFixed(2)}B`
  }
  if (numValue >= 1e6) {
    return `$${(numValue / 1e6).toFixed(2)}M`
  }
  if (numValue >= 1e3) {
    return `$${(numValue / 1e3).toFixed(2)}K`
  }
  
  return `$${numValue.toFixed(2)}`
}

export function formatDate(date: Date | string | undefined | null, format: 'short' | 'long' | 'time' = 'short'): string {
  if (!date) return '--'
  
  const dateObj = typeof date === 'string' ? new Date(date) : date
  
  if (format === 'time') {
    return new Intl.DateTimeFormat('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    }).format(dateObj)
  }
  
  if (format === 'long') {
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(dateObj)
  }
  
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(dateObj)
}

export function formatDuration(ms: number): string {
  const seconds = Math.floor(ms / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  
  if (days > 0) {
    return `${days}d ${hours % 24}h`
  }
  if (hours > 0) {
    return `${hours}h ${minutes % 60}m`
  }
  if (minutes > 0) {
    return `${minutes}m ${seconds % 60}s`
  }
  
  return `${seconds}s`
}
