# FinanceHub - AI Agent System Instructions

**Last Updated:** 2026-02-01
**Status:** ACTIVE - Use before starting any FinanceHub task
**Location:** `/Users/sergi/Desktop/Projects/FinanceHub/`

---

## 🚨 QUICK START (Most Agents Should Read This)

```bash
# FAST: Read only this for most tasks
cat /Users/sergi/Desktop/Projects/FinanceHub/docs/agents/QUICK_REFERENCE.md

# Your role-specific prompt
cat /Users/sergi/Desktop/Projects/FinanceHub/docs/agents/*_INITIAL_PROMPT.md

# Task list
cat /Users/sergi/Desktop/Projects/FinanceHub/tasks/TASK_TRACKER.md
```

**The QUICK_REFERENCE.md has:**
- Fast file search patterns
- Common commands
- Directory structure
- Troubleshooting
- Links to all development guides

---

## 🚨 MANDATORY PRE-WORK CHECKLIST

**BEFORE YOU START ANY TASK ON FinanceHub, YOU MUST:**

### 0. SECURITY CHECK (🚨 CRITICAL - READ FIRST)
```bash
# 🚨 READ THIS FIRST - Security is our top priority
cat ~/Desktop/Projects/FinanceHub/docs/security/FAILURE_POINT_ANALYSIS.md

# 🚨 CRITICAL: Verify you understand:
# - 23 security failure points identified by CHARO
# - 3 CRITICAL, 7 HIGH, 8 MEDIUM, 5 LOW severity issues
# - Token storage in localStorage vulnerable to XSS
# - DO NOT introduce new security vulnerabilities
# - ALL security fixes must be reviewed by CHARO
# - Report security concerns immediately

# 🚨 SECURITY TASKS APPROVED:
# - S-009 through S-016 (8 tasks, 3 CRITICAL due Feb 2)
# - See: tasks/security/CHARO_SECURITY_TASKS.md
```

### 1. Read This File First
```bash
cat ~/Desktop/Projects/FinanceHub/docs/agents/AGENTS.md
```

### 2. Read TASK_TRACKER.md
```bash
cat ~/Desktop/Projects/FinanceHub/tasks/TASK_TRACKER.md
```

### 3. Check Current Status
- Find your task in tasks.md
- Check if component already exists
- If exists, read the existing component
- Update task status to `IN PROGRESS` or `EXISTS - ENHANCE`

### 4. Read Related Documentation
- Backend tasks → Read backend guidelines
- Frontend tasks → Read frontend guidelines
- UI tasks → Read stylesheet and component standards
- Database tasks → Read schema and ORM patterns

---

## 📋 PROJECT OVERVIEW

**Project:** FinanceHub
**Type:** Financial platform (Bloomberg Terminal-inspired)
**Tech Stack:**
- Frontend: Next.js 16, React 19, TypeScript 5, shadcn/ui, Tailwind CSS 4
- Backend: Django 4.2.27, Django Ninja (REST API), Python 3.11
- Database: PostgreSQL 15 + TimescaleDB (time-series), Redis 7 (caching/WebSockets)
- Real-time: Django Channels (WebSocket), Dramatiq (background tasks)

**Current State:**
- Backend: ~95% complete
- Frontend: ~75% complete
- **Gap:** 25% of frontend needs work

---

## 🎯 YOUR WORKFLOW (MANDATORY)

### Step 1: Understand the Task
```bash
# Read TASK_TRACKER.md to find your task
cat ~/Desktop/Projects/FinanceHub/tasks/TASK_TRACKER.md

# Find your task number and read the description
# Check if status is PENDING, IN PROGRESS, or COMPLETED
```

### Step 2: Check if Component Exists
```bash
# Search for the component
cd ~/Desktop/Projects/FinanceHub

# Search for TypeScript/TSX files
find . -name "*[ComponentName]*.tsx" -o -name "*[ComponentName]*.ts"

# Example: If task is "Create data-table.tsx"
find . -name "*data-table*"
```

### Step 3: Read Existing Files (If Found)
```bash
# Read the existing component
cat ./components/ui/data-table.tsx

# Read related files
cat ./components/ui/button.tsx
cat ./components/ui/input.tsx
```

### Step 4: Read Project Standards
```bash
# Read development guides
cat ~/Desktop/Projects/development-guides/06-CODE-STANDARDS.md
cat ~/Desktop/Projects/development-guides/02-FRONTEND-DEVELOPMENT.md

# Read frontend guidelines
cat ~/Desktop/Projects/FinanceHub/FRONTEND_GUIDELINES.md  # if exists
cat ~/Desktop/Projects/FinanceHub/STYLESHEET.md  # if exists
```

