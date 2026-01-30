# 🎨 ARCHITECT ASSISTANT ROLE

**Version:** 1.0  
**Created:** January 30, 2026  
**Owner:** GAUDÍ (Architect)  
**Status:** ACTIVE

---

## 📋 OVERVIEW

The **Architect Assistant** is a specialized subagent that the Architect (GAUDÍ) can spawn to help with parallel work, task creation, and coordination.

**Purpose:** Multiply Architect's productivity by delegating specialized work

**When to Use:**
- Creating multiple similar tasks in parallel
- Analyzing large codebases quickly
- Reviewing agent reports
- Generating documentation
- Coordinating multiple agents
- Any work that can be split into independent chunks

**When NOT to Use:**
- Making architectural decisions (ONLY Architect can do this)
- Approving critical changes (ONLY Architect can do this)
- Tasks requiring full system context
- Simple tasks you can do yourself faster

---

## 🚀 HOW TO SPAWN ASSISTANT

### **Using the Task Tool:**

```python
task(
    subagent_type="general",
    description="Brief description of what to do",
    prompt="Full detailed instructions...",
    session_id="optional_session_id_for_continuation"
)
```

### **Example Spawns:**

```python
# Create multiple tasks from features spec
task(
    subagent_type="general",
    description="Create 5 tasks from features",
    prompt="Read docs/architecture/FEATURES_SPECIFICATION.md and create 5 new tasks...",
    session_id="ses_task_creation_001"
)

# Analyze agent reports
task(
    subagent_type="explore",
    description="Review all security findings",
    prompt="Search for all security-related files and summarize findings...",
    session_id="ses_security_review_001"
)

# Check git status and commits
task(
    subagent_type="general",
    description="Audit git activity",
    prompt="Check recent commits, verify agents are pushing, report blockers...",
    session_id="ses_git_audit_001"
)
```

---

## 🎯 ASSISTANT CAPABILITIES

### **Can Do (✅):**
- Create task files from templates
- Generate documentation
- Search and analyze code
- Review agent reports
- Summarize findings
- Create recommendations
- Format and organize files
- Check git status
- Test code patterns
- Research best practices

### **Cannot Do (❌):**
- Make architectural decisions
- Approve pull requests
- Assign final priorities
- Negotiate with stakeholders
- Override Architect's authority
- Access credentials/secrets
- Deploy to production
- Merge branches to main

---

## 📊 AVAILABLE ASSISTANT TYPES

### **1. General Assistant** (`subagent_type="general"`)
**Best For:**
- Creating tasks
- Writing documentation
- Analysis and research
- Multi-step workflows

**Capabilities:**
- Read files
- Write files
- Execute bash commands
- Search code
- Generate reports

**Use When:**
- Task creation from specs
- Documentation generation
- Feature analysis
- Code reviews

---

### **2. Explore Assistant** (`subagent_type="explore"`)
**Best For:**
- Quick codebase searches
- Finding specific patterns
- Understanding architecture
- Locating files

**Capabilities:**
- Fast glob searches
- Regex content searches
- File pattern matching
- Quick answers about codebase

**Use When:**
- "Where is X implemented?"
- "Find all Y patterns"
- "How does Z work?"
- Quick exploration tasks

---

## 🔄 SESSION MANAGEMENT

### **Starting a Session:**
```python
task(
    subagent_type="general",
    description="Create tasks",
    prompt="...",
    session_id="ses_unique_id"  # Creates new session
)
```

### **Continuing a Session:**
```python
task(
    subagent_type="general",
    description="Continue work",
    prompt="Add 5 more tasks to the previous work...",
    session_id="ses_unique_id"  # Reuses previous context
)
```

### **Session Lifecycle:**
1. **New Session:** Fresh context, no memory
2. **Continue Session:** Remembers previous work in that session
3. **End Session:** Context discarded (but files remain)

**Best Practices:**
- Use descriptive session IDs: `ses_task_creation_001`, `ses_security_review_20260130`
- Continue sessions for related work
- Start new sessions for different work types
- Session IDs are optional but recommended for complex work

---

## 📋 PROMPT ENGINEERING

### **Good Prompt Structure:**

