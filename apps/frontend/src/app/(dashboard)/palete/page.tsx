// src/app/design-system/page.tsx
'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { 
  TrendingUp, 
  TrendingDown, 
  AlertCircle, 
  CheckCircle2, 
  Info,
  Copy,
  Check
} from 'lucide-react'

export default function DesignSystemPage() {
  const [copiedCode, setCopiedCode] = useState<string | null>(null)

  const copyToClipboard = (code: string, id: string) => {
    navigator.clipboard.writeText(code)
    setCopiedCode(id)
    setTimeout(() => setCopiedCode(null), 2000)
  }

  const CodeBlock = ({ code, id }: { code: string; id: string }) => (
    <div className="relative group">
      <pre className="bg-foreground/5 border-2 border-foreground/10 p-4 rounded-none overflow-x-auto text-xs font-mono">
        <code>{code}</code>
      </pre>
      <button
        onClick={() => copyToClipboard(code, id)}
        className="absolute top-2 right-2 p-2 bg-foreground text-background opacity-0 group-hover:opacity-100 transition-opacity"
      >
        {copiedCode === id ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
      </button>
    </div>
  )

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b-4 border-foreground bg-foreground text-background p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 bg-primary border-4 border-background" />
            <div>
              <h1 className="text-4xl font-black uppercase tracking-tighter">Design System</h1>
              <p className="text-xs font-mono opacity-60">FINANCEHUB_V4.2.1</p>
            </div>
          </div>
          <p className="text-lg font-mono opacity-90 max-w-2xl">
            Production-ready components, colors, and utilities for building professional financial interfaces.
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-8 space-y-16">

        {/* ===================================================================
            COLOR PALETTE
            =================================================================== */}
        <section>
          <div className="mb-8">
            <h2 className="text-3xl font-black uppercase tracking-tighter mb-2">Color Palette</h2>
            <p className="text-muted-foreground font-mono text-sm">
              Monochromatic professional color system with semantic variants
            </p>
          </div>

          <Tabs defaultValue="base" className="w-full">
            <TabsList className="brutalist-glass mb-6">
              <TabsTrigger value="base" className="font-black uppercase text-xs">Base Colors</TabsTrigger>
              <TabsTrigger value="semantic" className="font-black uppercase text-xs">Semantic</TabsTrigger>
              <TabsTrigger value="chart" className="font-black uppercase text-xs">Charts</TabsTrigger>
              <TabsTrigger value="financial" className="font-black uppercase text-xs">Financial</TabsTrigger>
            </TabsList>

            {/* Base Colors */}
            <TabsContent value="base" className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <ColorCard
                  name="Background"
                  variable="--background"
                  className="bg-background border-2 border-foreground"
                  textColor="text-foreground"
                />
                <ColorCard
                  name="Foreground"
                  variable="--foreground"
                  className="bg-foreground border-2 border-background"
                  textColor="text-background"
                />
                <ColorCard
                  name="Primary"
                  variable="--primary"
                  className="bg-primary border-2 border-foreground"
                  textColor="text-primary-foreground"
                />
                <ColorCard
                  name="Secondary"
                  variable="--secondary"
                  className="bg-secondary border-2 border-foreground"
                  textColor="text-secondary-foreground"
                />
                <ColorCard
                  name="Muted"
                  variable="--muted"
                  className="bg-muted border-2 border-foreground"
                  textColor="text-muted-foreground"
                />
                <ColorCard
                  name="Accent"
                  variable="--accent"
                  className="bg-accent border-2 border-foreground"
                  textColor="text-accent-foreground"
                />
              </div>

              <div className="brutalist-glass p-6">
                <h3 className="font-black uppercase text-sm mb-4">Usage Example</h3>
                <CodeBlock
                  id="base-colors"
                  code={`// Tailwind classes
<div className="bg-background text-foreground">
<div className="bg-primary text-primary-foreground">
<div className="bg-muted text-muted-foreground">

// CSS variables
background: var(--background);
color: var(--foreground);`}
                />
              </div>
            </TabsContent>

            {/* Semantic Colors */}
            <TabsContent value="semantic" className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <ColorCard
                  name="Card"
                  variable="--card"
                  className="bg-card border-2 border-foreground"
                  textColor="text-card-foreground"
                />
                <ColorCard
                  name="Popover"
                  variable="--popover"
                  className="bg-popover border-2 border-foreground"
                  textColor="text-popover-foreground"
                />
                <ColorCard
                  name="Border"
                  variable="--border"
                  className="bg-background border-4 border-border"
                  textColor="text-foreground"
                />
                <ColorCard
                  name="Input"
                  variable="--input"
                  className="bg-input border-2 border-foreground"
                  textColor="text-foreground"
                />
                <ColorCard
                  name="Ring"
                  variable="--ring"
                  className="bg-background border-4 border-ring"
                  textColor="text-foreground"
                />
                <ColorCard
                  name="Destructive"
                  variable="--destructive"
                  className="bg-destructive border-2 border-foreground"
                  textColor="text-white"
                />
              </div>
            </TabsContent>

            {/* Chart Colors */}
            <TabsContent value="chart" className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                {[1, 2, 3, 4, 5].map((num) => (
                  <ColorCard
                    key={num}
                    name={`Chart ${num}`}
                    variable={`--chart-${num}`}
                    className={`bg-chart-${num} border-2 border-foreground`}
                    textColor="text-white"
                  />
                ))}
              </div>

              <div className="brutalist-glass p-6">
                <h3 className="font-black uppercase text-sm mb-4">Chart Example</h3>
                <div className="h-48 flex items-end gap-2">
                  {[65, 45, 80, 55, 70].map((height, i) => (
                    <div
                      key={i}
                      className={`flex-1 bg-chart-${i + 1} border-2 border-foreground transition-all hover:opacity-80`}
                      style={{ height: `${height}%` }}
                    />
                  ))}
                </div>
              </div>
            </TabsContent>

            {/* Financial Colors */}
            <TabsContent value="financial" className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="brutalist-glass p-6 space-y-3">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-green-600" />
                    <h3 className="font-black uppercase text-sm">Positive</h3>
                  </div>
                  <div className="space-y-2">
                    <div className="h-12 bg-green-500 border-2 border-foreground flex items-center justify-center">
                      <span className="text-white font-black">GREEN-500</span>
                    </div>
                    <div className="h-12 bg-green-600 border-2 border-foreground flex items-center justify-center">
                      <span className="text-white font-black">GREEN-600</span>
                    </div>
                    <div className="h-12 bg-green-700 border-2 border-foreground flex items-center justify-center">
                      <span className="text-white font-black">GREEN-700</span>
                    </div>
                  </div>
                  <code className="text-xs font-mono block">text-green-600</code>
                </div>

                <div className="brutalist-glass p-6 space-y-3">
                  <div className="flex items-center gap-2">
                    <TrendingDown className="w-5 h-5 text-red-600" />
                    <h3 className="font-black uppercase text-sm">Negative</h3>
                  </div>
                  <div className="space-y-2">
                    <div className="h-12 bg-red-500 border-2 border-foreground flex items-center justify-center">
                      <span className="text-white font-black">RED-500</span>
                    </div>
                    <div className="h-12 bg-red-600 border-2 border-foreground flex items-center justify-center">
                      <span className="text-white font-black">RED-600</span>
                    </div>
                    <div className="h-12 bg-red-700 border-2 border-foreground flex items-center justify-center">
                      <span className="text-white font-black">RED-700</span>
                    </div>
                  </div>
                  <code className="text-xs font-mono block">text-red-600</code>
                </div>

                <div className="brutalist-glass p-6 space-y-3">
                  <div className="flex items-center gap-2">
                    <Info className="w-5 h-5 text-blue-600" />
                    <h3 className="font-black uppercase text-sm">Info</h3>
                  </div>
                  <div className="space-y-2">
                    <div className="h-12 bg-blue-500 border-2 border-foreground flex items-center justify-center">
                      <span className="text-white font-black">BLUE-500</span>
                    </div>
                    <div className="h-12 bg-blue-600 border-2 border-foreground flex items-center justify-center">
                      <span className="text-white font-black">BLUE-600</span>
                    </div>
                    <div className="h-12 bg-blue-700 border-2 border-foreground flex items-center justify-center">
                      <span className="text-white font-black">BLUE-700</span>
                    </div>
                  </div>
                  <code className="text-xs font-mono block">text-blue-600</code>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </section>

        {/* ===================================================================
            GLASS EFFECTS
            =================================================================== */}
        <section>
          <div className="mb-8">
            <h2 className="text-3xl font-black uppercase tracking-tighter mb-2">Glass Effects</h2>
            <p className="text-muted-foreground font-mono text-sm">
              Brutalist glass morphism with sharp edges and bold shadows
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Base Glass */}
            <div className="space-y-3">
              <div className="brutalist-glass p-6 h-32 flex items-center justify-center">
                <span className="font-black uppercase text-sm">Base Glass</span>
              </div>
              <CodeBlock
                id="base-glass"
                code={`<div className="brutalist-glass">
  Content
</div>`}
              />
            </div>

            {/* Ghost Glass */}
            <div className="space-y-3">
              <div className="brutalist-glass-ghost p-6 h-32 flex items-center justify-center">
                <span className="font-black uppercase text-sm">Ghost Glass</span>
              </div>
              <CodeBlock
                id="ghost-glass"
                code={`<div className="brutalist-glass-ghost">
  Content
</div>`}
              />
            </div>

            {/* Accent Glass */}
            <div className="space-y-3">
              <div className="brutalist-glass-accent p-6 h-32 flex items-center justify-center">
                <span className="font-black uppercase text-sm">Accent Glass</span>
              </div>
              <CodeBlock
                id="accent-glass"
                code={`<div className="brutalist-glass-accent">
  Content
</div>`}
              />
            </div>

            {/* Liquid Glass */}
            <div className="space-y-3">
              <div className="liquid-glass p-6 h-32 flex items-center justify-center">
                <span className="font-black uppercase text-sm">Liquid Glass</span>
              </div>
              <CodeBlock
                id="liquid-glass"
                code={`<div className="liquid-glass">
  Content
</div>`}
              />
            </div>

            {/* Liquid Glass Subtle */}
            <div className="space-y-3">
              <div className="liquid-glass-subtle p-6 h-32 flex items-center justify-center">
                <span className="font-black uppercase text-sm">Liquid Subtle</span>
              </div>
              // eslint-disable-next-line react-hooks/static-components
              <CodeBlock
                id="liquid-subtle"
                code={`<div className="liquid-glass-subtle">
  Content
</div>`}
              />
            </div>

            {/* Liquid Glass Strong */}
            <div className="space-y-3">
              <div className="liquid-glass-strong p-6 h-32 flex items-center justify-center">
                <span className="font-black uppercase text-sm">Liquid Strong</span>
              </div>
              <CodeBlock
                id="liquid-strong"
                code={`<div className="liquid-glass-strong">
  Content
</div>`}
              />
            </div>

            {/* Positive Glass */}
            <div className="space-y-3">
              <div className="liquid-glass-positive p-6 h-32 flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-green-600" />
                <span className="font-black uppercase text-sm ml-2">Positive</span>
              </div>
              <CodeBlock
                id="positive-glass"
                code={`<div className="liquid-glass-positive">
  +2.45%
</div>`}
              />
            </div>

            {/* Negative Glass */}
            <div className="space-y-3">
              <div className="liquid-glass-negative p-6 h-32 flex items-center justify-center">
                <TrendingDown className="w-6 h-6 text-red-600" />
                <span className="font-black uppercase text-sm ml-2">Negative</span>
              </div>
              <CodeBlock
                id="negative-glass"
                code={`<div className="liquid-glass-negative">
  -1.23%
</div>`}
              />
            </div>

            {/* Shimmer Glass */}
            <div className="space-y-3">
              <div className="liquid-glass liquid-glass-shimmer p-6 h-32 flex items-center justify-center">
                <span className="font-black uppercase text-sm">Shimmer Effect</span>
              </div>
              <CodeBlock
                id="shimmer-glass"
                code={`<div className="liquid-glass liquid-glass-shimmer">
  Content
</div>`}
              />
            </div>
          </div>
        </section>

        {/* ===================================================================
            BUTTONS
            =================================================================== */}
        <section>
          <div className="mb-8">
            <h2 className="text-3xl font-black uppercase tracking-tighter mb-2">Buttons</h2>
            <p className="text-muted-foreground font-mono text-sm">
              Interactive elements with brutalist styling
            </p>
          </div>

          <div className="space-y-8">
            {/* Primary Buttons */}
            <div className="brutalist-glass p-6 space-y-4">
              <h3 className="font-black uppercase text-sm">Primary Variants</h3>
              <div className="flex flex-wrap gap-4">
                <Button className="brutalist-interactive rounded-none border-4 border-foreground bg-foreground text-background font-black uppercase shadow-[6px_6px_0px_0px_var(--foreground)]">
                  Default
                </Button>
                <Button className="brutalist-interactive rounded-none border-4 border-primary bg-primary text-primary-foreground font-black uppercase shadow-[6px_6px_0px_0px_var(--primary)]">
                  Primary
                </Button>
                <Button className="brutalist-interactive rounded-none border-4 border-green-600 bg-green-600 text-white font-black uppercase shadow-[6px_6px_0px_0px_rgb(22,163,74)]">
                  Success
                </Button>
                <Button className="brutalist-interactive rounded-none border-4 border-red-600 bg-red-600 text-white font-black uppercase shadow-[6px_6px_0px_0px_rgb(220,38,38)]">
                  Danger
                </Button>
              </div>
              <CodeBlock
                id="primary-button"
                code={`<Button className="brutalist-interactive rounded-none border-4 border-foreground bg-foreground text-background font-black uppercase shadow-[6px_6px_0px_0px_var(--foreground)]">
  Default
</Button>`}
              />
            </div>

            {/* Outline Buttons */}
            <div className="brutalist-glass p-6 space-y-4">
              <h3 className="font-black uppercase text-sm">Outline Variants</h3>
              <div className="flex flex-wrap gap-4">
                <Button variant="outline" className="brutalist-interactive rounded-none border-2 border-foreground font-black uppercase">
                  Outline
                </Button>
                <Button variant="outline" className="brutalist-interactive rounded-none border-2 border-primary text-primary font-black uppercase">
                  Primary
                </Button>
                <Button variant="outline" className="brutalist-interactive rounded-none border-2 border-green-600 text-green-600 font-black uppercase">
                  Success
                </Button>
                <Button variant="outline" className="brutalist-interactive rounded-none border-2 border-red-600 text-red-600 font-black uppercase">
                  Danger
                </Button>
              </div>
              <CodeBlock
                id="outline-button"
                code={`<Button variant="outline" className="brutalist-interactive rounded-none border-2 border-foreground font-black uppercase">
  Outline
</Button>`}
              />
            </div>

            {/* Ghost Buttons */}
            <div className="brutalist-glass p-6 space-y-4">
              <h3 className="font-black uppercase text-sm">Ghost Variants</h3>
              <div className="flex flex-wrap gap-4">
                <Button variant="ghost" className="brutalist-interactive rounded-none font-black uppercase">
                  Ghost
                </Button>
                <Button variant="ghost" className="brutalist-interactive rounded-none text-primary font-black uppercase">
                  Primary
                </Button>
                <Button variant="ghost" className="brutalist-interactive rounded-none text-green-600 font-black uppercase">
                  Success
                </Button>
                <Button variant="ghost" className="brutalist-interactive rounded-none text-red-600 font-black uppercase">
                  Danger
                </Button>
              </div>
            </div>

            {/* Sizes */}
            <div className="brutalist-glass p-6 space-y-4">
              <h3 className="font-black uppercase text-sm">Sizes</h3>
              <div className="flex flex-wrap items-center gap-4">
                <Button size="sm" className="brutalist-interactive rounded-none border-2 border-foreground bg-foreground text-background font-black uppercase text-xs">
                  Small
                </Button>
                <Button size="default" className="brutalist-interactive rounded-none border-2 border-foreground bg-foreground text-background font-black uppercase">
                  Default
                </Button>
                <Button size="lg" className="brutalist-interactive rounded-none border-4 border-foreground bg-foreground text-background font-black uppercase text-lg">
                  Large
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* ===================================================================
            INPUTS & FORMS
            =================================================================== */}
        <section>
          <div className="mb-8">
            <h2 className="text-3xl font-black uppercase tracking-tighter mb-2">Inputs & Forms</h2>
            <p className="text-muted-foreground font-mono text-sm">
              Form controls with brutalist aesthetics
            </p>
          </div>

          <div className="space-y-8">
            {/* Standard Input */}
            <div className="brutalist-glass p-6 space-y-4">
              <h3 className="font-black uppercase text-sm">Standard Input</h3>
              <div className="space-y-2">
                <Label className="text-xs font-black uppercase">Email Address</Label>
                <Input
                  type="email"
                  placeholder="trader@example.com"
                  className="brutalist-input h-12 rounded-none font-mono"
                />
              </div>
              <CodeBlock
                id="standard-input"
                code={`<Input
  type="email"
  placeholder="trader@example.com"
  className="brutalist-input h-12 rounded-none font-mono"
/>`}
              />
            </div>

            {/* Input Group */}
            <div className="brutalist-glass p-6 space-y-4">
              <h3 className="font-black uppercase text-sm">Input Group</h3>
              <div className="space-y-2">
                <Label className="text-xs font-black uppercase">Stock Price</Label>
                <div className="brutalist-input-group">
                  <input type="number" placeholder="0.00" defaultValue="150.25" />
                  <span className="unit">USD</span>
                </div>
              </div>
              <CodeBlock
                id="input-group"
                code={`<div className="brutalist-input-group">
  <input type="number" placeholder="0.00" />
  <span className="unit">USD</span>
</div>`}
              />
            </div>

            {/* Multiple Input Groups */}
            <div className="brutalist-glass p-6 space-y-4">
              <h3 className="font-black uppercase text-sm">Multiple Input Groups</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className="text-xs font-black uppercase">Quantity</Label>
                  <div className="brutalist-input-group">
                    <input type="number" placeholder="0" defaultValue="100" />
                    <span className="unit">SHARES</span>
                  </div>
                </div>
                <div className="space-y-2">
                  <Label className="text-xs font-black uppercase">Percentage</Label>
                  <div className="brutalist-input-group">
                    <input type="number" placeholder="0.00" defaultValue="2.45" />
                    <span className="unit">%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ===================================================================
            BADGES
            =================================================================== */}
        <section>
          <div className="mb-8">
            <h2 className="text-3xl font-black uppercase tracking-tighter mb-2">Badges</h2>
            <p className="text-muted-foreground font-mono text-sm">
              Status indicators and labels
            </p>
          </div>

          <div className="brutalist-glass p-6 space-y-6">
            <div className="space-y-3">
              <h3 className="font-black uppercase text-sm">Default Variants</h3>
              <div className="flex flex-wrap gap-3">
                <Badge className="rounded-none border-2 border-foreground font-mono text-xs">DEFAULT</Badge>
                <Badge variant="secondary" className="rounded-none border-2 border-foreground font-mono text-xs">SECONDARY</Badge>
                <Badge variant="outline" className="rounded-none border-2 border-foreground font-mono text-xs">OUTLINE</Badge>
                <Badge variant="destructive" className="rounded-none border-2 border-foreground font-mono text-xs">DESTRUCTIVE</Badge>
              </div>
            </div>

            <div className="space-y-3">
              <h3 className="font-black uppercase text-sm">Financial Status</h3>
              <div className="flex flex-wrap gap-3">
                <Badge className="rounded-none border-2 border-green-600 bg-green-600 text-white font-mono text-xs">
                  <TrendingUp className="w-3 h-3 mr-1" />
                  BULLISH
                </Badge>
                <Badge className="rounded-none border-2 border-red-600 bg-red-600 text-white font-mono text-xs">
                  <TrendingDown className="w-3 h-3 mr-1" />
                  BEARISH
                </Badge>
                <Badge className="rounded-none border-2 border-blue-600 bg-blue-600 text-white font-mono text-xs">
                  <Info className="w-3 h-3 mr-1" />
                  NEUTRAL
                </Badge>
              </div>
            </div>

            <CodeBlock
              id="badges"
              code={`<Badge className="rounded-none border-2 border-foreground font-mono text-xs">
  DEFAULT
</Badge>

<Badge className="rounded-none border-2 border-green-600 bg-green-600 text-white font-mono text-xs">
  <TrendingUp className="w-3 h-3 mr-1" />
  BULLISH
</Badge>`}
            />
          </div>
        </section>

        {/* ===================================================================
            ALERTS
            =================================================================== */}
        <section>
          <div className="mb-8">
            <h2 className="text-3xl font-black uppercase tracking-tighter mb-2">Alerts</h2>
            <p className="text-muted-foreground font-mono text-sm">
              Notification and message components
            </p>
          </div>

          <div className="space-y-4">
            <Alert className="brutalist-glass rounded-none">
              <Info className="h-4 w-4" />
              <AlertTitle className="font-black uppercase text-sm">Information</AlertTitle>
              <AlertDescription className="font-mono text-xs">
                This is a standard informational alert message.
              </AlertDescription>
            </Alert>

            <Alert className="brutalist-glass bg-green-500/10 border-green-600 text-green-600 dark:text-green-400 rounded-none">
              <CheckCircle2 className="h-4 w-4" />
              <AlertTitle className="font-black uppercase text-sm">Success</AlertTitle>
              <AlertDescription className="font-mono text-xs">
                Your order has been executed successfully.
              </AlertDescription>
            </Alert>

            <Alert className="brutalist-glass bg-red-500/10 border-red-600 text-red-600 dark:text-red-400 rounded-none">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle className="font-black uppercase text-sm">Error</AlertTitle>
              <AlertDescription className="font-mono text-xs">
                Failed to connect to market data feed.
              </AlertDescription>
            </Alert>

            <Alert className="brutalist-glass bg-blue-500/10 border-blue-600 text-blue-600 dark:text-blue-400 rounded-none">
              <Info className="h-4 w-4" />
              <AlertTitle className="font-black uppercase text-sm">Market Update</AlertTitle>
              <AlertDescription className="font-mono text-xs">
                S&P 500 has reached a new all-time high.
              </AlertDescription>
            </Alert>

            <CodeBlock
              id="alerts"
              code={`<Alert className="brutalist-glass bg-green-500/10 border-green-600 text-green-600 rounded-none">
  <CheckCircle2 className="h-4 w-4" />
  <AlertTitle className="font-black uppercase text-sm">Success</AlertTitle>
  <AlertDescription className="font-mono text-xs">
    Your order has been executed successfully.
  </AlertDescription>
</Alert>`}
            />
          </div>
        </section>

        {/* ===================================================================
            CARDS
            =================================================================== */}
        <section>
          <div className="mb-8">
            <h2 className="text-3xl font-black uppercase tracking-tighter mb-2">Cards</h2>
            <p className="text-muted-foreground font-mono text-sm">
              Container components for content grouping
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Standard Card */}
            <Card className="brutalist-glass rounded-none">
              <CardHeader>
                <CardTitle className="font-black uppercase tracking-tighter">Portfolio Value</CardTitle>
                <CardDescription className="font-mono text-xs">Total account balance</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-4xl font-black">$124,567.89</div>
                <div className="flex items-center gap-2 mt-2">
                  <TrendingUp className="w-4 h-4 text-green-600" />
                  <span className="text-green-600 font-black text-sm">+2.45%</span>
                  <span className="text-muted-foreground text-xs font-mono">TODAY</span>
                </div>
              </CardContent>
            </Card>

            {/* Glass Card with Hover */}
            <Card className="brutalist-glass liquid-glass-hover rounded-none cursor-pointer">
              <CardHeader>
                <CardTitle className="font-black uppercase tracking-tighter">Market Status</CardTitle>
                <CardDescription className="font-mono text-xs">Current trading session</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
                  <span className="font-black uppercase text-lg">OPEN</span>
                </div>
                <div className="text-xs font-mono text-muted-foreground mt-2">
                  Closes in 4h 23m
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="mt-6">
            <CodeBlock
              id="cards"
              code={`<Card className="brutalist-glass rounded-none">
  <CardHeader>
    <CardTitle className="font-black uppercase tracking-tighter">
      Portfolio Value
    </CardTitle>
    <CardDescription className="font-mono text-xs">
      Total account balance
    </CardDescription>
  </CardHeader>
  <CardContent>
    <div className="text-4xl font-black">$124,567.89</div>
  </CardContent>
</Card>`}
            />
          </div>
        </section>

        {/* ===================================================================
            TYPOGRAPHY
            =================================================================== */}
        <section>
          <div className="mb-8">
            <h2 className="text-3xl font-black uppercase tracking-tighter mb-2">Typography</h2>
            <p className="text-muted-foreground font-mono text-sm">
              Font styles and text utilities
            </p>
          </div>

          <div className="brutalist-glass p-6 space-y-8">
            <div className="space-y-4">
              <h1 className="text-6xl font-black uppercase tracking-tighter">Heading 1</h1>
              <h2 className="text-5xl font-black uppercase tracking-tighter">Heading 2</h2>
              <h3 className="text-4xl font-black uppercase tracking-tighter">Heading 3</h3>
              <h4 className="text-3xl font-black uppercase tracking-tighter">Heading 4</h4>
              <h5 className="text-2xl font-black uppercase tracking-tighter">Heading 5</h5>
              <h6 className="text-xl font-black uppercase tracking-tighter">Heading 6</h6>
            </div>

            <div className="border-t-2 border-foreground/20 pt-8 space-y-4">
              <p className="text-lg">Large body text for important content and descriptions.</p>
              <p className="text-base">Default body text for general content and paragraphs.</p>
              <p className="text-sm">Small text for secondary information and captions.</p>
              <p className="text-xs">Extra small text for labels and metadata.</p>
            </div>

            <div className="border-t-2 border-foreground/20 pt-8 space-y-4">
              <p className="font-mono text-sm">Monospace font for code and data: AAPL $150.25</p>
              <p className="font-black uppercase text-sm">Bold uppercase for emphasis</p>
              <p className="text-muted-foreground text-sm">Muted text for less important content</p>
            </div>

            <CodeBlock
              id="typography"
              code={`<h1 className="text-6xl font-black uppercase tracking-tighter">
  Heading 1
</h1>

<p className="font-mono text-sm">
  Monospace: AAPL $150.25
</p>

<p className="text-muted-foreground text-sm">
  Muted text
</p>`}
            />
          </div>
        </section>

        {/* ===================================================================
            USAGE GUIDELINES
            =================================================================== */}
        <section>
          <div className="mb-8">
            <h2 className="text-3xl font-black uppercase tracking-tighter mb-2">Usage Guidelines</h2>
            <p className="text-muted-foreground font-mono text-sm">
              Best practices for implementing the design system
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="brutalist-glass p-6 space-y-4">
              <h3 className="font-black uppercase text-sm flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-green-600" />
                Do's
              </h3>
              <ul className="space-y-2 text-sm">
                <li className="flex items-start gap-2">
                  <span className="text-green-600 font-black">✓</span>
                  <span>Use <code className="font-mono bg-foreground/10 px-1">brutalist-glass</code> for containers</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-600 font-black">✓</span>
                  <span>Apply <code className="font-mono bg-foreground/10 px-1">brutalist-interactive</code> to clickable elements</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-600 font-black">✓</span>
                  <span>Use uppercase + font-black for headings</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-600 font-black">✓</span>
                  <span>Use font-mono for data and numbers</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-600 font-black">✓</span>
                  <span>Maintain consistent border widths (2px or 4px)</span>
                </li>
              </ul>
            </div>

            <div className="brutalist-glass p-6 space-y-4">
              <h3 className="font-black uppercase text-sm flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-red-600" />
                Don'ts
              </h3>
              <ul className="space-y-2 text-sm">
                <li className="flex items-start gap-2">
                  <span className="text-red-600 font-black">✗</span>
                  <span>Don't use rounded corners (keep rounded-none)</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-red-600 font-black">✗</span>
                  <span>Don't mix soft shadows with brutalist components</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-red-600 font-black">✗</span>
                  <span>Don't use thin borders (minimum 2px)</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-red-600 font-black">✗</span>
                  <span>Don't apply hover effects to static containers</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-red-600 font-black">✗</span>
                  <span>Don't use multiple glass effects on nested elements</span>
                </li>
              </ul>
            </div>
          </div>
        </section>

      </div>

      {/* Footer */}
      <div className="border-t-4 border-foreground bg-foreground text-background p-8 mt-16">
        <div className="max-w-7xl mx-auto text-center">
          <p className="font-mono text-sm opacity-80">
            FinanceHub Design System v4.2.1 • Built with shadcn/ui & Tailwind CSS
          </p>
        </div>
      </div>
    </div>
  )
}

// Helper Component
function ColorCard({
  name,
  variable,
  className,
  textColor
}: {
  name: string
  variable: string
  className: string
  textColor: string
}) {
  return (
    <div className={`${className} p-6 h-32 flex flex-col justify-between`}>
      <span className={`${textColor} font-black uppercase text-sm`}>{name}</span>
      <code className={`${textColor} text-xs font-mono opacity-70`}>{variable}</code>
    </div>
  )
}