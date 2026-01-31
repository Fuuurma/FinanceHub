# Linus Quick Start Guide

**Created:** January 31, 2026
**Tracked by:** ARIA

---

## 🎯 Priority Order

| Priority | Task | Due | Status |
|----------|------|-----|--------|
| P0 | ScreenerPreset Model Fix | Feb 1, 12:00 PM | 🔴 NOT STARTED |
| P0 | S-009: Float Precision Fix | Feb 2 | 🔴 NOT STARTED |
| P0 | S-011: Remove Print Statements | Feb 2 | 🔴 NOT STARTED |
| P1 | C-022: Strategy Backtesting Engine | Feb 3 | ⏳ PENDING |
| P2 | S-014: Request ID Tracking | Feb 5 | ⏳ PENDING |
| P2 | C-037: Social Sentiment Analysis | Feb 7 | ⏳ PENDING |
| P2 | C-040: Robo-Advisor Asset Allocation | Feb 10 | ⏳ PENDING |

---

## 🚀 Quick Start Commands

```bash
# Navigate to backend
cd apps/backend

# Run tests for your tasks
python -m pytest tests/ -v -k "screener or precision or print" --tb=short

# Run linter
python -m pylint apps/backend/src/models/screener.py

# Check for print statements
grep -r "print(" apps/backend/src --include="*.py"

# Commit your changes
git add apps/backend/src/models/screener.py
git commit -m "fix: add models.Model base class to ScreenerPreset"
git push
```

---

## 👥 Who to Ask for Help

| Issue | Contact |
|-------|---------|
| Django models | Guido (Backend) |
| Testing | Karen (can review) |
| Security questions | Charo |
| General blocker | ARIA or Karen |

---

## 📁 Task Files

- ScreenerPreset fix: `tasks/coders/CODERS_SCREENER_PRESET_QUICK_FIX.md`
- C-022 Backtesting: `tasks/coders/022-strategy-backtesting-engine.md`
- S-009 Float Precision: `tasks/security/009-decimal-calculations.md`
- S-011 Print Statements: `tasks/security/010-remove-print-statements.md`

---

**Remember:** Send daily report at 5:00 PM to GAUDÍ + Karen
