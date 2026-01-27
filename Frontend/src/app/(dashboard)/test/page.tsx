// app/showcase/page.tsx
'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { Slider } from '@/components/ui/slider'
import { Checkbox } from '@/components/ui/checkbox'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Textarea } from '@/components/ui/textarea'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Progress } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'
import { 
  Search, TrendingUp, TrendingDown, AlertCircle, CheckCircle2, Info, XCircle, Plus, MoreVertical 
} from 'lucide-react'

export default function ShowcasePage() {
  const [sliderValue, setSliderValue] = useState([50])

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto space-y-12">
        {/* Header */}
        <div className="space-y-2">
          <h1 className="text-4xl font-bold tracking-tight">FinanceHub Design System</h1>
          <p className="text-muted-foreground text-lg">
            Professional monochromatic design with liquid glass & subtle accent
          </p>
        </div>

        <Separator />

        {/* Color Palette */}
        <section className="space-y-6">
          <div>
            <h2 className="text-3xl font-semibold mb-2">Color Palette</h2>
            <p className="text-muted-foreground">Monochromatic with subtle blue accent</p>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
            <ColorSwatch name="Primary" varName="--primary" fgVar="--primary-foreground" />
            <ColorSwatch name="Secondary" varName="--secondary" fgVar="--secondary-foreground" />
            <ColorSwatch name="Accent" varName="--accent" fgVar="--accent-foreground" />
            <ColorSwatch name="Muted" varName="--muted" fgVar="--muted-foreground" />
            <ColorSwatch name="Positive" varName="--positive" fgVar="--positive-foreground" />
            <ColorSwatch name="Negative" varName="--negative" fgVar="--negative-foreground" />
            <ColorSwatch name="Border" varName="--border" showBorder />
          </div>
        </section>

        <Separator />

        {/* Liquid Glass Effects */}
        <section className="space-y-6">
          <div>
            <h2 className="text-3xl font-semibold mb-2">Liquid Glass Effects</h2>
            <p className="text-muted-foreground">Apple-inspired frosted glass with blur</p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            <div className="liquid-glass-subtle p-6 rounded-xl">
              <h3 className="font-semibold mb-2">Subtle Glass</h3>
              <p className="text-sm text-muted-foreground">12px blur, light effect</p>
            </div>

            <div className="liquid-glass p-6 rounded-xl">
              <h3 className="font-semibold mb-2">Default Glass</h3>
              <p className="text-sm text-muted-foreground">20px blur, balanced</p>
            </div>

            <div className="liquid-glass-strong p-6 rounded-xl">
              <h3 className="font-semibold mb-2">Strong Glass</h3>
              <p className="text-sm text-muted-foreground">32px blur, prominent</p>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div className="liquid-glass liquid-glass-shimmer p-6 rounded-xl">
              <h3 className="font-semibold mb-2">Glass with Shimmer</h3>
              <p className="text-sm text-muted-foreground">
                Animated shimmer effect - works in both light and dark mode
              </p>
            </div>

            <div className="liquid-glass liquid-glass-hover p-6 rounded-xl cursor-pointer">
              <h3 className="font-semibold mb-2">Glass with Hover</h3>
              <p className="text-sm text-muted-foreground">
                Hover over this card to see lift effect
              </p>
            </div>
          </div>
        </section>

        <Separator />

        {/* Buttons */}
        <section className="space-y-6">
          <div>
            <h2 className="text-3xl font-semibold mb-2">Buttons</h2>
            <p className="text-muted-foreground">All button variants with proper hover states</p>
          </div>

          <div className="space-y-4">
            <div className="flex flex-wrap gap-4 items-center">
              <Button variant="default">Default</Button>
              <Button variant="secondary">Secondary</Button>
              <Button variant="outline">Outline</Button>
              <Button variant="ghost">Ghost</Button>
              <Button variant="destructive">Destructive</Button>
              <Button className="bg-accent text-accent-foreground hover:bg-accent/90">Accent</Button>
            </div>

            <div className="flex flex-wrap gap-4 items-center">
              <Button size="sm">Small</Button>
              <Button size="default">Default</Button>
              <Button size="lg">Large</Button>
              <Button size="icon"><Search className="h-4 w-4" /></Button>
            </div>

            <div className="flex flex-wrap gap-4 items-center">
              <Button disabled>Disabled</Button>
              <Button>
                <TrendingUp className="mr-2 h-4 w-4" />
                With Icon
              </Button>
              <Button variant="outline">
                <Plus className="mr-2 h-4 w-4" />
                Create New
              </Button>
            </div>
          </div>
        </section>

        <Separator />

        {/* Badges */}
        <section className="space-y-6">
          <div>
            <h2 className="text-3xl font-semibold mb-2">Badges</h2>
            <p className="text-muted-foreground">Status indicators and labels</p>
          </div>

          <div className="flex flex-wrap gap-4 items-center">
            <Badge variant="default">Default</Badge>
            <Badge variant="secondary">Secondary</Badge>
            <Badge variant="destructive">Destructive</Badge>
            <Badge variant="outline">Outline</Badge>
            <Badge className="bg-accent text-accent-foreground">Accent</Badge>
            <Badge className="bg-positive text-positive-foreground">+2.5%</Badge>
            <Badge className="bg-negative text-negative-foreground">-1.8%</Badge>
          </div>
        </section>

        <Separator />

        {/* Inputs */}
        <section className="space-y-6">
          <div>
            <h2 className="text-3xl font-semibold mb-2">Form Inputs</h2>
            <p className="text-muted-foreground">All form controls with proper focus states</p>
          </div>

          <div className="grid md:grid-cols-2 gap-6 max-w-4xl">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" placeholder="email@example.com" />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input id="password" type="password" placeholder="••••••••" />
            </div>

            <div className="space-y-2">
              <Label htmlFor="search">Search</Label>
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input id="search" placeholder="Search assets..." className="pl-10" />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="select">Asset Type</Label>
              <Select>
                <SelectTrigger id="select">
                  <SelectValue placeholder="Select type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="stocks">Stocks</SelectItem>
                  <SelectItem value="crypto">Cryptocurrency</SelectItem>
                  <SelectItem value="forex">Forex</SelectItem>
                  <SelectItem value="commodities">Commodities</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2 md:col-span-2">
              <Label htmlFor="textarea">Notes</Label>
              <Textarea id="textarea" placeholder="Enter your investment notes..." />
            </div>
          </div>
        </section>

        <Separator />

        {/* Form Controls */}
        <section className="space-y-6">
          <div>
            <h2 className="text-3xl font-semibold mb-2">Form Controls</h2>
            <p className="text-muted-foreground">Switches, checkboxes, radio buttons, sliders</p>
          </div>

          <div className="space-y-6 max-w-2xl">
            <div className="flex items-center space-x-2">
              <Switch id="notifications" />
              <Label htmlFor="notifications">Enable price alerts</Label>
            </div>

            <div className="space-y-2">
              <Label>Asset Classes</Label>
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <Checkbox id="stocks" />
                  <Label htmlFor="stocks">Stocks</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox id="crypto" />
                  <Label htmlFor="crypto">Cryptocurrency</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox id="forex" />
                  <Label htmlFor="forex">Forex</Label>
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <Label>Theme Preference</Label>
              <RadioGroup defaultValue="system">
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="light" id="light" />
                  <Label htmlFor="light">Light Mode</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="dark" id="dark" />
                  <Label htmlFor="dark">Dark Mode</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="system" id="system" />
                  <Label htmlFor="system">System</Label>
                </div>
              </RadioGroup>
            </div>

            <div className="space-y-2">
              <Label>Investment Amount - ${sliderValue[0]}k</Label>
              <Slider 
                value={sliderValue} 
                onValueChange={setSliderValue}
                max={100}
                step={5}
              />
            </div>

            <div className="space-y-2">
              <Label>Portfolio Allocation Progress</Label>
              <Progress value={75} />
              <p className="text-xs text-muted-foreground">75% of target allocation</p>
            </div>
          </div>
        </section>

        <Separator />

        {/* Cards */}
        <section className="space-y-6">
          <div>
            <h2 className="text-3xl font-semibold mb-2">Cards</h2>
            <p className="text-muted-foreground">Different card styles and variants</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Standard Card</CardTitle>
                <CardDescription>Default card styling</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Basic card with border and shadow
                </p>
              </CardContent>
            </Card>

            <Card className="liquid-glass">
              <CardHeader>
                <CardTitle>Glass Card</CardTitle>
                <CardDescription>With liquid glass effect</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm">
                  Frosted glass background with blur
                </p>
              </CardContent>
            </Card>

            <div className="liquid-glass p-6 rounded-xl">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <p className="text-sm text-muted-foreground">Portfolio Value</p>
                  <p className="text-3xl font-bold mt-1">$125,430</p>
                </div>
                <button className="p-2 hover:bg-white/20 dark:hover:bg-white/10 rounded-lg transition-colors">
                  <MoreVertical className="h-4 w-4" />
                </button>
              </div>
              
              <div className="flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-positive" />
                <span className="text-sm font-semibold text-positive">
                  +$2,340 (1.90%)
                </span>
              </div>
            </div>
          </div>
        </section>

        <Separator />

        {/* Alerts */}
        <section className="space-y-6">
          <div>
            <h2 className="text-3xl font-semibold mb-2">Alerts</h2>
            <p className="text-muted-foreground">System notifications and messages</p>
          </div>

          <div className="space-y-4 max-w-3xl">
            <Alert>
              <Info className="h-4 w-4" />
              <AlertTitle>Information</AlertTitle>
              <AlertDescription>
                Market data is updated in real-time during trading hours.
              </AlertDescription>
            </Alert>

            <Alert className="bg-positive/10 border-positive/30 text-positive dark:bg-positive/20">
              <CheckCircle2 className="h-4 w-4" />
              <AlertTitle>Success</AlertTitle>
              <AlertDescription>
                Your order has been executed successfully.
              </AlertDescription>
            </Alert>

            <Alert className="bg-yellow-500/10 border-yellow-500/30 text-yellow-600 dark:bg-yellow-500/20 dark:text-yellow-400">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Warning</AlertTitle>
              <AlertDescription>
                Your portfolio is approaching risk limits.
              </AlertDescription>
            </Alert>

            <Alert variant="destructive">
              <XCircle className="h-4 w-4" />
              <AlertTitle>Error</AlertTitle>
              <AlertDescription>
                Failed to connect to market data feed. Retrying...
              </AlertDescription>
            </Alert>
          </div>
        </section>

        <Separator />

        {/* Tabs */}
        <section className="space-y-6">
          <div>
            <h2 className="text-3xl font-semibold mb-2">Tabs</h2>
            <p className="text-muted-foreground">Tabbed navigation component</p>
          </div>

          <Tabs defaultValue="overview" className="max-w-3xl">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="chart">Chart</TabsTrigger>
              <TabsTrigger value="fundamentals">Fundamentals</TabsTrigger>
              <TabsTrigger value="news">News</TabsTrigger>
            </TabsList>
            <TabsContent value="overview">
              <Card>
                <CardHeader>
                  <CardTitle>Overview</CardTitle>
                  <CardDescription>Key metrics and performance</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    Overview content with key metrics, performance indicators, and summary data.
                  </p>
                </CardContent>
              </Card>
            </TabsContent>
            <TabsContent value="chart">
              <Card>
                <CardHeader>
                  <CardTitle>Price Chart</CardTitle>
                  <CardDescription>Technical analysis and trends</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    Interactive price chart with technical indicators and drawing tools.
                  </p>
                </CardContent>
              </Card>
            </TabsContent>
            <TabsContent value="fundamentals">
              <Card>
                <CardHeader>
                  <CardTitle>Fundamentals</CardTitle>
                  <CardDescription>Financial data and ratios</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    Company financials, earnings, revenue, and key financial ratios.
                  </p>
                </CardContent>
              </Card>
            </TabsContent>
            <TabsContent value="news">
              <Card>
                <CardHeader>
                  <CardTitle>News</CardTitle>
                  <CardDescription>Latest market updates</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    Real-time news feed with market-moving events and company announcements.
                  </p>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </section>

        {/* Footer */}
        <div className="liquid-glass-subtle p-6 rounded-xl text-center">
          <p className="text-sm text-muted-foreground">
            All components automatically adapt to light and dark modes • Radius: 0.5rem • Accent: oklch(0.55 0.12 240)
          </p>
        </div>
      </div>
    </div>
  )
}

function ColorSwatch({ 
  name, 
  varName, 
  fgVar, 
  showBorder = false 
}: { 
  name: string
  varName: string
  fgVar?: string
  showBorder?: boolean
}) {
  return (
    <div className="space-y-2">
      <div 
        className={`h-20 rounded-lg flex items-center justify-center font-medium ${showBorder ? 'border-2' : ''}`}
        style={{ 
          backgroundColor: `hsl(var(${varName}))`,
          color: fgVar ? `hsl(var(${fgVar}))` : 'inherit',
          borderColor: showBorder ? `hsl(var(${varName}))` : undefined
        }}
      >
        {name}
      </div>
      <p className="text-xs text-muted-foreground text-center">{varName}</p>
    </div>
  )
}