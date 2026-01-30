'use client'

import { LucideIcon } from 'lucide-react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { cn } from '@/lib/utils'

interface TabItem {
  value: string
  label: string
  icon: LucideIcon
  badge?: string | number
}

interface PageTabsProps {
  tabs: TabItem[]
  defaultValue: string
  children: React.ReactNode
  className?: string
  tabsClassName?: string
}

export function PageTabs({
  tabs,
  defaultValue,
  children,
  className,
  tabsClassName,
}: PageTabsProps) {
  return (
    <div className={className}>
      <Tabs defaultValue={defaultValue}>
        <TabsList className={cn('grid w-full', tabsClassName)}>
          {tabs.map((tab) => (
            <TabsTrigger
              key={tab.value}
              value={tab.value}
              className="relative"
            >
              <tab.icon className="w-4 h-4 mr-2" />
              {tab.label}
              {tab.badge !== undefined && (
                <span className="ml-2 px-2 py-0.5 text-xs bg-primary/20 rounded-full">
                  {tab.badge}
                </span>
              )}
            </TabsTrigger>
          ))}
        </TabsList>
        {children}
      </Tabs>
    </div>
  )
}

interface TabContentWrapperProps {
  value: string
  children: React.ReactNode
  className?: string
}

export function TabContent({ value, children, className }: TabContentWrapperProps) {
  return (
    <TabsContent value={value} className={cn('mt-4', className)}>
      {children}
    </TabsContent>
  )
}
