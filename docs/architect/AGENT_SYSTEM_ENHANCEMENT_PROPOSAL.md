# 🤖 FinanceHub Agent System - Enhanced Roles, Skills & MCP

**Date:** February 1, 2026
**Status:** PROPOSAL
**Author:** GAUDÍ (Architect)
**Inspired by:** ATLAS (clawdbot) + MCP integration

---

## 🎯 PROBLEM STATEMENT

**Current Issues:**
- 10 agents with overlapping responsibilities
- No standardized skill system
- Missing MCP (Model Context Protocol) integration
- Documentation is scattered and inconsistent
- No dedicated documentation maintainer
- Skills not defined per role
- MCP tools not configured

**Goal:** Create a clean, efficient agent system with:
1. Clear role definitions
2. Assigned skills per role
3. MCP tools for capabilities
4. Documentation Maintainer role
5. Reduced overlap/confusion

---

## 📊 PROPOSED AGENT STRUCTURE (11 Agents → 9 Focused Roles)

### Leadership (2)
1. **GAUDÍ** (Architect) - Strategic vision, technical leadership
2. **ARIA** (Agent Coordinator) - Agent monitoring, workflow coordination

### Core Development (3)
3. **Linus** (Backend Coder) - Django/Python APIs
4. **Turing** (Frontend Coder) - Next.js/React UI
5. **Atlas** (Full-Stack Coder) - **NEW** - Fills gaps, handles overflow

### Quality Assurance (3)
6. **Charo** (Security Engineer) - Security audits, vulnerability assessment
7. **GRACE** (QA Engineer) - Testing, quality assurance
8. **HADI** (Accessibility Engineer) - WCAG compliance, accessibility

### Specialized Support (2)
9. **MIES** (UI/UX Designer) - Design system, mockups
10. **SCRIBE** (**NEW** - Documentation Maintainer) - Docs, guides, standards
11. **Karen** (DevOps) - Infrastructure, deployment, CI/CD

**Changes:**
- ❌ **Removed:** Guido (Backend) - merged into Linus + Atlas
- ✅ **Added:** Atlas (Full-Stack) - flexible coder for overflow
- ✅ **Added:** Scribe (Documentation Maintainer) - docs organization

---

## 🎨 SKILL SYSTEM (From ATLAS + Custom)

### Skill Categories

#### **Technical Skills**
- `python` - Python 3.11+, type hints, pytest
- `typescript` - TypeScript 5+, strict mode
- `react` - React 18+, hooks, patterns
- `next-js` - Next.js 16, App Router, SSR
- `django-ninja` - Django 5, Django Ninja API
- `node-js` - Node.js, npm, package management
- `tailwind-css` - Tailwind CSS 4, utility-first
- `radix-ui` - Radix UI primitives
- `shadcn` - shadcn/ui components

#### **Specialized Skills**
- `security-analysis` - OWASP Top 10, vulnerability scanning
- `web-research` - Brave Search API, market research
- `data-providers` - Financial APIs, market data
- `accessibility` - WCAG 2.2, ARIA, screen readers
- `professional-frontend` - Frontend patterns, performance
- `professional-backend` - Backend patterns, scaling
- `financial-research` - Financial analysis, markets
- `documentation` - Technical writing, guides

---

## 🔧 SKILL ASSIGNMENTS PER ROLE

### GAUDÍ (Architect)
**Skills:**
- `financial-research` - Strategic market analysis
- `documentation` - Architecture decisions, RFCs
- `professional-frontend` - Frontend architecture oversight
- `professional-backend` - Backend architecture oversight

**MCP Tools:**
- `brave-search` - Market research, competitor analysis
- `glm-vision` - Architecture diagram review

**Responsibilities:**
- Strategic vision and technical leadership
- Architecture decisions and RFCs
- Agent coordination and task assignment
- Quality standards and decision making

---

### ARIA (Agent Coordinator)
**Skills:**
- `documentation` - Status reports, coordination logs
- `web-research` - Agent performance research

