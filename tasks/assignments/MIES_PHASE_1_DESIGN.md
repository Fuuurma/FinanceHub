# 📋 Task Assignment: Phase 1 UI/UX Design (C-036, C-037, C-030)

**Date:** February 1, 2026
**From:** GAUDÍ (Architect)
**To:** MIES (UI/UX Designer)
**Priority:** HIGH - Phase 1 Design Work
**Estimated Effort:** 12-15 hours total
**Timeline:** Start immediately, before development

---

## 🎯 OVERVIEW

You are assigned to **UI/UX design for Phase 1 features**:
- C-036: Paper Trading System
- C-037: Social Sentiment Analysis
- C-030: Broker API Integration

**Collaborators:**
- **Turing (Frontend):** Building UI components (needs your designs)
- **Linus (Backend):** Building APIs
- **Guido (Backend):** Building sentiment APIs
- **GAUDÍ (Architect):** Strategic direction, unified minimalistic brutalism

**Your Role:** Create design mockups, component specifications, user flows, and design system documentation.

---

## 🎨 DESIGN DIRECTION

**Unified Minimalistic Brutalism:**
- **Brutalist Foundation:** `rounded-none` everywhere, sharp edges
- **Minimalistic Application:** Tiered border widths (landing=4px, dashboard=2px, trading=1px)
- **Clean Despite Complexity:** Strategic whitespace for data-dense interfaces

**Key Principles:**
1. **Bold base, restrained application** - Use brutalist elements deliberately
2. **Data clarity first** - Financial interfaces require readability
3. **Consistent across all features** - Seamless user experience
4. **Accessibility always** - WCAG 2.1 Level AA compliant

---

## 📋 YOUR TASKS

### Task 1: C-036 Paper Trading UI Design (4h)

**Deliverables:**
1. **Page Layout Mockup** (Figma/Sketch)
2. **Component Specifications** (buttons, forms, tables)
3. **User Flow Diagram** (create portfolio → execute trade → view positions)
4. **Responsive Designs** (desktop, tablet, mobile)

#### 1.1 Paper Trading Page Layout

