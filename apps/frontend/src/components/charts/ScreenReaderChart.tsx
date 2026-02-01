'use client'

import { cn } from '@/lib/utils'

interface ScreenReaderData {
  label: string
  value: string | number
  description?: string
}

interface ScreenReaderTableProps {
  title: string
  description?: string
  data: ScreenReaderData[][]
  caption?: string
  className?: string
}

export function ScreenReaderTable({
  title,
  description,
  data,
  caption,
  className,
}: ScreenReaderTableProps) {
  if (!data || data.length === 0) {
    return null
  }

  return (
    <div
      role="region"
      aria-label={title}
      aria-description={description}
      className={cn('sr-only', className)}
      tabIndex={-1}
    >
      <table>
        {caption && <caption className="sr-only">{caption}</caption>}
        <thead>
          {data[0] && (
            <tr>
              {data[0].map((cell, index) => (
                <th key={index} scope="col">
                  {cell.label}
                </th>
              ))}
            </tr>
          )}
        </thead>
        <tbody>
          {data.slice(1).map((row, rowIndex) => (
            <tr key={rowIndex}>
              {row.map((cell, cellIndex) => (
                <td key={cellIndex}>
                  {cell.description ? (
                    <span aria-label={`${cell.label}, ${cell.description}, ${cell.value}`}>
                      {cell.value}
                    </span>
                  ) : (
                    cell.value
                  )}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

interface ScreenReaderSummaryProps {
  title: string
  summary: {
    label: string
    value: string | number
  }[]
}

export function ScreenReaderSummary({ title, summary }: ScreenReaderSummaryProps) {
  if (!summary || summary.length === 0) {
    return null
  }

  return (
    <div role="region" aria-label={title} className="sr-only" tabIndex={-1}>
      <h3>{title}</h3>
      <ul>
        {summary.map((item, index) => (
          <li key={index}>
            {item.label}: {item.value}
          </li>
        ))}
      </ul>
    </div>
  )
}

interface ChartScreenReaderProps {
  chartTitle: string
  chartDescription: string
  currentValue?: string | number
  change?: string | number
  changePercent?: string | number
  timeframe?: string
  data?: ScreenReaderData[][]
  summary?: {
    label: string
    value: string | number
  }[]
}

export function ChartScreenReader({
  chartTitle,
  chartDescription,
  currentValue,
  change,
  changePercent,
  timeframe,
  data,
  summary,
}: ChartScreenReaderProps) {
  const parts: string[] = []

  if (currentValue !== undefined) {
    parts.push(`Current value: ${currentValue}`)
  }
  if (change !== undefined) {
    parts.push(`Change: ${change}`)
  }
  if (changePercent !== undefined) {
    parts.push(`Change percent: ${changePercent}`)
  }
  if (timeframe) {
    parts.push(`Timeframe: ${timeframe}`)
  }

  return (
    <div className="sr-only">
      <h2>{chartTitle}</h2>
      <p>{chartDescription}</p>
      {parts.length > 0 && (
        <section aria-label="Current values">
          <ul>
            {parts.map((part, index) => (
              <li key={index}>{part}</li>
            ))}
          </ul>
        </section>
      )}
      {summary && <ScreenReaderSummary title="Summary statistics" summary={summary} />}
      {data && <ScreenReaderTable title="Chart data" data={data} />}
    </div>
  )
}

export default ScreenReaderTable
