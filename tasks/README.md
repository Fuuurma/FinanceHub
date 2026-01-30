# 📋 TASKS DIRECTORY - ROLE-BASED ORGANIZATION

**Last Updated:** 2026-01-30
**Status:** ACTIVE - Monorepo Migration in Progress

---

## 📁 Directory Structure

```
tasks/
├── README.md                    # This file
├── TASK_TRACKER.md             # Master task tracking
├── ROLE_ARCHITECT.md           # Architect role definition
├── ROLE_DEVOPS.md              # DevOps (Karen) role definition
├── ROLE_SECURITY.md            # Security (Charo) role definition
├── ROLE_CODERS.md              # Coders role definition
│
├── architect/                  # Architect tasks
│   ├── template.md            # Task template
│   ├── 001-monorepo-migration.md  # Current project
│   └── ...
│
├── devops/                     # DevOps (Karen) tasks
│   ├── template.md
│   ├── 001-backup-src.md
│   ├── 002-repository-fix.md
│   ├── 003-directory-reorg.md
│   ├── 004-ci-cd-update.md
│   └── 005-cleanup-src.md
│
├── security/                   # Security (Charo) tasks
│   ├── template.md
│   └── 001-migration-validation.md
│
├── coders/                     # Coder tasks (3 coders)
│   ├── template.md
│   ├── 001-backend-path-fixes.md
│   ├── 002-frontend-path-fixes.md
│   └── 003-integration-testing.md
│
└── shared/                     # Cross-role tasks
    ├── template.md
    └── ...
```

---

## 🎯 How This Works

### 1. Role-Based Tasks
Each role has its own folder:
- **Architect:** Strategy, design, coordination
- **DevOps:** Infrastructure, deployment, migration
- **Security:** Vulnerability scanning, validation
- **Coders:** Feature implementation, bug fixes
- **Shared:** Tasks that need multiple roles

### 2. Task Assignment Flow
```
Architect creates task
    ↓
Assigns to role (devops/security/coders)
    ↓
Agent reads task definition
    ↓
Executes using available tools (MCP/Skills)
    ↓
Reports back to Architect
    ↓
Architect reviews & approves
```

### 3. Communication Protocol
- **Agent → Architect:** Use feedback format (see role definitions)
- **Architect → Agent:** Use decision format
- **All agents can see:** All tasks in all folders
- **But ONLY work on:** Tasks in their own role folder

---

## 📊 Current Priority: Monorepo Migration

**Status:** 🚀 IN PROGRESS (Day 1 of 5)
**Start Date:** 2026-01-30
**Target End:** 2026-02-05

### Phase 1: Preparation (Day 1 - Today)
- ✅ Role definitions created
- ✅ Task structure established
- ⏳ DevOps: Backup src/ directory
- ⏳ DevOps: Create new GitHub repo

### Phase 2-7: See Individual Tasks
- `tasks/devops/001-005.md`
- `tasks/security/001.md`
- `tasks/coders/001-003.md`

---

## 🔑 IMPORTANT RULES

### For All Agents:

1. **Read Your Role Definition First**
   ```bash
   cat tasks/ROLE_[YOUR_ROLE].md
   ```

2. **Check Available Tools**
   - MCP servers (file operations, bash, git, etc.)
   - Skills (github, web search, etc.)
   - Reference: `AGENTS.md` → "🛠️ AVAILABLE SKILLS TO USE"

3. **Use Task Template**
   - Each role has a template.md
   - Follow the format exactly
   - Include all required sections

4. **Report Progress**
   - After each task: Report to Architect
   - If blocked: Report immediately
   - If completed: Provide evidence

5. **Stay in Your Lane**
   - DevOps: Only work in `tasks/devops/`
   - Security: Only work in `tasks/security/`
   - Coders: Only work in `tasks/coders/`
   - Architect: Can access all folders

---

## 📝 Task Template Usage

Each role has a `template.md` file. To create a new task:

```bash
# 1. Copy the template
cp tasks/[role]/template.md tasks/[role]/[task-number]-[short-name].md

# 2. Edit the task file
# Fill in all sections:
# - Task ID & Title
# - Priority & Status
# - Description & Context
# - Acceptance Criteria
# - Implementation Steps
# - Dependencies
# - Deliverables

# 3. Assign to agent
# Architect: Assign task to specific agent
# Agent: Read task, ask questions, execute
```

---

## 🔄 Task Status Values

- **PENDING:** Not started yet
- **IN_PROGRESS:** Currently being worked on
- **BLOCKED:** Waiting on something (report to Architect)
- **COMPLETED:** Finished and verified
- **CANCELLED:** No longer needed

---

## 📊 Priority Levels

- **P0 (CRITICAL):** Must do now, blocks everything else
- **P1 (HIGH):** Must do today/tomorrow
- **P2 (MEDIUM):** Must do this week
- **P3 (LOW):** Nice to have, backlog

---

## 💬 Communication Guidelines

### When to Communicate:
- ✅ **ALWAYS:** Before starting a task (confirm understanding)
- ✅ **ALWAYS:** After completing a task (provide evidence)
- ✅ **ALWAYS:** When blocked (don't wait)
- ✅ **ALWAYS:** When you discover something important

### How to Communicate:
See your role definition for the exact feedback format.

### Response Time Expectations:
- **Architect:** Decisions within 1 hour
- **DevOps/Security/Coders:** Response within 2 hours
- **Critical issues:** Immediate escalation

---

## 🎓 Getting Started

### New to the project?
1. Read your role definition: `tasks/ROLE_[YOUR_ROLE].md`
2. Read the master guide: `AGENTS.md`
3. Check current tasks: `TASK_TRACKER.md`
4. Pick up your first assigned task
5. Ask Architect if unsure

### Need help?
1. Check your role definition
2. Check `AGENTS.md` for available tools
3. Ask Architect a specific question
4. Provide context about what you tried

---

## 📈 Success Metrics

We're successful when:
- ✅ All tasks completed on time
- ✅ Zero security vulnerabilities
- ✅ All tests passing
- ✅ Clear documentation
- ✅ Happy team members

---

**Remember:** The Architect is the universal point of truth. When in doubt, ask!

**Quick Links:**
- 📖 Master Guide: `AGENTS.md` (root)
- 📊 Task Tracker: `TASK_TRACKER.md`
- 👤 Role Definitions: `ROLE_*.md`
- 💬 Agent Comms: `../docs/agents/COMMUNICATION_PROTOCOL.md`
