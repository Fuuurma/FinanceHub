# Infrastructure Architecture for FinanceHub

## Overview

FinanceHub is deployed on AWS with a multi-tier architecture designed for high availability, security, and scalability.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Layer                              │
├─────────────────────────────────────────────────────────────────┤
│  Web Browser (HTTPS)    │   Mobile Apps (API)                   │
└─────────────┬───────────────────────────┬───────────────────────┘
              │                           │
              ▼                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CDN & Edge Layer                           │
├─────────────────────────────────────────────────────────────────┤
│  CloudFront (CDN)        │   AWS WAF (Firewall)                 │
│  Route53 (DNS)           │   AWS Shield (DDoS Protection)       │
└─────────────┬───────────────────────────┬───────────────────────┘
              │                           │
              ▼                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Application Layer                            │
├─────────────────────────────────────────────────────────────────┤
│  Elastic Load Balancer (ALB)                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         ECS Fargate Cluster (Auto-scaling)              │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │   │
│  │  │  Frontend    │  │  Backend     │  │  Worker      │ │   │
│  │  │  (Next.js)   │  │  (Django)    │  │  (Dramatiq)  │ │   │
│  │  │   Container  │  │   Container  │  │   Container  │ │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘ │   │
│  │                                                          │   │
│  │   Min: 2 tasks per service   Max: 10 tasks             │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────┬───────────────────────────┬───────────────────────┘
              │                           │
              ▼                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Data Layer                                │