**MCP Tools:**
- `brave-search` - Best practices for agent coordination

**Responsibilities:**
- Monitor all agents and status
- Facilitate communication between agents
- Track responsiveness and productivity
- Escalate blockers to GAUDÍ

---

### Linus (Backend Coder)
**Skills:**
- `python` - Python 3.11+, type hints, pytest
- `django-ninja` - Django 5, Django Ninja API
- `node-js` - Node.js for backend scripts
- `security-analysis` - Backend security
- `professional-backend` - Backend patterns

**MCP Tools:**
- None (coding-focused)

**Responsibilities:**
- Django REST API development
- Database schema and ORM
- Backend business logic
- API documentation

---

### Turing (Frontend Coder)
**Skills:**
- `typescript` - TypeScript 5+, strict mode
- `react` - React 18+, hooks, patterns
- `next-js` - Next.js 16, App Router, SSR
- `tailwind-css` - Tailwind CSS 4
- `radix-ui` - Radix UI primitives
- `shadcn` - shadcn/ui components
- `accessibility` - Frontend accessibility
- `professional-frontend` - Frontend patterns

**MCP Tools:**
- `glm-vision` - UI screenshot analysis, component comparison

**Responsibilities:**
- Next.js frontend development
- React components and hooks
- UI state management
- Responsive design

---

### Atlas (Full-Stack Coder) - **NEW**
**Skills:**
- `python` - Python backend work
- `typescript` - TypeScript frontend work
- `react` - React components
- `next-js` - Next.js features
- `django-ninja` - Django API work
- `tailwind-css` - Styling
- `node-js` - Build tools, scripts
- `security-analysis` - Basic security

**MCP Tools:**
- `glm-vision` - UI understanding

**Responsibilities:**
- **Overflow work** - When Linus/Turing are blocked
- **Full-stack features** - Small features spanning frontend+backend
- **Bug fixes** - Quick fixes across the stack
- **Code reviews** - Second pair of eyes

**When to Use Atlas:**
- Linus/Turing are at capacity
- Need rapid prototyping
- Full-stack feature (small/medium)
- Emergency bug fixes

---

### Charo (Security Engineer)
**Skills:**
- `security-analysis` - OWASP Top 10, vulnerability scanning
- `python` - Security testing scripts
- `professional-backend` - Backend security review

**MCP Tools:**
- `brave-search` - Latest CVEs, security advisories

**Responsibilities:**
- Security audits and penetration testing
- Vulnerability assessment and reporting
- Security best practices enforcement
- Dependency scanning

---

### GRACE (QA Engineer)
**Skills:**
- `python` - pytest test frameworks
- `typescript` - Frontend testing (Jest, Playwright)
- `documentation` - Test plans, QA reports
- `professional-frontend` - Frontend testing
- `professional-backend` - Backend testing

**MCP Tools:**
- `brave-search` - Testing best practices

**Responsibilities:**
- Test strategy and planning
- Test case development
- Automated test implementation
- QA reporting and metrics

---

### HADI (Accessibility Engineer)
**Skills:**
- `accessibility` - WCAG 2.2, ARIA, screen readers
- `typescript` - Frontend accessibility testing
- `documentation` - Accessibility guides
- `professional-frontend` - Accessible frontend patterns

**MCP Tools:**
- `brave-search` - WCAG updates, a11y best practices

**Responsibilities:**
- WCAG compliance auditing
- Accessibility testing
- ARIA attribute implementation
- Screen reader testing

---

### MIES (UI/UX Designer)
**Skills:**
- `documentation` - Design system docs
- `professional-frontend` - Design patterns

**MCP Tools:**
- `glm-vision` - Design comparison, UI review

**Responsibilities:**
- Design system creation and maintenance
- UI/UX mockups and prototypes
- Design tokens and themes
- Component library governance

---

