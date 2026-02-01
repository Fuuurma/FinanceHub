# SEO Improvement Tasks for FinanceHub

**Task Group:** SEO
**Created:** February 1, 2026
**Author:** HADI (Accessibility Specialist)
**Priority:** Medium-High
**Status:** PROPOSED

---

## Executive Summary

FinanceHub currently has minimal SEO implementation. This document outlines comprehensive SEO improvements needed to enhance search engine visibility, social sharing, and overall discoverability.

**Current State:**
- Basic title and description in metadata
- No Open Graph tags
- No Twitter cards
- No JSON-LD structured data
- No sitemap.xml
- No robots.txt
- No manifest.json for PWA

**Estimated Impact:** High - Proper SEO can increase organic traffic by 30-50%

---

## Current SEO Analysis

### What Works
| Item | Status | Notes |
|------|--------|-------|
| Title tag | Present | "FinanceHub - Professional Market Analysis" |
| Meta description | Present | "Advanced financial terminal..." |
| Semantic HTML | Good | Uses proper heading hierarchy |
| Mobile responsive | Good | Tailwind CSS responsive classes |

### Missing/Needs Improvement
| Item | Status | Impact |
|------|--------|--------|
| Open Graph tags | Missing | High - Social sharing broken |
| Twitter Cards | Missing | Medium - Twitter sharing poor |
| JSON-LD Schema | Missing | High - Rich snippets unavailable |
| Sitemap.xml | Missing | High - Crawl efficiency low |
| Robots.txt | Missing | Medium - Crawl control missing |
| Canonical URLs | Missing | Medium - Duplicate content risk |
| Theme color | Missing | PWA installation |
| Core Web Vitals | Unknown | Needs testing |

---

## Task SEO-001: Enhanced Metadata & Open Graph

**Priority:** P1 HIGH
**Estimated Effort:** 2 hours
**Dependencies:** None

### Requirements

Update apps/frontend/src/app/layout.tsx with comprehensive metadata including Open Graph and Twitter cards.

### Files to Modify
- apps/frontend/src/app/layout.tsx

---

## Task SEO-002: JSON-LD Structured Data

**Priority:** P1 HIGH
**Estimated Effort:** 4 hours
**Dependencies:** SEO-001

### Requirements

Add comprehensive JSON-LD structured data for rich search results:
- Organization Schema (FinancialService)
- WebSite Schema with SearchAction
- Financial Product Schema

### Files to Create
- components/seo/OrganizationSchema.tsx
- components/seo/WebSiteSchema.tsx
- components/seo/FinancialProductSchema.tsx
- components/seo/index.ts

---

## Task SEO-003: Dynamic Metadata for Pages

**Priority:** P1 HIGH
**Estimated Effort:** 3 hours
**Dependencies:** SEO-001

### Requirements

Add dynamic metadata to key pages:
- Holdings page
- Options Chain page
- Stock Screener page
- Charts page
- Backtesting page

### Files to Modify
- apps/frontend/src/app/(dashboard)/holdings/page.tsx
- apps/frontend/src/app/(dashboard)/options/page.tsx
- apps/frontend/src/app/(dashboard)/screener/page.tsx
- And 2 more pages

---

## Task SEO-004: Sitemap Generation

**Priority:** P1 HIGH
**Estimated Effort:** 2 hours
**Dependencies:** None

### Requirements

Create dynamic sitemap.xml using Next.js MetadataRoute API.

### Files to Create
- apps/frontend/src/app/sitemap.ts

---

## Task SEO-005: Robots.txt

**Priority:** P2 MEDIUM
**Estimated Effort:** 1 hour
**Dependencies:** None

### Requirements

Create robots.txt for proper crawl control.

### Files to Create
- apps/frontend/src/app/robots.ts

---

## Task SEO-006: PWA Manifest

**Priority:** P2 MEDIUM
**Estimated Effort:** 2 hours
**Dependencies:** None

### Requirements

Create site.webmanifest for PWA installability with icons and shortcuts.

### Files to Create
- apps/frontend/public/site.webmanifest

---

## Task SEO-007: OG Image Generation

**Priority:** P2 MEDIUM
**Estimated Effort:** 4 hours
**Dependencies:** SEO-001

### Requirements

Create dynamic Open Graph images using @vercel/og.

### Files to Create
- apps/frontend/src/app/opengraph-image.tsx

---

## Task SEO-008: Core Web Vitals Optimization

**Priority:** P1 HIGH
**Estimated Effort:** 6 hours
**Dependencies:** None

### Requirements

Optimize for Core Web Vitals (LCP, FID, CLS):
- LCP: Preload fonts, optimize images
- FID/INP: Reduce JS bundle, code splitting
- CLS: Fixed dimensions, font loading strategies

---

## Task SEO-009: hreflang for Internationalization

**Priority:** P3 LOW
**Estimated Effort:** 2 hours
**Dependencies:** None

### Requirements

Add hreflang tags for multi-language support when needed.

---

## Estimated Timeline

| Task | Effort | Priority | Order |
|------|--------|----------|-------|
| SEO-001 | 2h | P1 | 1 |
| SEO-002 | 4h | P1 | 2 |
| SEO-003 | 3h | P1 | 3 |
| SEO-004 | 2h | P1 | 4 |
| SEO-005 | 1h | P2 | 5 |
| SEO-006 | 2h | P2 | 6 |
| SEO-007 | 4h | P2 | 7 |
| SEO-008 | 6h | P1 | 8 |
| SEO-009 | 2h | P3 | 9 |

**Total Estimated Time:** 26 hours

---

## Dependencies Between Tasks

```
SEO-001 (Enhanced Metadata)
    ↓
SEO-002 (JSON-LD) ──┐
SEO-003 (Dynamic Meta) ──┤
SEO-007 (OG Image) ──┘
         ↓
SEO-004 (Sitemap) ← Independent
SEO-005 (Robots) ← Independent
SEO-006 (Manifest) ← Independent
SEO-008 (Web Vitals) ← Independent
SEO-009 (hreflang) ← Independent
```

---

## Acceptance Criteria

### All Tasks
- [ ] Lighthouse SEO score 95+
- [ ] No critical SEO warnings
- [ ] All metadata properly implemented
- [ ] Social cards display correctly

### Specific
- [ ] Sitemap accessible at /sitemap.xml
- [ ] Robots.txt accessible at /robots.txt
- [ ] OG images work when sharing
- [ ] JSON-LD validates in Google Rich Results Test
- [ ] Core Web Vitals in green (LCP < 2.5s, FID < 100ms, CLS < 0.1)

---

## Tools for Verification

- Google Search Console
- Google Rich Results Test
- Lighthouse SEO Audit
- Ahrefs/SEMrush
- Bing Webmaster Tools

---

## Next Steps

1. Review and approve SEO task list
2. Assign tasks to available coder
3. Begin with SEO-001 (foundation for others)
4. Test each task before moving to next
5. Final verification with Lighthouse

---

**Created by:** HADI
**Date:** February 1, 2026
**Version:** 1.0
