# 🚀 AGENT INITIAL PROMPTS - MASTER LIST

**For:** New AI Assistant Sessions
**Created:** January 31, 2026
**Updated:** February 1, 2026
**Purpose:** Initialize all agents in new sessions

---

## 📁 Available Initial Prompts

| Agent | Role | File | Priority |
|-------|------|------|----------|
| **GAUDÍ** | Architect | `docs/roles/GAUDI_INITIAL_PROMPT.md` | P0 |
| **ARIA** | Architect Assistant | `docs/roles/ARIA_INITIAL_PROMPT.md` | P1 |
| **Karen** | DevOps Engineer | `docs/roles/KAREN_INITIAL_PROMPT.md` | P1 |
| **Charo** | Security Engineer | `docs/roles/CHARO_INITIAL_PROMPT.md` | P1 |
| **GRACE** | QA/Testing Engineer | `docs/roles/GRACE_INITIAL_PROMPT.md` | P1 |
| **MIES** | UI/UX Designer | `docs/roles/MIES_INITIAL_PROMPT.md` | P1 |
| **HADI** | Accessibility Specialist | `docs/roles/HADI_INITIAL_PROMPT.md` | P1 |
| **Linus** | Backend Coder | `docs/roles/CODERS_INITIAL_PROMPT.md` | P1 |
| **Guido** | Backend Coder | `docs/roles/CODERS_INITIAL_PROMPT.md` | P1 |
| **Turing** | Frontend Coder | `docs/roles/CODERS_INITIAL_PROMPT.md` | P1 |

---

## 📋 How to Use

### For New Sessions:

1. **Copy the relevant prompt** to the AI assistant
2. **AI reads the prompt** and follows instructions
3. **AI reports to GAUDÍ** by 5:00 PM daily

---

## 🎯 Quick Reference by Agent

### GAUDÍ (Architect)
- **Purpose:** Orchestrate project, make architectural decisions, big picture strategy
- **Key tasks:** Decision making, team coordination, competitor research, strategic planning
- **Daily:** Review feedback, make decisions, communicate with user, delegate to specialists
- **File:** `docs/roles/GAUDI_INITIAL_PROMPT.md`

### ARIA (Architect Assistant)
- **Purpose:** Save GAUDÍ 5-10 hours/week
- **Key tasks:** Intel, docs, communication, research
- **Daily:** Morning brief, coder check-ins, end-of-day summary
- **File:** `docs/roles/ARIA_INITIAL_PROMPT.md`

### Karen (DevOps Engineer)
- **Purpose:** Infrastructure, deployments, CI/CD
- **Key tasks:** Docker, migrations, server management
- **Current priority:** D-010 (Deployment Rollback, due Feb 3)
- **File:** `docs/roles/KAREN_INITIAL_PROMPT.md`

### Charo (Security Engineer)
- **Purpose:** Vulnerability scanning, security validation
- **Key tasks:** Scans, fixes verification, documentation
- **Current priority:** S-008 with Karen (Docker base image, due Feb 2)
- **File:** `docs/roles/CHARO_INITIAL_PROMPT.md`

### GRACE (QA/Testing Engineer)
- **Purpose:** Quality assurance, test strategy, test automation
- **Key tasks:** Write tests, validate fixes, ensure coverage
- **Current priority:** G-001, G-002, G-003 (tests for security fixes, due Feb 2)
- **File:** `docs/roles/GRACE_INITIAL_PROMPT.md`

### MIES (UI/UX Designer)
- **Purpose:** Design consistency, UX improvements, component library
- **Key tasks:** Design audits, create design systems, collaborate with frontend
- **Current priority:** M-001 (Design audit, due Feb 7)
- **File:** `docs/roles/MIES_INITIAL_PROMPT.md`

### HADI (Accessibility Specialist)
- **Purpose:** WCAG compliance, accessibility audits, inclusive design
- **Key tasks:** Keyboard navigation, screen reader support, WCAG audits
- **Current priority:** H-001 (WCAG audit, due Feb 14)
- **File:** `docs/roles/HADI_INITIAL_PROMPT.md`

### Coders (Linus, Guido, Turing)
- **Purpose:** Feature implementation, bug fixes
- **Key tasks:** Write code, tests, API endpoints
- **Current tasks:**
  - Linus: C-022 Backtesting (due Feb 3)
  - Guido: C-036 Paper Trading (due Feb 5)
  - Turing: C-016 Dashboards (due Feb 4)
- **File:** `docs/roles/CODERS_INITIAL_PROMPT.md`

---

## 📚 Required Reading (All Agents)

| Order | File | Description |
|-------|------|-------------|
| 1 | Role's INITIAL_PROMPT.md | This file - quick start |
| 2 | `tasks/ROLE_[ROLE].md` | Detailed role definition |
| 3 | `tasks/TASK_TRACKER.md` | Current project status |
| 4 | `docs/agents/feedback/2026/01-january/[agent]_feedback.md` | Recent improvements |

