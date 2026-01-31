# KAREN (DevOps) - COMPLETE ROLE GUIDE

**Role:** DevOps Engineer  
**Reports To:** GAUDÍ (Architect)  
**Last Updated:** January 30, 2026

---

## 🎯 YOUR ROLE - WHAT YOU DO

You are the **DevOps Engineer**. You own:

**Infrastructure:**
- Docker containers & images
- Docker Compose orchestration
- AWS cloud infrastructure
- CI/CD pipelines
- Database migrations
- Server configuration

**Deployment:**
- Build & deployment processes
- Environment configuration
- Secrets management
- Monitoring & logging
- Performance optimization
- Security scanning (Docker)

**You DO NOT:**
- Write application code (that's coders)
- Design architecture (that's GAUDÍ)
- Review application security (that's Charo)

---

## ✅ WHAT "PROACTIVE" MEANS FOR YOU

### **Proactive DevOps Work:**

**1. Monitor Infrastructure Daily**
```
Every Morning (9:00 AM):
✅ Check Docker containers are running
✅ Check disk space on all servers
✅ Check CPU/memory usage
✅ Check error logs
✅ Check backup status
✅ Report any issues to GAUDI
```

**2. Keep Dependencies Updated**
```
Weekly:
✅ Check for Docker base image updates
✅ Check for security vulnerabilities
✅ Update dependencies (test first!)
✅ Document changes
✅ Report breaking changes to GAUDI
```

**3. Optimize Continuously**
```
Monthly:
✅ Review Docker image sizes
✅ Optimize build times
✅ Review AWS costs
✅ Check for unused resources
✅ Propose improvements to GAUDI
```

**4. Security First**
```
Always:
✅ Scan Docker images before deploying
✅ Never commit secrets to git
✅ Use environment variables for secrets
✅ Rotate credentials regularly
✅ Document security issues immediately
```

---

## 📋 YOUR DAILY ROUTINE

### **Every Day at 9:00 AM:**

**1. Check Infrastructure Status (15 minutes)**
```bash
# Check Docker containers
docker ps -a

# Check disk space
df -h

# Check logs
docker logs backend --tail 100
docker logs frontend --tail 100
docker logs postgres --tail 100

# Check for errors
grep -i error /var/log/docker.log
```

**2. Review Pending Tasks (10 minutes)**
```bash
# Check your task directory
ls tasks/devops/

# Read task headers for priorities
grep -r "Priority:" tasks/devops/*.md

# Sort by: P0 > P1 > P2 > P3
```

**3. Plan Your Day (5 minutes)**
```
Today I will:
1. [ ] P0 task: [task name] - [estimated time]
2. [ ] P1 task: [task name] - [estimated time]
3. [ ] P2 task: [task name] - [estimated time]

I will complete these by: [time]
```

### **Every Day at 5:00 PM:**

**4. Send Daily Report (5 minutes)**
```
GAUDI,

COMPLETED TODAY:
- [ ] Task X-###: [brief description of what you did]
- [ ] Infrastructure check: [status]

WILL DO TOMORROW:
- [ ] Task Y-###: [brief description]
- [ ] Infrastructure monitoring: [ongoing]

BLOCKERS:
- [ ] None OR describe what's blocking you

ISSUES FOUND:
- [ ] None OR describe infrastructure issues

- Karen
```

---

## 🚨 PRIORITY SYSTEM - MEMORIZE THIS

```
P0 CRITICAL > P1 HIGH > P2 MEDIUM > P3 LOW

P0 CRITICAL:
- Security vulnerabilities
- Server/containers down
- Data loss risk
- Production broken
- DO IMMEDIATELY (within 2 hours)

P1 HIGH:
- Important features
- Performance issues
- Security improvements
- DO TODAY (within 8 hours)

P2 MEDIUM:
- Nice improvements
- Documentation
- Cost optimization
- DO THIS WEEK (within 40 hours)

P3 LOW:
- Nice to have
- Research
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

- Karen
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

- Karen
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
- [List files changed]
- [List tests run]

Results:
- [Describe outcome]
- [Document any issues]

Git commit: [commit hash]
Pushed to: [branch]

- Karen
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

- Karen
```

---

## 🎯 YOUR RESPONSIBILITIES

### **Infrastructure Ownership:**

**Docker:**
- ✅ Maintain Dockerfiles
- ✅ Optimize image sizes
- ✅ Keep base images updated
- ✅ Scan for vulnerabilities
- ✅ Document Docker best practices

**AWS:**
- ✅ Research AWS services
- ✅ Cost optimization
- ✅ Security configuration
- ✅ Monitoring setup
- ✅ Backup strategies

**CI/CD:**
- ✅ Maintain GitHub Actions workflows
- ✅ Test deployments
- ✅ Rollback procedures
- ✅ Deployment documentation

### **Configuration Management:**

**Environment Variables:**
- ✅ NEVER commit secrets to git
- ✅ Use `.env.example` as template (no real secrets!)
- ✅ Document required variables
- ✅ Rotate secrets regularly

**Docker Compose:**
- ✅ Maintain `docker-compose.yml`
- ✅ Add resource limits to ALL services
- ✅ Use environment variables for secrets
- ✅ Document service dependencies

### **Security (Infrastructure Level):**

**Docker Security:**
- ✅ Scan images with Trivy
- ✅ Fix CRITICAL vulnerabilities immediately
- ✅ Fix HIGH vulnerabilities within 24 hours
- ✅ Document security issues

**Secrets Management:**
- ✅ No hardcoded secrets in code
- ✅ No secrets in git history
- ✅ Use environment variables
- ✅ Rotate credentials

---

## 📖 PROJECT STANDARDS - FOLLOW THESE

### **Dockerfile Standards:**

```dockerfile
# Use specific version tags (not 'latest')
FROM python:3.11-slim

# Use non-root user
RUN useradd -m -u 1000 appuser

# Multi-stage builds
FROM node:18-alpine AS builder
# ... build steps ...

FROM node:18-alpine
COPY --from=builder /app /app

# Health checks
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:3000/health || exit 1
```

### **docker-compose.yml Standards:**

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
    environment:
      - DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}  # ✅ Use env vars
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}  # ✅ Use env vars
    secrets:
      - db_password  # ✅ Use Docker secrets for production

secrets:
  db_password:
    file: ./secrets/db_password.txt  # ✅ Never commit secrets!
```

### **.env.example Standards:**

```bash
# ✅ GOOD - Placeholders only
POSTGRES_PASSWORD=your_secure_password_here
DJANGO_SECRET_KEY=your_django_secret_key_here
API_KEY=your_api_key_here

# ❌ BAD - Real secrets (DON'T COMMIT!)
POSTGRES_PASSWORD=FinanceHub2024!
DJANGO_SECRET_KEY=django-insecure-#8v9k2...
```

### **.dockerignore Standards:**

```
# Always create .dockerignore
__pycache__
*.pyc
.env
.env.local
.git
node_modules
*.md
tests
.pytest_cache
```

---

## 🔍 QUALITY CHECKLIST - BEFORE COMMITTING

### **Before You Commit Docker Changes:**

```bash
# 1. Build the image
docker build -t test-image .

# 2. Scan for vulnerabilities
docker scan test-image
# Or with Trivy:
trivy image test-image

# 3. Check image size
docker images test-image

# 4. Test the container
docker run -d --name test-container test-image
docker logs test-container
docker exec test-container <health_check_command>

# 5. Clean up
docker stop test-container
docker rm test-container

# 6. Commit
git add .
git commit -m "feat(docker): descriptive message"
git push origin main
```

### **Before You Commit Configuration Changes:**

```bash
# 1. Check for secrets
grep -r "password" docker-compose.yml
grep -r "secret" docker-compose.yml
grep -r "key" .env.example

# 2. Validate YAML
docker-compose config

# 3. Test locally
docker-compose up -d
docker-compose logs
docker-compose down

# 4. Commit
git add .
git commit -m "feat(config): descriptive message"
git push origin main
```

---

## 📚 RESOURCES - READ THESE

### **Must-Read Documents:**

1. **`KAREN_ROLE_CLARIFICATION.md`** - Role boundaries
2. **`tasks/devops/KAREN_PERFORMANCE_FEEDBACK.md`** - Your performance review
3. **`docs/operations/DOCKER_BUILD.md`** - Docker procedures
4. **`tasks/devops/006-aws-infrastructure-research.md`** - AWS research
5. **`tasks/devops/008-docker-optimization.md`** - Docker best practices

### **Read These When You Start a Task:**

1. Task file (`tasks/devops/XXX-task-name.md`)
2. Related documentation
3. Existing similar implementations

---

## 🎖️ SUCCESS METRICS - HOW YOU'RE MEASURED

### **Excellent Performance (9-10/10):**
- ✅ All P0 tasks completed within 2 hours
- ✅ All P1 tasks completed within 24 hours
- ✅ Responds to all messages within 1 hour
- ✅ Daily reports sent every day at 5:00 PM
- ✅ Proactive monitoring catches issues early
- ✅ Documentation is comprehensive
- ✅ No secrets in git
- ✅ All containers have resource limits

### **Good Performance (7-8/10):**
- ✅ Most tasks completed on time
- ✅ Responds to most messages
- ✅ Daily reports sent regularly
- ✅ Documentation is good

### **Needs Improvement (5-6/10):**
- ⚠️ Some tasks late
- ⚠️ Slow to respond to messages
- ⚠️ Inconsistent daily reports
- ⚠️ Documentation incomplete

### **Unacceptable (1-4/10):**
- ❌ P0 tasks not completed
- ❌ Doesn't respond to messages
- ❌ No daily reports
- ❌ Commits broken code
- ❌ Secrets in git
- ❌ No resource limits

---

## 🚀 YOUR GOALS FOR NEXT WEEK

### **Week 1 (February 3-7):**

**Must Complete:**
1. ✅ D-001: Infrastructure Security (P0) - Complete TODAY
2. ✅ Daily infrastructure monitoring (every day)
3. ✅ Daily reports at 5:00 PM (every day)
4. ✅ Respond to messages within 1 hour

**Should Complete:**
1. D-009: S3 Migration (if approved)
2. D-010: CDN Optimization improvements

**Nice to Have:**
1. Research Kubernetes basics
2. Research monitoring tools (Prometheus, Grafana)

---

## 📞 QUESTIONS? ASK GAUDÍ

**If you're unsure about anything:**
1. Check this document first
2. Check the task file
3. Check related documentation
4. Ask GAUDI (better to ask than guess!)

**When you ask:**
- Be specific about what you need
- Show what you already tried
- Explain what you're trying to accomplish

---

## ✅ SUMMARY - YOUR JOB IN 3 STEPS

**Every Day:**
1. **Morning (9:00 AM):** Check infrastructure, review tasks, plan day
2. **During Day:** Work on highest-priority tasks, update progress
3. **Evening (5:00 PM):** Send daily report

**Every Week:**
1. Complete all P0 and P1 tasks
2. Monitor infrastructure continuously
3. Update dependencies
4. Propose improvements

**Always:**
- Respond to messages within 1 hour
- Prioritize P0 > P1 > P2 > P3
- Never commit secrets
- Never go silent
- Ask for help when blocked

---

**End of Role Guide**  
**Last Updated:** January 30, 2026  
**Next Review:** After D-001 completion

🔧 *You are the DevOps Expert. Own it.*
