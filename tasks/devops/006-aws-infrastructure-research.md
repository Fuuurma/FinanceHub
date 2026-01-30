# AWS Infrastructure Research - FinanceHub

**Task:** D-006 AWS Infrastructure Research
**Created:** 2026-01-30
**Status:** 🔄 IN PROGRESS

---

## 1. CDN Strategy Analysis

### CloudFlare vs AWS CloudFront Comparison

| Feature | CloudFlare | AWS CloudFront |
|---------|------------|----------------|
| **Free Tier** | ✅ Yes (Pro: $20/month) | ❌ No free tier |
| **Setup Time** | ~5 minutes | ~1+ hour |
| **DDoS Protection** | Unlimited (included) | Additional cost |
| **AWS Integration** | Basic | Native (no transfer fees for S3/EC2) |
| **Latency** | Good | Better for AWS-hosted origins |
| **Customization** | Limited | High (Lambda@Edge, etc.) |

### Cost Analysis by User Tier

| Users/month | CloudFlare (Pro) | CloudFront |
|-------------|------------------|------------|
| 1,000 | $20/month | ~$10/month |
| 5,000 | $20/month | ~$50/month |
| 10,000 | $20/month | ~$100/month |

**Recommendation:** 
- **< 5K users:** CloudFlare (simpler, fixed cost)
- **> 5K users:** CloudFront (better AWS integration, no S3 transfer fees)
- **Break-even:** ~3K users

---

## 2. S3 Migration Plan

### Current State
- Local file storage for images/uploads
- No CDN for static assets

### Target Architecture
```
Frontend → CloudFlare/CloudFront → S3 (images/uploads)
                                    ↓
                            django-storages + boto3
```

### Implementation Steps

1. **Create S3 Bucket** (Week 1)
   ```bash
   aws s3 mb s3://financehub-assets
   ```

2. **Configure CORS** (Week 1)
   ```json
   [
     {
       "AllowedHeaders": ["*"],
       "AllowedMethods": ["GET", "PUT", "POST"],
       "AllowedOrigins": ["https://financehub.app"],
       "ExposedHeaders": []
     }
   ]
   ```

3. **Update Django Settings** (Week 2)
   ```python
   # settings.py
   AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
   AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
   AWS_STORAGE_BUCKET_NAME = 'financehub-assets'
   AWS_S3_REGION_NAME = 'us-east-1'
   
   DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
   ```

4. **Migrate Existing Images** (Week 2)
   - Use AWS CLI to sync local uploads to S3
   - Update database paths

### Cost Projection (S3 + CDN)

| Storage/Requests | Cost |
|------------------|------|
| 10 GB storage | ~$0.23/month |
| 100 GB bandwidth | ~$9/month |
| 100K requests | ~$4/month |
| **Total at 5K users** | **~$15-25/month** |

---

## 3. AWS Services Research

### ECS (Elastic Container Service)

| Option | Cost | Use Case |
|--------|------|----------|
| **Fargate** | $0.0135/vCPU-hour + $0.0015/GB-hour | Serverless (recommended) |
| **EC2** | Variable (m5.large: ~$70/month) | More control |

**Recommendation:** Fargate for simplicity

### RDS (Managed PostgreSQL)

| Instance | Cost/month | Features |
|----------|------------|----------|
| db.t3.micro | ~$15 | Good for dev/staging |
| db.t3.small | ~$25 | Production (up to 10K users) |
| db.m5.large | ~$90 | High traffic |

**Recommendation:** db.t3.small for production

### ElastiCache (Redis)

| Node Type | Cost/month | Use Case |
|-----------|------------|----------|
| cache.t3.micro | ~$15 | Development |
| cache.t3.small | ~$25 | Production (up to 10K users) |

**Recommendation:** cache.t3.small for production

### CloudWatch (Monitoring)

| Feature | Cost |
|---------|------|
| Metrics (3 detailed) | Free |
| Logs | ~$0.50/GB |
| Alarms | $0.10/alarm/month |

**Recommendation:** Basic monitoring free tier sufficient

---

## 4. Terraform Templates

### Required Templates

1. **VPC Setup** (`vpc.tf`)
   - Public/private subnets
   - NAT Gateway
   - Security groups

2. **ECS Cluster** (`ecs.tf`)
   - Fargate cluster
   - Task definitions
   - Service configuration

3. **RDS Instance** (`rds.tf`)
   - PostgreSQL 15
   - Automated backups
   - Multi-AZ (optional)

4. **S3 Buckets** (`s3.tf`)
   - Assets bucket
   - Logs bucket
   - Backup bucket

5. **ElastiCache** (`elasticache.tf`)
   - Redis cluster
   - Parameter groups

6. **CloudFront Distribution** (`cloudfront.tf`)
   - S3 origin
   - SSL certificate (ACM)
   - Cache policies

### Sample Structure

```
terraform/
├── main.tf
├── variables.tf
├── outputs.tf
├── modules/
│   ├── vpc/
│   ├── ecs/
│   ├── rds/
│   ├── s3/
│   ├── elasticache/
│   └── cloudfront/
└── environments/
    ├── staging/
    └── production/
```

---

## 5. Cost Summary (Monthly)

### Current State (Render/Railway)
- ~$20-50/month (depending on usage)

### AWS Target State

| Service | Dev | Staging | Production (10K users) |
|---------|-----|---------|------------------------|
| ECS (Fargate) | $5 | $10 | $50 |
| RDS (t3.small) | $15 | $15 | $25 |
| ElastiCache | - | $15 | $25 |
| S3 + CloudFront | $5 | $10 | $30 |
| NAT Gateway | $30 | $30 | $45 |
| **Total** | **$55** | **$80** | **$175** |

### Break-even Analysis

| Scenario | Current Cost | AWS Cost | Users at Break-even |
|----------|--------------|----------|---------------------|
| Migration now | $25/month | $175/month | 10K+ users |
| Wait for 5K | $50/month | $175/month | 5K users |
| Optimal | $100/month | $175/month | 3K users |

**Recommendation:** Wait until 5K users before full AWS migration. Implement CDN at 3K users.

---

## 6. Implementation Timeline

### Phase 1: CDN (Month 1)
- **Week 1-2:** Research and select provider
- **Week 3-4:** Implementation and testing

### Phase 2: S3 Migration (Month 2)
- **Week 1-2:** S3 setup and Django integration
- **Week 3-4:** Data migration and validation

### Phase 3: AWS Infrastructure (Month 3)
- **Week 1-2:** Terraform templates and staging
- **Week 3-4:** Production deployment

---

## 7. Deliverables Checklist

- [ ] AWS Migration Plan document (this file)
- [ ] Cost breakdown analysis
- [ ] Implementation timeline
- [ ] Terraform templates in `terraform/`
- [ ] Rollback procedures
- [ ] Team training plan
- [ ] Architect approval for budget

---

## 8. Next Steps

1. Present findings to Architect
2. Get budget approval
3. Start D-007 (CDN Implementation) at 3K users
4. Start D-008 (S3 Migration) at 5K users
5. Start D-009 (AWS Infrastructure) at 10K users

---

**Research Completed:** 2026-01-30
**Status:** Ready for Architect review
