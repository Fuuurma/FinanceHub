# 🧠 CONTEXT MANAGEMENT PROTOCOL

**Purpose:** Keep agent context clean, focused, and efficient

---

## 🎯 GOLDEN RULE: FORGET AFTER COMPLETION

**When a task is 100% complete:**
- ✅ **Retain:** Skills learned, patterns, best practices
- ❌ **FORGET:** Task specifics, implementation details, file paths

---

## 📊 CONTEXT LIFECYCLE

### Phase 1: Active Task (IN PROGRESS)
**Retain Everything:**
- Task requirements
- Implementation details
- File paths and function names
- Debugging history
- Decisions made
- Code written

**Example:**
```
Working on: C-036 Paper Trading Backend
Remember:
- apps/backend/src/trading/models.py (PaperPosition model)
- apps/backend/src/trading/services/paper_trading.py (PaperTradingEngine)
- API endpoint: POST /api/v1/paper/orders
- Migration: 0003_add_paper_trading_models.py
```

---

### Phase 2: Task Complete (100% DONE)
**Transition to Clean Context:**

✅ **Keep (Abstract Knowledge):**
- "I implemented paper trading using Django models"
- "I learned how to use Django Ninja for APIs"
- "Paper trading requires position tracking and order execution"

❌ **Forget (Specific Details):**
- "I created PaperPosition model with fields X, Y, Z"
- "The file was apps/backend/src/trading/models.py"
- "Function signature was def execute_order(order_data)"
- "Migration was 0003_add_paper_trading_models.py"

**After Completion:**
```
Status: Task complete, context cleaned
Remember:
- ✅ Django Ninja API patterns (general skill)
- ✅ Paper trading concepts (business knowledge)
- ✅ Best practices for trading systems (lessons learned)

Forget:
- ❌ Specific file paths
- ❌ Function names and signatures
- ❌ Implementation details
- ❌ Migration numbers
```

---

## 🔄 CONTEXT CLEANING CHECKLIST

### When Task is 100% Complete:

1. **Commit and Push** - Save all work to git
2. **Document** - Update task status with completion summary
3. **Clean Context** - Clear task-specific details from memory
4. **Reset Focus** - Ready for next task

### What to Document (Before Forgetting):
```markdown
## Task Completion Summary

**Task:** C-036 Paper Trading Backend
**Status:** ✅ Complete
**Commits:** a1b2c3d, e4f5g6h

**What Was Built:**
- Paper trading backend with Django models and API endpoints
- Position tracking and order execution engine
- WebSocket support for real-time updates

**Lessons Learned:**
- Django Ninja makes API development fast
- WebSocket consumers require separate ASGI app
- Paper trading needs separate database from real trading

**Files Modified:**
- apps/backend/src/trading/ (new models, services, APIs)
- Migration files added

**Next Task:** Ready for new assignment
```

### What to Forget (After Documenting):
- ❌ Specific file paths
- ❌ Function signatures
- ❌ Variable names
- ❌ Implementation details
- ❌ Debugging history

---

## 🧠 MEMORY RETENTION POLICY

### Retain Long-Term (Career Memory):
- **Skills:** Django Ninja, React Hooks, WebSocket
- **Patterns:** Repository pattern, service layer architecture
- **Best Practices:** API design, testing strategies
- **Domain Knowledge:** Trading concepts, financial terminology
- **Lessons Learned:** What works, what doesn't

### Forget Short-Term (Task Memory):
- **Specific Files:** apps/backend/src/trading/models.py
- **Function Names:** execute_paper_order(), calculate_pnl()
- **Implementation Details:** How I solved that specific bug
- **Variable Names:** paper_position, order_quantity
- **Migration Numbers:** 0003_add_paper_trading_models.py

---

## 📝 EXAMPLES

### Example 1: Linus Completes C-036

**Before Context Clean:**
```
I remember everything about C-036:
- Created PaperPosition model in apps/backend/src/trading/models.py
- Fields: id, user, symbol, quantity, entry_price, current_price
- Created PaperTradingEngine with execute_order() method
- API endpoint: POST /api/v1/paper/orders
- Migration: 0003_add_paper_trading_models.py
- Wrote tests in test_paper_trading.py
- Debugged issue with decimal precision
```

**After Context Clean (What Linus Should Remember):**
```
Task C-036 complete. Ready for next task.

Skills retained:
- Django Ninja API development
- Django model design
- Trading system architecture
- WebSocket integration

Context forgotten:
- Specific file paths
- Function names
- Implementation details
```

---

### Example 2: Turing Completes Frontend Work

**Before Context Clean:**
```
I remember:
- Created PaperTradingDashboard component
- Added usePaperTrading hook with WebSocket
- Integrated PaperPerformanceChart with Recharts
- File: apps/frontend/src/components/paper-trading/
- Props: user, symbol, onOrderPlaced
- State management with useState
```

**After Context Clean:**
```
Frontend task complete. Ready for next task.

Skills retained:
- React hooks (useState, useEffect, custom hooks)
- WebSocket integration in React
- Recharts library
- Component composition

Context forgotten:
- Component file paths
- Specific prop names
- Implementation details
```

---

## 🎯 CONTEXT MANAGEMENT IN PROMPTS

### Active Task Prompt:
```markdown
You are working on: [TASK NAME]

**Task Details:**
- [Specific requirements]
- [File paths]
- [Implementation details]

**Remember everything while working on this task.**
```

### Task Complete Prompt:
```markdown
**Task Status:** ✅ 100% Complete

**Clean Your Context:**
1. Document what was built (high-level)
2. Note skills learned (abstract)
3. Forget task specifics (files, functions, details)
4. Reset for next task

**You are now ready for a new assignment.**
```

---

## ⚠️ WARNING SIGNS OF CONTEXT BLOAT

**You have too much context if:**
- You remember file paths from completed tasks
- You recall function names from last week
- You know migration numbers from previous work
- You can describe implementations from finished tasks

**Solution:** Clean your context!
- Keep the skills
- Forget the details
- Document the completion
- Move on to next task

---

## 🔧 IMPLEMENTATION IN AGENTS

Each agent will have:

1. **Task Start:** Load full context (files, requirements, details)
2. **Task In Progress:** Retain everything (debugging, decisions)
3. **Task 100% Complete:**
   - Document completion summary
   - Extract skills learned
   - **FORGET task specifics**
   - Reset for next task

---

## 💡 WHY THIS MATTERS

**Benefits:**
- ✅ **Faster Response:** Less context to process
- ✅ **Clearer Thinking:** Focus on current task
- ✅ **Better Performance:** Not bogged down by old details
- ✅ **Scalability:** Can handle many tasks over time

**Without Context Cleaning:**
- ❌ Agents become slow (too much context)
- ❌ Agents confuse tasks (mix details)
- ❌ Agents inefficient (processing irrelevant info)
- ❌ Context limits hit (can't take new tasks)

---

## 🎯 SUMMARY

**Rule of Thumb:**
> "When a task is done, it's gone. Keep the skills, forget the details."

**For Every Task:**
1. Work with full context while IN PROGRESS
2. Document completion when 100% DONE
3. **Clean context - forget specifics**
4. Retain skills and patterns only
5. Ready for next task with clean slate

---

*Context Management - Keep agents lean and efficient*
