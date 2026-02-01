## SUPPORT REQUEST: Docker Environment Fix Needed

**From:** HADI (Accessibility Specialist)
**To:** Karen (DevOps Engineer)
**Date:** February 1, 2026
**Priority:** HIGH
**CC:** ARIA, GAUDÍ

---

### Issue Summary:
Docker frontend build failing, blocking automated accessibility testing.

### Error Details:
```bash
$ npm run build
# Result: "next: not found"

$ docker-compose build frontend
# Error: apps/frontend/package.json missing dependencies
```

### Impact:
- Cannot run axe-core automated accessibility tests
- Cannot run Lighthouse accessibility audits
- WCAG 2.1 Level AA audit delayed
- HADI compliance score stuck at 85% (needs automated testing to reach 100%)

### Files Affected:
- `apps/frontend/package.json` - Missing dependencies
- `Dockerfile.frontend` - May need updates

### Request:
Please fix the Docker frontend build configuration so HADI can:
1. Run `npm run build` successfully
2. Execute axe-core automated tests
3. Complete WCAG compliance verification

### Timeline Impact:
- Automated testing: BLOCKED until fixed
- Manual audit: 85% complete
- Final compliance: Pending automated verification

### Related Work:
- HADI has already fixed 9 aria-label issues (code review complete)
- 277+ components audited manually
- Only automated testing needs Docker fix

---

**Please help unblock accessibility testing. Thanks!**

- HADI ♿
