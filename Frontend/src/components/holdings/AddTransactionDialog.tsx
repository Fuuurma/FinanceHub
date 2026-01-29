'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Calendar, DollarSign, Hash, FileText, Loader2 } from 'lucide-react'
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
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Calendar as CalendarComponent } from '@/components/ui/calendar'
import type { TransactionType, AssetClass } from '@/lib/types/holdings'
import { TRANSACTION_TYPE_LABELS, ASSET_CLASS_LABELS } from '@/lib/types/holdings'
import { cn } from '@/lib/utils'

const transactionSchema = z.object({
  symbol: z.string().min(1, 'Symbol is required').max(10, 'Symbol too long'),
  type: z.enum(['buy', 'sell', 'dividend', 'transfer', 'split', 'fee', 'deposit', 'withdrawal']),
  asset_class: z.enum(['stocks', 'crypto', 'bonds', 'etf', 'options', 'cash', 'commodities', 'real_estate', 'other']),
  quantity: z.coerce.number().positive('Quantity must be positive'),
  price: z.coerce.number().nonnegative('Price must be non-negative'),
  fees: z.coerce.number().min(0, 'Fees must be non-negative').default(0),
  date: z.date({ required_error: 'Date is required' }),
  notes: z.string().optional(),
})

type TransactionFormData = z.infer<typeof transactionSchema>

interface AddTransactionDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmit: (data: TransactionFormData) => Promise<void>
  existingHoldings?: { symbol: string; name: string; quantity: number; average_cost: number }[]
}

export function AddTransactionDialog({
  open,
  onOpenChange,
  onSubmit,
  existingHoldings = [],
}: AddTransactionDialogProps) {
  const [loading, setLoading] = useState(false)

  const form = useForm<TransactionFormData>({
    resolver: zodResolver(transactionSchema),
    defaultValues: {
      type: 'buy',
      asset_class: 'stocks',
      quantity: 1,
      price: 0,
      fees: 0,
    },
  })

  const { watch, setValue, handleSubmit, reset, formState: { errors } } = form
  const watchedType = watch('type')
  const watchedSymbol = watch('symbol')

  const handleSymbolSelect = (symbol: string) => {
    const holding = existingHoldings.find(h => h.symbol === symbol)
    if (holding) {
      setValue('symbol', symbol)
      setValue('price', holding.average_cost)
    }
  }

  const calculateTotal = () => {
    const quantity = watch('quantity') || 0
    const price = watch('price') || 0
    const fees = watch('fees') || 0
    const subtotal = quantity * price
    if (watchedType === 'sell' || watchedType === 'withdrawal' || watchedType === 'fee') {
      return subtotal + fees
    }
    return subtotal + fees
  }

  const onFormSubmit = async (data: TransactionFormData) => {
    setLoading(true)
    try {
      await onSubmit(data)
      reset()
      onOpenChange(false)
    } finally {
      setLoading(false)
    }
  }

  const assetClassOptions = Object.entries(ASSET_CLASS_LABELS).map(([value, label]) => ({
    value,
    label,
  }))

  const transactionTypeOptions = Object.entries(TRANSACTION_TYPE_LABELS).map(([value, label]) => ({
    value,
    label,
  }))

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Add Transaction</DialogTitle>
          <DialogDescription>
            Record a new buy, sell, dividend, or other transaction.
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="type"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Type</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select type" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {transactionTypeOptions.map((option) => (
                          <SelectItem key={option.value} value={option.value}>
                            {option.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="asset_class"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Asset Class</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select class" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {assetClassOptions.map((option) => (
                          <SelectItem key={option.value} value={option.value}>
                            {option.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="symbol"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Symbol</FormLabel>
                    <FormControl>
                      <div className="relative">
                        <Hash className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <Input
                          {...field}
                          placeholder="AAPL"
                          className="pl-9 uppercase"
                          onChange={(e) => {
                            field.onChange(e.target.value.toUpperCase())
                          }}
                        />
                      </div>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="date"
                render={({ field }) => (
                  <FormItem className="flex flex-col">
                    <FormLabel>Date</FormLabel>
                    <Popover>
                      <PopoverTrigger asChild>
                        <FormControl>
                          <Button
                            variant="outline"
                            className={cn(
                              'pl-3 text-left font-normal',
                              !field.value && 'text-muted-foreground'
                            )}
                          >
                            {field.value ? (
                              field.value.toLocaleDateString()
                            ) : (
                              <span>Pick a date</span>
                            )}
                            <Calendar className="ml-auto h-4 w-4 opacity-50" />
                          </Button>
                        </FormControl>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0" align="start">
                        <CalendarComponent
                          mode="single"
                          selected={field.value}
                          onSelect={field.onChange}
                          disabled={(date) => date > new Date()}
                          initialFocus
                        />
                      </PopoverContent>
                    </Popover>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="quantity"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Quantity</FormLabel>
                    <FormControl>
                      <div className="relative">
                        <Hash className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <Input
                          {...field}
                          type="number"
                          min="0"
                          step="0.0001"
                          className="pl-9"
                        />
                      </div>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="price"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Price</FormLabel>
                    <FormControl>
                      <div className="relative">
                        <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <Input
                          {...field}
                          type="number"
                          min="0"
                          step="0.01"
                          className="pl-9"
                        />
                      </div>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <FormField
              control={form.control}
              name="fees"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Fees (optional)</FormLabel>
                  <FormControl>
                    <div className="relative">
                      <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input
                        {...field}
                        type="number"
                        min="0"
                        step="0.01"
                        className="pl-9"
                      />
                    </div>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="p-3 bg-muted rounded-lg">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Total Amount:</span>
                <span className="font-semibold">
                  ${calculateTotal().toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </span>
              </div>
            </div>

            <FormField
              control={form.control}
              name="notes"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Notes (optional)</FormLabel>
                  <FormControl>
                    <div className="relative">
                      <FileText className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                      <Textarea
                        {...field}
                        placeholder="Add any notes..."
                        className="pl-9 min-h-[80px]"
                      />
                    </div>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={loading}>
                {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Add Transaction
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
