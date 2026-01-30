# Task Template - Coders

**Copy this file to create new tasks:**
```bash
cp tasks/coders/template.md tasks/coders/[ID]-[short-name].md
```

---

# Task #[ID]: [Title]

**Assigned To:** Coder(s) - [Backend/Frontend/All]
**Priority:** [P0 | P1 | P2 | P3]
**Status:** [PENDING | IN_PROGRESS | BLOCKED | COMPLETED]
**Created:** [YYYY-MM-DD]
**Deadline:** [YYYY-MM-DD]
**Estimated Time:** [X hours]

---

## Overview
[What needs to be coded/fixed]

## Context
[Why this task is important]
[Related to: Feature, Bug, Migration, etc.]

## Acceptance Criteria
- [ ] [Code change 1]
- [ ] [Code change 2]
- [ ] [Test passes]
- [ ] [Lint passes]
- [ ] [Typecheck passes]

## Prerequisites
- [ ] [What must exist first]
- [ ] [What you need to understand]
- [ ] [Tools installed]

## Implementation Steps

### Step 1: [Title]
```bash
# Commands to run
# Files to edit
# What to change
```

### Step 2: [Title]
```bash
# Commands to run
# Files to edit
# What to change
```

### Step 3: [Title]
```bash
# Commands to run
# Files to edit
# What to change
```

## Testing

### Backend Testing (if applicable):
```bash
cd apps/backend
python manage.py check
python manage.py test
```

### Frontend Testing (if applicable):
```bash
cd apps/frontend
npm run lint
npm run typecheck
npm run test
npm run build
```

### Integration Testing:
```bash
# Start both apps and verify they work together
```

## Files Modified
- [ ] [File 1] - [What changed]
- [ ] [File 2] - [What changed]
- [ ] [File 3] - [What changed]

## Code Quality Checklist
- [ ] Lint passes (no warnings)
- [ ] Typecheck passes (no errors)
- [ ] Tests pass (all green)
- [ ] No console errors
- [ ] Follows existing patterns
- [ ] Proper TypeScript types (no `any`)
- [ ] Comments on complex logic

## Rollback Plan
If something doesn't work:
```bash
# Revert changes
git checkout [file]

# Or reset entire task
git reset --hard HEAD
```

## Tools to Use
- **MCP:** File operations, code search, bash commands
- **Skills:** web search (for docs), github (for examples)
- **Reference:** `AGENTS.md` for standards

## Dependencies
- [Task_ID] - [Must complete first]
- [Document] - [Reference link]

## Feedback to Architect
[After completing, report using this format]

### What I Did:
- [File 1]: [Changes made]
- [File 2]: [Changes made]
- [Files N]: [Changes made]

### Testing:
- ✅ Lint: [PASSED/FAILED]
- ✅ Typecheck: [PASSED/FAILED]
- ✅ Tests: [PASSED/FAILED] ([N] passing)
- ✅ Build: [PASSED/FAILED]
- ✅ Manual testing: [PASSED/FAILED]

### What I Discovered:
- [Issues encountered]
- [Unexpected behaviors]
- [Dependencies found]

### Next Steps:
- [What you recommend next]

## Updates
- **[YYYY-MM-DD HH:MM]:** [Status update]
- **[YYYY-MM-DD HH:MM]:** [Status update]

---
**Last Updated:** [YYYY-MM-DD]