**Layout Structure:**
```
┌─────────────────────────────────────────────────────────────┐
│  Paper Trading                                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │ Portfolio│  │  Order   │  │Performance│                 │
│  │ Summary  │  │   Form   │  │  Chart   │                 │
│  │          │  │          │  │          │                 │
│  │ $98,500  │  │ [Symbol] │  │  📈      │                 │
│  │ +2.5%    │  │ [Buy/Sell│  │          │                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
│                                                              │
│  ┌────────────────────────────────────────────┐            │
│  │  Positions                                  │            │
│  │  ┌─────────────────────────────────────┐   │            │
│  │  │ Symbol │ Qty │ Avg   │ Current│P/L  │   │            │
│  │  │ AAPL   │ 10  │ $150  │ $160  │+$100│   │            │
│  │  │ TSLA   │ 5   │ $200  │ $190  │ -$50 │   │            │
│  │  └─────────────────────────────────────┘   │            │
│  └────────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

**Design Specifications:**
- **Grid:** 12-column grid
- **Spacing:** 8px base unit
- **Borders:** `border-2` (minimalistic brutalist)
- **Border Radius:** `rounded-none` (brutalist base)
- **Colors:** High contrast for data readability

**Components to Design:**

##### Portfolio Summary Card
```
┌──────────────────┐
│ Portfolio Value  │
├──────────────────┤
│ Cash:    $98,500 │
│ Value:   $52,500 │
│ Return:  +5.25% │ (green)
├──────────────────┤
│ Total:   $151,000│
└──────────────────┘
```

**Design Questions:**
- [ ] What metrics to display? (Cash, Value, Return, Day Change?)
- [ ] How to show positive/negative returns? (Color coding)
- [ ] Update frequency indicator? (Real-time badge)

##### Order Form
```
┌──────────────────┐
│ Place Order      │
├──────────────────┤
│ Symbol: [AAPL 🔍]│
│ Side:   [BUY|SELL]│
│ Type:   [Market|Limit]│
│ Qty:    [10]     │
│ Price:  [$150]   │ (if limit)
│                  │
│ [EXECUTE BUY]    │
└──────────────────┘
```

**Design Questions:**
- [ ] How to show buy/sell toggle? (Buttons or dropdown?)
- [ ] How to show market vs limit order differences?
- [ ] Order confirmation modal design?
- [ ] Error message placement?

##### Position List Table
```
┌──────────────────────────────────────────┐
│ Symbol │ Qty │ Avg   │ Current│ P/L     │
│ AAPL   │ 10  │ $150  │ $160  │+$100 (+6.7%)│
│ TSLA   │ 5   │ $200  │ $190  │-$50 (-2.5%) │
└──────────────────────────────────────────┘
```

**Design Questions:**
- [ ] How to highlight P/L? (Color coding, bolding?)
- [ ] How to show actions? (Close button in last column?)
- [ ] Empty state design?
- [ ] Loading state design?

#### 1.2 User Flow

**Flow: Create Portfolio → Execute Trade**

1. **Navigate to Paper Trading**
   - User sees: Empty state (no portfolio yet)
   - Action: "Start Paper Trading" button
   - Result: Portfolio created with $100,000

2. **Execute First Trade**
   - User sees: Order form
   - Action: Search symbol, select buy/sell, enter quantity
   - Result: Order confirmation modal

3. **Confirm Order**
   - User sees: Order details (symbol, side, quantity, estimated cost)
   - Action: "Confirm" or "Cancel"
   - Result: Order executed, portfolio updated

4. **View Results**
   - User sees: Portfolio summary updated, new position in list
   - Real-time updates via WebSocket

**Design Deliverables:**
- [ ] User flow diagram (Figma flow)
- [ ] Wireframes for each step
- [ ] State designs (empty, loading, error, success)

---

### Task 2: C-037 Social Sentiment UI Design (4h)

**Deliverables:**
1. **Page Layout Mockup** (Figma/Sketch)
2. **Component Specifications** (sentiment gauge, social feed)
3. **User Flow Diagram** (view sentiment → analyze → track)
4. **Responsive Designs** (desktop, tablet, mobile)

#### 2.1 Sentiment Overview Page Layout

**Layout Structure:**
```
┌─────────────────────────────────────────────────────────────┐
│  Social Sentiment - AAPL                                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐  ┌────────────────────────────────┐          │
│  │Sentiment │  │     Sentiment History           │          │
│  │  Gauge   │  │  📈 (line chart)               │          │
│  │          │  │                                │          │
│  │  BULLISH │  │  [24h] [7d] [30d]              │          │
│  │  +0.45   │  │                                │          │
│  │  🐦 87   │  │                                │          │
│  └──────────┘  └────────────────────────────────┘          │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │  Trending Assets│  │   Social Feed    │               │
│  │  📈             │  │  (Tweets/Posts)  │               │
│  │  AAPL 87 mentions│  │                  │               │
│  │  TSLA 65 mentions│  │  🐦 @user: ...   │               │
│  │  NVDA 42 mentions│  │  🐦 @user: ...   │               │
│  └──────────────────┘  └──────────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

**Components to Design:**

##### Sentiment Gauge
```
     ┌─────────┐
     │   🐦    │
     │ BULLISH │
     │  +0.45  │
     │ 87 📝   │
     └─────────┘
```

**Design Questions:**
- [ ] Gauge visualization? (Semicircle gauge, progress bar?)
- [ ] Color coding for bullish/bearish/neutral?
- [ ] How to show source breakdown (Twitter vs Reddit)?

##### Sentiment History Chart
```
┌─────────────────────────────────┐
│ Sentiment Over Time             │
├─────────────────────────────────┤
│ 1.0 │ ┌───┐                     │
│ 0.5 ││   │   ┌───┐              │
│ 0.0 │└───┘───┘   └───┐          │
│-0.5 │                └───┐      │
│-1.0 │                    └───   │
│     └───────────────────────────│
│     0h  6h  12h  18h   24h     │
└─────────────────────────────────┘
```

**Design Questions:**
- [ ] Time period selector? (24h, 7d, 30d tabs)
- [ ] Zero line reference?
- [ ] Tooltip design for exact values?

##### Trending Assets List
```
┌──────────────────────────────┐
│ Trending Assets              │
├──────────────────────────────┤
│ AAPL  87 📝  📈 Bullish      │
│ TSLA  65 📝  📉 Bearish      │
│ NVDA  42 📝  ➡️  Neutral     │
└──────────────────────────────┘
```

**Design Questions:**
- [ ] How to show mention count trend? (Up/down arrow?)
- [ ] Click to navigate to asset sentiment page?

