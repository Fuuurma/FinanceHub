'use client'

import { useState, useEffect } from 'react'
import { useTheme } from 'next-themes'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Textarea } from '@/components/ui/textarea'
import { useSettingsStore } from '@/stores/settingsStore'
import {
  User,
  Bell,
  Palette,
  Shield,
  Monitor,
  Moon,
  Sun,
  Check,
  Save,
  Loader2,
  Download,
  Upload,
  RotateCcw,
} from 'lucide-react'

export default function SettingsPage() {
  const { setTheme: setNextTheme, theme: nextTheme } = useTheme()
  
  const {
    display,
    notifications,
    profile,
    investment,
    isLoading,
    error,
    lastSaved,
    setDisplaySettings,
    setNotificationSettings,
    setProfileSettings,
    setInvestmentProfile,
    setTheme,
    saveSettings,
    resetSettings,
    exportSettings,
    importSettings,
  } = useSettingsStore()

  const [saved, setSaved] = useState(false)
  const [importError, setImportError] = useState<string | null>(null)

  useEffect(() => {
    if (nextTheme) {
      setTheme(nextTheme as 'light' | 'dark' | 'system')
    }
  }, [nextTheme, setTheme])

  const handleThemeChange = (newTheme: 'light' | 'dark' | 'system') => {
    setTheme(newTheme)
    setNextTheme(newTheme)
  }

  const handleSave = async () => {
    await saveSettings()
    setSaved(true)
    setTimeout(() => setSaved(false), 3000)
  }

  const handleExport = () => {
    const json = exportSettings()
    const blob = new Blob([json], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `financehub-settings-${new Date().toISOString().split('T')[0]}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  const handleImport = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const json = e.target?.result as string
        importSettings(json)
        setImportError(null)
        setSaved(true)
        setTimeout(() => setSaved(false), 3000)
      } catch (err) {
        setImportError(err instanceof Error ? err.message : 'Failed to import settings')
      }
    }
    reader.readAsText(file)
    event.target.value = ''
  }

  const handleReset = () => {
    if (confirm('Are you sure you want to reset all settings to default? This cannot be undone.')) {
      resetSettings()
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    }
  }

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight">Settings</h1>
          <p className="text-muted-foreground mt-1 text-sm">
            Manage your account preferences and application settings
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="outline" size="sm" onClick={handleExport}>
            <Download className="h-4 w-4 mr-2" />
            <span className="hidden sm:inline">Export</span>
          </Button>
          <Button variant="outline" size="sm" asChild>
            <label htmlFor="import-settings" className="cursor-pointer">
              <Upload className="h-4 w-4 mr-2" />
              <span className="hidden sm:inline">Import</span>
            </label>
          </Button>
          <input
            id="import-settings"
            type="file"
            accept=".json"
            className="hidden"
            onChange={handleImport}
          />
          <Button variant="outline" size="sm" onClick={handleReset}>
            <RotateCcw className="h-4 w-4 mr-2" />
            <span className="hidden sm:inline">Reset</span>
          </Button>
        </div>
      </div>

      {importError && (
        <Alert variant="destructive">
          <AlertDescription>{importError}</AlertDescription>
        </Alert>
      )}

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Tabs defaultValue="appearance" className="space-y-6">
        <TabsList>
          <TabsTrigger value="appearance">
            <Palette className="h-4 w-4 mr-2" />
            Appearance
          </TabsTrigger>
          <TabsTrigger value="notifications">
            <Bell className="h-4 w-4 mr-2" />
            Notifications
          </TabsTrigger>
          <TabsTrigger value="account">
            <User className="h-4 w-4 mr-2" />
            Account
          </TabsTrigger>
          <TabsTrigger value="security">
            <Shield className="h-4 w-4 mr-2" />
            Security
          </TabsTrigger>
        </TabsList>

        <TabsContent value="appearance" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Theme</CardTitle>
              <CardDescription>
                Choose how FinanceHub appears to you
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid gap-3 sm:gap-4 md:grid-cols-3">
                <button
                  onClick={() => handleThemeChange('light')}
                  aria-pressed={display.theme === 'light'}
                  aria-label="Select light theme - Clean and bright interface"
                  className={`flex flex-col items-center gap-2 sm:gap-3 p-4 sm:p-6 border-2 rounded-lg transition-all ${
                    display.theme === 'light' ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50'
                  }`}
                >
                  <div className="p-2 sm:p-3 bg-white border-2 rounded-lg shadow-sm">
                    <Sun className="h-5 w-5 sm:h-6 sm:w-6 text-amber-500" />
                  </div>
                  <div className="text-center">
                    <p className="font-medium">Light</p>
                    <p className="text-xs sm:text-sm text-muted-foreground">Clean & bright</p>
                  </div>
                  {display.theme === 'light' && (
                    <Check className="h-4 w-4 sm:h-5 sm:w-5 text-primary" />
                  )}
                </button>

                <button
                  onClick={() => handleThemeChange('dark')}
                  aria-pressed={display.theme === 'dark'}
                  aria-label="Select dark theme - Easy on the eyes"
                  className={`flex flex-col items-center gap-2 sm:gap-3 p-4 sm:p-6 border-2 rounded-lg transition-all ${
                    display.theme === 'dark' ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50'
                  }`}
                >
                  <div className="p-2 sm:p-3 bg-slate-900 border-2 rounded-lg shadow-sm">
                    <Moon className="h-5 w-5 sm:h-6 sm:w-6 text-blue-400" />
                  </div>
                  <div className="text-center">
                    <p className="font-medium">Dark</p>
                    <p className="text-xs sm:text-sm text-muted-foreground">Easy on the eyes</p>
                  </div>
                  {display.theme === 'dark' && (
                    <Check className="h-4 w-4 sm:h-5 sm:w-5 text-primary" />
                  )}
                </button>

                <button
                  onClick={() => handleThemeChange('system')}
                  aria-pressed={display.theme === 'system'}
                  aria-label="Select system theme - Match your operating system setting"
                  className={`flex flex-col items-center gap-2 sm:gap-3 p-4 sm:p-6 border-2 rounded-lg transition-all ${
                    display.theme === 'system' ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50'
                  }`}
                >
                  <div className="p-2 sm:p-3 bg-gradient-to-br from-white to-slate-900 border-2 rounded-lg shadow-sm">
                    <Monitor className="h-5 w-5 sm:h-6 sm:w-6 text-purple-500" />
                  </div>
                  <div className="text-center">
                    <p className="font-medium">System</p>
                    <p className="text-xs sm:text-sm text-muted-foreground">Match OS setting</p>
                  </div>
                  {display.theme === 'system' && (
                    <Check className="h-4 w-4 sm:h-5 sm:w-5 text-primary" />
                  )}
                </button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Display Preferences</CardTitle>
              <CardDescription>
                Customize how information is displayed
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="compact-mode">Compact Mode</Label>
                  <p className="text-sm text-muted-foreground">
                    Use more compact spacing in the interface
                  </p>
                </div>
                <Switch
                  id="compact-mode"
                  aria-label="Toggle compact mode"
                  checked={display.compactMode}
                  onCheckedChange={(checked) => setDisplaySettings({ compactMode: checked })}
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="show-price-change">Show Price Change</Label>
                  <p className="text-sm text-muted-foreground">
                    Display percentage change on all assets
                  </p>
                </div>
                <Switch
                  id="show-price-change"
                  aria-label="Toggle price change display"
                  checked={display.showPriceChange}
                  onCheckedChange={(checked) => setDisplaySettings({ showPriceChange: checked })}
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="animated-charts">Animated Charts</Label>
                  <p className="text-sm text-muted-foreground">
                    Enable smooth animations in charts
                  </p>
                </div>
                <Switch
                  id="animated-charts"
                  aria-label="Toggle chart animations"
                  checked={display.animatedCharts}
                  onCheckedChange={(checked) => setDisplaySettings({ animatedCharts: checked })}
                />
              </div>

              <Separator />

              <div className="space-y-2">
                <Label>Default Currency</Label>
                <Select
                  value={display.currency}
                  onValueChange={(value) => setDisplaySettings({ currency: value as any })}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="USD">USD - US Dollar</SelectItem>
                    <SelectItem value="EUR">EUR - Euro</SelectItem>
                    <SelectItem value="GBP">GBP - British Pound</SelectItem>
                    <SelectItem value="JPY">JPY - Japanese Yen</SelectItem>
                    <SelectItem value="AUD">AUD - Australian Dollar</SelectItem>
                    <SelectItem value="CAD">CAD - Canadian Dollar</SelectItem>
                    <SelectItem value="CHF">CHF - Swiss Franc</SelectItem>
                    <SelectItem value="CNY">CNY - Chinese Yuan</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Number Format</Label>
                <Select
                  value={display.numberFormat}
                  onValueChange={(value) => setDisplaySettings({ numberFormat: value as any })}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1,234.56">1,234.56 (US/UK)</SelectItem>
                    <SelectItem value="1 234.56">1 234.56 (EU)</SelectItem>
                    <SelectItem value="1.234,56">1.234,56 (Latin America)</SelectItem>
                    <SelectItem value="1234.56">1234.56 (No separator)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="notifications" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Alert Notifications</CardTitle>
              <CardDescription>
                Manage how you receive price and portfolio alerts
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Enable Notifications</Label>
                  <p className="text-sm text-muted-foreground">
                    Turn all notifications on or off
                  </p>
                </div>
                <Switch
                  checked={notifications.enabled}
                  onCheckedChange={(checked) => setNotificationSettings({ enabled: checked })}
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Price Alerts</Label>
                  <p className="text-sm text-muted-foreground">
                    Get notified when assets hit your target price
                  </p>
                </div>
                <Switch
                  checked={notifications.types.price}
                  onCheckedChange={(checked) => 
                    setNotificationSettings({ types: { ...notifications.types, price: checked } })
                  }
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Portfolio Changes</Label>
                  <p className="text-sm text-muted-foreground">
                    Notify about significant portfolio movements
                  </p>
                </div>
                <Switch
                  checked={notifications.types.portfolio}
                  onCheckedChange={(checked) => 
                    setNotificationSettings({ types: { ...notifications.types, portfolio: checked } })
                  }
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Market News</Label>
                  <p className="text-sm text-muted-foreground">
                    Receive breaking news for your watchlist
                  </p>
                </div>
                <Switch
                  checked={notifications.types.news}
                  onCheckedChange={(checked) => 
                    setNotificationSettings({ types: { ...notifications.types, news: checked } })
                  }
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Email Digest</Label>
                  <p className="text-sm text-muted-foreground">
                    Daily summary of your portfolio performance
                  </p>
                </div>
                <Switch
                  checked={notifications.types.digest}
                  onCheckedChange={(checked) => 
                    setNotificationSettings({ types: { ...notifications.types, digest: checked } })
                  }
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Notification Channels</CardTitle>
              <CardDescription>
                Choose how you want to receive notifications
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Push Notifications</Label>
                  <p className="text-sm text-muted-foreground">
                    Receive notifications in your browser
                  </p>
                </div>
                <Switch
                  checked={notifications.channels.push}
                  onCheckedChange={(checked) => 
                    setNotificationSettings({ channels: { ...notifications.channels, push: checked } })
                  }
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Email Notifications</Label>
                  <p className="text-sm text-muted-foreground">
                    Receive notifications via email
                  </p>
                </div>
                <Switch
                  checked={notifications.channels.email}
                  onCheckedChange={(checked) => 
                    setNotificationSettings({ channels: { ...notifications.channels, email: checked } })
                  }
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>SMS Notifications</Label>
                  <p className="text-sm text-muted-foreground">
                    Get critical alerts via SMS
                  </p>
                </div>
                <Switch
                  checked={notifications.channels.sms}
                  onCheckedChange={(checked) => 
                    setNotificationSettings({ channels: { ...notifications.channels, sms: checked } })
                  }
                />
              </div>

              <Separator />

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label>Quiet Hours</Label>
                  <Switch
                    checked={notifications.quietHours.enabled}
                    onCheckedChange={(checked) => 
                      setNotificationSettings({ 
                        quietHours: { ...notifications.quietHours, enabled: checked } 
                      })
                    }
                  />
                </div>
                {notifications.quietHours.enabled && (
                  <div className="grid gap-4 md:grid-cols-2 mt-4">
                    <div className="space-y-2">
                      <Label className="text-sm text-muted-foreground">Start Time</Label>
                      <Input
                        type="time"
                        value={notifications.quietHours.startTime}
                        onChange={(e) => 
                          setNotificationSettings({ 
                            quietHours: { ...notifications.quietHours, startTime: e.target.value } 
                          })
                        }
                      />
                    </div>
                    <div className="space-y-2">
                      <Label className="text-sm text-muted-foreground">End Time</Label>
                      <Input
                        type="time"
                        value={notifications.quietHours.endTime}
                        onChange={(e) => 
                          setNotificationSettings({ 
                            quietHours: { ...notifications.quietHours, endTime: e.target.value } 
                          })
                        }
                      />
                    </div>
                  </div>
                )}
                <p className="text-xs text-muted-foreground">
                  Notifications will be silenced during these hours
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="account" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Profile Information</CardTitle>
              <CardDescription>
                Update your personal information
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label>First Name</Label>
                  <Input
                    value={profile.firstName || ''}
                    onChange={(e) => setProfileSettings({ firstName: e.target.value })}
                    placeholder="John"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Last Name</Label>
                  <Input
                    value={profile.lastName || ''}
                    onChange={(e) => setProfileSettings({ lastName: e.target.value })}
                    placeholder="Doe"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Email Address</Label>
                <Input
                  type="email"
                  value={profile.email || ''}
                  onChange={(e) => setProfileSettings({ email: e.target.value })}
                  placeholder="john@example.com"
                />
              </div>

              <div className="space-y-2">
                <Label>Phone Number</Label>
                <Input
                  type="tel"
                  value={profile.phone || ''}
                  onChange={(e) => setProfileSettings({ phone: e.target.value })}
                  placeholder="+1 (555) 123-4567"
                />
              </div>

              <div className="space-y-2">
                <Label>Timezone</Label>
                <Select
                  value={profile.timezone}
                  onValueChange={(value) => setProfileSettings({ timezone: value as any })}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="America/New_York">Eastern Time (ET)</SelectItem>
                    <SelectItem value="America/Chicago">Central Time (CT)</SelectItem>
                    <SelectItem value="America/Denver">Mountain Time (MT)</SelectItem>
                    <SelectItem value="America/Los_Angeles">Pacific Time (PT)</SelectItem>
                    <SelectItem value="UTC">UTC (Coordinated Universal Time)</SelectItem>
                    <SelectItem value="Europe/London">London (GMT/BST)</SelectItem>
                    <SelectItem value="Europe/Paris">Central European (CET)</SelectItem>
                    <SelectItem value="Asia/Tokyo">Japan (JST)</SelectItem>
                    <SelectItem value="Asia/Shanghai">China (CST)</SelectItem>
                    <SelectItem value="Asia/Hong_Kong">Hong Kong (HKT)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Bio</Label>
                <Textarea
                  value={profile.bio || ''}
                  onChange={(e) => setProfileSettings({ bio: e.target.value })}
                  placeholder="Tell us a bit about yourself..."
                  rows={3}
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Investment Profile</CardTitle>
              <CardDescription>
                Your investment preferences and risk tolerance
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label>Risk Tolerance</Label>
                <Select
                  value={investment.riskTolerance}
                  onValueChange={(value) => setInvestmentProfile({ riskTolerance: value as any })}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="conservative">Conservative</SelectItem>
                    <SelectItem value="moderate">Moderate</SelectItem>
                    <SelectItem value="aggressive">Aggressive</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Investment Goals</Label>
                <Select
                  value={investment.goal}
                  onValueChange={(value) => setInvestmentProfile({ goal: value as any })}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="growth">Growth</SelectItem>
                    <SelectItem value="income">Income</SelectItem>
                    <SelectItem value="balanced">Balanced</SelectItem>
                    <SelectItem value="preservation">Capital Preservation</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Preferred Asset Classes</Label>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { key: 'stocks', label: 'Stocks' },
                    { key: 'etfs', label: 'ETFs' },
                    { key: 'cryptocurrency', label: 'Cryptocurrency' },
                    { key: 'forex', label: 'Forex' },
                    { key: 'commodities', label: 'Commodities' },
                    { key: 'bonds', label: 'Bonds' },
                  ].map((asset) => (
                    <div key={asset.key} className="flex items-center space-x-2 p-2 border rounded">
                      <input
                        type="checkbox"
                        id={asset.key}
                        className="rounded"
                        checked={investment.preferredAssetClasses.includes(asset.key as any)}
                        onChange={(e) => {
                          const updated = e.target.checked
                            ? [...investment.preferredAssetClasses, asset.key as any]
                            : investment.preferredAssetClasses.filter((c) => c !== asset.key)
                          setInvestmentProfile({ preferredAssetClasses: updated })
                        }}
                      />
                      <Label htmlFor={asset.key} className="text-sm font-normal cursor-pointer">
                        {asset.label}
                      </Label>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="security" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Password</CardTitle>
              <CardDescription>
                Change your password to keep your account secure
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label>Current Password</Label>
                <Input type="password" placeholder="••••••••" />
              </div>

              <div className="space-y-2">
                <Label>New Password</Label>
                <Input type="password" placeholder="••••••••" />
              </div>

              <div className="space-y-2">
                <Label>Confirm New Password</Label>
                <Input type="password" placeholder="••••••••" />
              </div>

              <Alert>
                <AlertDescription className="text-sm">
                  Password must be at least 8 characters and include uppercase, lowercase, number, and special character.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Two-Factor Authentication</CardTitle>
              <CardDescription>
                Add an extra layer of security to your account
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center gap-4">
                  <div className="p-2 bg-primary/10 rounded-lg">
                    <Shield className="h-6 w-6 text-primary" />
                  </div>
                  <div>
                    <p className="font-medium">Authenticator App</p>
                    <p className="text-sm text-muted-foreground">Use an authenticator app like Google Authenticator</p>
                  </div>
                </div>
                <Button variant="outline">Enable</Button>
              </div>

              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center gap-4">
                  <div className="p-2 bg-primary/10 rounded-lg">
                    <Bell className="h-6 w-6 text-primary" />
                  </div>
                  <div>
                    <p className="font-medium">SMS Verification</p>
                    <p className="text-sm text-muted-foreground">Receive a code via SMS</p>
                  </div>
                </div>
                <Button variant="outline">Enable</Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Active Sessions</CardTitle>
              <CardDescription>
                Manage devices that have access to your account
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center gap-4">
                    <div className="p-2 bg-green-500/10 rounded-lg">
                      <Monitor className="h-6 w-6 text-green-600" />
                    </div>
                    <div>
                      <p className="font-medium">MacBook Pro - Chrome</p>
                      <p className="text-sm text-muted-foreground">San Francisco, CA • Current session</p>
                    </div>
                  </div>
                  <Badge variant="secondary">Active</Badge>
                </div>

                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center gap-4">
                    <div className="p-2 bg-muted rounded-lg">
                      <Monitor className="h-6 w-6 text-muted-foreground" />
                    </div>
                    <div>
                      <p className="font-medium">iPhone 14 Pro - Safari</p>
                      <p className="text-sm text-muted-foreground">San Francisco, CA • Last active 2 hours ago</p>
                    </div>
                  </div>
                  <Button variant="outline" size="sm">Revoke</Button>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-destructive/50">
            <CardHeader>
              <CardTitle className="text-destructive">Danger Zone</CardTitle>
              <CardDescription>
                Irreversible actions that affect your account
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button variant="outline" className="w-full" onClick={handleExport}>
                <Download className="h-4 w-4 mr-2" />
                Export All Data
              </Button>
              <Button variant="destructive" className="w-full">
                Delete Account
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <div className="flex justify-end gap-3">
        {saved && (
          <div className="flex items-center gap-2 text-green-600 mr-auto">
            <Check className="h-4 w-4" />
            <span className="text-sm font-medium">Settings saved successfully</span>
          </div>
        )}
        {lastSaved && (
          <span className="text-sm text-muted-foreground mr-auto">
            Last saved: {new Date(lastSaved).toLocaleString()}
          </span>
        )}
        <Button variant="outline" disabled={isLoading}>
          Cancel
        </Button>
        <Button onClick={handleSave} disabled={isLoading}>
          {isLoading ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Saving...
            </>
          ) : (
            <>
              <Save className="h-4 w-4 mr-2" />
              Save Changes
            </>
          )}
        </Button>
      </div>
    </div>
  )
}
