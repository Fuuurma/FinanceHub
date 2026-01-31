'use client'

import { useState, useRef, useCallback } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Switch } from '@/components/ui/switch'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import {
  Minus,
  TrendingUp,
  Square,
  Type,
  Activity,
  Plus,
  Trash2,
  Save,
  Undo,
  Camera,
  Share2,
  Download,
  Link,
  Loader2,
} from 'lucide-react'
import { DRAWING_TOOLS, FIBONACCI_LEVELS } from '@/lib/constants/indicators'
import { cn } from '@/lib/utils'

export type DrawingType =
  | 'horizontal_line'
  | 'vertical_line'
  | 'trend_line'
  | 'fibonacci'
  | 'rectangle'
  | 'text'

interface Drawing {
  id: string
  type: DrawingType
  symbol: string
  timeframe: string
  startX: number
  startY: number
  endX?: number
  endY?: number
  color: string
  width: number
  style: 'solid' | 'dashed'
  text?: string
  fibonacciLevels?: number[]
  visible: boolean
  created_at: string
}

interface DrawingToolsProps {
  symbol: string
  timeframe: string
  drawings: Drawing[]
  onDrawingsChange: (drawings: Drawing[]) => void
  onToolSelect?: (tool: DrawingType | null) => void
  selectedTool?: DrawingType | null
  onScreenshot?: () => Promise<string>
  onShare?: () => Promise<string>
  className?: string
}

