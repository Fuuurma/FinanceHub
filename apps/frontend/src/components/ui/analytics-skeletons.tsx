'use client'

import { Skeleton } from '@/components/ui/skeleton'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { cn } from '@/lib/utils'

export function ChartSkeleton({ className }: { className?: string }) {
  return (
    <Card className={cn('h-[400px]', className)}>
      <CardHeader className="pb-2">
        <Skeleton className="h-6 w-48" />
        <Skeleton className="h-4 w-32" />
      </CardHeader>
      <CardContent>
        <div className="h-[300px] w-full space-y-4">
          <Skeleton className="h-full w-full rounded" />
        </div>
      </CardContent>
    </Card>
  )
}

export function KPICardsSkeleton({ count = 4 }: { count?: number }) {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {Array.from({ length: count }).map((_, i) => (
        <Card key={i}>
          <CardHeader className="pb-2">
            <Skeleton className="h-4 w-24" />
          </CardHeader>
          <CardContent>
            <Skeleton className="h-8 w-32" />
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

export function AnalyticsPageSkeleton() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-4 w-64" />
        </div>
        <div className="flex gap-2">
          <Skeleton className="h-10 w-24" />
          <Skeleton className="h-10 w-24" />
        </div>
      </div>

      <div className="flex gap-2 flex-wrap">
        {Array.from({ length: 8 }).map((_, i) => (
          <Skeleton key={i} className="h-9 w-12" />
        ))}
      </div>

      <KPICardsSkeleton count={4} />

      <div className="grid gap-6 md:grid-cols-2">
        <ChartSkeleton />
        <ChartSkeleton />
      </div>

      <ChartSkeleton className="h-[300px]" />
    </div>
  )
}

export function TableRowSkeleton({ columns = 4 }: { columns?: number }) {
  return (
    <div className="flex gap-4 py-3 border-b last:border-0">
      {Array.from({ length: columns }).map((_, i) => (
        <Skeleton key={i} className="h-4" style={{ width: `${100 / columns}%` }} />
      ))}
    </div>
  )
}

export function TableSkeleton({ rows = 10, columns = 4 }: { rows?: number; columns?: number }) {
  return (
    <div className="space-y-1">
      <div className="flex gap-4 py-2 border-b">
        {Array.from({ length: columns }).map((_, i) => (
          <Skeleton key={i} className="h-4 w-20" />
        ))}
      </div>
      {Array.from({ length: rows }).map((_, i) => (
        <TableRowSkeleton key={i} columns={columns} />
      ))}
    </div>
  )
}

export function ListSkeleton({ items = 5 }: { items?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: items }).map((_, i) => (
        <div key={i} className="flex items-center gap-3">
          <Skeleton className="h-10 w-10 rounded-full" />
          <div className="space-y-2 flex-1">
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-3 w-1/2" />
          </div>
        </div>
      ))}
    </div>
  )
}

export function FullPageSkeleton() {
  return (
    <div className="container mx-auto py-6 space-y-6">
      <Skeleton className="h-10 w-64" />
      <Skeleton className="h-6 w-96" />
      <AnalyticsPageSkeleton />
    </div>
  )
}
