# 🚀 INITIAL PROMPT FOR CODERS - START WORKING

**To:** Linus, Guido, Turing
**From:** GAUDÍ (Project Lead)
**Date:** January 31, 2026
**Priority:** 🔴 URGENT - Read and Respond Today

---

## 👋 Welcome to the New Workflow

We're making important changes to improve communication and get tasks done efficiently. Please read this carefully and respond by **5:00 PM today**.

---

## 🎯 Your Assignments (Start Immediately)

### **Linus (Backend Coder)**

**🔴 CRITICAL - Fix ScreenerPreset Model**
**Deadline:** February 1, 12:00 PM (TOMORROW)
**File:** `apps/backend/src/models/screener.py`
**Issue:** Missing base classes, screener save/load broken

```python
# BEFORE (WRONG):
class ScreenerPreset:
    name = models.CharField()

# AFTER (CORRECT):
from django.db import models

class ScreenerPreset(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # ... rest of fields

    class Meta:
        db_table = 'screener_presets'
```

**Test it:**
```bash
cd apps/backend
python manage.py makemigrations
python manage.py migrate
python manage.py test screener
```

---

**📋 PRIMARY TASK: C-022 Strategy Backtesting Engine**
**Estimated:** 18-24 hours
**Deadline:** February 3, 5:00 PM
**Location:** `tasks/coders/022-strategy-backtesting-engine.md`

**What you'll build:**
- BaseStrategy abstract class
- SMA crossover strategy
- RSI mean reversion strategy
- Backtesting engine
- Performance metrics (Sharpe, Sortino, max drawdown)
- 3 REST API endpoints

**Enhanced guide available** - Complete working code included

**Files to create:**
- `apps/backend/src/backtesting/base.py`
- `apps/backend/src/backtesting/strategies.py`
- `apps/backend/src/backtesting/engine.py`
- `apps/backend/src/backtesting/metrics.py`
- `apps/backend/src/api/backtesting.py`
- `apps/backend/src/tests/test_backtesting.py`

---

### **Guido (Backend Coder)**

**📋 PRIMARY TASK: C-036 Paper Trading System**
**Estimated:** 16-20 hours
**Deadline:** February 5, 5:00 PM
**Location:** `tasks/coders/036-paper-trading-system.md`

**What you'll build:**
- PaperTradingAccount model
- PaperTrade model
- Trading service (buy, sell, portfolio)
- 6 REST API endpoints
- Performance tracking
- Slippage simulation

**Enhanced guide available** - Complete working code included

**Files to create:**
- `apps/backend/src/models/paper_trading.py`
- `apps/backend/src/services/paper_trading.py`
- `apps/backend/src/api/paper_trading.py`
- `apps/backend/src/tests/test_paper_trading.py`

**Next tasks:** C-030 (Broker API Integration), C-012 (Portfolio Rebalancing)

---

### **Turing (Frontend Coder)**

**📋 PRIMARY TASK: C-016 Customizable Dashboards**
**Estimated:** 14-18 hours
**Deadline:** February 4, 5:00 PM
**Location:** `tasks/coders/016-customizable-dashboards.md`

**What you'll build:**
- Dashboard layout editor
- Widget component system
- Drag-and-drop interface (React Grid Layout)
- User preferences persistence
- 5+ pre-built templates

**Tech Stack:** React, Next.js, Zustand, React Grid Layout

**Files to create:**
- `apps/frontend/src/components/dashboard/DashboardEditor.tsx`
- `apps/frontend/src/components/dashboard/widgets/`
- `apps/frontend/src/stores/dashboardStore.ts`
- `apps/frontend/src/components/dashboard/templates/`

**Next tasks:** C-017 (Market Heat Map), C-038 (Options Chain Visualization)

---

## 📞 DAILY COMMUNICATION (Required)

### Send Daily Report by **5:00 PM Every Day**

**To:** GAUDÍ + Karen (DevOps)

**Format:**

```
GAUDÍ + Karen,

[CODER NAME] DAILY REPORT - [Date]

✅ COMPLETED:
- [Task ID]: [What I did]
  * [Files modified]
  * [Commit hash if any]
  * [Progress %]

🔄 IN PROGRESS:
- [Task ID]: [What I'm working on]
  * [Current step]
  * [Estimated completion]

🚧 BLOCKERS:
- [Description of blocker]
- [What help I need] (or "NONE")

⏰ TOMORROW:
- [What I'll work on]

❓ QUESTIONS:
- [Any questions] (or "NONE")

- [Your Name]
```

**Example:**

```
GAUDÍ + Karen,

Linus DAILY REPORT - January 31, 2026

✅ COMPLETED:
- ScreenerPreset model fix
  * Added models.Model base class
  * Added ForeignKey to User
  * Added Meta class
  * Progress: 100%
  * Commit: abc123def

🔄 IN PROGRESS:
- C-022: Backtesting Engine
  * Created BaseStrategy abstract class
  * Working on SMA crossover strategy
  * Progress: 20%
  * Est. completion: Feb 2

🚧 BLOCKERS:
- Question: Should BaseStrategy be abstract or concrete?

⏰ TOMORROW:
- Finish SMA crossover strategy
- Start RSI mean reversion strategy
- Create backtesting engine skeleton

❓ QUESTIONS:
- Should I use scipy.optimize for efficient frontier?

- Linus
```