##### Social Feed
```
┌──────────────────────────────────────┐
│ Social Feed                         │
├──────────────────────────────────────┤
│ [All] [Twitter] [Reddit]            │
├──────────────────────────────────────┤
│ 🐦 @trader_guru                     │
│ $AAPL looking strong today! 🚀     │
│ Bullish (+0.8) • 2h ago             │
├──────────────────────────────────────┤
│ 🐦 @investor_pro                    │
│ Buying more $TSLA at dip 📉        │
│ Bullish (+0.6) • 3h ago             │
├──────────────────────────────────────┤
│ 📌 u/wallstreetbets                 │
│ NVDA to the moon! 🌙                │
│ Bullish (+0.9) • 1h ago             │
└──────────────────────────────────────┘
```

**Design Questions:**
- [ ] How to distinguish tweets vs posts? (Icons, badges?)
- [ ] Truncation for long posts?
- [ ] Link to original post?

#### 2.2 User Flow

**Flow: View Sentiment → Analyze → Track**

1. **Navigate to Sentiment Page**
   - User sees: Search bar for symbols
   - Action: Enter symbol (e.g., AAPL)
   - Result: Sentiment overview for AAPL

2. **Analyze Sentiment**
   - User sees: Sentiment gauge, history chart, social feed
   - Action: Read tweets/posts, check trend
   - Result: Informed trading decision

3. **Track Asset**
   - User sees: "Add to Watchlist" button
   - Action: Click to add
   - Result: Asset added to watchlist, sentiment alerts enabled

---

### Task 3: C-030 Broker Integration UI Design (3h)

**Deliverables:**
1. **Page Layout Mockup** (Figma/Sketch)
2. **Component Specifications** (broker connection, live trading UI)
3. **User Flow Diagram** (connect broker → execute live trade)
4. **Warning Modal Designs** (test vs live trading)

#### 3.1 Broker Connection Page Layout

**Layout Structure:**
```
┌─────────────────────────────────────────────────────────────┐
│  Connect Broker Account                                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────┐            │
│  │  Select Broker                             │            │
│  │  [Alpaca] [Interactive Brokers] [TD Ameritrade]│      │
│  └────────────────────────────────────────────┘            │
│                                                              │
│  ┌────────────────────────────────────────────┐            │
│  │  Enter API Credentials                     │            │
│  │                                            │            │
│  │  API Key:    [________________]            │            │
│  │  API Secret: [________________]            │            │
│  │                                            │            │
│  │  ☐ Test Account (recommended)             │            │
│  │  ☐ Live Account (⚠️ Real money)           │            │
│  │                                            │            │
│  │  [Connect Broker]                          │            │
│  └────────────────────────────────────────────┘            │
│                                                              │
│  ℹ️  Why connect? Execute real trades, sync positions       │
└─────────────────────────────────────────────────────────────┘
```

**Design Questions:**
- [ ] How to show test vs live account distinction? (Prominent warning)
- [ ] API key input masking?
- [ ] Broker logo/images?

#### 3.2 Live Trading Interface

**Layout:** Similar to paper trading, but with broker account selector

**Additions:**
- Broker account selector (if multiple)
- "Live Trading" badge (prominent)
- Real money warning

**Design Questions:**
- [ ] How to distinguish paper vs live trading UI? (Color, badges?)
- [ ] Confirmation modal for live trades? (More prominent than paper)

---

### Task 4: Design System Documentation (2h)

**Deliverables:**
1. **Update `docs/design/DESIGN_SYSTEM.md`** with minimalistic brutalism
2. **Create component library documentation** (buttons, cards, tables)
3. **Create spacing/typography guidelines**

#### 4.1 Design System Updates

**Add to `docs/design/DESIGN_SYSTEM.md`:**

```markdown
# Minimalistic Brutalism Design System

## Principles
1. **Brutalist Foundation:** `rounded-none` everywhere
2. **Tiered Border Widths:**
   - Landing: `border-4` (bold)
   - Dashboard: `border-2` (standard)
   - Trading: `border-1` (subtle, data-dense)
3. **Color Palette:** High contrast, data-first

## Components

### Buttons
- Base: `rounded-none` (brutalist)
- Landing: `border-4 bg-primary text-primary-foreground`
- Dashboard: `border-2 bg-primary text-primary-foreground`
- Trading: `border-1 bg-primary text-primary-foreground`

### Cards
- Base: `rounded-none border-2`
- Elevation: Minimal (no shadows or very subtle)

### Tables
- Base: `rounded-none`
- Borders: `border-1` for data-dense interfaces
- Row hover: Subtle background color change
```

