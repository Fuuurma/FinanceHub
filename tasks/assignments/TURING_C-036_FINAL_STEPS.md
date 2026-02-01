# 📋 Task Assignment: C-036 Paper Trading Frontend - Final Steps

**Date:** February 1, 2026
**From:** GAUDÍ (Architect)
**To:** Turing (Frontend Coder)
**Priority:** HIGH - Phase 1 Core Feature
**Estimated Effort:** 4-6 hours
**Timeline:** Complete C-036 frontend work

---

## 🎯 OVERVIEW

Complete the Paper Trading frontend by adding the "Close Position" button functionality and writing component tests.

**Current Status:**
- ✅ WebSocket integration complete
- ✅ Real-time portfolio updates working
- ✅ Order forms, charts, confirmation dialogs done
- ⏳ **Missing:** Close Position button, component tests

**Context:**
- Linus backend is complete ✅
- Charo security audit ready
- HADI accessibility fixes identified
- GRACE tests created, need execution

---

## 📋 YOUR TASKS

### Task 1: Close Position Button (2-3h)

**Location:** PaperPortfolioSummary component

**Requirements:**
1. Add "Close Position" button to each position row
2. Button triggers market order to sell entire position
3. Show confirmation dialog before closing
4. Update position status after closing
5. Handle errors (API failures)

**Implementation:**

```typescript
// apps/frontend/src/components/trading/PaperPortfolioSummary.tsx

import { useMutation, useQueryClient } from '@tanstack/react-query'
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog'
import { Button } from '@/components/ui/button'
import { Trash2 } from 'lucide-react'

interface ClosePositionButtonProps {
  symbol: string
  quantity: number
  currentPrice: number
}

export function ClosePositionButton({ symbol, quantity, currentPrice }: ClosePositionButtonProps) {
  const queryClient = useQueryClient()

  const closePositionMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch('/api/trading/positions/close', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol, quantity })
      })
      if (!response.ok) throw new Error('Failed to close position')
      return response.json()
    },
    onSuccess: () => {
      // Invalidate portfolio queries to refetch
      queryClient.invalidateQueries({ queryKey: ['paper-positions'] })
      queryClient.invalidateQueries({ queryKey: ['paper-portfolio'] })
      toast({
        title: 'Position Closed',
        description: `Closed ${quantity} shares of ${symbol}`
      })
    },
    onError: (error: Error) => {
      toast({
        title: 'Failed to Close Position',
        description: error.message,
        variant: 'destructive'
      })
    }
  })

  const handleClose = () => {
    closePositionMutation.mutate()
  }

  const totalValue = quantity * currentPrice

  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>
        <Button
          variant="ghost"
          size="sm"
          className="h-8 w-8 p-0 text-destructive hover:text-destructive hover:bg-destructive/10"
          disabled={closePositionMutation.isPending}
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Close Position</AlertDialogTitle>
          <AlertDialogDescription>
            Are you sure you want to close your position in {symbol}?
            <br /><br />
            <strong>Symbol:</strong> {symbol}<br />
            <strong>Quantity:</strong> {quantity} shares<br />
            <strong>Estimated Value:</strong> ${totalValue.toFixed(2)}<br /><br />
            This will execute a market order to sell all {quantity} shares at the current market price.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction
            onClick={handleClose}
            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            disabled={closePositionMutation.isPending}
          >
            {closePositionMutation.isPending ? 'Closing...' : 'Close Position'}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
```

**Add to position table:**
```typescript
// In positions table row
<TableCell className="text-right">
  <div className="flex items-center justify-end gap-2">
    <ClosePositionButton
      symbol={position.symbol}
      quantity={position.quantity}
      currentPrice={position.current_price}
    />
  </div>
</TableCell>
```

**Accessibility (HADI requirements):**
- Button has descriptive aria-label: `aria-label="Close position for {symbol}"`
- AlertDialog is properly labelled
- Focus management (return focus to trigger after close)
- Keyboard navigation (Esc to cancel, Enter to confirm)

### Task 2: Component Tests (2-3h)

**Test file:** `apps/frontend/src/components/trading/__tests__/PaperPortfolioSummary.test.tsx`

**Test cases:**

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { PaperPortfolioSummary } from '../PaperPortfolioSummary'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { toast } from '@/hooks/use-toast'

// Mock fetch
global.fetch = jest.fn()

// Mock toast
jest.mock('@/hooks/use-toast', () => ({
  toast: jest.fn()
}))

