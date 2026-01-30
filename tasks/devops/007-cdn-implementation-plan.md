# D-007: CloudFlare CDN Implementation Plan

**Task:** CDN Implementation  
**Provider:** CloudFlare (Pro Plan - $20/month)  
**Status:** IN PROGRESS  
**Start Date:** 2026-01-30  
**Target Completion:** 2026-02-15  
**Estimated Time:** 1 week  

---

## Executive Summary

Based on D-006 AWS Infrastructure Research, implementing CloudFlare CDN is recommended for current scale (<5K users) due to:
- Fixed $20/month cost (predictable budgeting)
- Simple setup (~5 minutes)
- Unlimited DDoS protection included
- Excellent performance for static assets
- Easy migration path to CloudFront when scaling

**Expected Benefits:**
- 40-60% faster static asset loading
- 30-50% reduced server bandwidth
- Better global performance
- Improved SEO (faster page loads)

---

## Phase 1: CloudFlare Setup (1-2 days)

### 1.1 Account Creation & Domain Setup

**Step 1: Create CloudFlare Account**
- [ ] Navigate to cloudflare.com and sign up
- [ ] Verify email address
- [ ] Select Pro plan ($20/month)

**Step 2: Add Domain**
- [ ] Enter domain: financehub.app (verify ownership)
- [ ] Select appropriate plan (Pro - $20/month)
- [ ] Verify DNS records are detected
- [ ] Review all records before proceeding

**Step 3: Update Nameservers**
- [ ] Copy CloudFlare nameservers
- [ ] Update domain registrar nameservers
- [ ] Wait for propagation (up to 24 hours, usually 1-2 hours)
- [ ] Verify nameserver change in CloudFlare dashboard

### 1.2 DNS Configuration

**Current DNS Records to Configure:**

| Type | Name | Value | TTL | Proxy Status |
|------|------|-------|-----|--------------|
| A | financehub.app | [current server IP] | Auto | Proxied |
| A | www | [current server IP] | Auto | Proxied |
| A | api | [current server IP] | Auto | Proxied |
| CNAME | assets | assets.financehub.app | Auto | Proxied |
| TXT | @ | v=spf1 include:_spf.google.com ~all | Auto | DNS Only |

**DNS Setup Steps:**
- [ ] Review existing DNS records in- [ ] Enable proxy ( CloudFlare
orange cloud) for A records pointing to origin server
- [ ] Create CNAME for assets subdomain
- [ ] Configure appropriate TTL values
- [ ] Test DNS resolution

### 1.3 SSL/TLS Configuration

**TLS Settings:**
- [ ] Mode: Full (strict)
- [ ] TLS 1.3: Enabled
- [ ] Automatic HTTPS Rewrites: Enabled
- [ ] HSTS: Enabled (max age: 6 months)
- [ ] Certificate: CloudFlare Origin Certificate

**Edge Certificates:**
- [ ] Review TLS 1.3 availability
- [ ] Configure TLS versions (1.2, 1.3 only)
- [ ] Set up certificate monitoring
- [ ] Configure OCSP stapling

### 1.4 Caching Rules

**Cache Level Rules:**

| Rule Name | Pattern | Settings |
|-----------|---------|----------|
| Static Assets | `assets.financehub.app/*` | Cache Everything, Edge TTL: 1 month |
| Images | `*.financehub.app/*.jpg,*.png,*.gif` | Cache Everything, Browser TTL: 1 week |
| CSS/JS | `*.financehub.app/*.css,*.js` | Cache Everything, Edge TTL: 1 week |
| HTML | `financehub.app/*` | Respect Origin Headers, Browser TTL: 30 min |
| API | `api.financehub.app/*` | Bypass Cache |

**Configuration Steps:**
- [ ] Navigate to Rules > Cache Rules
- [ ] Create rule for static assets (assets subdomain)
- [ ] Create rule for images
- [ ] Create rule for CSS/JS
- [ ] Configure page rules for optimal caching
- [ ] Test cache behavior

### 1.5 Security Settings

**DDoS Protection:**
- [ ] Enable DDoS protection (automatic with Pro)
- [ ] Configure protection level (Under Attack mode available)
- [ ] Set up rate limiting rules