export function DrawingTools({
  symbol,
  timeframe,
  drawings,
  onDrawingsChange,
  onToolSelect,
  selectedTool,
  onScreenshot,
  onShare,
  className,
}: DrawingToolsProps) {
  const [activeTab, setActiveTab] = useState<'tools' | 'manage'>('tools')
  const [isTakingScreenshot, setIsTakingScreenshot] = useState(false)
  const [isSharing, setIsSharing] = useState(false)
  const [shareUrl, setShareUrl] = useState<string | null>(null)
  const [showShareModal, setShowShareModal] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleSelectTool = (type: DrawingType) => {
    if (selectedTool === type) {
      onToolSelect?.(null)
    } else {
      onToolSelect?.(type)
    }
  }

  const handleClearAll = () => {
    if (confirm('Are you sure you want to clear all drawings?')) {
      onDrawingsChange([])
    }
  }

  const handleToggleVisibility = (drawingId: string) => {
    const newDrawings = drawings.map((d) =>
      d.id === drawingId ? { ...d, visible: !d.visible } : d
    )
    onDrawingsChange(newDrawings)
  }

  const handleDeleteDrawing = (drawingId: string) => {
    const newDrawings = drawings.filter((d) => d.id !== drawingId)
    onDrawingsChange(newDrawings)
  }

  const handleScreenshot = useCallback(async () => {
    if (!onScreenshot) {
      return
    }

    setIsTakingScreenshot(true)
    try {
      const dataUrl = await onScreenshot()
      const link = document.createElement('a')
      link.download = `chart-${symbol}-${Date.now()}.png`
      link.href = dataUrl
      link.click()
    } catch (error) {
      console.error('Failed to take screenshot:', error)
    } finally {
      setIsTakingScreenshot(false)
    }
  }, [onScreenshot, symbol])

  const handleShare = useCallback(async () => {
    if (!onShare) {
      return
    }

    setIsSharing(true)
    setShareUrl(null)
    try {
      const url = await onShare()
      setShareUrl(url)
      setShowShareModal(true)
    } catch (error) {
      console.error('Failed to share:', error)
    } finally {
      setIsSharing(false)
    }
  }, [onShare])

  const copyShareUrl = useCallback(async () => {
    if (shareUrl) {
      await navigator.clipboard.writeText(shareUrl)
    }
  }, [shareUrl])

  const getToolIcon = (type: DrawingType) => {
    switch (type) {
      case 'horizontal_line':
        return <Minus className="h-4 w-4" />
      case 'vertical_line':
        return <Minus className="h-4 w-4 rotate-90" />
      case 'trend_line':
        return <TrendingUp className="h-4 w-4" />
      case 'fibonacci':
        return <Activity className="h-4 w-4" />
      case 'rectangle':
        return <Square className="h-4 w-4" />
      case 'text':
        return <Type className="h-4 w-4" />
      default:
        return <Minus className="h-4 w-4" />
    }
  }

  const getToolLabel = (type: DrawingType) => {
    return DRAWING_TOOLS.find((t) => t.type === type)?.label || type
  }

  return (
    <div className={cn('space-y-4', className)}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Type className="h-5 w-5" />
            Drawing Tools
            <Badge variant="secondary">{drawings.length} drawings</Badge>
          </CardTitle>
          <CardDescription>
            Draw support, resistance, and annotations on charts
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as 'tools' | 'manage')}>
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="tools">Tools</TabsTrigger>
              <TabsTrigger value="manage">Manage</TabsTrigger>
            </TabsList>

            <TabsContent value="tools" className="space-y-4 mt-4">
              <div className="grid grid-cols-2 gap-2">
                {DRAWING_TOOLS.map((tool) => (
                  <Button
                    key={tool.type}
                    variant={selectedTool === tool.type ? 'default' : 'outline'}
                    onClick={() => handleSelectTool(tool.type as DrawingType)}
                    className={cn(
                      'gap-2 justify-start',
                      selectedTool === tool.type && 'bg-primary text-primary-foreground'
                    )}
                  >
                    {getToolIcon(tool.type as DrawingType)}
                    <span className="text-sm">{tool.label}</span>
                  </Button>
                ))}
              </div>

              {selectedTool && (
                <Card className="bg-muted/30 border-2 border-primary">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm">
                      Selected: {getToolLabel(selectedTool)}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="text-sm text-muted-foreground">
                      {selectedTool === 'horizontal_line' && 'Click to set price level'}
                      {selectedTool === 'vertical_line' && 'Click to set time point'}
                      {selectedTool === 'trend_line' && 'Drag to draw trend line'}
                      {selectedTool === 'fibonacci' && 'Drag to draw Fibonacci retracement'}
                      {selectedTool === 'rectangle' && 'Drag to create rectangle zone'}
                      {selectedTool === 'text' && 'Click to add text annotation'}
                    </div>

                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" onClick={() => onToolSelect?.(null)}>
                        Cancel
                      </Button>
                      <Button size="sm" className="flex-1">
                        <Save className="h-4 w-4 mr-2" />
                        Save Drawing
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )}

              <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3">
                <p className="text-xs text-blue-600 dark:text-blue-500">
                  <strong>Tip:</strong> Select a drawing tool, then click and drag on the chart to create. Drawings are saved per symbol and timeframe.
                </p>
              </div>

              <div className="border-t pt-4">
                <Label className="text-xs font-medium text-muted-foreground mb-2 block">
                  Export & Share
                </Label>
                <div className="grid grid-cols-2 gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleScreenshot}
                    disabled={isTakingScreenshot || !onScreenshot}
                  >
                    {isTakingScreenshot ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Camera className="h-4 w-4" />
                    )}
                    <span className="ml-2">Screenshot</span>
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleShare}
                    disabled={isSharing || !onShare}
                  >
                    {isSharing ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Share2 className="h-4 w-4" />
                    )}
                    <span className="ml-2">Share</span>
                  </Button>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="manage" className="space-y-4 mt-4">
              {drawings.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <Type className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No drawings yet</p>
                  <p className="text-sm">Use drawing tools to create annotations</p>
                </div>
              ) : (
                <>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleClearAll}
                      className="text-destructive"
                    >
                      <Trash2 className="h-4 w-4 mr-2" />
                      Clear All
                    </Button>
                  </div>

                  <div className="space-y-2">
                    {drawings.map((drawing) => (
                      <div
                        key={drawing.id}
                        className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50"
                      >
                        <div className="flex items-center gap-3">
                          {getToolIcon(drawing.type)}
                          <div>
                            <p className="font-medium text-sm">
                              {getToolLabel(drawing.type)}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {new Date(drawing.created_at).toLocaleString()}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Switch
                            checked={drawing.visible}
                            onCheckedChange={() => handleToggleVisibility(drawing.id)}
                          />
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDeleteDrawing(drawing.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      <Dialog open={showShareModal} onOpenChange={setShowShareModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Share2 className="h-5 w-5" />
              Share Chart
            </DialogTitle>
            <DialogDescription>
              Share your chart with drawings and annotations.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            {shareUrl ? (
              <>
                <div className="flex items-center gap-2 p-3 bg-muted rounded-lg">
                  <Link className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                  <code className="text-sm flex-1 break-all">{shareUrl}</code>
                  <Button variant="ghost" size="sm" onClick={copyShareUrl}>
                    Copy
                  </Button>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" className="flex-1" onClick={() => window.open(shareUrl, '_blank')}>
                    <Download className="h-4 w-4 mr-2" />
                    Open Link
                  </Button>
                  <Button className="flex-1" onClick={() => {
                    if (navigator.share) {
                      navigator.share({
                        title: `Chart: ${symbol}`,
                        text: 'Check out this chart on FinanceHub',
                        url: shareUrl,
                      })
                    }
                  }}>
                    <Share2 className="h-4 w-4 mr-2" />
                    Share Via...
                  </Button>
                </div>
              </>
            ) : (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowShareModal(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
