# FinanceHub Agent Instructions - Summary

**Date:** 2026-01-30
**Purpose:** System instructions for AI agents working on FinanceHub

---

## What I Created

### 1. Comprehensive Agent Instructions (AGENTS.md)
**File:** `/Users/sergi/Desktop/Projects/FinanceHub/AGENTS.md`
**Length:** ~12,000 words
**Contains:**
- Mandatory pre-work checklist
- Complete workflow (8 steps)
- All documentation to read
- Available skills to use
- MCP servers to use
- Good sources to reference
- App guidelines to follow
- Stylesheet standards
- Critical rules (6 mandatory rules)
- Task workflow example
- Current project status
- Priority tasks list
- Success checklist

**Use when:** Agent needs comprehensive guidance for FinanceHub

### 2. Quick Reference (QUICK_INSTRUCTIONS.md)
**File:** `/Users/sergi/Desktop/Projects/FinanceHub/QUICK_INSTRUCTIONS.md`
**Length:** ~200 lines
**Contains:**
- Essential pre-work steps
- Tech stack overview
- Documentation to read
- Critical rules summary
- Example workflow
- Success checklist

**Use when:** Faster onboarding needed or quick reference

---

## Key Features

### ✅ Pre-Work Checklist
Before ANY task, agents must:
1. Read AGENTS.md
2. Read tasks.md
3. Check if component exists
4. Read related documentation
5. Update task status

### ✅ Workflow Enforcement
Step-by-step process:
1. Understand the task
2. Check if component exists (SEARCH FIRST)
3. Read existing files (if found)
4. Read project standards
5. Read feature specs
6. START WORKING
7. Push changes

### ✅ No Hallucination Rule
```bash
# Before creating anything:
find . -name "*ComponentName*"

# Read what exists:
cat ./path/to/component.tsx

# Enhance, don't recreate
```

### ✅ Clarification Required
Agents instructed to:
- ASK if unsure about requirements
- ASK if component existence is unclear
- ASK about business logic
- ASK about styling preferences
- NEVER guess

### ✅ Mandatory Documentation Reading

**For all tasks:**
- tasks.md (your task)
- FEATURES_SPECIFICATION.md (what to build)
- CODE_STANDARDS.md (how to write code)

**For frontend:**
- FRONTEND_DEVELOPMENT.md
- frontend-shadcn-builder.md prompt

**For backend:**
- BACKEND_DEVELOPMENT.md
- DATABASE_OPTIMIZATION.md

