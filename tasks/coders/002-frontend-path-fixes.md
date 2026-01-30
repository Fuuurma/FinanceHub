# Task C-002: Fix Frontend Path References

**Assigned To:** Coder(s) - Frontend focus (1 coder recommended)
**Priority:** P0 (CRITICAL)
**Status:** PENDING
**Created:** 2026-01-30
**Deadline:** 2026-01-31 5:00 PM
**Estimated Time:** 4 hours
**Dependencies:** D-003 (Directory reorganization complete)

---

## Overview
Update all frontend code to use new monorepo paths (`apps/frontend/` instead of `Frontend/`).

## Context
After moving `Frontend/` to `apps/frontend/`, all internal path references need updating. This includes TypeScript config, imports, Next.js config, and API endpoints.

**Path Changes:**
- `Frontend/` → `apps/frontend/`
- `Frontend/src/` → `apps/frontend/src/`

## Acceptance Criteria
- [ ] All imports updated
- [ ] TypeScript config paths corrected
- [ ] Next.js config updated
- [ ] No "Module not found" errors
- [ ] Lint passes (no warnings)
- [ ] Typecheck passes (no errors)
- [ ] Build succeeds
- [ ] All tests pass
- [ ] Frontend dev server starts

## Prerequisites
- [ ] D-003 complete (directories moved)
- [ ] Node.js environment ready
- [ ] Dependencies installed (`npm install`)

## Implementation Steps

### Step 1: Find All Path References
```bash
cd /Users/sergi/Desktop/Projects/FinanceHub/apps/frontend

# Search for old paths in TypeScript/JavaScript files
grep -r "Frontend" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" . 2>/dev/null

# Search for old paths in config files
grep -r "Frontend" --include="*.json" --include="*.yml" . 2>/dev/null

# Document all findings
grep -r "Frontend" . > frontend-paths-to-fix.txt 2>/dev/null
```

### Step 2: Update TypeScript Path Aliases
```bash
# Edit tsconfig.json
nano tsconfig.json

# Verify paths are correct:
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@/components/*": ["./src/components/*"],
      "@/lib/*": ["./src/lib/*"],
      "@/app/*": ["./src/app/*"],
      "@/types/*": ["./src/types/*"]
    }
  }
}

# Most imports should work with @ alias
# Relative imports may need adjustment
```

### Step 3: Update Next.js Configuration
```bash
# Edit next.config.js or next.config.ts
nano next.config.js

# Update any transpilation or path configs
# Example:
module.exports = {
  // ...
  transpilePackages: [],  // Remove Frontend references
  webpack: (config) => {
    // Update any Frontend/ paths
    return config;
  }
}
```

### Step 4: Fix Import Statements
```bash
# Find imports referencing old paths
grep -rn "from.*Frontend" src/
grep -rn "import.*Frontend" src/

# Most should use @ alias already
# Fix any absolute imports:
# from Frontend/src/X → from @/X
# or use relative: from ../X

# Example updates:
# - import { Button } from 'Frontend/src/components/ui/button'
# + import { Button } from '@/components/ui/button'
```

### Step 5: Update API Client
```bash
# Check API client configuration
cat src/lib/api/client.ts

# Update backend URL if needed
# Should use environment variable:
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

# If hardcoded, update to use env var
```

### Step 6: Update Docker Configuration
```bash
# Check Dockerfile
cat Dockerfile

# Update WORKDIR if needed
# Example:
# WORKDIR /app  # was /app/Frontend

# Update build context in docker-compose.yml
# (Should be handled by DevOps, but verify)
```

### Step 7: Update Environment Variables
```bash
# Check .env.example
cat .env.example

# Verify API endpoint references:
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Update if any Frontend/ specific paths
```

### Step 8: Test Frontend
```bash
cd /Users/sergi/Desktop/Projects/FinanceHub/apps/frontend

# 1. Lint
npm run lint
# Expected: No warnings (or only known ones)

# 2. Typecheck
npm run typecheck
# Expected: No errors

# 3. Build
npm run build
# Expected: Build succeeds

# 4. Test
npm run test
# Expected: Tests pass

# 5. Start dev server
npm run dev
# Expected: Server starts, no errors
```

### Step 9: Fix Remaining Issues
```bash
# For any remaining issues:
1. Read the error message
2. Find the file with the import
3. Update to use @ alias or relative path
4. Re-test

# Common issues:
# - Module not found: Fix import path
# - Type errors: Fix import or add type
# - Build errors: Fix path in config
```

### Step 10: Commit Changes
```bash
git add .
git status  # Review changes

git commit -m "refactor: update frontend paths for monorepo structure

- Update TypeScript path aliases
- Fix import statements
- Update Next.js configuration
- Fix API client configuration
- All tests passing

Part of monorepo migration."

git push
```

## Testing

### Automated Tests:
```bash
cd apps/frontend

# 1. Lint
npm run lint
# Expected: 0 warnings (or only known ones)

# 2. Typecheck
npm run typecheck
# Expected: 0 errors

# 3. Build
npm run build
# Expected: Build successful

# 4. Tests
npm run test
# Expected: All tests pass

# 5. Dev server
npm run dev
# Expected: Server starts, loads pages
```

### Manual Verification:
```bash
# Test in browser
# http://localhost:3000

# Verify:
# - Homepage loads
# - Navigation works
# - No console errors
# - API calls succeed
# - Pages render correctly
```

## Files Modified
- [ ] `apps/frontend/tsconfig.json` - Path aliases
- [ ] `apps/frontend/next.config.js` - Config updates
- [ ] `apps/frontend/src/lib/api/client.ts` - API URL
- [ ] Various import statements - Path fixes
- [ ] `apps/frontend/.env.example` - Environment vars

## Code Quality Checklist
- [ ] Lint passes (0 warnings)
- [ ] Typecheck passes (0 errors)
- [ ] Build succeeds
- [ ] All tests pass
- [ ] Dev server starts
- [ ] No "Module not found" errors
- [ ] Pages load correctly
- [ ] API calls work

## Rollback Plan
```bash
# If changes break everything:
git reset --hard HEAD
git checkout [previous-commit]

# Start over with careful review
```

## Tools to Use
- **MCP:** File operations, grep for searching, bash commands
- **Skills:** web search (for Next.js docs), github (for examples)
- **Reference:** Next.js documentation, TypeScript handbook

## Dependencies
- ✅ D-003 (Directory reorganization)

## Feedback to Architect
[After completing, report using this format]

### What I Did:
- Updated TypeScript path aliases
- Fixed import statements ([N] files)
- Updated Next.js configuration
- Fixed API client configuration
- Tested all changes

### Testing:
- ✅ Lint: PASSED (0 warnings)
- ✅ Typecheck: PASSED (0 errors)
- ✅ Build: PASSED
- ✅ Tests: PASSED ([N] passing)
- ✅ Dev server: STARTED

### What I Discovered:
- [N] files needed path updates
- No unexpected issues
- All imports resolved correctly

### Files Modified:
- `tsconfig.json` - Updated paths
- `next.config.js` - Updated config
- [List all modified files]

### Ready for Next Step:
Frontend paths fixed. Ready for Task C-003 (Integration testing).

## Updates
- **2026-01-30 09:00:** Task created, status PENDING
- **[YYYY-MM-DD HH:MM]:** [Update when start working]
- **[YYYY-MM-DD HH:MM]:** [Update when complete]

---
**Last Updated:** 2026-01-30
**Next Task:** C-003 (Integration Testing) - All coders participate