```python
prompt="""
You are my [ROLE]. I need you to [TASK].

**Context:**
- Project: [NAME]
- Location: [PATH]
- Dependencies: [LIST]

**Your Assignment:**

1. **READ** [FILE]
2. **ANALYZE** [WHAT]
3. **CREATE** [OUTPUT]
4. **VERIFY** [HOW]

**Requirements:**
- [SPECIFIC REQUIREMENT 1]
- [SPECIFIC REQUIREMENT 2]

**Return to me:**
1. [EXPECTED OUTPUT 1]
2. [EXPECTED OUTPUT 2]

**GO.**
"""
```

### **Prompt Tips:**
- **Be Specific:** Don't say "analyze code", say "check for SQL injection vulnerabilities"
- **Give Context:** Project location, existing files, dependencies
- **Define Output:** Exactly what you want back
- **Set Constraints:** Time limits, file size limits, scope boundaries
- **Provide Examples:** Show what "good" looks like

---

## 🎨 REAL-WORLD EXAMPLES

### **Example 1: Creating Multiple Tasks**

**Architect spawns:**
```python
task(
    subagent_type="general",
    description="Create 5 feature tasks",
    prompt="""
You are my assistant architect. I need you to CREATE 5 TASKS from features spec.

**Context:**
- Project: FinanceHub
- Features: docs/architecture/FEATURES_SPECIFICATION.md (351 lines)
- Already created: C-006 through C-016

**Assignment:**
1. READ features spec
2. IDENTIFY 5 high-value features NOT yet assigned
3. CREATE 5 tasks in tasks/coders/ (C-020 through C-024)
4. Each task needs: priority, time estimate, implementation plan, deliverables

**Prioritize:**
- High user value
- Builds on existing work
- 8-16 hour tasks
- NOT duplicates

**Return:**
1. List of 5 features chosen
2. Why you chose each
3. Confirmation files created

**GO.**
""",
    session_id="ses_feature_tasks_001"
)
```

**Assistant returns:**
- 5 task files created
- Summary of features
- Rationale for choices

---

### **Example 2: Reviewing Security**

**Architect spawns:**
```python
task(
    subagent_type="general",
    description="Review security reports",
    prompt="""
Review all security reports and create summary.

**Files to check:**
- docs/security/CRITICAL_SECURITY_STATUS.md
- tasks/security/001-migration-validation.md
- tasks/security/002-docker-security-scans.md
- docs/security/SECURITY_VULNERABILITIES_REMEDIATION.md

**Return:**
1. Total vulnerabilities found
2. Breakdown by severity
3. What's been fixed
4. What's pending
5. Immediate actions needed

**Create:** docs/security/SECURITY_SUMMARY_20260130.md

**GO.**
""",
    session_id="ses_security_review_001"
)
```

---

### **Example 3: Checking Agent Activity**

**Architect spawns:**
```python
task(
    subagent_type="general",
    description="Audit agent git activity",
    prompt="""
Check if agents are pushing their work.

**Check:**
1. git log --oneline -20 (recent commits)
2. git status (uncommitted work)
3. Compare to TASK_TRACKER.md (what should be done)

**Report:**
1. Which agents are committing?
2. Which agents are NOT committing?
3. Uncommitted work by role
4. Commits not pushed to origin
5. Recommendations for fixing

**GO.**
""",
    session_id="ses_git_audit_001"
)
```

---

## ⚡ PERFORMANCE TIPS

### **Speed Up Work:**
1. **Parallel Spawns:** Create 2-3 assistants at once for different tasks
2. **Clear Prompts:** Reduces back-and-forth
3. **Specific Scope:** Smaller tasks = faster completion
4. **Session Continuation:** Reuse context for related work

### **Avoid Bottlenecks:**
1. **Don't Micromanage:** Trust the assistant, review output
2. **Set Time Limits:** "Complete in 10 minutes" focuses work
3. **File Limits:** "Check only tasks/coders/*.md" not entire repo
4. **Scope Boundaries:** "Only C-020 through C-025" not all tasks

---

## 🔍 QUALITY CONTROL

### **Reviewing Assistant Work:**

**Checklist:**
- [ ] Files created in correct locations?
- [ ] File names follow conventions?
- [ ] Content matches requirements?
- [ ] No duplications?
- [ ] Links and references correct?
- [ ] Code examples valid?
- [ ] Time estimates reasonable?
- [ ] Dependencies accurate?

**If Issues Found:**
1. **Minor Issues:** Edit files yourself
2. **Major Issues:** Spawn new session with feedback
3. **Systematic Issues:** Update this doc with better prompts

---

## 📊 METRICS TO TRACK

