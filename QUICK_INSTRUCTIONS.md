# FinanceHub - Quick Agent Instructions

**For quick copy-paste when sending AI agents to FinanceHub**

---

```
You are working on FinanceHub, a financial platform.

## BEFORE STARTING (MANDATORY):

1. Read tasks.md:
   cat ~/Desktop/Projects/FinanceHub/tasks.md

2. Find your task in the list
   - Check if component already exists
   - If exists, read it first
   - Don't recreate - enhance existing

3. Update task status in tasks.md
   - PENDING → IN PROGRESS (when starting)
   - PENDING → EXISTS-ENHANCE (if component found)
   - IN PROGRESS → COMPLETED (when done)

## PROJECT CONTEXT:

Tech Stack:
- Frontend: Next.js 14, TypeScript, shadcn/ui, Tailwind CSS
- Backend: NestJS, TypeScript, Prisma, PostgreSQL
- Status: Backend 95%, Frontend 65%

## READ THESE:

For all tasks:
- ~/Desktop/Projects/FinanceHub/tasks.md
- ~/Desktop/Projects/FinanceHub/FEATURES_SPECIFICATION.md
- ~/Desktop/Projects/development-guides/06-CODE-STANDARDS.md

For frontend:
- ~/Desktop/Projects/development-guides/02-FRONTEND-DEVELOPMENT.md
- ~/clawd/prompts/frontend-shadcn-builder.md

For backend:
- ~/Desktop/Projects/development-guides/01-BACKEND-DEVELOPMENT.md
- ~/Desktop/Projects/development-guides/03-DATABASE-OPTIMIZATION.md

## CRITICAL RULES:

1. NEVER HALLUCINATE OR GUESS
   - Search for files before assuming they exist
   - Read actual code, don't make assumptions

2. ALWAYS WORK FROM EXISTING CODE
   - find . -name "*ComponentName*"
   - cat ./path/to/component.tsx
   - Enhance, don't recreate

3. ALWAYS ASK FOR CLARIFICATION
   - If unsure, ASK
   - Don't guess requirements

4. ALWAYS PUSH CHANGES
   - git add .
   - git commit -m "feat: [description]"
   - git push

5. USE AVAILABLE SKILLS
   - Check skills before starting
   - Use MCP if available

6. FOLLOW GUIDELINES
   - Code standards from development guides
   - Component patterns from existing code
   - Styling from stylesheet

## GOOD SOURCES:

Frontend:
- https://ui.shadcn.com (shadcn/ui)
- https://nextjs.org/docs (Next.js)
- https://www.radix-ui.com/primitives (Radix UI)

Backend:
- https://docs.nestjs.com (NestJS)
- https://www.prisma.io/docs (Prisma)

## EXAMPLE WORKFLOW:

Task: "Create MarketHeatmap.tsx"

1. Check if exists:
   find . -name "*MarketHeatmap*"

2. If found, read it:
   cat ./components/charts/MarketHeatmap.tsx

3. Update tasks.md:
   Change status to EXISTS-ENHANCE

4. Enhance existing code or create new

5. Test:
   npm run lint
   npm run typecheck

6. Push:
   git add .
   git commit -m "feat: enhance MarketHeatmap"
   git push

7. Update tasks.md to COMPLETED

## SUCCESS CHECKLIST:

- [ ] Read all relevant docs
- [ ] Checked for existing components
- [ ] Worked from existing code (if found)
- [ ] Followed code standards
- [ ] TypeScript strict mode
- [ ] Responsive design
- [ ] Dark mode support
- [ ] Accessible
- [ ] No errors/warnings
- [ ] Committed and pushed
- [ ] Updated tasks.md

---

**ASK IF UNSURE ABOUT ANYTHING**
```

---

## How to Use

**Copy to agent when starting FinanceHub task:**
```bash
cat ~/Desktop/Projects/FinanceHub/QUICK_INSTRUCTIONS.md
# Paste the prompt above to your AI agent
```

**Also available:**
- Full instructions: `~/Desktop/Projects/FinanceHub/AGENTS.md`
- Tasks list: `~/Desktop/Projects/FinanceHub/tasks.md`
- Features spec: `~/Desktop/Projects/FinanceHub/FEATURES_SPECIFICATION.md`
