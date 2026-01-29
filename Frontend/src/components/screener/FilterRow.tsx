'use client'

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
import { SCREENER_CATEGORIES, SCREENER_PRESETS } from '@/lib/constants/screener'
import type { ScreenerFilter } from '@/lib/types/screener'
import { useScreenerStore } from '@/stores/screenerStore'

interface FilterRowProps {
  index: number
  filter: ScreenerFilter
}

export function FilterRow({ index, filter }: FilterRowProps) {
  const { updateFilter, removeFilter } = useScreenerStore()

  const getFilterOptions = () => {
    for (const category of SCREENER_CATEGORIES) {
      const found = category.filters.find(f => f.key === filter.key)
      if (found) return found
    }
    return null
  }

  const filterDef = getFilterOptions()

  const handleFieldChange = (value: string) => {
    updateFilter(index, { key: value })
    updateFilter(index, { value: '' })
  }

  return (
    <div className="flex gap-2 items-start p-3 border rounded-lg bg-card">
      <div className="flex-1 space-y-2">
        <Label className="text-xs text-muted-foreground">Field</Label>
        <Select value={filter.key} onValueChange={handleFieldChange}>
          <SelectTrigger className="h-9">
            <SelectValue placeholder="Select field" />
          </SelectTrigger>
          <SelectContent>
            {SCREENER_CATEGORIES.map(category => (
              <div key={category.id} className="px-2 py-1.5">
                <p className="text-xs font-medium text-muted-foreground mb-1">{category.name}</p>
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
        <Label className="text-xs text-muted-foreground">Operator</Label>
        <Select
          value={filter.operator}
          onValueChange={(value) => updateFilter(index, { operator: value })}
          disabled={!filter.key}
        >
          <SelectTrigger className="h-9">
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
        <Label className="text-xs text-muted-foreground">Value</Label>
        {filterDef?.type === 'select' || filterDef?.type === 'multiselect' ? (
          <Select
            value={String(filter.value)}
            onValueChange={(value) => updateFilter(index, { value })}
            disabled={!filter.key}
          >
            <SelectTrigger className="h-9">
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
          <div className="flex gap-2">
            <Input
              type="number"
              placeholder="Min"
              className="h-9"
              value={Array.isArray(filter.value) ? filter.value[0] || '' : ''}
              onChange={(e) => updateFilter(index, { value: [e.target.value, Array.isArray(filter.value) ? filter.value[1] || '' : ''] })}
            />
            <Input
              type="number"
              placeholder="Max"
              className="h-9"
              value={Array.isArray(filter.value) ? filter.value[1] || '' : ''}
              onChange={(e) => updateFilter(index, { value: [Array.isArray(filter.value) ? filter.value[0] || '' : '', e.target.value] })}
            />
          </div>
        ) : (
          <Input
            type={filterDef?.type === 'number' ? 'number' : 'text'}
            placeholder={filterDef?.placeholder || 'Enter value'}
            className="h-9"
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
      >
        <X className="h-4 w-4" />
      </Button>
    </div>
  )
}