### ✅ Skills & MCP Usage
Agents reminded to:
- Check available skills before starting
- Use MCP for code context
- Reference good sources (don't reinvent)

### ✅ Push Changes Required
Every task must end with:
```bash
git add .
git commit -m "feat: [description]"
git push
```

### ✅ Follow Guidelines
- Code standards from development guides
- Component patterns from existing code
- Styling from stylesheet/theme
- Testing requirements

---

## Current Project Status

**Backend:** 95% complete
**Frontend:** 65% complete
**Gap:** 30% of frontend needs work

**Priority Tasks:**
1. Advanced Chart Suite (Task #3) - IN PROGRESS
2. Universal DataTable (Task #1) - EXISTS, needs enhancement
3. Market Heatmap (Task #4)
4. Performance Metrics (Task #5)
5. Risk Dashboard (Task #6)

---

## How to Use These Instructions

### When Starting a New FinanceHub Task

**Option 1: Full Instructions**
```bash
cat ~/Desktop/Projects/FinanceHub/AGENTS.md
# Send this to your AI agent
```

**Option 2: Quick Reference**
```bash
cat ~/Desktop/Projects/FinanceHub/QUICK_INSTRUCTIONS.md
# Send this to your AI agent
```

### What Agent Will Do

1. **Pre-work:**
   - Read tasks.md to find their task
   - Search for existing components
   - Read relevant documentation
   - Update task status

2. **Execution:**
   - Work from existing code (not recreate)
   - Follow all standards
   - Ask for clarification when unsure
   - Use available skills

3. **Post-work:**
   - Test everything
   - Commit and push changes
   - Update tasks.md to COMPLETED
   - Report what was done

---

## Example: Sending Agent to Work

### Scenario: Task #3 - Advanced Chart Suite

**You send:**
```
Work on FinanceHub Task #3: Advanced Chart Suite

First, read:
cat ~/Desktop/Projects/FinanceHub/AGENTS.md
cat ~/Desktop/Projects/FinanceHub/tasks.md

Follow the workflow in AGENTS.md.
Update task status as you work.
Push changes when complete.
```

**Agent will:**
1. Read AGENTS.md (full instructions)
2. Read tasks.md (find Task #3)
3. Check: `find . -name "*Chart*"` → finds RealTimeChart.tsx
4. Read RealTimeChart.tsx (319 lines)
5. Update tasks.md status to EXISTS-ENHANCE
6. Read related chart components
7. Enhance with candlestick, more indicators, drawing tools
8. Test, commit, push
9. Update tasks.md to COMPLETED

---

## Critical Rules Enforced

### 1. NO HALLUCINATION
- Search before assuming
- Read actual code
- Verify file paths
- Don't guess types or APIs

### 2. WORK FROM EXISTING
- If component exists, enhance it
- Never recreate from scratch
- Build on what's there
- Preserve existing functionality

### 3. ASK FOR CLARIFICATION
- If unsure about requirements
- If spec is ambiguous
- If multiple approaches possible
- If component choice unclear

### 4. PUSH CHANGES
- After every task
- With meaningful commit messages
- Update tasks.md status
- Document what was done

### 5. USE SKILLS & MCP
- Check available skills
- Use MCP for context
- Reference good sources
- Don't reinvent the wheel

### 6. FOLLOW GUIDELINES
- Code standards (from guides)
- Component patterns (existing code)
- Styling (stylesheet/theme)
- Testing requirements

---

## Documentation Structure

```
~/Desktop/Projects/FinanceHub/
├── AGENTS.md                  # Full instructions (12,000 words)
├── QUICK_INSTRUCTIONS.md      # Quick reference (200 lines)
├── tasks.md                   # Task list with status
├── FEATURES_SPECIFICATION.md  # 200+ features
├── PROJECT_CONTEXT.md         # Project overview (if exists)
└── [other documentation...]
```

---

## Success Metrics

When agents follow these instructions, you get:

✅ **No duplicate components** - Always check for existing
✅ **No hallucinated code** - Only use real APIs/types
✅ **Consistent code style** - Follow all standards
✅ **Proper git history** - Always commit and push
✅ **Clarification when needed** - Ask, don't guess
✅ **Better code quality** - Reference good sources
✅ **Faster development** - Build on existing work
✅ **Easier maintenance** - Clear documentation

---

## Files Created

✅ `/Users/sergi/Desktop/Projects/FinanceHub/AGENTS.md` - Comprehensive instructions
✅ `/Users/sergi/Desktop/Projects/FinanceHub/QUICK_INSTRUCTIONS.md` - Quick reference
✅ This summary

---

## Customization

### For Specific Tasks
Add to QUICK_INSTRUCTIONS.md:
```
## TASK-SPECIFIC NOTES:

For Chart tasks:
- Use Chart.js or lightweight-charts
- Follow TradingView patterns
- Reference: https://www.tradingview.com/lightweight-charts/

For Form tasks:
- Use React Hook Form + Zod
- Follow examples in components/forms/
- Reference: https://react-hook-form.com
```

### For Specific Skills
Add to AGENTS.md:
```
## SKILLS TO USE FOR FinanceHub:

For backend:
- `github` - For PRs and issues
- `coding-agent` - For running tests

For frontend:
- `github` - For PRs and issues
- `obsidian` - For documentation
```

---

**All set!** Every AI agent working on FinanceHub will now:
- Read the necessary docs
- Check for existing components
- Work from what's there (not recreate)
- Ask for clarification
- Push changes
- Follow all standards
- Reference good sources

No more duplicate work. No more hallucinations. No more confusion. 🎯✅