---

## 🤝 WORK WITH KAREN (DevOps)

**Karen is your 2nd in command** and will help coordinate:

- **Infrastructure issues** → Ask Karen
- **Database problems** → Ask Karen
- **Deployment questions** → Ask Karen
- **General coordination** → Ask Karen
- **Code reviews** → Ask Karen first, then GAUDÍ

**Karen is excellent** - He just fixed D-001 (Infrastructure Security) with world-class work. Trust him!

---

## 🎯 QUALITY STANDARDS

### Every Task Must Have:
- ✅ **Test coverage > 80%**
- ✅ **No TypeScript errors** (Turing)
- ✅ **No pylint warnings** (Linus, Guido)
- ✅ **Documentation complete**
- ✅ **Code reviewed by peer**
- ✅ **Working commit pushed**

### Before Marking Complete:
1. Run all tests locally
2. Check for linting errors
3. Update documentation
4. Create pull request
5. Ask for review

---

## ⚠️ CRITICAL REMINDERS

### 1. Don't Stay Silent!
- ❌ 2+ days of silence = UNACCEPTABLE
- ✅ Daily reports at 5:00 PM = REQUIRED
- ✅ Ask questions when blocked
- ✅ Report progress every day

### 2. Use Enhanced Task Guides
- Your tasks have detailed guides
- Complete working code included
- Common mistakes documented
- FAQ sections for questions

### 3. Collaborate
- Review each other's code
- Help when teammates are stuck
- Share knowledge
- Ask questions in public channels

---

## 📋 TODAY'S ACTION ITEMS (Due 5:00 PM)

### For All Coders:

1. ✅ **Reply to this message** - Acknowledge you read it
2. ✅ **Read your assigned task** - Check the detailed guide
3. ✅ **Send your first daily report** - Use the template above
4. ✅ **Ask questions** - Don't stay silent!

### For Linus:
5. ✅ **Start ScreenerPreset fix** - Due TOMORROW 12:00 PM

---

## 🎉 Recognition

**What you've done well:**
- ✅ C-001 to C-010 migration tasks (60% complete)
- ✅ C-011 to C-015 feature tasks (5/30 complete)
- ✅ Integration testing complete

**What needs improvement:**
- ❌ Communication (2+ days silent)
- ❌ ScreenerPreset bug
- ❌ Task acknowledgment

**We can do better!** Let's fix the communication and get these tasks done.

---

## 🚀 Next Steps

### RIGHT NOW:
1. Read your assigned task file
2. Start working on your primary task
3. Prepare your daily report

### TODAY by 5:00 PM:
- Send your first daily report
- Acknowledge this message
- Ask any questions

### TOMORROW (Feb 1):
- **Linus:** ScreenerPreset fix due (12:00 PM)
- All coders: Continue primary tasks
- Daily report at 5:00 PM

### THIS WEEK:
- Complete your primary task
- Send daily reports every day
- Ask for help when blocked
- Review peer code

---

## 💡 HOW TO SUCCEED

1. **Communicate daily** - Reports at 5:00 PM, no exceptions
2. **Start immediately** - Don't wait, begin now
3. **Ask questions** - We're here to help
4. **Use the guides** - Enhanced tasks have everything you need
5. **Collaborate** - Help each other succeed
6. **Focus on quality** - Test, document, review
7. **Be proactive** - Report blockers early

---

## 📞 CONTACT

**Daily Communication:**
- Email GAUDÍ + Karen
- 5:00 PM every day
- Use the template above

**For Help:**
- **Technical blockers:** Ask Karen first
- **Architecture decisions:** Ask GAUDÍ
- **Security issues:** Ask Charo

**Emergency:**
- Critical blockers: Email immediately
- Don't wait until 5:00 PM

---

## ✅ SUCCESS CRITERIA

### This Week You Will:
- [ ] Send daily report every day (5:00 PM)
- [ ] Complete your primary task
- [ ] Fix ScreenerPreset model (Linus)
- [ ] Review peer code
- [ ] Ask questions when blocked

### Quality Targets:
- [ ] Test coverage > 80%
- [ ] No linting errors
- [ ] Documentation complete
- [ ] Peer review approved

### Communication Targets:
- [ ] Daily reports: 100% on-time
- [ ] Response time: < 24 hours
- [ ] Blocker reporting: Immediate
- [ ] Questions asked: Don't stay silent!

---

**We believe in you!** Let's work together, communicate daily, and build something excellent.

**Your first daily report is due TODAY at 5:00 PM.** We're waiting to hear from you!

---

🎨 *GAUDÍ - Building Financial Excellence*

📧 *Reply to this message to acknowledge receipt*
