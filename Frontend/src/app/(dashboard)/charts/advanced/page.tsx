'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { RealTimeChart } from '@/components/realtime/RealTimeChart'
import { TechnicalIndicators } from '@/components/charts/TechnicalIndicators'
import { DrawingTools } from '@/components/charts/DrawingTools'
import { ComparisonChart } from '@/components/charts/ComparisonChart'
import { ConnectionStatus } from '@/components/realtime/ConnectionStatus'
import {
  TrendingUp,
  Activity,
  Type,
  BarChart3,
  Settings2,
  Info,
} from 'lucide-react'
import type { IndicatorConfig, DrawingType, TimeFrame } from '@/lib/types/indicators'
import { cn } from '@/lib/utils'

export default function AdvancedChartPage() {
  const [symbol, setSymbol] = useState('AAPL')
  const [timeframe, setTimeframe] = useState<TimeFrame>('1d')
  const [indicators, setIndicators] = useState<IndicatorConfig[]>([])
  const [drawings, setDrawings] = useState<any[]>([])
  const [selectedTool, setSelectedTool] = useState<DrawingType | null>(null)
  const [comparisonMode, setComparisonMode] = useState(false)
  const [comparisonSymbols, setComparisonSymbols] = useState<string[]>(['AAPL', 'MSFT', 'GOOGL'])

  const handleAddIndicator = (indicator: IndicatorConfig) => {
    setIndicators([...indicators, indicator])
  }

  const handleRemoveIndicator = (indicator: IndicatorConfig) => {
    setIndicators(indicators.filter((ind) => ind.type !== indicator.type))
  }

  const handleUpdateIndicators = (newIndicators: IndicatorConfig[]) => {
    setIndicators(newIndicators)
  }

  const handleToolSelect = (tool: DrawingType | null) => {
    setSelectedTool(tool)
  }

  const handleAddDrawing = (drawing: any) => {
    setDrawings([...drawings, drawing])
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-4">
            <h1 className="text-3xl font-bold">Advanced Charts</h1>
            <ConnectionStatus />
          </div>
          <p className="text-muted-foreground mt-2">
            Technical analysis, drawing tools, and multi-symbol comparison
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant={comparisonMode ? 'default' : 'outline'}
            onClick={() => setComparisonMode(!comparisonMode)}
          >
            <BarChart3 className="h-4 w-4 mr-2" />
            {comparisonMode ? 'Exit Comparison' : 'Comparison Mode'}
          </Button>
        </div>
      </div>

      {!comparisonMode ? (
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Main Chart */}
          <div className="lg:col-span-2 space-y-6">
            <Card className="border-2 border-foreground">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      <TrendingUp className="h-5 w-5" />
                      {symbol} Chart
                    </CardTitle>
                    <CardDescription>
                      Real-time price and volume with technical indicators
                    </CardDescription>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setIndicators([])
                        setSelectedTool(null)
                      }}
                    >
                      Reset All
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <RealTimeChart
                  symbol={symbol}
                  timeframe={timeframe}
                  indicators={indicators}
                  onIndicatorsChange={handleUpdateIndicators}
                  showIndicatorsPanel={indicators.length > 0}
                />
              </CardContent>
            </Card>

            {selectedTool && (
              <Card className="border-2 border-primary">
                <CardHeader>
                  <CardTitle className="text-sm">
                    Drawing Mode Active: {selectedTool}
                  </CardTitle>
                  <CardDescription>
                    Click and drag on the chart to draw
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setSelectedTool(null)}
                  >
                    Exit Drawing Mode
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Side Panel */}
          <div className="space-y-6">
            {/* Drawing Tools */}
            <DrawingTools
              symbol={symbol}
              timeframe={timeframe}
              drawings={drawings}
              onDrawingsChange={handleAddDrawing}
              onToolSelect={handleToolSelect}
              selectedTool={selectedTool}
            />

            {/* Technical Indicators */}
            <TechnicalIndicators
              symbol={symbol}
              selectedIndicators={indicators}
              onIndicatorsChange={setIndicators}
            />
          </div>
        </div>
      ) : (
        /* Comparison Mode */
        <ComparisonChart
          symbols={comparisonSymbols}
          timeframe={timeframe}
          normalize={true}
        />
      )}

      {/* Info Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Info className="h-5 w-5" />
            Chart Features Guide
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="indicators" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="indicators">Technical Indicators</TabsTrigger>
              <TabsTrigger value="drawing">Drawing Tools</TabsTrigger>
              <TabsTrigger value="comparison">Comparison Mode</TabsTrigger>
            </TabsList>

            <TabsContent value="indicators" className="space-y-3 mt-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-semibold mb-2">Trend Indicators</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• <strong>SMA/EMA:</strong> Moving averages for trend identification</li>
                    <li>• <strong>Bollinger Bands:</strong> Volatility and price channels</li>
                    <li>• <strong>Ichimoku Cloud:</strong> Support/resistance zones</li>
                    <li>• <strong>Parabolic SAR:</strong> Trend reversal signals</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">Momentum Indicators</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• <strong>RSI:</strong> Overbought/oversold conditions (70/30)</li>
                    <li>• <strong>MACD:</strong> Momentum and trend strength</li>
                    <li>• <strong>Stochastic:</strong> Momentum oscillator</li>
                    <li>• <strong>Williams %R:</strong> Momentum reversal signals</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">Volume Indicators</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• <strong>OBV:</strong> Buying/selling pressure</li>
                    <li>• <strong>MFI:</strong> Money flow intensity</li>
                    <li>• <strong>A/D Line:</strong> Accumulation/distribution</li>
                  </ul>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="drawing" className="space-y-3 mt-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-semibold mb-2">Drawing Tools</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• <strong>Horizontal Line:</strong> Support/resistance levels</li>
                    <li>• <strong>Vertical Line:</strong> Time markers</li>
                    <li>• <strong>Trend Line:</strong> Draw trend channels</li>
                    <li>• <strong>Fibonacci:</strong> Retracement levels (23.6%, 38.2%, 61.8%)</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">Tips</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• Drawings are saved per symbol and timeframe</li>
                    <li>• Toggle visibility to show/hide without deleting</li>
                    <li>• Use contrasting colors for multiple drawings</li>
                    <li>• Combine multiple indicators for confirmation</li>
                  </ul>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="comparison" className="space-y-3 mt-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-semibold mb-2">Comparison Features</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• Compare up to 4 symbols simultaneously</li>
                    <li>• Normalized view for relative performance</li>
                    <li>• Absolute price view for actual values</li>
                    <li>• Correlation matrix for relationships</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">Presets Available</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• Tech Giants (AAPL, MSFT, GOOGL, AMZN, META)</li>
                    <li>• Major Indices (SPY, QQQ, IWM, DIA)</li>
                    <li>• Auto Makers (TSLA, F, GM, RIVN, LCID)</li>
                    <li>• Banks (JPM, BAC, WFC, C, GS)</li>
                  </ul>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  )
}
