# ⚡ QUICK WINS - Memory Optimization (Do These Now!)

**Date:** February 1, 2026
**Time Required:** 5 minutes
**Memory Saved:** 2-3 GB (60-75% reduction)

---

## 🚨 Action 1: Reduce Instances (2 minutes)

**Current:** 6-7 instances running simultaneously
**Recommended:** 2-3 instances maximum

### Step-by-Step:

1. **Assess your active agents:**
   ```bash
   # Check which instances are running
   ps aux | grep -i "code" | grep -v grep
   ```

2. **Keep only these agents active:**
   - **Morning:** Linus (Backend) + Turing (Frontend) = 2 instances
   - **Afternoon:** Karen (DevOps) + Charo (Security) = 2 instances
   - **Evening:** GRACE (QA) = 1 instance

3. **Close unused instances:**
   - Save work
   - Close VSCode windows
   - Keep only 2-3 agents active

**Impact:** 1.5-2.5 GB saved (50-60% reduction)

---

## 🚨 Action 2: Disable MCP Servers (1 minute)

**Current:** `glm-vision` MCP enabled for all instances
**Issue:** Each instance spawns separate Node.js process (50-100 MB)

### Step-by-Step:

1. **Edit MCP configuration:**
   ```bash
   code ~/.opencode.jsonc
   ```

2. **Disable glm-vision:**
   ```jsonc
   {
     "mcp": {
       "brave-search": {
         "type": "remote",
         "url": "https://search.brave.com/api",
         "enabled": true  // Keep this
       },
       "glm-vision": {
         "type": "local",
         "command": ["npx", "-y", "@z_ai/mcp-server"],
         "enabled": false  // CHANGE: true → false
       }
     }
   }
   ```

3. **Save and restart opencode**

**Impact:** 300-700 MB saved (6-7 instances × 50-100 MB)

---

## 🚨 Action 3: Use Lightweight Workflow (2 minutes)

**Current:** All agents load full prompts + documentation
**Recommended:** Task-specific rotation

### Step-by-Step:

1. **Phase-based workflow:**
   ```
   Phase 1 (Feature Development):
   - Linus (Backend) - Implement API
   - Turing (Frontend) - Implement UI
   - Close other agents

   Phase 2 (Security & DevOps):
   - Charo (Security) - Audit code
   - Karen (DevOps) - Deploy changes
   - Close Phase 1 agents

   Phase 3 (QA):
   - GRACE (QA) - Test deployment
   - Close Phase 2 agents
   ```

2. **Coordinate in COMMUNICATION_HUB.md:**
   - Add "Active Phases" section
   - Note which agents to use when

**Impact:** Better focus, less memory, smoother coordination

---

## 📊 Before vs After

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Active Instances** | 6-7 | 2-3 | 60% reduction |
| **MCP Processes** | 6-7 | 0-1 | 85% reduction |
| **Memory Usage** | 3-4 GB | 0.75-1 GB | 75% reduction |
| **VSCode Windows** | 6-7 | 2-3 | 60% reduction |
| **Agent Coordination** | Chaotic | Phased | ✅ Improved |

---

## ✅ Verification

After implementing quick wins:

```bash
# Check memory usage
ps aux | grep -i "code" | awk '{sum+=$6} END {print "VSCode:", sum/1024, "MB"}'

ps aux | grep -i "mcp\|node.*z_ai" | awk '{sum+=$6} END {print "MCP:", sum/1024, "MB"}'

# Total should be under 1 GB now
```

---

## 🎯 Expected Results

✅ **Mac mini no longer runs out of memory**
✅ **VSCode remains responsive**
✅ **Faster agent context switching**
✅ **Better workflow coordination**
✅ **No computer restarts needed**

---

## 📋 Next Steps (Optional - This Week)

If you want to optimize further:

1. **Create lightweight prompts** (30 minutes)
   - See `docs/agents/QUICK_START/` examples
   - Reduce prompt size from 40 KB to 10-15 KB

2. **Implement skills caching** (1 hour)
   - Combine frequently used skills
   - Reduce repeated loading

3. **Task-specific documentation** (2 hours)
   - Extract relevant sections only
   - Avoid loading 40 KB guides

**Total additional savings:** 500-1000 MB

---

## 🚨 IMPORTANT NOTES

**When do you need all agents active?**
- **RARELY.** Most work is sequential (design → backend → frontend → test)
- **PARALLEL EXCEPTION:** When Linus + Turing work on same feature simultaneously

**When to disable MCP:**
- **MOST TASKS** don't need image processing
- **ENABLE ONLY:** When analyzing UI mockups, diagrams, or design files

**When to use 3 instances:**
- Backend + Frontend + QA (full feature pipeline)
- Any other time, 2 instances suffice

---

**Memory crisis solved!** 🎉

**Questions?** Check COMMUNICATION_HUB.md for workflow coordination
