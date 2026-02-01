'use client'

import * as React from 'react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { AlertTriangle, Shield, X } from 'lucide-react'

interface WarningModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  type: 'live-trading' | 'delete-account' | 'disconnect-broker'
  onConfirm: () => void
  title?: string
  message?: string
  confirmText?: string
  cancelText?: string
  className?: string
}

const WARNING_CONFIG = {
  'live-trading': {
    icon: AlertTriangle,
    iconColor: 'text-destructive',
    bgColor: 'bg-destructive/10',
    confirmVariant: 'destructive' as const,
    title: '⚠️ WARNING: LIVE TRADING',
    message: 'You are about to execute REAL trades with REAL MONEY.',
    risks: [
      'Real trades will be executed in your brokerage account',
      'Real money will be at risk',
      'Losses are FINAL and cannot be reversed',
      'This action cannot be undone'
    ]
  },
  'delete-account': {
    icon: AlertTriangle,
    iconColor: 'text-destructive',
    bgColor: 'bg-destructive/10',
    confirmVariant: 'destructive' as const,
    title: '⚠️ WARNING: DELETE ACCOUNT',
    message: 'You are about to permanently delete your account.',
    risks: [
      'All your data will be permanently deleted',
      'This action cannot be reversed',
      'You will lose access to all your portfolios',
      'Your trading history will be removed'
    ]
  },
  'disconnect-broker': {
    icon: AlertTriangle,
    iconColor: 'text-warning',
    bgColor: 'bg-warning/10',
    confirmVariant: 'default' as const,
    title: '⚠️ DISCONNECT BROKER',
    message: 'You are about to disconnect your brokerage account.',
    risks: [
      'You will no longer be able to execute trades',
      'Your positions will not be synced',
      'Real-time data may be unavailable'
    ]
  }
}

export function WarningModal({
  open,
  onOpenChange,
  type,
  onConfirm,
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  className
}: WarningModalProps) {
  const config = WARNING_CONFIG[type]
  const Icon = config.icon
  const [acknowledged, setAcknowledged] = React.useState(false)
  const [isConfirming, setIsConfirming] = React.useState(false)

  const handleConfirm = async () => {
    setIsConfirming(true)
    try {
      await onConfirm()
      setAcknowledged(false)
    } finally {
      setIsConfirming(false)
    }
  }

  const handleCancel = () => {
    setAcknowledged(false)
    onOpenChange(false)
  }

  if (!open) return null

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      role="dialog"
      aria-modal="true"
      aria-labelledby="warning-modal-title"
    >
      <div className={cn(
        'w-full max-w-md rounded-none border-2 p-6 shadow-xl',
        'bg-background',
        className
      )}>
        <div className="flex items-start gap-4 mb-6">
          <div className={cn('p-3 rounded-none border-2', config.bgColor, config.iconColor)}>
            <Icon className="h-6 w-6" aria-hidden="true" />
          </div>
          <div className="flex-1">
            <h2 id="warning-modal-title" className="text-lg font-black uppercase">
              {title || config.title}
            </h2>
            <p className="text-sm text-muted-foreground mt-1">
              {message || config.message}
            </p>
          </div>
        </div>

        <div className={cn('p-4 mb-6 border-l-4', config.bgColor, config.iconColor.replace('text', 'border'))}>
          <h3 className="font-bold uppercase text-xs mb-3 flex items-center gap-2">
            <Shield className="h-3 w-3" aria-hidden="true" />
            Key Risks
          </h3>
          <ul className="space-y-2">
            {config.risks.map((risk, index) => (
              <li key={index} className="flex items-start gap-2 text-sm">
                <span className="text-muted-foreground font-mono text-xs mt-0.5">•</span>
                <span>{risk}</span>
              </li>
            ))}
          </ul>
        </div>

        <label className="flex items-start gap-3 mb-6 cursor-pointer">
          <Checkbox
            checked={acknowledged}
            onCheckedChange={(checked) => setAcknowledged(checked as boolean)}
            id="acknowledge-risks"
            className="rounded-none border-2 mt-0.5"
          />
          <span className="text-sm">
            I understand the risks and want to proceed
          </span>
        </label>

        <div className="flex gap-3">
          <Button
            variant="outline"
            onClick={handleCancel}
            className="flex-1 font-black uppercase rounded-none border-2"
          >
            {cancelText}
          </Button>
          <Button
            variant={config.confirmVariant}
            onClick={handleConfirm}
            disabled={!acknowledged || isConfirming}
            className={cn(
              'flex-1 font-black uppercase rounded-none',
              config.confirmVariant === 'destructive' ? '' : 'bg-primary'
            )}
          >
            {isConfirming ? 'Processing...' : confirmText}
          </Button>
        </div>
      </div>
    </div>
  )
}
