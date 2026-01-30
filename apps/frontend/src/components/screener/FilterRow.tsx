'use client'

import { useMemo, useCallback } from 'react'
import { X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { SCREENER_CATEGORIES } from '@/lib/constants/screener'
import type { ScreenerFilter } from '@/lib/types/screener'
import { useScreenerStore } from '@/stores/screenerStore'

interface FilterRowProps {
  index: number
  filter: ScreenerFilter
}

export function FilterRow({ index, filter }: FilterRowProps) {
  const { updateFilter, removeFilter } = useScreenerStore()

  const filterDef = useMemo(() => {
    for (const category of SCREENER_CATEGORIES) {
      const found = category.filters.find(f => f.key === filter.key)
      if (found) return found
    }
    return null
  }, [filter.key])

  const handleFieldChange = useCallback((value: string) => {
    updateFilter(index, { key: value })
    updateFilter(index, { value: '' })
  }, [index, updateFilter])

  return (
    <div
      role="group"
      aria-label={`Filter ${index + 1}`}
      className="flex gap-2 items-start p-3 border rounded-lg bg-card"
    >
      <div className="flex-1 space-y-2">
        <Label htmlFor={`filter-field-${index}`} className="text-xs text-muted-foreground">
          Field
        </Label>
        <Select value={filter.key} onValueChange={handleFieldChange}>
          <SelectTrigger id={`filter-field-${index}`} className="h-9" aria-label="Select filter field">
            <SelectValue placeholder="Select field" />
          </SelectTrigger>
          <SelectContent>
            {SCREENER_CATEGORIES.map(category => (
              <div key={category.id} role="group" aria-labelledby={`category-${category.id}`}>
                <p
                  id={`category-${category.id}`}
                  className="px-2 py-1.5 text-xs font-medium text-muted-foreground mb-1"
                  role="separator"
                >
                  {category.name}
                </p>
                {category.filters.map(f => (
                  <SelectItem key={f.key} value={f.key}>
                    {f.label}
                  </SelectItem>
                ))}
              </div>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="flex-1 space-y-2">
        <Label htmlFor={`filter-operator-${index}`} className="text-xs text-muted-foreground">
          Operator
        </Label>
        <Select
          value={filter.operator}
          onValueChange={(value) => updateFilter(index, { operator: value })}
          disabled={!filter.key}
        >
          <SelectTrigger id={`filter-operator-${index}`} className="h-9" aria-label="Select operator">
            <SelectValue placeholder="Operator" />
          </SelectTrigger>
          <SelectContent>
            {filterDef?.operators.map(op => (
              <SelectItem key={op} value={op}>
                {op === '>' ? 'Greater than' :
                 op === '<' ? 'Less than' :
                 op === '>=' ? 'Greater or equal' :
                 op === '<=' ? 'Less or equal' :
                 op === '=' ? 'Equals' :
                 op === '!=' ? 'Not equals' :
                 op === 'between' ? 'Between' : op}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="flex-[1.5] space-y-2">
        <Label htmlFor={`filter-value-${index}`} className="text-xs text-muted-foreground">
          Value
        </Label>
        {filterDef?.type === 'select' || filterDef?.type === 'multiselect' ? (
          <Select
            value={String(filter.value)}
            onValueChange={(value) => updateFilter(index, { value })}
            disabled={!filter.key}
          >
            <SelectTrigger id={`filter-value-${index}`} className="h-9" aria-label="Select value">
              <SelectValue placeholder="Select value" />
            </SelectTrigger>
            <SelectContent>
              {filterDef.options?.map(opt => (
                <SelectItem key={opt.value} value={opt.value}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        ) : filterDef?.type === 'range' ? (
          <div className="flex gap-2" role="group" aria-label="Range values">
            <Input
              type="number"
              placeholder="Min"
              className="h-9"
              aria-label="Minimum value"
              value={Array.isArray(filter.value) ? filter.value[0] || '' : ''}
              onChange={(e) => updateFilter(index, { value: [e.target.value, Array.isArray(filter.value) ? filter.value[1] || '' : ''] })}
            />
            <Input
              type="number"
              placeholder="Max"
              className="h-9"
              aria-label="Maximum value"
              value={Array.isArray(filter.value) ? filter.value[1] || '' : ''}
              onChange={(e) => updateFilter(index, { value: [Array.isArray(filter.value) ? filter.value[0] || '' : '', e.target.value] })}
            />
          </div>
        ) : (
          <Input
            type={filterDef?.type === 'number' ? 'number' : 'text'}
            placeholder={filterDef?.placeholder || 'Enter value'}
            className="h-9"
            id={`filter-value-${index}`}
            aria-label="Enter value"
            value={filter.value as string}
            onChange={(e) => updateFilter(index, { value: e.target.value })}
            disabled={!filter.key}
          />
        )}
      </div>

      <Button
        variant="ghost"
        size="icon"
        className="mt-6 h-9 w-9"
        onClick={() => removeFilter(index)}
        aria-label={`Remove filter ${index + 1}`}
      >
        <X className="h-4 w-4" />
      </Button>
    </div>
  )
}