### What Each Initial Prompt Includes:
1. **Project Documentation Overview** - App structure and where to find docs
2. **Role Definition** - Core responsibilities and quality standards
3. **Current Tasks** - What to work on now
4. **Feedback Integration** - Lessons learned from previous sessions
5. **Daily Communication** - Report formats and timing
6. **Toolkit** - Commands and resources
7. **Critical Rules** - Must-follow guidelines from feedback

---

## 📂 Project Documentation Overview (Included in All Prompts)

All agents now receive this information at session start:

### Application Structure:
- **Backend:** `apps/backend/src/` - Django 5 REST API
  - api/, assets/, core/, data/, fundamentals/, investments/, trading/, tasks/, users/, utils/, backtesting/
- **Frontend:** `apps/frontend/src/` - Next.js 16 + React 19
  - app/, components/ (80+), contexts/, hooks/, lib/ (api/, types/, utils/), stores/ (4 Zustand stores)

### Quickstart Documentation:
- `docs/references/SETUP_COMPLETE.md` - Setup guide
- `docs/references/ONBOARDING.md` - Onboarding
- `docs/references/QUICK_INSTRUCTIONS.md` - Quick commands
- `docs/references/WHERE_TO_START.md` - Where to contribute

### Full Documentation:
- `docs/INDEX.md` - Master index (48+ files)
- `docs/architecture/` - System design, database schema, roadmaps
- `docs/development/` - Development guides, implementation docs
- `docs/operations/` - DevOps, infrastructure, deployment
- `docs/security/` - Security assessments, vulnerability reports
- `docs/agents/` - Agent communication, instructions, workflows

### Tech Stack:
- Backend: Django 5 + Django Ninja + MySQL 8 + TimescaleDB + Redis 7 + Dramatiq
- Frontend: Next.js 16 + React 19 + TypeScript 5 + Zustand + Tailwind CSS 4 + shadcn/ui

### Current Status:
- Backend: 95% complete
- Frontend: 75% complete

---

## 🎯 Daily Routine (All Agents)

| Time | Action |
|------|--------|
| 9:00 AM | Check status, verify state |
| Ongoing | Work on tasks, test incrementally |
| During session | Send progress updates to GAUDÍ + ARIA |
| 5:00 PM | Send daily report |

---

## 📞 Communication Channels

### Daily Reports (5:00 PM)
- **To:** GAUDÍ + ARIA
- **Format:** See each initial prompt

### Progress Updates (During Session)
- **To:** GAUDÍ + ARIA
- **When:** Complete subtask, hit blocker, need clarification

### Blockers/Emergencies
- **DevOps:** Ask Karen first, then GAUDÍ
- **Security:** Ask Charo first, then GAUDÍ
- **Architecture:** Ask GAUDÍ directly
- **General:** Ask ARIA

---

## 🎓 Feedback System

**Location:** `docs/agents/feedback/`

**Process:**
1. After each session, agents submit feedback
2. ARIA synthesizes and updates role definitions
3. GAUDÍ reviews for approval
4. Publish improved prompts for next session

**Template:** `docs/agents/feedback/TEMPLATE.md`

---

## 📊 Role Definitions (Master)

| Role | File | Last Updated |
|------|------|--------------|
| Architect (GAUDÍ) | `docs/roles/ROLE_GAUDI.md` | Feb 1 (updated) |
| ARIA | `docs/roles/ROLE_ARCHITECT_ASSISTANT.md` | Jan 31 |
| DevOps (Karen) | `docs/roles/ROLE_KAREN.md` | Feb 1 |
| Security (Charo) | `docs/roles/ROLE_CHARO.md` | Feb 1 |
| QA/Testing (GRACE) | `docs/roles/ROLE_GRACE.md` | Feb 1 (new) |
| UI/UX (MIES) | `docs/roles/ROLE_MIES.md` | Feb 1 (new) |
| Accessibility (HADI) | `docs/roles/ROLE_HADI.md` | Feb 1 (new) |
| Coders | `tasks/ROLE_CODERS.md` | Feb 1 |

---

## 🚀 Starting a New Session

**Steps:**
1. Copy the appropriate INITIAL_PROMPT.md
2. Paste to AI assistant
3. AI follows instructions
4. AI reads role definition
5. AI reports daily at 5:00 PM

---

## 📝 Notes

- All prompts updated with feedback from Jan 31 session
- Role definitions enhanced based on agent input
- Feedback system established for continuous improvement
- Communication templates standardized

---

**Next Update:** February 7, 2026 (after next feedback cycle)

---

GAUDI - Building Financial Excellence