**WAF (Web Application Firewall):**
- [ ] Enable OWASP Core Rule Set
- [ ] Configure custom rules if needed
- [ ] Set up SQL injection protection
- [ ] Configure XSS protection rules

**Bot Fight Mode:**
- [ ] Enable Bot Fight Mode
- [ ] Configure JS challenge for suspicious traffic
- [ ] Set up challenge passage duration

---

## Phase 2: Static Asset Optimization (2-3 days)

### 2.1 Django Configuration

**Update settings.py:**

```python
# CDN Configuration
CDN_URL = os.environ.get('CDN_URL', 'https://assets.financehub.app')

# Static Files Configuration
STATIC_URL = f'{CDN_URL}/static/'
MEDIA_URL = f'{CDN_URL}/media/'

# WhiteNoise for local static files (fallback)
INSTALLED_APPS = [
    # ... other apps
    'whitenoise',
]

MIDDLEWARE = [
    # ... other middleware
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

# Compress static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

**Update collectstatic Command:**
- [ ] Test collectstatic with new CDN URLs
- [ ] Verify static files are uploaded correctly
- [ ] Configure manifest for cache busting

### 2.2 Static Asset Organization

**Directory Structure:**
```
financehub/
├── apps/
│   ├── backend/
│   │   ├── static/
│   │   │   ├── css/
│   │   │   ├── js/
│   │   │   └── images/
│   │   └── templates/
│   └── frontend/
│       ├── public/
│       └── .next/static/
```

**Configuration:**
- [ ] Update Django STATIC_ROOT
- [ ] Configure MEDIA_ROOT for user uploads
- [ ] Set up separate storage for user-generated content
- [ ] Implement cache busting with manifest

### 2.3 Cache Busting Implementation

**Manifest File:**
```python
# utils.py
import json
from django.conf import settings
from django.templatetags.static import static

def get_cache_busted_url(path):
    """Get static file URL with cache busting."""
    try:
        manifest = json.load(open(settings.STATIC_ROOT / 'manifest.json'))
        if path in manifest:
            return settings.CDN_URL + manifest[path]
    except (FileNotFoundError, KeyError):
        pass
    return settings.CDN_URL + static(path)
```

**Template Usage:**
```django
<!-- Use in templates -->
<link rel="stylesheet" href="{% static 'css/style.css' %}">
<script src="{% static 'js/app.js' %}"></script>
```

### 2.4 Frontend Configuration

**Next.js Configuration:**
```javascript
// next.config.js
module.exports = {
  assetPrefix: process.env.NODE_ENV === 'production' 
    ? 'https://assets.financehub.app' 
    : undefined,
  // ... other config
}
```

**Build Configuration:**
- [ ] Configure Next.js asset prefix
- [ ] Test production build with CDN
- [ ] Verify _next/static files are served correctly
- [ ] Test SSR pages with CDN assets

### 2.5 Testing All Assets

**Test Checklist:**
- [ ] Verify CSS loads from CDN
- [ ] Verify JavaScript loads from CDN
- [ ] Verify images load from CDN
- [ ] Test cache busting works on file changes
- [ ] Test fallback to origin server
- [ ] Verify response headers (cache-control, etc.)

**Performance Testing:**
- [ ] Run Lighthouse performance audit
- [ ] Compare load times before/after CDN
- [ ] Test from multiple geographic locations
- [ ] Verify cache hit rates in CloudFlare dashboard

---

## Phase 3: Monitoring & Optimization (2 days)

### 3.1 Performance Monitoring

**CloudFlare Analytics:**
- [ ] Set up analytics dashboard
- [ ] Monitor cache hit ratio (target: >90%)
- [ ] Track bandwidth savings
- [ ] Monitor request rates by geography

**Key Metrics to Track:**
- Cache Hit Ratio: >90%
- Bandwidth Served by CloudFlare: >80%
- Average Response Time: <100ms
- Error Rate: <0.1%

### 3.2 Cache Optimization

**Optimization Rules:**
- [ ] Review cache penetration patterns
- [ ] Adjust TTL values based on access patterns
- [ ] Configure stale-while-revalidate
- [ ] Set up cache purge hooks for deployments

**Purge Strategy:**
```python
# purge_cache.py - Run after deployments
import requests