├─────────────────────────────────────────────────────────────────┤
│  Amazon RDS PostgreSQL  │   ElastiCache Redis                  │
│  (Multi-AZ, Read Replica)   (Caching, Sessions)                │
│                                                            │     │
│  S3 (Static Assets)        │   EFS (Shared File System)        │
└─────────────────────────────────────────────────────────────────┘
```

## Infrastructure Components

### Compute

#### ECS Fargate (Container Orchestration)
- **Frontend Service**: Next.js application
  - Container: 2 GB RAM, 1 vCPU
  - Tasks: 2-10 (auto-scaling)
  - Health check: `/health`

- **Backend API**: Django REST API
  - Container: 4 GB RAM, 2 vCPU
  - Tasks: 2-10 (auto-scaling)
  - Health check: `/api/health`

- **Worker Service**: Dramatiq background jobs
  - Container: 2 GB RAM, 1 vCPU
  - Tasks: 2-5 (auto-scaling)
  - Queues: default, high-priority, low-priority

#### Auto-scaling Configuration
- **Scale up**: CPU > 70% for 2 minutes
- **Scale down**: CPU < 30% for 5 minutes
- **Min instances**: 2 per service
- **Max instances**: 10 per service
- **Target tracking**: 50% CPU utilization

### Database

#### Amazon RDS PostgreSQL 15
- **Instance**: db.t3.large (2 vCPU, 8 GB RAM)
- **Storage**: 500 GB SSD (gp3)
- **Multi-AZ**: Yes (high availability)
- **Read Replica**: 1 instance for read queries
- **Backup**: 30-day retention
- **Maintenance Window**: Sunday 3 AM UTC

#### ElastiCache Redis 7
- **Node Type**: cache.t3.medium (2 vCPU, 3.08 GB RAM)
- **Replication**: 1 replica (primary + replica)
- **Eviction Policy**: allkeys-lru
- **Automatic Failover**: Enabled
- **Use Cases**:
  - Session storage
  - Query result caching
  - Real-time data caching
  - Rate limiting

### Storage

#### Amazon S3
- **Static Assets Bucket**: `finance-hub-static`
  - CloudFront origin
  - Versioning: Enabled
  - Lifecycle: Transition to Glacier after 90 days

- **User Uploads Bucket**: `finance-hub-uploads`
  - Private access only
  - Virus scanning: Enabled
  - Size limit: 10 MB per file

- **Backup Bucket**: `finance-hub-backups`
  - Cross-region replication: Enabled
  - Retention: 1 year

#### Amazon EFS
- **Mount Point**: `/mnt/efs`
- **Throughput**: 1 MB/s
- **Use Cases**:
  - Shared logs
  - Temporary file storage
  - Worker file processing

### Networking

#### VPC Configuration
- **CIDR**: 10.0.0.0/16
- **Availability Zones**: 2 (us-east-1a, us-east-1b)
- **Subnets**:
  - Public: 10.0.1.0/24, 10.0.2.0/24
  - Private: 10.0.10.0/24, 10.0.11.0/24
  - Database: 10.0.20.0/24, 10.0.21.0/24

#### Security Groups
- **ALB Security Group**: 80, 443 from 0.0.0.0/0
- **ECS Security Group**: 8080 from ALB only
- **RDS Security Group**: 5432 from ECS only
- **Redis Security Group**: 6379 from ECS only

### Load Balancing

#### Application Load Balancer (ALB)
- **Scheme**: Internet-facing
- **Type**: Application Load Balancer
- **Listeners**:
  - HTTP (80) → Redirect to HTTPS
  - HTTPS (443) → Forward to ECS
- **Target Groups**:
  - Frontend: Port 3000
  - Backend: Port 8000
  - Health checks: `/health`

### CDN & Edge

#### CloudFront
- **Distribution ID**: E1234567890
- **Origin**: ALB
- **Behaviors**:
  - `/static/*`: Cache for 1 year
  - `/api/*`: No caching
  - `/*`: Cache for 1 hour
- **Geo Restriction**: None
- **Price Class**: 100 (US, Canada, Europe)

#### Route53
- **Hosted Zone**: financehub.com
- **Records**:
  - `financehub.com` → ALB
  - `www.financehub.com` → ALB
  - `api.financehub.com` → ALB
  - `staging.financehub.com` → Staging ALB

### Security

#### AWS WAF (Web Application Firewall)
- **Rules**:
  - Block SQL injection
  - Block XSS attacks
  - Rate limiting: 2000 requests/5 minutes
  - IP reputation list
  - Bot control

#### AWS Shield
- **Type**: Standard (DDoS protection)
- **Coverage**: All public resources

#### Secrets Management
- **AWS Secrets Manager**:
  - Database credentials
  - API keys
  - OAuth tokens
  - Rotation: Every 30 days

#### Certificate Management
- **AWS Certificate Manager (ACM)**:
  - Certificate: *.financehub.com
  - Renewal: Automatic
  - Validation: DNS

### Monitoring & Logging

#### CloudWatch
- **Metrics**:
  - ECS CPU/Memory utilization
  - RDS connections/performance
  - ELB request count/latency
  - Custom application metrics

- **Alarms**:
  - High CPU (> 80%)
  - High memory (> 85%)
  - High error rate (> 5%)
  - High latency (P95 > 2s)

- **Dashboards**:
  - Infrastructure overview
  - Application performance
  - Database performance
  - Error tracking

#### CloudWatch Logs
- **Log Groups**:
  - `/ecs/frontend`
  - `/ecs/backend`
  - `/ecs/worker`
  - `/aws/rds/financehub`
- **Retention**: 7 days (production), 1 day (staging)
- **Log Streams**: One per container

#### X-Ray (Distributed Tracing)
- **Sampling**: 10% of requests
- **Annotations**: User ID, Request ID
- **Metadata**: Environment, Version

## Cost Management

### Monthly Cost Estimate

| Service | Configuration | Cost (USD) |
|---------|--------------|------------|
| ECS Fargate | 30 avg tasks × $40/month | $1,200 |
| RDS PostgreSQL | db.t3.large × 2 | $350 |
| ElastiCache Redis | cache.t3.medium × 2 | $120 |
| S3 Storage | 500 GB + requests | $25 |
| CloudFront | 1 TB transfer | $85 |
| Data Transfer | 1 TB outbound | $80 |
| CloudWatch Logs | 10 GB/month | $5 |
| **Total** | | **~$1,865/month** |

### Cost Optimization
- Reserved instances for RDS (30% savings)
- S3 lifecycle policies (reduce storage costs)
- CloudFront caching (reduce data transfer)
- Right-sizing ECS tasks (optimize compute)

## Disaster Recovery

### Backup Strategy
- **Database**: Automated daily backups (30-day retention)
- **S3**: Versioning + cross-region replication
- **EFS**: Daily snapshots (7-day retention)

### Recovery Procedures
- **RTO (Recovery Time Objective)**: 4 hours
- **RPO (Recovery Point Objective)**: 15 minutes
- **Failover**: Automatic (Multi-AZ)

### Testing
- Monthly restoration drills
- Quarterly failover tests
- Annual disaster recovery simulation

## High Availability

### Redundancy
- **Multi-AZ deployment**: 2 availability zones
- **Load balancer**: Cross-zone load balancing
- **Database**: Multi-AZ with automatic failover
- **Cache**: Redis replica with auto-failover

### Scaling
- **Horizontal scaling**: ECS auto-scaling
- **Database scaling**: Read replicas for reads
- **Cache scaling**: ElastiCache cluster mode (if needed)

## Security & Compliance

### Network Security
- **VPC**: Private subnets for resources
- **Security Groups**: Restrictive rules
- **NACLs**: Additional network layer
- **VPN**: Direct Connect for corporate access

### Data Protection
- **Encryption at rest**: RDS, S3, EFS
- **Encryption in transit**: TLS 1.3
- **Key management**: AWS KMS
- **Secrets**: AWS Secrets Manager

### Compliance
- **SOC 2 Type II**: Certified
- **GDPR**: Compliant
- **PCI DSS**: Level 1 (if handling payments)

## Deployment Pipeline

### CI/CD Flow
```
Developer Push → GitHub → GitHub Actions → Build & Test
                                              ↓
                                         Push to ECR
                                              ↓
                                         Deploy to ECS
                                              ↓
                                         Run Smoke Tests
                                              ↓
                                     Notify Team (Slack)
```

### Environments
- **Staging**: https://staging.financehub.com
- **Production**: https://financehub.com
- **Isolation**: Separate ECS clusters, RDS instances

## Future Enhancements

### Planned Improvements
- [ ] Kubernetes (EKS) for orchestration
- [ ] Aurora Serverless for database
- [ ] Global database (Multi-region)
- [ ] AWS Fargate Spot instances
- [ ] Infrastructure as Code (Terraform)
- [ ] Service Mesh (AWS App Mesh)

---

**Last Updated**: 2026-01-30
**Maintained By**: DevOps Team
**Next Review**: 2026-02-28
