'use client'

import { useState } from 'react'
import { Plus, Trash2, Edit2, Upload, FolderOpen, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { useScreenerPresets } from '@/stores/screenerPresetsStore'
import { useScreenerStore } from '@/stores/screenerStore'
import type { UserScreenerPreset, ScreenerRequest } from '@/lib/types/screener'

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  return date.toLocaleDateString()
}

function countFilters(filters: Partial<ScreenerRequest>): number {
  return Object.values(filters).filter(
    (v) => v !== undefined && v !== null && v !== ''
  ).length
}

interface SavePresetDialogProps {
  onSave?: () => void
}

function SavePresetDialog({ onSave }: SavePresetDialogProps) {
  const [open, setOpen] = useState(false)
  const [name, setName] = useState('')
  const { savePreset, loading, error } = useScreenerPresets()
  const { filters } = useScreenerStore()

  const handleSave = async () => {
    if (!name.trim()) return
    try {
      await savePreset(name.trim(), filters)
      setOpen(false)
      setName('')
      onSave?.()
    } catch (e) {
      // Error is handled by the store
    }
  }

  const filterCount = countFilters(filters)
  const isValid = name.trim() && filterCount > 0

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <Plus className="h-4 w-4 mr-2" />
          Save Preset
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Save Screener Preset</DialogTitle>
          <DialogDescription>
            Save your current filter criteria as a named preset for quick access later.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Preset Name</label>
            <Input
              placeholder="e.g., Tech Growth Stocks"
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={loading}
            />
          </div>
          {error && (
            <p className="text-sm text-destructive">{error}</p>
          )}
          {filterCount > 0 ? (
            <p className="text-sm text-muted-foreground">
              This preset will save {filterCount} filter{filterCount !== 1 ? 's' : ''}.
            </p>
          ) : (
            <p className="text-sm text-muted-foreground">
              No filters applied. Add some filters before saving.
            </p>
          )}
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)} disabled={loading}>
            Cancel
          </Button>
          <Button onClick={handleSave} disabled={!isValid || loading}>
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Saving...
              </>
            ) : (
              'Save Preset'
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

interface RenamePresetDialogProps {
  preset: UserScreenerPreset
  onRename?: () => void
}

function RenamePresetDialog({ preset, onRename }: RenamePresetDialogProps) {
  const [open, setOpen] = useState(false)
  const [name, setName] = useState(preset.name)
  const { updatePreset, loading, error } = useScreenerPresets()

  const handleRename = async () => {
    if (!name.trim() || name.trim() === preset.name) {
      setOpen(false)
      return
    }
    try {
      await updatePreset(preset.id, { name: name.trim() })
      setOpen(false)
      onRename?.()
    } catch (e) {
      // Error is handled by the store
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="icon" className="h-8 w-8">
          <Edit2 className="h-4 w-4" />
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Rename Preset</DialogTitle>
          <DialogDescription>
            Give your preset a new name.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <Input
            placeholder="Preset name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            disabled={loading}
          />
          {error && (
            <p className="text-sm text-destructive">{error}</p>
          )}
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)} disabled={loading}>
            Cancel
          </Button>
          <Button onClick={handleRename} disabled={!name.trim() || loading}>
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Saving...
              </>
            ) : (
              'Rename'
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

interface PresetListProps {
  onSelectPreset?: (filters: Partial<ScreenerRequest>) => void
}

export function PresetList({ onSelectPreset }: PresetListProps) {
  const { presets, loading, fetchPresets, deletePreset } = useScreenerPresets()
  const { filters, applyPreset } = useScreenerStore()
  const [deletingId, setDeletingId] = useState<string | null>(null)

  const handleLoadPreset = (preset: UserScreenerPreset) => {
    applyPreset({
      key: preset.id,
      name: preset.name,
      description: '',
      filters: preset.filters,
    })
    onSelectPreset?.(preset.filters)
  }

  const handleDeletePreset = async (id: string) => {
    if (confirm('Are you sure you want to delete this preset?')) {
      setDeletingId(id)
      try {
        await deletePreset(id)
      } finally {
        setDeletingId(null)
      }
    }
  }

  // Fetch presets on mount
  const hasFetched = presets.length > 0 || !loading

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Saved Screeners</CardTitle>
          <SavePresetDialog onSave={fetchPresets} />
        </div>
      </CardHeader>
      <CardContent>
        {loading && !hasFetched ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        ) : presets.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <FolderOpen className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p className="text-sm">No saved presets</p>
            <p className="text-xs mt-1">
              Save your current filters as a preset for quick access
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {presets.map((preset) => (
              <div
                key={preset.id}
                className="flex items-center justify-between p-3 rounded-lg border bg-card hover:bg-muted/50 transition-colors"
              >
                <div className="flex-1 min-w-0 mr-3">
                  <p className="font-medium truncate">{preset.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {countFilters(preset.filters)} filters • {formatDate(preset.updated_at)}
                  </p>
                </div>
                <div className="flex items-center gap-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleLoadPreset(preset)}
                    disabled={deletingId === preset.id}
                  >
                    <Upload className="h-4 w-4 mr-1" />
                    Load
                  </Button>
                  <RenamePresetDialog preset={preset} onRename={fetchPresets} />
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-destructive hover:text-destructive"
                    onClick={() => handleDeletePreset(preset.id)}
                    disabled={deletingId === preset.id}
                  >
                    {deletingId === preset.id ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Trash2 className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
