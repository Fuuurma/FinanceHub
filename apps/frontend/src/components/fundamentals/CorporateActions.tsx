'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Scissors,
  RefreshCw,
  Download,
  FileSpreadsheet,
  FileJson,
  ArrowRightLeft,
  Building2,
  Scale,
  Calendar,
} from 'lucide-react'
import { cn, formatDate } from '@/lib/utils'
import { useDownloadFile } from '@/hooks/useDownload'

interface CorporateActionsProps {
  symbol?: string
  className?: string
}

interface CorporateActionData {
  id: string
  date: string
  type: 'split' | 'reverse_split' | 'merger' | 'spin_off' | 'tender' | 'rights' | 'bonus'
  description: string
  ratio?: string
  effectiveDate?: string
  recordDate?: string
  terms?: string
  targetCompany?: string
}

const ACTION_LABELS: Record<string, { label: string; icon: typeof Scissors; color: string }> = {
  split: { label: 'Stock Split', icon: Scissors, color: 'bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-400' },
  reverse_split: { label: 'Reverse Split', icon: ArrowRightLeft, color: 'bg-orange-100 text-orange-700 dark:bg-orange-950 dark:text-orange-400' },
  merger: { label: 'Merger', icon: Building2, color: 'bg-purple-100 text-purple-700 dark:bg-purple-950 dark:text-purple-400' },
  spin_off: { label: 'Spin-off', icon: RefreshCw, color: 'bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-400' },
  tender: { label: 'Tender Offer', icon: Scale, color: 'bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-400' },
  rights: { label: 'Rights Issue', icon: Calendar, color: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-950 dark:text-yellow-400' },
  bonus: { label: 'Bonus Issue', icon: Building2, color: 'bg-indigo-100 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-400' },
}

function generateMockActions(): CorporateActionData[] {
  const today = new Date()
  const actions: CorporateActionData[] = []

  const actionTypes: Array<'split' | 'reverse_split' | 'merger' | 'spin_off' | 'tender' | 'rights'> = [
    'split', 'split', 'split', 'split', 'split',
    'merger', 'spin_off', 'rights', 'tender'
  ]

  const companies = ['Apple Inc.', 'Microsoft Corp.', 'Google LLC', 'Amazon.com', 'Meta Platforms', 'Tesla Inc.']

  for (let i = 0; i < 15; i++) {
    const date = new Date(today)
    date.setFullYear(date.getFullYear() - Math.floor(i / 2) - 1)

    const type = actionTypes[i % actionTypes.length]
    let description = ''
    let ratio = ''
    let targetCompany = ''

    switch (type) {
      case 'split':
        const splitRatios = ['4-for-1', '7-for-1', '2-for-1', '10-for-1', '3-for-2']
        ratio = splitRatios[Math.floor(Math.random() * splitRatios.length)]
        description = `${ratio} stock split`
        break
      case 'reverse_split':
        const reverseRatios = ['1-for-10', '1-for-7', '1-for-4', '1-for-20']
        ratio = reverseRatios[Math.floor(Math.random() * reverseRatios.length)]
        description = `${reverseRatios[Math.floor(Math.random() * reverseRatios.length)]} reverse stock split`
        break
      case 'merger':
        targetCompany = companies[Math.floor(Math.random() * companies.length)]
        description = `Merger with ${targetCompany}`
        break
      case 'spin_off':
        description = 'Spin-off of subsidiary'
        break
      case 'tender':
        description = 'Tender offer completed'
        break
      case 'rights':
        description = 'Rights issue for existing shareholders'
        break
    }

    actions.push({
      id: `CA-${Date.now()}-${i}`,
      date: formatDate(date),
      type,
      description,
      ratio,
      effectiveDate: formatDate(new Date(date.getTime() + 7 * 24 * 60 * 60 * 1000)),
      recordDate: formatDate(new Date(date.getTime() + 3 * 24 * 60 * 60 * 1000)),
      targetCompany,
    })
  }

  return actions.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
}

export function CorporateActions({ symbol = 'AAPL', className }: CorporateActionsProps) {
  const [loading, setLoading] = useState(true)
  const [actions, setActions] = useState<CorporateActionData[]>([])
  const [actionType, setActionType] = useState<string>('all')
  const [sortOrder, setSortOrder] = useState<'desc' | 'asc'>('desc')
  const { downloadCSV, downloadJSON } = useDownloadFile()

  const loadActions = () => {
    setLoading(true)
    setTimeout(() => {
      const data = generateMockActions()
      setActions(data)
      setLoading(false)
    }, 600)
  }

  const filteredActions = actions
    .filter((a) => actionType === 'all' || a.type === actionType)
    .sort((a, b) => {
      const dateA = new Date(a.date).getTime()
      const dateB = new Date(b.date).getTime()
      return sortOrder === 'desc' ? dateB - dateA : dateA - dateB
    })

  const actionCounts = actions.reduce((acc, action) => {
    acc[action.type] = (acc[action.type] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const handleExportCSV = () => {
    const headers = ['Date', 'Type', 'Description', 'Ratio', 'Effective Date', 'Record Date', 'Target']
    const rows = filteredActions.map((a) => [
      a.date,
      a.type,
      a.description,
      a.ratio || '',
      a.effectiveDate || '',
      a.recordDate || '',
      a.targetCompany || '',
    ])
    downloadCSV(rows, `${symbol}_corporate_actions`)
  }

  const handleExportJSON = () => {
    downloadJSON(filteredActions, `${symbol}_corporate_actions`)
  }

  if (loading) {
    return (
      <Card className={cn('', className)}>
        <CardHeader className="pb-2">
          <CardTitle className="text-lg flex items-center gap-2">
            <RefreshCw className="h-5 w-5" />
            Corporate Actions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-[300px] w-full" />
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={cn('', className)}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <ArrowRightLeft className="h-5 w-5" />
            Corporate Actions
            {symbol && (
              <Badge variant="secondary" className="ml-2">
                {symbol}
              </Badge>
            )}
          </CardTitle>
          <div className="flex items-center gap-2">
            <Select value={actionType} onValueChange={setActionType}>
              <SelectTrigger className="w-36 h-8">
                <SelectValue placeholder="Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="split">Splits</SelectItem>
                <SelectItem value="reverse_split">Reverse Splits</SelectItem>
                <SelectItem value="merger">Mergers</SelectItem>
                <SelectItem value="spin_off">Spin-offs</SelectItem>
                <SelectItem value="tender">Tender Offers</SelectItem>
                <SelectItem value="rights">Rights Issues</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" size="icon" className="h-8 w-8" onClick={loadActions}>
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-4 gap-4 mb-4">
          {Object.entries(ACTION_LABELS).slice(0, 4).map(([type, config]) => {
            const count = actionCounts[type] || 0
            if (count === 0) return null
            const Icon = config.icon
            return (
              <div key={type} className="rounded-lg p-3">
                <div className={cn('flex items-center gap-2', config.color.split(' ')[1])}>
                  <Icon className="h-4 w-4" />
                  <span className="text-xs font-medium">{config.label}</span>
                </div>
                <div className="text-xl font-bold mt-1">
                  {count}
                </div>
              </div>
            )
          })}
        </div>

        <div className="flex items-center justify-between mb-4">
          <div className="text-sm text-muted-foreground">
            Showing {filteredActions.length} corporate actions
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={handleExportCSV}>
              <FileSpreadsheet className="h-4 w-4 mr-1" />
              CSV
            </Button>
            <Button variant="outline" size="sm" onClick={handleExportJSON}>
              <FileJson className="h-4 w-4 mr-1" />
              JSON
            </Button>
          </div>
        </div>

        <div className="border rounded-lg">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Date</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Ratio/Details</TableHead>
                <TableHead>Effective</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredActions.map((action) => {
                const config = ACTION_LABELS[action.type]
                const Icon = config?.icon || RefreshCw
                return (
                  <TableRow key={action.id}>
                    <TableCell className="font-medium">{action.date}</TableCell>
                    <TableCell>
                      <Badge className={cn('gap-1', config?.color)}>
                        <Icon className="h-3 w-3" />
                        {config?.label || action.type}
                      </Badge>
                    </TableCell>
                    <TableCell className="max-w-xs truncate">
                      {action.description}
                    </TableCell>
                    <TableCell>
                      {action.ratio && (
                        <Badge variant="outline">{action.ratio}</Badge>
                      )}
                      {action.targetCompany && (
                        <span className="text-xs text-muted-foreground ml-2">
                          {action.targetCompany}
                        </span>
                      )}
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {action.effectiveDate || '-'}
                    </TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
        </div>

        <div className="mt-4 flex items-center justify-between text-xs text-muted-foreground">
          <div>
            Corporate actions history for {symbol}
          </div>
          <div className="flex items-center gap-1">
            <span>Sorted by:</span>
            <Select value={sortOrder} onValueChange={(v) => setSortOrder(v as 'desc' | 'asc')}>
              <SelectTrigger className="h-7 w-28">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="desc">Newest First</SelectItem>
                <SelectItem value="asc">Oldest First</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
