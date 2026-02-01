# Web Research Skill

## Overview
Web research involves using search engines and APIs to gather information from the internet, including market data, competitor analysis, best practices, and industry trends.

## Key Concepts
- **Search Queries**: Effective search terms and operators
- **Source Credibility**: Evaluating trustworthiness of sources
- **Information Synthesis**: Combining multiple sources
- **Fact-Checking**: Verifying claims and data
- **Market Research**: Competitive analysis, trends
- **Technical Research**: Best practices, patterns, libraries
- **API Integration**: Using search APIs programmatically
- **Rate Limiting**: Respecting API limits and quotas

## Learning Resources
- [Google Search Operators](https://www.google.com/advanced_search)
- [Brave Search API](https://brave.com/search/api/)
- [Research Methods](https://www.sciencebuddies.org/science-fair-projects/science-fair/background-research)

## Best Practices
- **Specific Queries**: Use precise search terms
- **Search Operators**: Use quotes, site:, -exclude, OR
- **Multiple Sources**: Cross-reference information
- **Recent Data**: Check publication dates
- **Primary Sources**: Prefer official documentation
- **Source Diversity**: Don't rely on single source
- **Cite Sources**: Attribute information properly
- **Verify Doubts**: Fact-check surprising claims

## Search Operators

### Google/Brave Search
```
"exact phrase"           - Exact match
-site:example.com        - Exclude specific site
site:reddit.com          - Search specific site
filetype:pdf             - Specific file type
year:2024                - Specific year
before:2024-01-01        - Before date
after:2024-01-01         - After date
intitle:"trading"        - Words in title
inurl:api               - Words in URL
OR                      - Combine terms
-                       - Exclude term
```

### Examples
```bash
# Specific technology
"Django Ninja" authentication tutorial

# Exclude certain sites
Next.js performance guide -site:nextjs.org

# Recent articles
React hooks best practices after:2023-01-01

# File types
PostgreSQL indexing filetype:pdf

# Specific sites
site:stackoverflow.com "paper trading" Django

# Exclude results
financial API integration -tutorial -course
```

## Tools

### Search APIs
- **Brave Search API**: Privacy-focused search (integrated via MCP)
- **Google Custom Search API**: Google search results
- **Bing Search API**: Microsoft search results
- **DuckDuckGo Instant Answer API**: Quick answers

### Research Tools
- **Notion Web Clipper**: Save articles for later
- **Obsidian**: Knowledge base for research
- **Zotero**: Academic research management
- **Perplexity AI**: AI-powered research

### MCP Integration (FinanceHub)
```jsonc
{
  "brave-search": {
    "type": "remote",
    "url": "https://search.brave.com/api",
    "enabled": true
  }
}
```

**Usage in FinanceHub:**
- Market research and competitor analysis
- Security vulnerability research (CVEs)
- Best practices for DevOps, testing
- Accessibility standards updates (WCAG)
- Documentation standards research

## Research Process

### 1. Define Research Question
**Bad:** "Learn about trading"
**Good:** "How do paper trading platforms handle order execution?"

### 2. Choose Search Strategy
```
# Start broad, then narrow
"paper trading implementation"
→ "paper trading Django implementation"
→ "paper trading Django Ninja tutorial"
```

### 3. Evaluate Sources
**Checklist:**
- [ ] Is the source credible? (.edu, official docs)
- [ ] Is the information recent? (check date)
- [ ] Is the author authoritative? (expert in field)
- [ ] Is there a bias? (promotional content)
- [ ] Can you verify the info? (cross-reference)

### 4. Synthesize Findings
- Take notes on key points
- Identify common patterns
- Note contradictions (investigate further)
- Extract code examples

### 5. Apply to Context
- Adapt examples to your tech stack
- Consider your specific requirements
- Test assumptions before committing

## Research Scenarios

### Competitive Analysis
**Query:** "paper trading platforms features comparison 2024"
**Sources:**
- Official documentation (TradingView, Thinkorswim)
- Review sites (G2, Capterra)
- Reddit discussions (r/algotrading)
- YouTube demos

**Key Information:**
- Feature comparison matrix
- User feedback and pain points
- Pricing models
- Technical architecture (if available)

### Security Research
**Query:** "Django security vulnerabilities 2024 CVE"
**Sources:**
- CVE database (cve.mitre.org)
- Django security advisories
- OWASP Top 10
- Security blogs (PortSwigger, Snyk)

**Key Information:**
- CVE numbers and severity
- Patch versions
- Mitigation strategies
- Exploit details (for understanding)

### Best Practices Research
**Query:** "Next.js production deployment checklist 2024"
**Sources:**
- Vercel deployment guide
- Next.js official docs
- Community best practices
- Case studies (blog posts)

**Key Information:**
- Performance optimization
- Security headers
- Monitoring setup
- CI/CD pipelines

### Technical Implementation
**Query:** "WebSocket Django Channels React implementation"
**Sources:**
- Official docs (Django Channels, React)
- Stack Overflow solutions
- GitHub repositories (examples)
- Tutorial sites

**Key Information:**
- Code examples
- Common pitfalls
- Best practices
- Alternative approaches

## Common Research Mistakes
- **Trusting Outdated Info**: 5-year-old tutorial for current tech
- **Single Source**: Believing one blog post without verification
- **Ignoring Context**: Applying Java patterns to Python
- **Tutorial Hell**: Endless watching without doing
- **Confirmation Bias**: Only reading what confirms your view
- **Paralysis**: Too much research, not enough action

## Research vs. Implementation
```
Research = 20% of time
Implementation = 80% of time

❌ 90% research, 10% action (tutorial hell)
✅ 20% research, 80% action (learn by doing)
```

## Tips for Efficient Research
1. **Start with Official Docs**: Most authoritative source
2. **Use Site Search**: `site:docs.example.com` for specific docs
3. **Check Dates**: Filter by recency (after:2024-01-01)
4. **Look for Code**: Examples over explanations
5. **Verify on Stack Overflow**: See real-world issues
6. **Set Time Limits**: Research for 30 min, then implement

## Context for FinanceHub
**Relevance:** Medium - Research for competitive analysis, best practices, security

**Use Cases:**
- **Market Research**: Competitor features, pricing models
- **Technical Research**: Best practices, libraries, patterns
- **Security Research**: Latest CVEs, security advisories
- **DevOps Research**: Deployment strategies, monitoring
- **Accessibility Research**: WCAG updates, a11y patterns
- **Documentation Research**: Documentation standards, tools

**When to Use:**
- GAUDÍ: Market research, competitor analysis
- ARIA: Agent coordination best practices
- Charo: Security vulnerabilities, CVEs
- GRACE: Testing frameworks, QA patterns
- HADI: WCAG updates, accessibility standards
- Karen: DevOps best practices, monitoring tools
- Scribe: Documentation standards, tools

**When NOT to Use:**
- Coding tasks (use skills instead)
- Routine implementation (follow patterns)
- Well-defined tasks (execute, don't research)

**MCP Usage:**
```typescript
// Example: Research competitor features
await braveSearch({
  query: "TradingView paper trading features 2024",
  count: 10,
  freshness: "py" // Past year
})

// Example: Security research
await braveSearch({
  query: "Django 5.0 security vulnerabilities CVE",
  count: 5,
  freshness: "pw" // Past week
})
```

**Updates:**
- AI-powered search (Perplexity, You.com)
- Semantic search (vector embeddings)
- Real-time search (Google, Brave APIs)

**Notes:**
- Research is a means to an end, not the end itself
- Apply what you learn, don't just collect information
- Verify information from multiple sources
- Respect rate limits on search APIs
- Cite sources when using research
