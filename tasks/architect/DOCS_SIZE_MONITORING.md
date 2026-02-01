# 📊 DOCS SIZE MONITORING SYSTEM

**Created:** February 1, 2026
**Monitored by:** ARIA
**Status:** ACTIVE

---

## 📈 CURRENT SIZE METRICS

### Docs Directory (Total: ~2.3 MB)
| Directory | Size | Files | Status |
|-----------|------|-------|--------|
| `docs/security/` | 852K | ~30 | ⚠️ LARGE |
| `docs/archive/` | 276K | ~15 | ✅ OK |
| `docs/roles/` | 264K | ~20 | ✅ OK |
| `docs/operations/` | 212K | ~15 | ✅ OK |
| `docs/architecture/` | 208K | ~15 | ✅ OK |
| `docs/references/` | 148K | ~10 | ✅ OK |
| `docs/development/` | 124K | ~10 | ✅ OK |
| `docs/agents/` | 100K | ~15 | ✅ OK |
| `docs/design/` | 44K | ~5 | ✅ OK |
| `docs/accessibility/` | 40K | ~5 | ✅ OK |
| `docs/migration/` | 24K | ~5 | ✅ OK |
| `docs/api/` | 4K | ~1 | ✅ OK |

### Tasks Directory (Total: ~2.4 MB)
| Directory | Size | Files | Status |
|-----------|------|-------|--------|
| `tasks/coders/` | 1.2M | ~30 | ⚠️ LARGE |
| `tasks/devops/` | 536K | ~25 | ⚠️ LARGE |
| `tasks/architect/` | 244K | ~20 | ✅ OK |
| `tasks/security/` | 124K | ~15 | ✅ OK |
| `tasks/assignments/` | 120K | ~10 | ✅ OK |
| `tasks/new-agents/` | 40K | ~10 | ✅ OK |
| `tasks/communication/` | 36K | ~10 | ✅ OK |
| `tasks/reports/` | 32K | ~10 | ✅ OK |
| `tasks/qa/` | 28K | ~5 | ✅ OK |
| `tasks/seo/` | 8K | ~5 | ✅ OK |

---

## 🚨 SIZE THRESHOLDS

### Warning Thresholds
| Category | Warning Limit | Action |
|----------|---------------|--------|
| Single file | >50K | Review content |
| Directory | >500K | Archive old files |
| Total docs | >5MB | Archive aggressively |
| Daily growth | >20 files | Consolidate |

### Critical Thresholds
| Category | Critical Limit | Action |
|----------|----------------|--------|
| Single file | >100K | Split or archive |
| Directory | >1MB | Immediate archive |
| Total docs | >10MB | Full cleanup |

---

## 📋 ARCHIVE TRIGGERS

### Automatic Archive (When):
1. **Daily:** Files older than 7 days in active directories
2. **Weekly:** All reports older than 2 weeks
3. **Monthly:** All session files older than 1 month
4. **Size-based:** Directory exceeds 500K

### Manual Archive (When):
1. Session complete
2. Task complete (move to `docs/archive/tasks/`)
3. Communication obsolete (move to `docs/archive/communications/`)
4. Duplicate found (delete one)

---

## 🔄 ARCHIVE SCHEDULE

### Daily (ARIA - 6:00 PM)
- [ ] Check for files older than 7 days
- [ ] Move old reports to `docs/archive/reports/`
- [ ] Update SIZE_METRICS

### Weekly (ARIA - Friday)
- [ ] Full size audit
- [ ] Archive all completed session files
- [ ] Consolidate duplicate reports
- [ ] Report to GAUDÍ

### Monthly (ARIA - 1st of month)
- [ ] Full cleanup
- [ ] Archive all but current month
- [ ] Compress old archives
- [ ] Report size reduction

---

## 📊 GROWTH TRACKING

### Today (Feb 1, 2026)
| Metric | Value |
|--------|-------|
| Total .md files | ~380 |
| Files created today | ~30 |
| Files archived today | 15 |
| Net growth | +15 |

### This Week
| Day | Files | Net Change |
|-----|-------|------------|
| Jan 30 | ~350 | - |
| Jan 31 | ~365 | +15 |
| Feb 1 | ~380 | +15 |

### Target Growth
| Period | Target |
|--------|--------|
| Daily | <10 files |
| Weekly | <50 files |
| Monthly | <200 files |

---

## 🎯 DOCS REDUCTION ACTIONS

### Immediate (Today)
1. ✅ Archive completed: 15 files
2. ✅ Consolidate: `tasks/communications/` → `tasks/communication/`
3. ⏳ Review: `docs/security/` (852K - largest)

### This Week
1. [ ] Review `tasks/coders/` for obsolete task specs
2. [ ] Archive all Jan 30 session files
3. [ ] Consolidate duplicate reports

### This Month
1. [ ] Full archive of Jan 2026
2. [ ] Compress archives
3. [ ] Target: <300 total .md files

---

## 📁 ARCHIVE STRUCTURE

```
docs/archive/
├── sessions/           # Session summaries
├── communications/     # Old messages
├── devops/            # DevOps reports
├── tasks/             # Completed tasks
├── reports/           # Weekly/monthly reports
└── quarterly/         # Q1 2026, Q2 2026, etc.

tasks/archive/
├── old_sessions/      # Session-specific tasks
├── completed/         # Completed task specs
└── deprecated/        # Obsolete workflows
```

---

## 📈 SIZE GOALS

| Metric | Current | End of Week | End of Month |
|--------|---------|-------------|--------------|
| Total .md files | ~380 | <350 | <300 |
| Total size | ~4.7MB | <4MB | <3MB |
| Largest dir | 1.2M (coders) | <800K | <500K |
| Daily growth | +15 | <10 | <5 |

---

## 🔔 ALERTS

### If Growth Exceeds Target:
1. **+20 files/day:** Investigate duplicate creation
2. **+50 files/week:** Consolidate reports
3. **Size >5MB:** Full archive week

### If Archive Falls Behind:
1. **7+ days old in active:** Auto-archive
2. **14+ days old reports:** Archive immediately
3. **30+ days old sessions:** Move to quarterly

---

**Monitor daily. Archive weekly. Report monthly.**

---
*ARIA - Keeping docs lean for GAUDÍ*
