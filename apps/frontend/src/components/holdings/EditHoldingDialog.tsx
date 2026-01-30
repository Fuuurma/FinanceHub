'use client'

import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import type { Holding, AssetClass } from '@/lib/types/holdings'
import { ASSET_CLASS_LABELS } from '@/lib/types/holdings'
import { cn } from '@/lib/utils'

const editHoldingSchema = z.object({
  quantity: z.coerce.number().positive('Quantity must be positive'),
  average_cost: z.coerce.number().positive('Average cost must be positive'),
  current_price: z.coerce.number().nonnegative('Current price must be non-negative').optional(),
  sector: z.string().optional(),
  exchange: z.string().optional(),
})

type EditHoldingFormData = z.infer<typeof editHoldingSchema>

interface EditHoldingDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  holding: Holding | null
  onSubmit: (id: string, data: EditHoldingFormData) => Promise<void>
}

export function EditHoldingDialog({
  open,
  onOpenChange,
  holding,
  onSubmit,
}: EditHoldingDialogProps) {
  const [loading, setLoading] = useState(false)

  const form = useForm<EditHoldingFormData>({
    resolver: zodResolver(editHoldingSchema) as any,
    defaultValues: {
      quantity: 0,
      average_cost: 0,
      current_price: undefined,
      sector: '',
      exchange: '',
    },
  })

  useEffect(() => {
    if (holding) {
      form.reset({
        quantity: holding.quantity,
        average_cost: holding.average_cost,
        current_price: holding.current_price,
        sector: holding.sector || '',
        exchange: holding.exchange || '',
      })
    }
  }, [holding, form])

  const { watch, handleSubmit, reset, formState: { errors } } = form
  const watchedQuantity = watch('quantity')
  const watchedAverageCost = watch('average_cost')

  const calculateCurrentValue = () => {
    return watchedQuantity * watchedAverageCost
  }

  const calculateUnrealizedPnL = () => {
    const currentValue = watchedQuantity * (watch('current_price') || watchedAverageCost)
    const costBasis = watchedQuantity * watchedAverageCost
    return {
      value: currentValue - costBasis,
      percent: costBasis > 0 ? ((currentValue - costBasis) / costBasis) * 100 : 0,
    }
  }

  const handleFormSubmit = async (data: EditHoldingFormData) => {
    if (!holding) return

    setLoading(true)
    try {
      await onSubmit(holding.id, data)
      onOpenChange(false)
      reset()
    } catch (error) {
      console.error('Failed to update holding:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value)

  const pnl = calculateUnrealizedPnL()

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Edit Holding</DialogTitle>
          <DialogDescription>
            Update the details for {holding?.symbol} - {holding?.name}
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="quantity"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Quantity</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        step="0.00000001"
                        placeholder="0.00"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="average_cost"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Average Cost</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        step="0.01"
                        placeholder="0.00"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <FormField
              control={form.control}
              name="current_price"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Current Price (Optional)</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      step="0.01"
                      placeholder="Auto-fetched if empty"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="sector"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Sector (Optional)</FormLabel>
                    <FormControl>
                      <Input placeholder="Technology" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="exchange"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Exchange (Optional)</FormLabel>
                    <FormControl>
                      <Input placeholder="NASDAQ" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <div className="border rounded-lg p-4 bg-muted/50 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Cost Basis:</span>
                <span className="font-medium">{formatCurrency(watchedQuantity * watchedAverageCost)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Current Value:</span>
                <span className="font-medium">{formatCurrency(calculateCurrentValue())}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Unrealized P&L:</span>
                <span className={cn(
                  'font-medium',
                  pnl.value >= 0 ? 'text-green-600' : 'text-red-600'
                )}>
                  {formatCurrency(pnl.value)} ({pnl.percent >= 0 ? '+' : ''}{pnl.percent.toFixed(2)}%)
                </span>
              </div>
            </div>

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
                disabled={loading}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={loading}>
                {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Save Changes
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
