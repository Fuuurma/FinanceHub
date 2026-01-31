# Guido Quick Start Guide

**Created:** January 31, 2026
**Tracked by:** ARIA

---

## 🎯 Priority Order

| Priority | Task | Due | Status |
|----------|------|-----|--------|
| P0 | S-010: Token Race Conditions | Feb 2 | 🔴 NOT STARTED |
| P1 | C-036: Paper Trading System | Feb 5 | ⏳ PENDING |
| P2 | S-012: Input Validation | Feb 5 | ⏳ PENDING |
| P2 | S-013: Rate Limiting | Feb 5 | ⏳ PENDING |
| P2 | C-030: Broker API Integration | Feb 8 | ⏳ PENDING |

---

## 🚀 Quick Start Commands

```bash
# Navigate to backend
cd apps/backend

# Run tests for token/security
python -m pytest tests/ -v -k "token or auth" --tb=short

# Check for race conditions
python -m pytest tests/ -v -k "race" --tb=short

# Run linter
python -m pylint apps/backend/src/users/

# Check token implementation
grep -r "token" apps/backend/src/users/authentication.py

# Commit your changes
git add apps/backend/src/users/authentication.py
git commit -m "fix: add token race condition protection"
git push
```

---

## 👥 Who to Ask for Help

| Issue | Contact |
|-------|---------|
| Authentication | Linus (can help review) |
| Token implementation | Charo (security expert) |
| Testing patterns | Karen |
| General blocker | ARIA or Karen |

---

## 📁 Task Files

- S-010 Token Race: `tasks/security/008-token-rotation.md`
- S-012 Input Validation: `tasks/security/011-narrow-exception-handling.md`
- S-013 Rate Limiting: `tasks/api/RATE_LIMITS.md`
- C-036 Paper Trading: `tasks/coders/036-paper-trading-system.md`

---

## 🔐 Token Security Best Practices

1. Use atomic operations for token updates
2. Add transaction locks where needed
3. Test concurrent requests
4. Log failed attempts
5. Set proper timeouts

---

**Remember:** Send daily report at 5:00 PM to GAUDÍ + Karen