describe('PaperPortfolioSummary', () => {
  let queryClient: QueryClient

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false }
      }
    })
  })

  const mockPositions = [
    {
      id: 1,
      symbol: 'AAPL',
      quantity: 10,
      average_price: 150.00,
      current_price: 155.00,
      total_value: 1550.00,
      total_return: 50.00,
      total_return_percent: 3.33
    },
    {
      id: 2,
      symbol: 'GOOGL',
      quantity: 5,
      average_price: 2800.00,
      current_price: 2850.00,
      total_value: 14250.00,
      total_return: 250.00,
      total_return_percent: 1.79
    }
  ]

  describe('Close Position Button', () => {
    it('renders close button for each position', () => {
      render(
        <QueryClientProvider client={queryClient}>
          <PaperPortfolioSummary />
        </QueryClientProvider>
      )

      expect(screen.getAllByLabelText(/close position/i)).toHaveLength(2)
    })

    it('shows confirmation dialog when clicked', async () => {
      const user = userEvent.setup()

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockPositions
      })

      render(
        <QueryClientProvider client={queryClient}>
          <PaperPortfolioSummary />
        </QueryClientProvider>
      )

      await waitFor(() => {
        expect(screen.getByLabelText(/close position for AAPL/i)).toBeInTheDocument()
      })

      await user.click(screen.getByLabelText(/close position for AAPL/i))

      expect(screen.getByText('Close Position')).toBeInTheDocument()
      expect(screen.getByText(/Are you sure you want to close your position in AAPL/i)).toBeInTheDocument()
    })

    it('closes position when confirmed', async () => {
      const user = userEvent.setup()

      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockPositions
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true })
        })

      render(
        <QueryClientProvider client={queryClient}>
          <PaperPortfolioSummary />
        </QueryClientProvider>
      )

      await waitFor(() => {
        expect(screen.getByLabelText(/close position for AAPL/i)).toBeInTheDocument()
      })

      await user.click(screen.getByLabelText(/close position for AAPL/i))
      await user.click(screen.getByText('Close Position'))

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          '/api/trading/positions/close',
          expect.objectContaining({
            method: 'POST',
            body: JSON.stringify({ symbol: 'AAPL', quantity: 10 })
          })
        )
      })

      expect(toast).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Position Closed'
        })
      )
    })

    it('handles errors when closing position fails', async () => {
      const user = userEvent.setup()

      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockPositions
        })
        .mockRejectedValueOnce(new Error('Network error'))

      render(
        <QueryClientProvider client={queryClient}>
          <PaperPortfolioSummary />
        </QueryClientProvider>
      )

      await waitFor(() => {
        expect(screen.getByLabelText(/close position for AAPL/i)).toBeInTheDocument()
      })

      await user.click(screen.getByLabelText(/close position for AAPL/i))
      await user.click(screen.getByText('Close Position'))

      await waitFor(() => {
        expect(toast).toHaveBeenCalledWith(
          expect.objectContaining({
            title: 'Failed to Close Position',
            variant: 'destructive'
          })
        )
      })
    })
  })

  describe('Accessibility', () => {
    it('has proper aria labels', () => {
      render(
        <QueryClientProvider client={queryClient}>
          <PaperPortfolioSummary />
        </QueryClientProvider>
      )

      const closeButtons = screen.getAllByLabelText(/close position/i)
      closeButtons.forEach(button => {
        expect(button).toHaveAttribute('aria-label')
      })
    })

    it('is keyboard navigable', async () => {
      const user = userEvent.setup()

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockPositions
      })

      render(
        <QueryClientProvider client={queryClient}>
          <PaperPortfolioSummary />
        </QueryClientProvider>
      )

      await waitFor(() => {
        expect(screen.getByLabelText(/close position for AAPL/i)).toBeInTheDocument()
      })

      const closeButton = screen.getByLabelText(/close position for AAPL/i)
      closeButton.focus()

      await user.keyboard('{Enter}')

      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })
  })
})
```

**Run tests:**
```bash
cd apps/frontend
npm test -- PaperPortfolioSummary.test.tsx
```

---

## ✅ ACCEPTANCE CRITERIA

### Close Position Button:
- [ ] Button appears in position table
- [ ] Clicking shows confirmation dialog
- [ ] Dialog shows symbol, quantity, estimated value
- [ ] Confirming executes market order to sell
- [ ] Loading state during API call
- [ ] Success toast after closing
- [ ] Error toast on failure
- [ ] Portfolio refreshes after closing

### Component Tests:
- [ ] All test cases pass
- [ ] Close button renders correctly
- [ ] Confirmation dialog works
- [ ] API call on confirm
- [ ] Error handling tested
- [ ] Accessibility tested (aria labels, keyboard)

### Accessibility (HADI audit):
- [ ] Proper aria labels
- [ ] Focus management
- [ ] Keyboard navigation
- [ ] Screen reader support

---

## 🧪 TESTING CHECKLIST

Before marking complete:
- [ ] Manual test: Close a position
- [ ] Manual test: Cancel closing
- [ ] Manual test: Close position with API error
- [ ] Manual test: Keyboard navigation (Tab, Enter, Esc)
- [ ] Run Jest tests: `npm test`
- [ ] Run accessibility tests: `npm run test:a11y`
- [ ] Test with screen reader
- [ ] Test on mobile

---

## 📚 REFERENCES

**React Query Documentation:**
- https://tanstack.com/query/latest/docs/react/guides/mutations

**shadcn/ui AlertDialog:**
- https://ui.shadcn.com/docs/components/alert-dialog

**Accessibility Resources:**
- https://www.w3.org/WAI/ARIA/apg/
- HADI's audit: `docs/accessibility/PRIORITY_FIXES_FOR_TURING.md`

---

## 🚨 SECURITY NOTES

- Validate quantity before closing (no negative numbers)
- Confirm dialog prevents accidental closes
- API should verify ownership of position
- Handle race conditions (position already closed)

---

## 📊 DELIVERABLES

1. ✅ Close Position button component
2. ✅ Confirmation dialog
3. ✅ API integration
4. ✅ Error handling
5. ✅ Component tests (10+ test cases)
6. ✅ Accessibility fixes (from HADI audit)

---

## ✅ COMPLETION CHECKLIST

Before marking complete:
- [ ] Close Position button works
- [ ] Confirmation dialog shows correct info
- [ ] API call executes correctly
- [ ] Toast notifications work
- [ ] All tests pass
- [ ] Accessibility verified
- [ ] No console errors
- [ ] Code reviewed by Linus (API matching)

---

**Next Task:** C-037 Social Sentiment Frontend

---

**Questions?** Ask in COMMUNICATION_HUB.md

**Status Updates:** Add to COMMUNICATION_HUB.md Agent Updates section

**When Complete:** Update TASK_TRACKER.md, notify GAUDÍ