def purge_cdn_cache(urls):
    """Purge CDN cache for specific URLs."""
    zone_id = os.environ.get('CLOUDFLARE_ZONE_ID')
    api_token = os.environ.get('CLOUDFLARE_API_TOKEN')
    
    response = requests.post(
        f'https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache',
        headers={
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        },
        json={'files': urls}
    )
    return response.json()
```

### 3.3 Cost Monitoring

**Budget Tracking:**
- [ ] Set up billing alerts ($15, $25, $30)
- [ ] Monitor monthly spend
- [ ] Track cost per user
- [ ] Review bandwidth patterns

**Expected Monthly Costs:**
- CloudFlare Pro: $20
- Expected savings on server bandwidth: $5-15
- Net monthly impact: $5-15 additional cost

### 3.4 Documentation

**Operations Manual:**
- [ ] Document CDN configuration
- [ ] Create runbook for cache purging
- [ ] Document troubleshooting steps
- [ ] Set up on-call procedures

**Monitoring Dashboard:**
- [ ] Create CloudFlare dashboard
- [ ] Set up alerts for errors
- [ ] Configure rate limiting warnings
- [ ] Document escalation procedures

---

## Rollback Procedures

**If CDN causes issues:**
1. Disable proxy status in CloudFlare DNS
2. Update Django STATIC_URL to use local server
3. Run collectstatic to update local files
4. Test functionality without CDN
5. Investigate and fix issues
6. Re-enable CDN after resolution

**Quick Rollback Commands:**
```bash
# Disable CDN temporarily
export STATIC_URL='/static/'
export MEDIA_URL='/media/'

# Rebuild static files locally
python manage.py collectstatic --noinput
python manage.py compress --force
```

---

## Success Criteria

**Functional Requirements:**
- [ ] All static assets served through CDN
- [ ] Cache hit ratio >90%
- [ ] Page load times improved by 40-60%
- [ ] Server bandwidth reduced by 30-50%

**Non-Functional Requirements:**
- [ ] Zero security regressions
- [ ] No increase in error rates
- [ ] Consistent performance across regions
- [ ] Predictable monthly costs ($20)

**Go-Live Checklist:**
- [ ] All tests passing
- [ ] Performance benchmarks met
- [ ] Monitoring configured
- [ ] Documentation complete
- [ ] Team trained on operations
- [ ] Rollback plan tested

---

## Timeline

| Day | Phase | Tasks |
|-----|-------|-------|
| 1 | Phase 1 | CloudFlare account setup, DNS configuration |
| 2 | Phase 1 | SSL/TLS setup, caching rules |
| 3 | Phase 2 | Django configuration, static asset optimization |
| 4 | Phase 2 | Frontend configuration, testing |
| 5 | Phase 3 | Monitoring setup, optimization |
| 6 | Phase 3 | Documentation, final testing |
| 7 | Buffer | Fixes, optimization, go-live |

---

## Resources

**CloudFlare Documentation:**
- Getting Started: https://developers.cloudflare.com/fundamentals/get-started/
- Caching: https://developers.cloudflare.com/cache/
- Rules: https://developers.cloudflare.com/rules/
- Analytics: https://developers.cloudflare.com/analytics/

**API Resources:**
- API Documentation: https://developers.cloudflare.com/api/
- Client Libraries: https://github.com/cloudflare

**Cost Information:**
- Pro Plan: $20/month
- Includes: Unlimited bandwidth, DDoS protection, SSL, WAF

---

## Notes

**Key Decisions Made:**
1. Using CloudFlare Pro ($20/month) over CloudFront due to current scale
2. Proxied DNS for all origin server records
3. Cache Everything for static assets with 1-month TTL
4. Bypass cache for API endpoints
5. Full TLS (strict) for security

**Open Questions:**
- [ ] Confirm domain registrar access for nameserver updates
- [ ] Verify current server IP addresses
- [ ] Confirm budget approval for $20/month
- [ ] Identify deployment window for changes

---

**Implementation Started:** 2026-01-30  
**Target Completion:** 2026-02-15  
**Status:** Phase 1 IN PROGRESS
