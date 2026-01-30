# Deployment Failure Runbook

## Severity
- **Level**: P0 (Critical)
- **Response Time**: < 5 minutes

## Symptoms
- Deployment pipeline fails
- New version not accessible
- Health checks failing
- Rollback may be required

## Diagnosis

### 1. Check Deployment Status
```bash
# GitHub Actions workflow status
gh run list --workflow=deploy.yml

# ECS deployment status
aws ecs describe-services \
  --cluster finance-hub-production \
  --services finance-hub-api \
  --query 'services[0].deployments[0]'

# Check for failed events
aws ecs describe-services \
  --cluster finance-hub-production \
  --services finance-hub-api \
  --query 'services[0].events'
```

### 2. Check Application Logs
```bash
# ECS task logs
aws logs tail /ecs/frontend --follow
aws logs tail /ecs/backend --follow

# Or via Docker (local)
docker-compose logs backend
docker-compose logs frontend
```

### 3. Verify Health Checks
```bash
# Backend health
curl http://localhost:8000/api/health

# Frontend health
curl http://localhost:3000/health

# Database connection
docker-compose exec postgres pg_isready -U financehub
```

### 4. Check Container Status
```bash
# ECS tasks
aws ecs list-tasks --cluster finance-hub-production

# Container health
aws ecs describe-tasks \
  --cluster finance-hub-production \
  --tasks <task-id>
```

## Resolution

### 1. Immediate Rollback (If Critical)

#### Automated Rollback
```bash
# Rollback ECS service
aws ecs update-service \
  --cluster finance-hub-production \
  --service finance-hub-api \
  --task-definition finance-hub:OLD_VERSION \
  --force-new-deployment

# Or use script
./scripts/rollback.sh production
```

#### Manual Rollback Steps
1. Identify last stable version
```bash
gh run list --workflow=deploy.yml | head -5
```

2. Get previous task definition
```bash
aws ecs list-task-definitions \
  --family-prefix finance-hub-api \
  --sort DESC \
  --max-items 5
```

3. Update service to old version
```bash
aws ecs update-service \
  --cluster finance-hub-production \
  --service finance-hub-api \
  --task-definition <old-task-definition>
```

4. Verify rollback
```bash
# Wait for deployment
aws ecs wait services-stable \
  --cluster finance-hub-production \
  --services finance-hub-api

# Run smoke tests
./scripts/smoke-test.sh production
```

### 2. Fix and Redeploy

#### If Build Failed
```bash
# Check build logs
gh run view [run-id] --log

# Common fixes:
# - Dependency conflicts: Update requirements.txt or package.json
# - Type errors: Fix TypeScript errors
# - Lint errors: Fix linting issues
# - Build timeout: Optimize Dockerfile or increase timeout

# Test fix locally
docker build -f Dockerfile.backend -t test-build .
```

#### If Tests Failed
```bash
# Run tests locally
cd Backend/src && pytest -xvs
cd Frontend && npm test

# Fix failing tests
# Update test expectations
# Mock external dependencies if needed
```

#### If Health Check Failed
```bash
# Check what's failing
curl -v http://localhost:8000/api/health

# Common issues:
# - Database connection: Check DATABASE_URL
# - Missing environment variables: Check AWS Secrets Manager
# - Port not accessible: Check security groups
# - Dependencies not installed: Check Dockerfile

# Fix database migrations
docker-compose exec backend python manage.py migrate
```

#### If Runtime Error
```bash
# Check application logs for errors
docker-compose logs backend | grep ERROR

# Common fixes:
# - Import errors: Fix imports or add to requirements
# - Configuration errors: Check environment variables
# - Missing files: Verify COPY commands in Dockerfile
# - Permission issues: Check file permissions in container
```

### 3. Manual Deployment (If CI/CD Failed)

#### Build and Push Image
```bash
# Build image
docker build -f Dockerfile.backend -t financehub-backend:latest .

# Tag for ECR
docker tag financehub-backend:latest <ECR_REPO>:latest

# Push to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <ECR_REPO>
docker push <ECR_REPO>:latest
```

#### Deploy to ECS
```bash
# Update service
aws ecs update-service \
  --cluster finance-hub-production \
  --service finance-hub-api \
  --force-new-deployment

# Monitor deployment
watch -n 5 'aws ecs describe-services \
  --cluster finance-hub-production \
  --services finance-hub-api \
  --query "services[0].deployments[0].rolloutState"'
```

## Prevention

### 1. Pre-Deployment Checklist
- [ ] All CI checks pass
- [ ] Tests pass locally
- [ ] Health checks configured
- [ ] Rollback plan ready
- [ ] Monitoring set up
- [ ] Team notified

### 2. Staging Testing
```bash
# Always deploy to staging first
./scripts/deploy.sh staging

# Run smoke tests
./scripts/smoke-test.sh staging

# Run E2E tests
cd Frontend && npx playwright test
```

### 3. Gradual Rollout
```bash
# Use ECS deployment configuration
# - Set minimum healthy percent to 50%
# - Set maximum percent to 200%
# - Enable rolling updates
# - Set health check grace period

aws ecs create-service \
  --service-name finance-hub-api \
  --deployment-configuration \
    "minimumHealthyPercent=50,maximumPercent=200,deploymentCircuitBreaker={enable=true,rollback=true}"
```

### 4. Blue-Green Deployment
```bash
# Create blue-green deployment
# 1. Deploy new version to green environment
# 2. Test green environment
# 3. Switch traffic to green
# 4. Keep blue for rollback
```

## Communication

### During Incident
1. Update Slack #incidents channel
2. Post status on status page (if public)
3. Notify stakeholders if prolonged

### Post-Incident
1. Create post-mortem
2. Identify root cause
3. Update runbooks
4. Implement preventive measures

## Common Failure Scenarios

### Scenario 1: Container Won't Start
**Symptoms**: Tasks keep stopping
**Cause**: Application error on startup
**Fix**: Check logs, fix startup command, rebuild image

### Scenario 2: Health Check Fails
**Symptoms**: Tasks marked unhealthy
**Cause**: Health endpoint returning 500
**Fix**: Fix health endpoint, increase timeout, adjust threshold

### Scenario 3: Database Migration Failure
**Symptoms**: Errors in logs about database
**Cause**: Migration conflict or error
**Fix**: Rollback migration, fix migration file, reapply

### Scenario 4: Out of Memory
**Symptoms**: Container OOMKilled
**Cause**: Memory leak or insufficient memory
**Fix**: Increase container memory, fix leak, restart service

## Related
- [API_PERFORMANCE_ISSUES.md](./API_PERFORMANCE_ISSUES.md)
- [HIGH_CPU_MEMORY.md](./HIGH_CPU_MEMORY.md)
- [DATABASE_ISSUES.md](./DATABASE_ISSUES.md)

## Deployment Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Deployment Success Rate | > 95% | |
| Mean Time to Recovery | < 30 min | |
| Rollback Rate | < 5% | |

## Escalation
- If rollback fails: Page on-call immediately
- If critical system down: Page on-call + notify management
- If unresolved after 30 min: Escalate to engineering lead