### Step 5: Read Feature Specs
```bash
# Read feature specifications
cat ~/Desktop/Projects/FinanceHub/FEATURES_SPECIFICATION.md

# Read implementation guides
cat ~/Desktop/Projects/FinanceHub/FEATURE_IMPLEMENTATION_GUIDES.md
```

### Step 6: START WORKING
- Only after completing all checks above
- Update tasks.md status
- Work from existing code (don't recreate)
- Follow all standards

### Step 7: Push Changes
```bash
# After completing work
git add .
git commit -m "feat: [task description]"
git push
```

---

## 📚 MANDATORY DOCUMENTATION TO READ

### Fast Lookup (Recommended)
- ✅ **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Fast lookup for common needs

### Standardized Development Guides (Portfolio-Wide)
All FinanceHub agents MUST read these portfolio-wide guides:

| Guide | Path | When |
|-------|------|------|
| **Introduction** | `~/Desktop/Projects/development-guides/00-INTRODUCTION.md` | First time |
| **Code Standards** | `~/Desktop/Projects/development-guides/06-CODE-STANDARDS.md` | Every task |
| **Backend Guide** | `~/Desktop/Projects/development-guides/01-BACKEND-DEVELOPMENT.md` | Backend tasks |
| **Frontend Guide** | `~/Desktop/Projects/development-guides/02-FRONTEND-DEVELOPMENT.md` | Frontend tasks |
| **Database** | `~/Desktop/Projects/development-guides/03-DATABASE-OPTIMIZATION.md` | DB tasks |
| **Security** | `~/Desktop/Projects/development-guides/04-SECURITY-BEST-PRACTICES.md` | Every task |

### Cheatsheets (Quick Reference)
```
~/Desktop/Projects/development-guides/cheatsheets/
├── DJANGO-NINJA-CHEATSHEET.md
├── NEXTJS-14-CHEATSHEET.md
├── TYPESCRIPT-CHEATSHEET.md
└── DJANGO-NINJA-FILTER-SCHEMA.md
```

### For All Tasks
- ✅ `~/Desktop/Projects/FinanceHub/tasks.md`
- ✅ `~/Desktop/Projects/FinanceHub/FEATURES_SPECIFICATION.md`
- ✅ `~/Desktop/Projects/development-guides/06-CODE-STANDARDS.md`

### For Backend Tasks
- ✅ `~/Desktop/Projects/development-guides/01-BACKEND-DEVELOPMENT.md`
- ✅ `~/Desktop/Projects/development-guides/03-DATABASE-OPTIMIZATION.md`
- ✅ `~/Desktop/Projects/development-guides/04-SECURITY-BEST-PRACTICES.md`

### For Frontend Tasks
- ✅ `~/Desktop/Projects/development-guides/02-FRONTEND-DEVELOPMENT.md`
- ✅ `~/clawd/prompts/frontend-shadcn-builder.md` (shadcn/ui standards)

### For UI Components
- ✅ `~/Desktop/Projects/FinanceHub/STYLESHEET.md` (if exists)
- ✅ All existing components in same folder

### For Database Tasks
- ✅ `~/Desktop/Projects/FinanceHub/prisma/schema.prisma`
- ✅ `~/Desktop/Projects/development-guides/03-DATABASE-OPTIMIZATION.md`

---

## 🛠️ AVAILABLE SKILLS & PROMPTS

**Portfolio-wide resources are consolidated in `/Users/sergi/Desktop/Projects/PROMPTS_INDEX.md`**

### AI Skills (`/Users/sergi/Desktop/Projects/AI/`)

| Skill File | Purpose |
|------------|---------|
| `backend-skill.md` | Backend development patterns |
| `frontend-skill.md` | Frontend development patterns |
| `frontend-design-skill.md` | UI/UX design patterns |
| `How-to-skill.md` | General how-to guides |

**Usage:** Load skills as needed for your task type.

### Clawd Prompts (`/Users/sergi/clawd/prompts/`)

| Prompt | When to Use |
|--------|-------------|
| `frontend-shadcn-builder.md` | Building UI with shadcn/ui (~21KB) |
| `frontend-shadcn-quick.md` | Quick UI iterations |
| `documentation-project-full.md` | Comprehensive documentation |

### ATLAS Prompts (`/Users/sergi/clawd/ATLAS/prompts/`)

| Prompt | When to Use |
|--------|-------------|
| `bug-fix.md` | Debugging and fixing issues |
| `code-review.md` | Code quality review |
| `feature-implementation.md` | Adding new features |

---

## 🔌 MCP (Model Context Protocol) TO USE

**If available, use MCP servers for:**

### Code Context
- File reading and analysis
- Project structure understanding
- Code pattern recognition

### External APIs
- Market data (if integrating)
- News feeds (if adding features)

### Tools
- Linters and formatters
- Testing tools
- Documentation generators

---

## 🔍 GOOD SOURCES TO REFERENCE

### Frontend (Next.js, shadcn/ui)
- **Documentation:** https://nextjs.org/docs
- **shadcn/ui:** https://ui.shadcn.com
- **Radix UI:** https://www.radix-ui.com/primitives
- **Tailwind CSS:** https://tailwindcss.com/docs
- **Framer Motion:** https://www.framer.com/motion/

### Backend (NestJS)
- **Documentation:** https://docs.nestjs.com
- **Prisma:** https://www.prisma.io/docs

### Database (PostgreSQL)
- **PostgreSQL:** https://www.postgresql.org/docs
- **Prisma:** https://www.prisma.io/docs

### Patterns & Best Practices
- **React Patterns:** https://reactpatterns.com
- **TypeScript:** https://www.typescriptlang.org/docs
- **Frontend Masters:** https://frontendmasters.com/guides

### Finance & Trading
- **TradingView Charts:** https://www.tradingview.com/chart/
- **Chart.js:** https://www.chartjs.org/docs
- **Lightweight Charts:** https://www.tradingview.com/lightweight-charts/

---

## 📏 APP GUIDELINES TO FOLLOW

### Code Standards
```typescript
// Always use TypeScript strict mode
// Always type props and functions
// Never use `any` type

interface ComponentProps {
  // Proper interfaces
}

// Use functional components with hooks
const Component: React.FC<ComponentProps> = ({ prop }) => {
  // Implementation
}
```

### Component Structure
```typescript
// 1. Imports (grouped: external, internal, types)
import { Button } from "@/components/ui/button"
import type { User } from "@/types"

// 2. Component definition
const Component = ({ prop }: Props) => {
  // 3. Hooks (in order)
  const [state, setState] = useState()
  const ref = useRef()
  useEffect(() => {}, [])

  // 4. Event handlers
  const handleClick = () => {}

  // 5. Derived values
  const computed = useMemo(() => {}, [])

  // 6. Effects
  useEffect(() => {}, [])

  // 7. Render
  return <div>...</div>
}
```

### File Naming
- Components: PascalCase (e.g., `DataTable.tsx`)
- Utilities: camelCase (e.g., `formatCurrency.ts`)
- Types: PascalCase (e.g., `UserTypes.ts`)
- Hooks: camelCase with `use` prefix (e.g., `useUserData.ts`)

### Folder Structure
```
components/
├── ui/              # shadcn/ui components
├── charts/          # Chart components
├── analytics/       # Analytics components
├── forms/           # Form components
└── lib/             # Utilities
```

---

## 🎨 STYLESHEET STANDARDS

### Color Palette (from theme)
```css
/* Use semantic color tokens */
--primary: hsl(var(--primary))
--secondary: hsl(var(--secondary))
--muted: hsl(var(--muted))
--accent: hsl(var(--accent))
--destructive: hsl(var(--destructive))
```

### Spacing
```css
/* Use Tailwind spacing scale */
spacing-1: 0.25rem
spacing-2: 0.5rem
spacing-3: 0.75rem
spacing-4: 1rem
spacing-6: 1.5rem
spacing-8: 2rem
```

### Typography
```css
/* Use defined font sizes */
text-xs: 0.75rem
text-sm: 0.875rem
text-base: 1rem
text-lg: 1.125rem
text-xl: 1.25rem
text-2xl: 1.5rem
```

### Component Patterns
```typescript
// Always use cn() for class merging
import { cn } from "@/lib/utils"

<div className={cn("base-class", className)} />
```

---

## ⚠️ CRITICAL RULES

### 1. NEVER HALLUCINATE OR GUESS
- ❌ **DON'T:** Assume file paths, functions, or types exist
- ✅ **DO:** Search for files, read actual code, verify existence
- ❌ **DON'T:** Create new files if component exists
- ✅ **DO:** Read existing component, enhance it

### 2. ALWAYS WORK FROM EXISTING CODE
```bash
# Step 1: Search for component
find . -name "*ComponentName*"

# Step 2: Read it
cat ./path/to/component.tsx

# Step 3: Enhance it
# Add features, fix bugs, improve performance

# Step 4: Update tasks.md
# Change status to EXISTS-ENHANCE
```

### 3. ALWAYS ASK FOR CLARIFICATION
If you're unsure about:
- Component requirements
- Data structures
- API endpoints
- Business logic
- Styling preferences

**ASK! Don't guess.**

Example questions:
- "I found `data-table.tsx` exists. Should I enhance it with export features?"
- "The spec says 'create chart component' but `RealTimeChart.tsx` exists. Should I extend it?"
- "What timeframe options should be available for the chart selector?"
- "Should the heatmap support drill-down on click?"

### 4. ALWAYS PUSH CHANGES
```bash
# After every task
git add .
git commit -m "feat: [task description]"
git push

# Update tasks.md status to COMPLETED
```

### 5. ALWAYS USE SKILLS AND MCP
- Check available skills before starting
- Use MCP for code context if available
- Reference good sources (don't reinvent)

### 6. ALWAYS FOLLOW GUIDELINES
- Code standards from development guides
- Component patterns from existing code
- Styling from stylesheet/theme
- Testing requirements from project standards

---

## 🔄 TASK WORKFLOW EXAMPLE

### Scenario: Task says "Create MarketHeatmap.tsx"

**Step 1: Read tasks.md**
```bash
cat ~/Desktop/Projects/FinanceHub/tasks.md | grep -A 10 "MarketHeatmap"
```

**Step 2: Check if exists**
```bash
cd ~/Desktop/Projects/FinanceHub
find . -name "*MarketHeatmap*"
find . -name "*heatmap*"
find . -name "*treemap*"
```

**Step 3: If exists, read it**
```bash
cat ./components/charts/MarketHeatmap.tsx
```

**Step 4: Update tasks.md**
```bash
# Change status from PENDING to EXISTS-ENHANCE
# Note the file path found
```

**Step 5: Read related files**
```bash
cat ./components/charts/ComparisonChart.tsx  # Similar component
cat ~/Desktop/Projects/FinanceHub/FEATURES_SPECIFICATION.md | grep -A 20 "Market Heatmap"
```

**Step 6: Enhance or create**
- If exists: Add missing features
- If not exists: Create new component

**Step 7: Test**
```bash
npm run lint
npm run typecheck
npm run build
```

**Step 8: Push**
```bash
git add .
git commit -m "feat: enhance MarketHeatmap with drill-down"
git push
```

**Step 9: Update tasks.md**
- Change status to COMPLETED
- Note files modified

---

## 📊 CURRENT PROJECT STATUS

### Backend: 95% Complete
- ✅ API endpoints
- ✅ Database schema
- ✅ Authentication
- ✅ Real-time data
- ✅ WebSocket connections

### Frontend: 75% Complete
- ✅ Basic components
- ✅ Layout structure
- ✅ Some charts
- ⚠️ **Missing 30%:**
  - Advanced charting
  - Export functionality
  - Analytics dashboards
  - Risk management UI
  - Options trading UI

---

## 🎯 PRIORITY TASKS (from tasks.md)

### Critical (P0)
1. Advanced Chart Suite (Task #3)
2. Universal DataTable (Task #1) - EXISTS, enhance
3. Market Heatmap (Task #4)
4. Performance Metrics (Task #5)
5. Risk Dashboard (Task #6)

### High (P1)
6. Screener Filter Panel (Task #7)
7. Correlation Matrix (Task #8)
8. Options Chain (Task #9)
9. Economic Calendar (Task #13)
10. Analyst Ratings (Task #14)

### Medium (P2)
11. Backtest Results UI (Task #10)
12. AI Price Prediction (Task #11)
13. News Feed Expansion (Task #12)

### Low (P3)
14. Keyboard Shortcuts (Task #15)

---

## ✅ SUCCESS CHECKLIST

Before marking a task complete, verify:

- [ ] Read all relevant documentation
- [ ] Checked if component exists (not recreated unnecessarily)
- [ ] Worked from existing code (if found)
- [ ] Followed code standards
- [ ] Used TypeScript strict mode
- [ ] Made component responsive
- [ ] Added dark mode support
- [ ] Added accessibility attributes
- [ ] Tested on multiple devices
- [ ] Ran linter and type checker
- [ ] No console errors or warnings
- [ ] Committed and pushed changes
- [ ] Updated tasks.md status
- [ ] Asked for clarification when unsure

---

## 🚨 FINAL REMINDERS

### DO ✅
- Read tasks.md before starting
- Search for existing components
- Work from existing code
- Ask for clarification
- Push changes after completion
- Use available skills
- Follow all guidelines
- Reference good sources

### DON'T ❌
- Hallucinate or guess
- Create duplicate components
- Skip reading documentation
- Forget to push changes
- Ignore code standards
- Work in isolation without context
- Assume file paths exist
- Guess requirements

---

**Remember:** When in doubt, ASK. It's better to ask a clarifying question than to create duplicate work or incorrect implementations.

---

**Last Updated:** 2026-01-30
**Status:** ACTIVE - Use before every FinanceHub task
**Version:** 2.0
