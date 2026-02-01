## TEST COORDINATION REQUEST - C-036 Paper Trading

**From:** GRACE (QA Engineer)
**To:** Turing (Frontend) + Linus (Backend)
**Date:** February 1, 2026

---

### Test Files Created

**Backend:** `apps/backend/src/trading/tests/test_paper_trading.py`
- 15 test scenarios (TC-PT-001 through TC-PT-015)
- Tests: Portfolio creation, market/limit orders, P/L calculation, WebSocket updates, performance

**Frontend:** `apps/frontend/src/components/trading/__tests__/PaperTrading.test.tsx`
- Component tests for Dashboard, OrderForm, PortfolioSummary, PositionList

### What I Need From You

1. **Turing:**
   - PaperTradingDashboard component at `components/trading/PaperTradingDashboard.tsx`
   - OrderForm component at `components/trading/OrderForm.tsx`
   - PortfolioSummary component at `components/trading/PortfolioSummary.tsx`
   - PositionList component at `components/trading/PositionList.tsx`
   - API mock file at `lib/api/paperTrading.ts`

2. **Linus:**
   - PaperPortfolio model at `src/trading/models/paper_portfolio.py`
   - PaperPosition model at `src/trading/models/paper_position.py`
   - PaperOrder model at `src/trading/models/paper_order.py`
   - PaperTradingService at `src/trading/services/paper_trading_service.py`
   - get_current_price utility

### Test Status
- ✅ Test files created
- ⏳ Pending execution (need dev builds)
- ⏳ Performance testing (need Locust/k6 setup)

### Performance Targets
- Order execution: < 200ms p95
- Concurrent users: 1000+

**Ready to execute tests when builds are available.**

- GRACE
