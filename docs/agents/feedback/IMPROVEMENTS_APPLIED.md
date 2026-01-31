# Agent Feedback Integration - Improvements Applied

**Date:** January 31, 2026
**Compiled by:** ARIA

---

## 📊 Feedback Summary

| Agent | Feedback Received | Improvements Applied |
|-------|-------------------|---------------------|
| Karen (DevOps) | 4 ✅, 5 ❌ | 3 rules added |
| Charo (Security) | 5 ✅, 4 ❌ | 4 practices added |
| Linus (Coder) | 4 ✅, 4 ❌ | 4 rules added |
| Turing (Coder) | 3 ✅, 5 ❌ | 5 checklist items |
| Guido (Coder) | 4 ✅, 5 ❌ | 4 rules added |

---

## 🎯 Improvements by Category

### 1. Debugging & Diagnostics

| Before | After |
|--------|-------|
| Assume error cause | Check logs first: `docker-compose logs --tail 50` |
| Rebuild container multiple times | Test with `docker exec` before rebuilding |
| Skip migration state check | Always run `showmigrations` after failures |

**Rules Added:**
- ✅ CHECK LOGS FIRST
- ✅ TEST INCREMENTALLY  
- ✅ CHECK MIGRATION STATE FIRST

---

### 2. Code Review & Verification

| Before | After |
|--------|-------|
| Apply migrations blindly | Review generated migrations before applying |
| Mark complete without verification | Add verification step before marking done |
| Ignore generated code | Review AlterField operations specifically |

**Rules Added:**
- ✅ REVIEW GENERATED CODE
- ✅ VERIFY BEFORE MARKING COMPLETE

---

### 3. Process & Workflow

| Before | After |
|--------|-------|
| Large autodetected migrations | Create smaller, focused migrations |
| Context switch between 5+ tasks | Max 2 active tasks at once |
| Final session reports only | Send interim updates during session |

**Rules Added:**
- ✅ SMALLER MIGRATIONS
- ✅ LIMIT PARALLEL WORK
- ✅ REAL-TIME PROGRESS UPDATES

---

### 4. Technical Best Practices

| Before | After |
|--------|-------|
| Assume model fields exist | PRE-FLIGHT CHECKS - verify fields before using |
| Forget async patterns | ASYNC AWARENESS - Django ORM needs sync_to_async |
| Skip type/LSP errors | Address errors proactively, don't accumulate |

**Rules Added:**
- ✅ PRE-FLIGHT CHECKS
- ✅ ASYNC AWARENESS
- ✅ NO ACCUMULATING ERRORS

---

## 📝 Updated Role Documents

| File | Changes |
|------|---------|
| `tasks/ROLE_DEVOPS.md` | 3 new critical rules, failure handling workflow |
| `tasks/ROLE_SECURITY.md` | Verification practices, feedback guidelines |
| `tasks/ROLE_CODERS.md` | 5 new rules, expanded checklist |
| `docs/agents/feedback/README.md` | New feedback folder structure |
| `docs/agents/feedback/TEMPLATE.md` | Standardized feedback template |

---

## 🎓 Team-Wide Improvements

### All Agents Should:
1. ✅ Check logs first before fixing
2. ✅ Verify before marking complete
3. ✅ Send interim progress updates
4. ✅ Document errors to avoid repetition
5. ✅ Limit parallel work to 2 tasks max

### For Next Session:
1. All agents submit feedback to `docs/agents/feedback/`
2. ARIA synthesizes and updates roles
3. GAUDÍ reviews for approval
4. Publish improved role definitions

---

**Next Review:** February 7, 2026