#### 4.2 Component Specifications

**For each component, specify:**
- Border width
- Border color
- Background color
- Text color
- Spacing (padding, margin)
- Hover states
- Focus states
- Disabled states
- Loading states
- Error states

**Components to spec:**
- [ ] Buttons (all variants)
- [ ] Cards
- [ ] Forms (inputs, selects, toggles)
- [ ] Tables
- [ ] Badges
- [ ] Modals
- [ ] Alerts/Notifications

---

## ✅ ACCEPTANCE CRITERIA

Your design work is complete when:

### C-036 Paper Trading
- [ ] Page layout mockup created (Figma/Sketch)
- [ ] All components designed (Portfolio Summary, Order Form, Position List, Performance Chart)
- [ ] User flow diagram created
- [ ] Responsive designs (desktop, tablet, mobile)
- [ ] Design specifications documented
- [ ] Design review with Turing completed

### C-037 Social Sentiment
- [ ] Page layout mockup created
- [ ] All components designed (Sentiment Gauge, History Chart, Trending Assets, Social Feed)
- [ ] User flow diagram created
- [ ] Responsive designs
- [ ] Design specifications documented
- [ ] Design review with Turing completed

### C-030 Broker Integration
- [ ] Page layout mockups created (Broker Connection, Live Trading)
- [ ] Warning modals designed
- [ ] User flow diagram created
- [ ] Responsive designs
- [ ] Design specifications documented
- [ ] Design review with Turing completed

### Design System
- [ ] `docs/design/DESIGN_SYSTEM.md` updated with minimalistic brutalism
- [ ] Component specifications documented
- [ ] Spacing/typography guidelines created
- [ ] Color palette documented
- [ ] Accessibility guidelines included (WCAG 2.1 Level AA)

---

## 📊 SUCCESS METRICS

### Design Metrics
- **Design Consistency:** 100% of components follow minimalistic brutalism
- **Component Coverage:** All UI components designed
- **Responsive Coverage:** All pages designed for 3 screen sizes
- **Accessibility:** All designs meet WCAG 2.1 Level AA

### Collaboration Metrics
- **Developer Handoff:** 100% of specifications clear to Turing
- **Design Review:** All designs reviewed with Turing before development
- **Iteration:** < 3 rounds of design revisions per feature

---

## 🚀 NEXT STEPS

### Immediate (Today)
1. **Set up Figma file** for Phase 1 designs
2. **Create wireframes** for paper trading page
3. **Review design direction** (minimalistic brutalism)
4. **Coordinate with Turing:** Schedule design review

### This Week
1. **Complete C-036 designs** (all components, user flows)
2. **Complete C-037 designs** (all components, user flows)
3. **Complete C-030 designs** (all components, user flows)
4. **Update design system documentation**

### Next Week
1. **Design review with Turing** for all 3 features
2. **Incorporate feedback** from developers
3. **Finalize designs** and hand off to Turing
4. **Support development** (answer questions, provide assets)

---

## 📞 COMMUNICATION

**Daily Check-ins:**
- Turing: Design questions, implementation feedback
- GAUDÍ: Design direction, strategic alignment

**Weekly Updates:**
- Report design progress to GAUDÍ (Architect)
- Flag blockers immediately

**Design Reviews:**
- Schedule 1-hour design review with Turing for each feature
- Get feedback on feasibility, implementation complexity
- Iterate based on feedback

---

## 🎨 DESIGN TOOLS

### Primary Tools
- **Figma:** UI design, prototyping, collaboration
- **Sketch:** Alternative to Figma (if preferred)

### Component Libraries
- **shadcn/ui:** Base component library (we're using this)
- **Recharts:** Charting library (performance charts, sentiment history)

### Design Resources
- `docs/design/DESIGN_SYSTEM.md` (existing)
- `docs/design/COMPONENT_USAGE_AUDIT.md` (existing)
- `tasks/architect/DECISION_DESIGN_DIRECTION.md` (revised brutalist direction)

---

**Status:** ✅ Task Assigned
**Timeline:** Start immediately, before development
**Collaborators:** Turing, GAUDÍ

---

🎨 *MIES - UI/UX Designer*

✏️ *Focus: Phase 1 UI/UX Design*

*"Design is not just what it looks like and feels like. Design is how it works." - Steve Jobs*