### Scribe (Documentation Maintainer) - **NEW**
**Skills:**
- `documentation` - Technical writing, guides, API docs
- `web-research` - Documentation best practices

**MCP Tools:**
- `brave-search` - Documentation standards research
- `glm-vision` - Diagram understanding

**Responsibilities:**
- **Documentation organization** - Keep docs clean and structured
- **Guide creation** - Getting started guides, tutorials
- **API documentation** - Auto-generate from code
- **Standards enforcement** - Doc standards, formatting
- **Changelog maintenance** - Track changes, releases
- **README management** - Keep READMEs up to date
- **Onboarding docs** - Help new agents/users

**Why This Role is Needed:**
- Current docs are scattered and inconsistent
- No one owns documentation quality
- Developers shouldn't maintain docs (they focus on code)
- Needs someone dedicated to doc organization

**Docs Scribe Maintains:**
- `docs/` folder structure
- `README.md` files
- `docs/INDEX.md` - Documentation index
- `docs/getting-started/` - Tutorials
- `docs/api/` - API documentation
- `docs/guides/` - How-to guides
- `CHANGELOG.md` - Version history

---

### Karen (DevOps)
**Skills:**
- `node-js` - Build scripts, CI/CD
- `python` - Deployment scripts
- `documentation` - Runbooks, deployment docs

**MCP Tools:**
- `brave-search` - DevOps best practices

**Responsibilities:**
- Infrastructure management
- CI/CD pipeline maintenance
- Deployment automation
- Monitoring and alerting
- Runbook creation

---

## 🔌 MCP INTEGRATION

### MCP Servers to Configure

#### 1. **Brave Search MCP** (Web Research)
**Purpose:** Market research, competitor analysis, best practices

**Configuration:**
```json
{
  "brave-search": {
    "type": "remote",
    "url": "https://search.brave.com/api",
    "enabled": true
  }
}
```

**Agents Using It:**
- GAUDÍ - Market research
- ARIA - Agent coordination research
- Charo - Security CVEs
- GRACE - Testing best practices
- HADI - Accessibility standards
- Scribe - Documentation standards
- Karen - DevOps best practices

---

#### 2. **GLM-4.7 Vision MCP** (Visual Understanding)
**Purpose:** UI analysis, diagram understanding, design comparison

**Configuration:**
```json
{
  "glm-vision": {
    "type": "local",
    "command": ["npx", "-y", "@z_ai/mcp-server"],
    "enabled": true,
    "environment": {
      "Z_AI_API_KEY": "{env:GLM_API_KEY}",
      "Z_AI_MODE": "ZAI"
    }
  }
}
```

**Agents Using It:**
- GAUDÍ - Architecture diagram review
- Turing - UI screenshot analysis, component comparison
- Atlas - UI understanding
- MIES - Design comparison, UI review
- Scribe - Diagram understanding for docs

---

#### 3. **MiniMax MCP** (Media Generation) - Optional
**Purpose:** Generate images, audio, video for tutorials/demos

**Configuration:**
```json
{
  "minimax": {
    "type": "local",
    "command": ["uvx", "-y", "minimax-mcp"],
    "enabled": true,
    "environment": {
      "MINIMAX_API_KEY": "{env:MINIMAX_API_KEY}",
      "MINIMAX_MCP_BASE_PATH": "/Users/sergi/Desktop/Projects/FinanceHub/generated",
      "MINIMAX_API_HOST": "https://api.minimax.io",
      "MINIMAX_API_RESOURCE_MODE": "local"
    }
  }
}
```

**Agents Using It:**
- Scribe - Generate tutorial screenshots, diagrams
- MIES - Generate design mockup previews
- GAUDÍ - Generate architecture diagrams

---

## 📁 MCP CONFIGURATION FILE