### **Assistant Performance:**
- **Tasks Created:** Count of tasks created per session
- **Time Spent:** Actual vs. estimated time
- **Quality Issues:** Number of edits needed
- **Reuse:** Sessions continued vs. new sessions

### **When to Use Assistant:**
- **Task Creation:** 5+ tasks at once → YES
- **Single Task:** 1 task → NO (do it yourself)
- **Code Review:** 10+ files → YES
- **Documentation:** 20+ pages → YES
- **Quick Question:** 1 answer → NO (use grep/read)

---

## 🚨 COMMON PITFALLS

### **❌ Don't:**
- Spawn assistant for 5-minute tasks
- Use vague prompts like "analyze everything"
- Forget to set file boundaries
- Skip review of assistant work
- Create too many sessions (hard to track)
- Use for architectural decisions

### **✅ Do:**
- Spawn for parallel work (5+ similar items)
- Use specific prompts with clear outputs
- Set file/location boundaries
- Always review assistant output
- Continue sessions for related work
- Use for analysis, creation, documentation

---

## 🎓 BEST PRACTICES

### **1. Prompt Engineering**
```
BAD: "Create some tasks from features"
GOOD: "Create 5 tasks (C-020 through C-024) from docs/architecture/FEATURES_SPECIFICATION.md, each with priority, time estimate, and implementation plan"
```

### **2. Session Management**
```
BAD: ses_1, ses_2, ses_3 (hard to track)
GOOD: ses_task_creation_001, sec_security_review_001, ses_git_audit_001 (descriptive)
```

### **3. File Boundaries**
```
BAD: "Check all files in repo"
GOOD: "Check only tasks/coders/C-020.md through C-025.md"
```

### **4. Quality Control**
```
BAD: Accept assistant work without review
GOOD: Review files, fix issues, provide feedback
```

---

## 🔧 TROUBLESHOOTING

### **Assistant Returns Too Little:**
- **Cause:** Prompt too vague
- **Fix:** Be more specific about expected output
- **Example:** "Create task" → "Create task with sections: Overview, Implementation, Deliverables, Acceptance Criteria"

### **Assistant Returns Too Much:**
- **Cause:** Scope too broad
- **Fix:** Set file/location boundaries
- **Example:** "Analyze backend" → "Analyze only apps/backend/src/api/"

### **Assistant Makes Mistakes:**
- **Cause:** Instructions unclear
- **Fix:** Provide examples of expected output
- **Example:** Show a sample task file

### **Assistant Takes Too Long:**
- **Cause:** Task too large
- **Fix:** Split into smaller sessions
- **Example:** "Create 20 tasks" → "Create 5 tasks (C-020 to C-024)"

---

## 📚 REFERENCE MATERIALS

### **Related Documents:**
- `docs/agents/AGENTS.md` - Main agent definitions
- `docs/agents/AI_AGENT_COMMUNICATION.md` - Communication protocols
- `tasks/ROLE_ARCHITECT.md` - Architect role definition
- `tasks/ROLE_CODERS.md` - Coder role definition

### **Tool Documentation:**
- Task tool: Spawn assistants for parallel work
- Explore tool: Fast codebase searches
- General tool: Multi-step workflows

---

## ✅ CHECKLIST FOR USING ASSISTANT

Before spawning:
- [ ] Task is too large for me to do quickly?
- [ ] Work can be split into independent chunks?
- [ ] I can clearly specify expected output?
- [ ] I have time to review the results?

After spawning:
- [ ] Received expected output?
- [ ] Files created in correct locations?
- [ ] Content meets quality standards?
- [ ] No duplications or conflicts?

Before continuing session:
- [ ] Related to previous work?
- [ ] Same context needed?
- [ ] Session ID available?

---

## 🎯 SUMMARY

**The Architect Assistant is a FORCE MULTIPLIER.**

**Use it to:**
- Create 5+ tasks at once
- Analyze large codebases
- Generate documentation
- Review agent reports
- Coordinate parallel work

**Don't use it for:**
- Architectural decisions
- Single simple tasks
- Approvals
- Credentials access

**Key to success:**
1. Specific prompts with clear outputs
2. File and location boundaries
3. Always review output
4. Continue sessions for related work
5. Track with descriptive session IDs

**When in doubt: SPAWN IT.**

**If you can do it in 5 minutes: DO IT YOURSELF.**

---

**Created by:** GAUDÍ (Architect)  
**Last Updated:** January 30, 2026  
**Version:** 1.0  
**Status:** ACTIVE
