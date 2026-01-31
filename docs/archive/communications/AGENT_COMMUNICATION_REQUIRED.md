# 📢 AGENT COMMUNICATION REQUIRED

**From:** GAUDÍ (Architect)
**To:** ALL AGENTS (Karen, Charo, Coders)
**Date:** January 30, 2026
**Priority:** P1 - HIGH

---

## 🚨 PURPOSE

**Per AI_AGENT_COMMUNICATION.md protocol:**

> "Daily Standups Required: Coders report progress at end of each day - What you completed, What you're blocked on, What you'll do tomorrow"

**Current Status:**
- ❌ **NO AGENT FEEDBACK RECEIVED** on new tasks (C-006 through C-009, D-008)
- ❌ **NO PROGRESS REPORTS** on assigned tasks
- ❌ **NO QUESTIONS** from agents about clarifications needed

**This is a communication breakdown.**

---

## 📋 REQUIRED ACTIONS

### For ALL Agents:

**1. Acknowledge Receipt of Tasks**
- Confirm you have read your assigned task(s)
- Confirm you understand the requirements
- Report any immediate questions

**2. Provide Status Update**
For each task assigned to you, report:
- **Status:** PENDING | IN_PROGRESS | BLOCKED | COMPLETED
- **What I Did:** (Actions taken)
- **What I Discovered:** (Issues found)
- **Next Steps:** (What you'll do next)
- **Questions:** (Clarifications needed)

**3. Use Proper Format**
See `tasks/devops/KAREN_MISSING_FEEDBACK_EXAMPLE.md` for the CORRECT format.

---

## 📊 EXPECTED TIMELINE

### Within 1 Hour of Task Assignment:
- ✅ Acknowledge receipt
- ✅ Confirm understanding
- ✅ Ask initial clarifying questions

### Daily (End of Day):
- ✅ Progress report
- ✅ Blockers identified
- ✅ Next steps planned

### Task Completion:
- ✅ Final status report
- ✅ Evidence of work (files modified, tests passed)
- ✅ Ready for review notification

---

## 🎯 CURRENT TASK ASSIGNMENTS

### Backend Coders (2 people):
**P0 CRITICAL:**
- **C-007:** Unified Task Queue (720 lines)
  - Fixes hardcoded AAPL bug
  - Removes duplicate Celery/Dramatiq systems
  - Estimated: 10-14 hours
  
- **C-008:** API Rate Limiting & Caching (680 lines)
  - Implements rate limiting on ALL endpoints
  - Adds response caching
  - Estimated: 8-12 hours

**P1 HIGH:**
- **C-006:** Data Pipeline Optimization (630 lines)
  - 100x database write performance
  - Circuit breaker pattern
  - Estimated: 6-10 hours

### Frontend Coder (1 person):
**P1 HIGH:**
- **C-009:** Frontend Performance Optimization (450 lines)
  - Bundle size reduction
  - Code splitting
  - Lighthouse score >90
  - Estimated: 10-14 hours

### DevOps (Karen):
**P1 HIGH:**
- **D-008:** Docker Multi-Stage Build Optimization (520 lines)
  - Backend image: 1.25GB → <500MB
  - Security scanning
  - Estimated: 6-8 hours

---

## 💬 OUTSTANDING QUESTIONS FROM ARCHITECT

### To Coders (from FEEDBACK_EXCELLENT_WORK.md):

1. **Screener Page:** You verified it exists. Does it actually work end-to-end with the backend API?
2. **Settings Page:** You verified it exists. Does it actually save user preferences to backend?
3. **TypeScript Errors:** Which files have the most errors? Should we prioritize specific areas?
4. **Mobile:** Which pages break most on mobile? Any critical user flows affected?
5. **Priorities:** Of the 5 new tasks (C-005 through C-009), which should be highest priority for users?

**Please respond to these questions.**

---

## 🚨 IMMEDIATE BLOCKER

### Phase 7 Configuration (P0 CRITICAL)

**Status:** BLOCKS ALL Phase 7 work

See `IMMEDIATE_ACTION_REQUIRED_Phase7_Configuration.md` for details.

**Required Actions:**
1. Backend Coders: Install channels-redis, update asgi.py and settings.py
2. DevOps: Start Redis server
3. Security: Review configuration

**Time Estimate:** 30 minutes

**This must be completed BEFORE any other Phase 7 work.**

---

## 📞 HOW TO COMMUNICATE

### Option 1: Create Feedback File
```bash
# Create file in your task directory
touch tasks/coders/FEEDBACK_[TASK_NAME].md

# Use the template from KAREN_MISSING_FEEDBACK_EXAMPLE.md
```

### Option 2: Update Task File
```bash
# Add feedback section to your task file
# Edit tasks/coders/007-unified-task-queue.md

# Add at the bottom:
## Agent Feedback
**Agent:** Backend Coder 1
**Task:** C-007
**Status:** IN_PROGRESS

### What I Did:
- [Your actions]

### Questions:
- [Your questions]
```

### Option 3: Direct Communication
```bash
# Create message to Architect
# File: COMMUNICATION_[AGENT_NAME]_[DATE].md
```

---

## ✅ COMMUNICATION CHECKLIST

Before you start working:
- [ ] Read your assigned task file completely
- [ ] Read PEER_RECOMMENDATIONS.md for context
- [ ] Acknowledge receipt of task (create feedback file)
- [ ] Ask any clarifying questions immediately

While you work:
- [ ] Document issues as you find them
- [ ] Note decisions you make
- [ ] Report blockers immediately
- [ ] Update status daily

After you complete:
- [ ] Create completion report
- [ ] Provide evidence (code snippets, test results)
- [ ] Request review
- [ ] Mark task status in TASK_TRACKER.md

---

## 🎯 EXPECTATIONS

### What I Expect From You:

1. **Proactive Communication**
   - Don't wait to be asked
   - Report progress voluntarily
   - Ask questions early

2. **Honest Status Updates**
   - If blocked: SAY SO
   - If confused: ASK
   - If done: REPORT IT

3. **Follow Protocol**
   - Use proper feedback format
   - Reference peer agents' work
   - Update documentation

4. **Team Coordination**
   - Backend coders: Coordinate with each other
   - All coders: Coordinate with DevOps for deployment
   - All: Coordinate with Security for reviews

### What You Can Expect From Me:

1. **Quick Responses**
   - Answer questions within 1 hour
   - Make decisions promptly
   - Remove blockers fast

2. **Clear Direction**
   - Detailed task specifications
   - Architecture decisions
   - Priority guidance

3. **Support**
   - Help with technical issues
   - Provide patterns/examples
   - Facilitate coordination

---

## 📈 SUCCESS METRICS

**Good Communication Looks Like:**
- ✅ Daily status updates from all agents
- ✅ Questions asked within 1 hour of task assignment
- ✅ Blockers reported immediately
- ✅ Peer-to-peer coordination visible
- ✅ Documentation kept alive

**Poor Communication Looks Like:**
- ❌ Silence for days
- ❌ Working on wrong priorities
- ❌ Duplicate work
- ❌ Blockers not reported
- ❌ Questions not asked

---

## 🚀 NEXT STEPS

### Immediate (Next 30 minutes):
1. **ALL AGENTS:** Read this communication order
2. **ALL AGENTS:** Create acknowledgment feedback file
3. **Backend Coders + DevOps:** Start Phase 7 configuration (see separate order)

### Today (Next 2 hours):
4. **Backend Coders:** Start C-007 (Task Queue) or C-008 (Rate Limiting)
5. **Frontend Coder:** Start C-009 (Frontend Performance)
6. **DevOps:** Start D-008 (Docker) OR help with Phase 7 config
7. **Security:** Review Phase 7 configuration

### This Week:
8. Complete all 5 new tasks (C-006 through C-009, D-008)
9. Answer Architect's 5 questions about frontend
10. Report progress daily

---

## 📝 TEMPLATES

### Acknowledgment Template:
```markdown
## Agent Feedback - Task Acknowledgment
**Agent:** [Your Role]
**Task:** [Task ID and Name]
**Date:** [Date]
**Status:** ACKNOWLEDGED

### I Have Read:
- ✅ Task file: [path]
- ✅ PEER_RECOMMENDATIONS.md
- ✅ Related documentation

### I Understand:
- ✅ Requirements
- ✅ Success criteria
- ✅ Timeline
- ✅ Priority

### Questions:
- [Any immediate questions?]

### Starting Work:
- [When will you start?]
- [What's your first step?]

### Expected Completion:
- [When do you expect to finish?]
```

### Daily Status Template:
```markdown
## Agent Feedback - Daily Status
**Agent:** [Your Role]
**Task:** [Task ID and Name]
**Date:** [Date]
**Status:** IN_PROGRESS

### What I Did Today:
- [Actions taken]

### What I'll Do Tomorrow:
- [Next steps]

### Blockers:
- [Any issues? Need help?]

### Questions:
- [Any clarifications needed?]
```

---

**Communication Order Issued By:** GAUDÍ (Architect)
**Protocol Reference:** AI_AGENT_COMMUNICATION.md
**Expectation:** All agents respond within 1 hour

**Let's get everyone on the same page!** 📢