**Location:** `/Users/sergi/Desktop/Projects/FinanceHub/.opencode.jsonc`

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "brave-search": {
      "type": "remote",
      "url": "https://search.brave.com/api",
      "enabled": true
    },
    "glm-vision": {
      "type": "local",
      "command": ["npx", "-y", "@z_ai/mcp-server"],
      "enabled": true,
      "environment": {
        "Z_AI_API_KEY": "{env:GLM_API_KEY}",
        "Z_AI_MODE": "ZAI"
      }
    },
    "minimax": {
      "type": "local",
      "command": ["uvx", "-y", "minimax-mcp"],
      "enabled": false,
      "environment": {
        "MINIMAX_API_KEY": "{env:MINIMAX_API_KEY}",
        "MINIMAX_MCP_BASE_PATH": "/Users/sergi/Desktop/Projects/FinanceHub/generated",
        "MINIMAX_API_HOST": "https://api.minimax.io",
        "MINIMAX_API_RESOURCE_MODE": "local"
      }
    }
  },
  "permission": {
    "skill": {
      "python": "allow",
      "typescript": "allow",
      "javascript": "allow",
      "react": "allow",
      "next-js": "allow",
      "django-ninja": "allow",
      "node-js": "allow",
      "tailwind-css": "allow",
      "radix-ui": "allow",
      "shadcn": "allow",
      "security-analysis": "allow",
      "accessibility": "allow",
      "web-research": "allow",
      "data-providers": "allow",
      "professional-frontend": "allow",
      "professional-backend": "allow",
      "financial-research": "allow",
      "documentation": "allow",
      "*": "allow"
    }
  },
  "tools": {
    "brave-search_*": true,
    "glm-vision_*": true,
    "minimax_*": false
  }
}
```

---

## 📚 DOCUMENTATION STRUCTURE (Maintained by Scribe)

```
docs/
├── agents/                  # Agent documentation (Scribe maintains)
│   ├── AGENTS.md           # All agent roles
│   ├── GAUDI_INITIAL_PROMPT.md
│   ├── ARIA_INITIAL_PROMPT.md
│   ├── LINUS_INITIAL_PROMPT.md
│   ├── TURING_INITIAL_PROMPT.md
│   ├── ATLAS_INITIAL_PROMPT.md
│   ├── CHARO_INITIAL_PROMPT.md
│   ├── GRACE_INITIAL_PROMPT.md
│   ├── HADI_INITIAL_PROMPT.md
│   ├── MIES_INITIAL_PROMPT.md
│   ├── SCRIBE_INITIAL_PROMPT.md
│   ├── KAREN_INITIAL_PROMPT.md
│   └── COMMUNICATION_HUB.md
├── api/                     # API documentation (auto-generated + Scribe)
│   ├── backend/
│   │   ├── authentication.md
│   │   ├── portfolios.md
│   │   └── trading.md
│   └── frontend/
│       ├── components.md
│       └── hooks.md
├── architecture/            # Architecture docs (GAUDÍ + Scribe)
│   ├── system-design.md
│   ├── database-schema.md
│   └── api-contracts.md
├── design/                  # Design system (MIES + Scribe)
│   ├── design-tokens.md
│   ├── component-library.md
│   └── brutalist-guidelines.md
├── getting-started/         # Tutorials (Scribe creates)
│   ├── installation.md
│   ├── quick-start.md
│   └── first-trade.md
├── guides/                  # How-to guides (Scribe creates)
│   ├── adding-features.md
│   ├── testing-guide.md
│   ├── deployment-guide.md
│   └── security-guide.md
├── security/                # Security docs (Charo + Scribe)
│   ├── security-checklist.md
│   └── vulnerability-reporting.md
├── operations/              # Operations docs (Karen + Scribe)
│   ├── runbooks/
│   ├── monitoring.md
│   └── incident-response.md
├── archive/                 # Old docs (Scribe organizes)
│   ├── communications/
│   ├── sessions/
│   └── tasks/
├── reports/                 # Reports (ARIA + Scribe)
├── deployment/              # Deployment docs (Karen + Scribe)
├── architect/               # Strategic docs (GAUDÍ)
└── INDEX.md                 # Documentation index (Scribe maintains)
```

---

## 🎯 SKILL FILES (Create from ATLAS)

**Location:** `/Users/sergi/Desktop/Projects/FinanceHub/.opencode/skills/`

**Copy from ATLAS:**
- `python-skill.md`
- `typescript-skill.md`
- `react-skill.md`
- `next-js-skill.md`
- `django-ninja-skill.md`
- `node-js-skill.md`
- `tailwind-css-skill.md`
- `radix-ui-skill.md`
- `shadcn-skill.md`
- `security-analysis-skill.md`
- `professional-frontend-skill.md`
- `professional-backend-skill.md`
- `financial-research-advisor-skill.md`
- `financial-research-report-skill.md`

**Create new:**
- `accessibility-skill.md` - WCAG, ARIA, screen readers
- `documentation-skill.md` - Technical writing, guides
- `web-research-skill.md` - Brave Search API usage
- `data-providers-skill.md` - Financial APIs, market data

---

## 📋 IMPLEMENTATION PLAN

### Phase 1: MCP Integration (1-2 hours)
1. Create `.opencode.jsonc` with MCP configuration
2. Test MCP servers (brave-search, glm-vision)
3. Configure environment variables
4. Test MCP tools with each agent

### Phase 2: Skill System Setup (2-3 hours)
1. Copy skill files from ATLAS to FinanceHub
2. Create new skill files (accessibility, documentation, web-research)
3. Map skills to agent roles
4. Update agent prompts with skill assignments

### Phase 3: Create New Agents (2-3 hours)
1. **Atlas (Full-Stack Coder)**
   - Create `docs/agents/ATLAS_INITIAL_PROMPT.md`
   - Define overflow workflow
   - Set up skill assignments
2. **Scribe (Documentation Maintainer)**
   - Create `docs/agents/SCRIBE_INITIAL_PROMPT.md`
   - Define documentation standards
   - Set up doc structure
   - Hand over messy docs for cleanup

### Phase 4: Remove Guido, Update Docs (1 hour)
1. Reassign Guido's tasks to Linus + Atlas
2. Update agent count (10 → 11)
3. Update all documentation to reflect new structure
4. Archive Guido's initial prompt

### Phase 5: Scribe Cleanup (3-5 hours)
1. Scribe reviews current docs
2. Organizes docs into proper structure
3. Creates documentation index (`docs/INDEX.md`)
4. Creates getting started guides
5. Enforces documentation standards

---

## ✅ SUCCESS METRICS

**Before:**
- 10 agents with overlapping roles
- No skill system
- No MCP integration
- Scattered documentation
- No documentation owner

**After:**
- 11 focused agents (Atlas + Scribe added, Guido removed)
- 14 defined skills mapped to roles
- 3 MCP servers integrated (Brave, GLM-Vision, MiniMax)
- Organized documentation structure
- Dedicated documentation maintainer

**Benefits:**
- ✅ Clearer role definitions
- ✅ Skills enable faster context loading
- ✅ MCP tools expand capabilities
- ✅ Cleaner documentation
- ✅ Scribe keeps docs organized
- ✅ Atlas handles overflow work

---

## 🎯 NEXT STEPS

1. **Approve this proposal** - User feedback
2. **Phase 1: MCP Integration** - Configure MCP servers
3. **Phase 2: Skill System** - Copy/create skill files
4. **Phase 3: New Agents** - Create Atlas + Scribe
5. **Phase 4: Cleanup** - Remove Guido, update docs
6. **Phase 5: Handoff** - Scribe organizes documentation

---

**Status:** 🟡 AWAITING USER APPROVAL

**Questions:**
- Do you approve the agent structure changes (Guido → Atlas + Scribe)?
- Should we enable MiniMax MCP for media generation?
- Should Scribe start with a full documentation audit?
- Any other MCP servers you want to integrate?

---

*Proposal inspired by ATLAS (clawdbot) skill system + MCP integration*
