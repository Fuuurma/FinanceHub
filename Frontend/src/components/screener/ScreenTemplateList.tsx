"use client"

import { useState } from 'react'
import { FolderOpen, Copy, Play, MoreHorizontal, Search, Plus } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { cn } from '@/lib/utils'

export interface ScreenTemplate {
  id: string
  name: string
  description: string
  category: string
  criteriaCount: number
  createdBy: string
  lastUsed?: string
  popularity: number
}

export interface ScreenTemplateListProps {
  templates?: ScreenTemplate[]
  onSelect?: (template: ScreenTemplate) => void
  onCopy?: (template: ScreenTemplate) => void
  onRun?: (template: ScreenTemplate) => void
  loading?: boolean
  error?: string
  className?: string
}

const CATEGORIES = ['All', 'Growth', 'Value', 'Dividend', 'Momentum', 'Quality', 'Low Volatility', 'Technical']

export function ScreenTemplateList({
  templates = [],
  onSelect,
  onCopy,
  onRun,
  loading = false,
  error,
  className,
}: ScreenTemplateListProps) {
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [search, setSearch] = useState('')

  const filteredTemplates = templates.filter(t => {
    const matchesSearch = t.name.toLowerCase().includes(search.toLowerCase()) || t.description.toLowerCase().includes(search.toLowerCase())
    const matchesCategory = selectedCategory === 'All' || t.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  if (loading) {
    return (
      <Card className={cn('w-full', className)}>
        <CardHeader>
          <Skeleton className="h-6 w-40" />
          <Skeleton className="h-4 w-56 mt-2" />
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-24 w-full" />)}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error || (!templates.length)) {
    return (
      <Card className={cn('w-full', className)}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><FolderOpen className="h-5 w-5" />Screen Templates</CardTitle>
          <CardDescription>Pre-built screening criteria templates</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-red-500">{error || 'No templates available'}</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={cn('w-full', className)}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2"><FolderOpen className="h-5 w-5" />Screen Templates</CardTitle>
            <CardDescription>Pre-built screening criteria templates</CardDescription>
          </div>
          <Button size="sm"><Plus className="h-4 w-4 mr-2" />Create Template</Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-2 mb-4 overflow-x-auto pb-2">
          {CATEGORIES.map(cat => (
            <Button
              key={cat}
              variant={selectedCategory === cat ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedCategory(cat)}
              className="whitespace-nowrap"
            >
              {cat}
            </Button>
          ))}
        </div>

        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search templates..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredTemplates.map(template => (
            <div key={template.id} className="p-4 border rounded-lg hover:bg-muted/50 transition-colors">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h4 className="font-semibold">{template.name}</h4>
                  <p className="text-sm text-muted-foreground line-clamp-2">{template.description}</p>
                </div>
                <Badge variant="outline">{template.category}</Badge>
              </div>
              <div className="flex items-center justify-between mt-3">
                <span className="text-xs text-muted-foreground">{template.criteriaCount} criteria</span>
                <div className="flex items-center gap-1">
                  <Button variant="ghost" size="icon" onClick={() => onRun?.(template)}><Play className="h-4 w-4" /></Button>
                  <Button variant="ghost" size="icon" onClick={() => onCopy?.(template)}><Copy className="h-4 w-4" /></Button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredTemplates.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            <FolderOpen className="h-12 w-12 mx-auto mb-2 opacity-50" />
            <p>No templates match your search</p>
          </div>
        )}

        <div className="mt-4 pt-4 border-t">
          <p className="text-xs text-muted-foreground text-center">{filteredTemplates.length} templates</p>
        </div>
      </CardContent>
    </Card>
  )
}
