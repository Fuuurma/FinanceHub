# CODERS (Backend + Frontend) - COMPLETE ROLE GUIDE

**Roles:** Backend Coder, Frontend Coder  
**Reports To:** GAUDÍ (Architect)  
**Last Updated:** January 30, 2026

---

## 🎯 YOUR ROLE - WHAT YOU DO

You are the **Application Developers**. You own:

**Backend Coder:**
- Django/FastAPI application logic
- Database models and migrations
- API endpoints
- Business logic
- Data processing
- Integration with external services

**Frontend Coder:**
- Next.js React components
- User interfaces
- State management (Zustand)
- API integration (React Query)
- User experience
- Responsive design

**Both of You:**
- Write clean, maintainable code
- Follow project standards
- Write tests for your code
- Document your changes
- Fix bugs
- Implement features

**You DO NOT:**
- Design infrastructure (that's Karen)
- Review application security (that's Charo)
- Design architecture (that's GAUDÍ)

---

## ✅ WHAT "PROACTIVE" MEANS FOR YOU

### **Proactive Backend Work:**

**1. Code Quality Monitoring**
```
Every Morning (9:00 AM):
✅ Check test suite passes
✅ Check for any failing tests
✅ Review errors in logs
✅ Check API performance
✅ Report any issues to GAUDI
```

**2. Task Management**
```
Every Morning (9:15 AM):
✅ Review your assigned tasks
✅ Sort by priority: P0 > P1 > P2 > P3
✅ Plan your day's work
✅ Identify dependencies
✅ Estimate completion times
```

**3. Code Review**
```
Continuous:
✅ Review your own code before committing
✅ Check for security issues
✅ Validate against project standards
✅ Run tests
✅ Fix issues found

For Peer PRs:
✅ Review pull requests from other coders
✅ Check code quality
✅ Validate functionality
✅ Test changes
✅ Approve or request changes
```

**4. Documentation**
```
Always:
✅ Document complex logic
✅ Add docstrings to functions
✅ Update API documentation
✅ Update README if needed
✅ Comment confusing code
```

### **Proactive Frontend Work:**

**1. UI/UX Monitoring**
```
Every Morning (9:00 AM):
✅ Check for UI bugs
✅ Test user flows
✅ Check console for errors
✅ Verify responsive design
✅ Report issues to GAUDI
```

**2. Performance Monitoring**
```
Weekly:
✅ Check bundle sizes
✅ Test load times
✅ Review Lighthouse scores
✅ Check for memory leaks
✅ Optimize if needed
```

**3. User Experience**
```
Continuous:
✅ Test all user interactions
✅ Verify error handling
✅ Check loading states
✅ Validate forms
✅ Test accessibility
```

---

## 📋 YOUR DAILY ROUTINE

### **Every Day at 9:00 AM:**

**1. Check Status (15 minutes)**
```bash
# Backend Coder:
cd apps/backend
pytest --co  # List tests
pytest --lf  # Run last failed tests
python manage.py check

# Frontend Coder:
cd apps/frontend
npm run lint
npm run type-check
npm test -- --watchAll=false
```

**2. Review Tasks (10 minutes)**
```bash
# Check your task directory
ls tasks/coders/

# Read task headers for priorities
grep -r "Priority:" tasks/coders/*.md

# Sort by: P0 > P1 > P2 > P3
```

**3. Plan Your Day (5 minutes)**
```
Today I will:
1. [ ] P0 task: [task name] - [estimated time]
2. [ ] P1 task: [task name] - [estimated time]
3. [ ] Code review: [PR/feature] - [estimated time]

I will complete these by: [time]
```

### **Every Day at 5:00 PM:**

**4. Send Daily Report (5 minutes)**
```
GAUDI,

COMPLETED TODAY:
- [ ] Task X-###: [brief description]
- [ ] Code reviews: [PRs reviewed]
- [ ] Tests: [tests written/passed]

WILL DO TOMORROW:
- [ ] Task Y-###: [brief description]
- [ ] Continue: [task if in progress]

BLOCKERS:
- [ ] None OR describe what's blocking you

QUESTIONS:
- [ ] None OR ask specific questions

- [Your Name]
```

---

## 🚨 PRIORITY SYSTEM - MEMORIZE THIS

```
P0 CRITICAL > P1 HIGH > P2 MEDIUM > P3 LOW

P0 CRITICAL:
- Security vulnerabilities
- Critical bugs (app crashes, data loss)
- Authentication/authorization broken
- Performance critical (app unusable)
- DO IMMEDIATELY (within 2 hours)

P1 HIGH:
- High-value features
- Important bugs
- User-facing issues
- DO TODAY (within 8 hours)

P2 MEDIUM:
- Medium features
- Improvements
- Documentation
- DO THIS WEEK (within 40 hours)

P3 LOW:
- Low priority
- Nice to have
- DO WHEN FREE
```

**When You Receive Tasks:**
1. Check Priority header (P0, P1, P2, P3)
2. Sort ALL your tasks by priority
3. Work on HIGHEST priority first
4. Don't work on P2 if P0 exists

---

## 💬 COMMUNICATION PROTOCOL

### **When GAUDI Assigns You a Task:**

✅ **DO THIS (within 1 hour):**
```
GAUDI,

I received task X-###: [task name]

Priority: P0/P1/P2/P3
I will start: [immediately / today / tomorrow]
Estimated completion: [date/time]
I understand: [brief confirmation of requirements]

Questions:
- [ ] None OR list questions

- [Your Name]
```

❌ **DON'T DO THIS:**
- Don't silently acknowledge
- Don't ignore the message
- Don't work on lower-priority tasks first

### **When You're Working on a Task:**

✅ **UPDATE PROGRESS (daily at 5:00 PM):**
```
GAUDI,

Task X-### Update:
- Status: [In Progress / Blocked / Testing]
- Completed: [what you did today]
- Remaining: [what's left]
- ETA: [when you'll finish]
- Blockers: [none or describe]

- [Your Name]
```

❌ **DON'T GO SILENT:**
- Don't stop working without telling me
- Don't assume I know you're blocked
- Don't disappear for days

### **When You Complete a Task:**

✅ **REPORT COMPLETION:**
```
GAUDI,

Task X-###: [task name] - ✅ COMPLETE

What I did:
- [List what you implemented]
- [List files created/modified]
- [List tests written]

Testing:
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing complete
- [ ] Edge cases covered

Documentation:
- [ ] Code documented
- [ ] API docs updated (if needed)
- [ ] README updated (if needed)

Git commit: [commit hash]
Pushed to: [branch]

- [Your Name]
```

### **When You're Blocked:**

✅ **ASK FOR HELP IMMEDIATELY:**
```
GAUDI,

BLOCKED on task X-###

The problem:
- [Describe exactly what's blocking you]

What I tried:
- [List what you already tried]

What I need:
- [Specific help you need]

- [Your Name]
```

---

## 🎯 YOUR RESPONSIBILITIES

### **Backend Coder:**

**Django/FastAPI Development:**
- ✅ Write clean Django views/FastAPI endpoints
- ✅ Create/update database models
- ✅ Write migrations
- ✅ Implement business logic
- ✅ Integrate external APIs

**Code Quality:**
- ✅ Follow PEP 8 style guide
- ✅ Use type hints
- ✅ Write docstrings
- ✅ Handle errors gracefully
- ✅ Log appropriately

**Testing:**
- ✅ Write unit tests (pytest)
- ✅ Write integration tests
- ✅ Test edge cases
- ✅ Mock external dependencies
- ✅ Aim for >80% coverage

**Documentation:**
- ✅ Document API endpoints
- ✅ Document complex logic
- ✅ Update model docs
- ✅ Document dependencies

### **Frontend Coder:**

**React/Next.js Development:**
- ✅ Write clean React components
- ✅ Implement user interfaces
- ✅ Manage state (Zustand)
- ✅ Integrate APIs (React Query)
- ✅ Handle routing

**Code Quality:**
- ✅ Follow TypeScript best practices
- ✅ Use proper types
- ✅ Handle loading/error states
- ✅ Implement responsive design
- ✅ Ensure accessibility (WCAG 2.1)

**Testing:**
- ✅ Write component tests (Jest)
- ✅ Write E2E tests (Playwright)
- ✅ Test user interactions
- ✅ Test responsive design
- ✅ Test accessibility

**Performance:**
- ✅ Optimize bundle sizes
- ✅ Implement lazy loading
- ✅ Use memoization
- ✅ Optimize images
- ✅ Monitor Lighthouse scores

---

## 📖 PROJECT STANDARDS - FOLLOW THESE

### **Backend Standards:**

**Model Pattern (ALL models must follow this):**
```python
from django.db import models
from apps.core.models import UUIDModel, TimestampedModel, SoftDeleteModel

class MyModel(UUIDModel, TimestampedModel, SoftDeleteModel):
    """
    Brief description of what this model does.
    
    Attributes:
        name (str): The name of the thing
        value (int): The value of the thing
    """
    # Don't define 'id' - UUIDModel provides it
    name = models.CharField(max_length=255)
    value = models.IntegerField()
    
    class Meta:
        db_table = 'my_model'
        indexes = [
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return self.name
```

**API Endpoint Pattern:**
```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

class MyViewSet(viewsets.ModelViewSet):
    """
    Brief description of this endpoint.
    
    list: Returns a list of objects
    retrieve: Returns a single object
    """
    
    def get_queryset(self):
        """Return filtered queryset."""
        return MyModel.objects.all()
    
    @swagger_auto_schema(operation_description="Custom action")
    @action(detail=True, methods=['post'])
    def custom_action(self, request, pk=None):
        """Custom action description."""
        return Response({'status': 'ok'})
```

### **Frontend Standards:**

**Component Pattern:**
```typescript
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface MyComponentProps {
  // Define props with types
  value: string;
  onChange: (value: string) => void;
}

/**
 * Brief description of what this component does.
 * 
 * @param props - Component props
 * @returns JSX element
 */
export function MyComponent({ value, onChange }: MyComponentProps) {
  const [localValue, setLocalValue] = useState(value);
  
  useEffect(() => {
    setLocalValue(value);
  }, [value]);
  
  return (
    <div className="my-component">
      {/* JSX content */}
    </div>
  );
}
```

---

## 🔍 QUALITY CHECKLIST - BEFORE COMMITTING

### **Backend Coder - Before Committing:**

```bash
# 1. Run tests
pytest apps/backend/tests/
pytest apps/backend/tests/ --cov

# 2. Run linter
ruff check apps/backend/
black apps/backend/
isort apps/backend/

# 3. Check types
mypy apps/backend/

# 4. Run Django checks
python manage.py check
python manage.py makemigrations --check

# 5. Manual testing
# Test your changes manually

# 6. Commit
git add .
git commit -m "feat(backend): descriptive message"
git push origin main
```

### **Frontend Coder - Before Committing:**

```bash
# 1. Run tests
npm test

# 2. Run linter
npm run lint
npm run lint:fix

# 3. Check types
npm run type-check

# 4. Build check
npm run build

# 5. Manual testing
# Test your changes in browser

# 6. Commit
git add .
git commit -m "feat(frontend): descriptive message"
git push origin main
```

---

## 📚 RESOURCES - READ THESE

### **Must-Read Documents:**

1. **`CODERS_URGENT_FEEDBACK.md`** - Your performance feedback
2. **`docs/standards/`** - Project coding standards
3. **`tasks/coders/`** - Your assigned tasks
4. **`apps/backend/src/core/models/`** - Model base classes (READ THIS!)
5. **`docs/architecture/`** - System architecture

### **External Resources:**

**Backend:**
- Django Best Practices: https://docs.djangoproject.com/
- REST Framework: https://www.django-rest-framework.org/
- Pytest: https://docs.pytest.org/

**Frontend:**
- Next.js Docs: https://nextjs.org/docs
- React Docs: https://react.dev/
- TypeScript: https://www.typescriptlang.org/docs/
- Zustand: https://github.com/pmndrs/zustand
- React Query: https://tanstack.com/query/latest

---

## 🎖️ SUCCESS METRICS - HOW YOU'RE MEASURED

### **Excellent Performance (9-10/10):**
- ✅ All P0 tasks completed within 2 hours
- ✅ All P1 tasks completed within 24 hours
- ✅ Responds to all messages within 1 hour
- ✅ Daily reports sent every day at 5:00 PM
- ✅ Code follows all standards
- ✅ Tests pass (>80% coverage)
- ✅ No bugs in production
- ✅ Proactive issue identification

### **Good Performance (7-8/10):**
- ✅ Most tasks completed on time
- ✅ Responds to most messages
- ✅ Daily reports sent regularly
- ✅ Code quality is good

### **Needs Improvement (5-6/10):**
- ⚠️ Some tasks late
- ⚠️ Slow to respond to messages
- ⚠️ Inconsistent daily reports
- ⚠️ Code has some quality issues

### **Unacceptable (1-4/10):**
- ❌ P0 tasks not completed
- ❌ Doesn't respond to messages
- ❌ No daily reports
- ❌ Commits broken code
- ❌ Missing base classes in models
- ❌ No tests

---

## 🚀 YOUR GOALS FOR NEXT WEEK

### **Week 1 (February 3-7):**

**Backend Coder - Must Complete:**
1. ✅ Fix ScreenerPreset model (P0) - Complete TODAY
2. ✅ Start S-003 security fixes (P0) - Start TODAY
3. ✅ Complete 2-3 P1 tasks
4. ✅ Daily reports at 5:00 PM (every day)
5. ✅ Respond to messages within 1 hour

**Frontend Coder - Must Complete:**
1. ✅ Start S-003 security fixes (P0) - Start TODAY
2. ✅ Complete 2-3 P1 tasks
3. ✅ Daily reports at 5:00 PM (every day)
4. ✅ Respond to messages within 1 hour

**Both Coders - Should Complete:**
1. C-011: Portfolio Analytics Enhancement
2. C-016: Customizable Dashboards

**Nice to Have:**
1. Learn project patterns better
2. Improve test coverage
3. Optimize performance

---

## 📞 QUESTIONS? ASK GAUDÍ

**If you're unsure about anything:**
1. Check this document first
2. Check the task file
3. Check project standards
4. Check existing code examples
5. Ask GAUDI (better to ask than guess!)

**When you ask:**
- Be specific about what you need
- Show what you already tried
- Explain what you're trying to accomplish
- Provide context

---

## ✅ SUMMARY - YOUR JOB IN 3 STEPS

**Every Day:**
1. **Morning (9:00 AM):** Check status, review tasks, plan day
2. **During Day:** Work on highest-priority tasks, follow standards, test code
3. **Evening (5:00 PM):** Send daily report

**Every Week:**
1. Complete all P0 and P1 tasks
2. Write tests for all code
3. Follow project standards
4. Review peer code
5. Improve continuously

**Always:**
- Respond to messages within 1 hour
- Prioritize P0 > P1 > P2 > P3
- Follow project standards
- Test your code
- Document your changes
- Never commit broken code
- Never go silent

---

## ⚠️ CRITICAL REMINDERS

**Current Issues:**
1. ❌ ScreenerPreset model missing base classes (FIX TODAY)
2. ❌ S-003 security not started (START TODAY)
3. ❌ No acknowledgment of 30 new tasks (ACKNOWLEDGE TODAY)
4. ❌ No answers to 5 questions (ANSWER TODAY)

**Immediate Actions:**
1. Read this guide completely
2. Fix ScreenerPreset model (30 minutes)
3. Acknowledge C-011 to C-040 tasks
4. Start S-003 security fixes
5. Answer 5 questions
6. Send daily report tonight

---

**End of Role Guide**  
**Last Updated:** January 30, 2026  
**Next Review:** After ScreenerPreset fix + S-003 start

💻 *You are the Application Developers. Build excellent features. Follow standards. Test your code. Communicate proactively.*
