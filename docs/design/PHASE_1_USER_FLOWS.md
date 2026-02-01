# Phase 1 User Flows

**Date:** February 1, 2026
**Author:** MIES (UI/UX Designer)
**Features:** C-036, C-037, C-030

---

## C-036: Paper Trading User Flows

### Flow 1: Create Portfolio → Execute Trade

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CREATE PORTFOLIO → EXECUTE TRADE                      │
└─────────────────────────────────────────────────────────────────────────┘

  ┌─────────────┐
  │   START     │
  │ User lands  │
  │ on Paper    │
  │ Trading     │
  │ page        │
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐     ┌─────────────┐
  │  Empty      │────▶│  Create     │
  │  State      │     │  Portfolio  │
  │  CTA:       │     │  Modal      │
  │  "Start     │     │             │
  │  Paper      │     │  - $100K    │
  │  Trading"   │     │    demo     │
  └─────────────┘     │    balance  │
                      └──────┬──────┘
                             │
                             ▼
                      ┌─────────────┐
                      │ Portfolio   │
                      │ Created     │
                      │ Success     │
                      └──────┬──────┘
                             │
                             ▼
                      ┌─────────────┐     ┌─────────────┐
                      │  Portfolio  │────▶│  Order      │
                      │  Summary    │     │  Form       │
                      │  Displayed  │     │  Ready      │
                      └─────────────┘     └──────┬──────┘
                                                 │
                                                 ▼
                      ┌─────────────┐     ┌─────────────┐
                      │  Search     │────▶│  Symbol     │
                      │  Symbol     │     │  Selected   │
                      │  "AAPL"     │     │             │
                      └─────────────┘     └──────┬──────┘
                                                 │
                                                 ▼
                      ┌─────────────┐     ┌─────────────┐
                      │  Select     │────▶│  Order      │
                      │  Buy/Sell   │     │  Details    │
                      │  "BUY"      │     │  Filled     │
                      └─────────────┘     └──────┬──────┘
                                                 │
                                                 ▼
                      ┌─────────────┐     ┌─────────────┐
                      │  Order      │────▶│  Order      │
                      │  Confirm    │     │  Executed   │
                      │  Modal      │     │             │
                      └─────────────┘     └──────┬──────┘
                                                 │
                                                 ▼
                      ┌─────────────┐     ┌─────────────┐
                      │  Portfolio  │────▶│  Position   │
                      │  Updated    │     │  Added      │
                      │             │     │  Success    │
                      └─────────────┘     └──────┬──────┘
                                                 │
                                                 ▼
                      ┌─────────────┐
                      │    END      │
                      │  Trade      │
                      │  Complete   │
                      └─────────────┘
```

### Flow 2: Close Position

```
  ┌─────────────┐
  │  Position   │     ┌─────────────┐     ┌─────────────┐
  │  Listed     │────▶│  Click      │────▶│  Confirm    │
  │             │     │  Close (✕)  │     │  Modal      │
  └─────────────┘     └─────────────┘     └──────┬──────┘
                                                 │
                    ┌────────────────────────────┤
                    │                            │
                    ▼                            ▼
            ┌─────────────┐             ┌─────────────┐
            │  Cancel     │             │  Position   │
            │             │             │  Closed     │
            └─────────────┘             │  Portfolio  │
                                        │  Updated    │
                                        └──────┬──────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │    END      │
                                        │  Position   │
                                        │  Closed     │
                                        └─────────────┘
```

---

## C-037: Social Sentiment User Flows

### Flow 1: View Sentiment → Analyze → Track

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  VIEW SENTIMENT → ANALYZE → TRACK                        │
└─────────────────────────────────────────────────────────────────────────┘

  ┌─────────────┐
  │   START     │
  │ User lands  │
  │ on          │
  │ Sentiment   │
  │ page        │
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐     ┌─────────────┐
  │  Sentiment  │────▶│  Enter      │
  │  Page       │     │  Symbol     │
  │  Load       │     │  "AAPL"     │
  └─────────────┘     └──────┬──────┘
                             │
                             ▼
                      ┌─────────────┐
                      │  Sentiment  │
                      │  Overview   │
                      │  Loaded     │
                      └──────┬──────┘
                             │
                             ▼
                      ┌─────────────┐     ┌─────────────┐
                      │  Review     │────▶│  Analyze    │
                      │  Gauge +    │     │  Chart +    │
                      │  History    │     │  Feed       │
                      └─────────────┘     └──────┬──────┘
                                                 │
                                                 ▼
                      ┌─────────────┐     ┌─────────────┐
                      │  Trading    │────▶│  Add to     │
                      │  Decision   │     │  Watchlist  │
                      │  Made       │     │             │
                      └─────────────┘     └──────┬──────┘
                                                 │
                                                 ▼
                      ┌─────────────┐
                      │  Asset      │
                      │  Tracked    │
                      │  Alerts     │
                      │  Enabled    │
                      └─────────────┘
```

### Flow 2: Browse Trending Assets

```
  ┌─────────────┐
  │  Trending   │     ┌─────────────┐     ┌─────────────┐
  │  Assets     │────▶│  Click      │────▶│  Sentiment  │
  │  List       │     │  Asset      │     │  Page       │
  │  Displayed  │     │  "AAPL"     │     │  Loaded     │
  └─────────────┘     └─────────────┘     └──────┬──────┘
                                                 │
                                                 ▼
                                          ┌─────────────┐
                                          │  Analyze    │
                                          │  Sentiment  │
                                          └──────┬──────┘
                                                 │
                                                 ▼
                                          ┌─────────────┐
                                          │  Add to     │
                                          │  Watchlist  │
                                          │  or Skip    │
                                          └─────────────┘
```

---

## C-030: Broker Integration User Flows

### Flow 1: Connect Broker Account

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      CONNECT BROKER ACCOUNT                               │
└─────────────────────────────────────────────────────────────────────────┘

  ┌─────────────┐
  │   START     │
  │ User clicks │
  │ "Connect    │
  │ Broker"     │
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐     ┌─────────────┐
  │  Broker     │────▶│  Select     │
  │  Connect    │     │  Broker     │
  │  Page       │     │  "Alpaca"   │
  └─────────────┘     └──────┬──────┘
                             │
                             ▼
                      ┌─────────────┐
                      │  Enter API  │
                      │  Credentials│
                      └──────┬──────┘
                             │
                             ▼
                      ┌─────────────┐     ┌─────────────┐
                      │  Select     │────▶│  Account    │
                      │  Account    │     │  Type       │
                      │  Type       │     │             │
                      └─────────────┘     │  - Test     │
                                         │  - Live     │
                                         └──────┬──────┘
                                                │
                                     ┌──────────┴──────────┐
                                     │                     │
                                     ▼                     ▼
                             ┌─────────────┐       ┌─────────────┐
                             │  Test       │       │  Live       │
                             │  Selected   │       │  Selected   │
                             └──────┬──────┘       └──────┬──────┘
                                    │                     │
                                    ▼                     ▼
                            ┌─────────────┐       ┌─────────────┐
                            │  Warning    │       │  WARNING    │
                            │  Modal      │       │  MODAL      │
                            │  (if test)  │       │  ⚠️ REAL    │
                            └──────┬──────┘       │  MONEY      │
                                   │              └──────┬──────┘
                                   │                     │
                                   ▼                     ▼
                            ┌─────────────┐       ┌─────────────┐
                            │  Click      │       │  Click      │
                            │  "Connect"  │       │  "I         │
                            │             │       │  Understand"│
                            └──────┬──────┘       └──────┬──────┘
                                   │                     │
                                   └──────────┬──────────┘
                                              │
                                              ▼
                                       ┌─────────────┐
                                       │  Connect    │
                                       │  Request    │
                                       │  Sent       │
                                       └──────┬──────┘
                                              │
                                              ▼
                                       ┌─────────────┐
                                       │  Success    │
                                       │  / Error    │
                                       │  Message    │
                                       └─────────────┘
```

### Flow 2: Execute Live Trade

```
  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
  │  Broker     │────▶│  Navigate   │────▶│  Live       │
  │  Connected  │     │  to Trading │     │  Trading    │
  │             │     │  Page       │     │  Interface  │
  └─────────────┘     └─────────────┘     └──────┬──────┘
                                                 │
                                                 ▼
                                          ┌─────────────┐
                                          │  Live       │
                                          │  Trading    │
                                          │  Badge      │
                                          │  Displayed  │
                                          └──────┬──────┘
                                                 │
                                                 ▼
                                          ┌─────────────┐
                                          │  Execute    │
                                          │  Live Trade │
                                          └──────┬──────┘
                                                 │
                                                 ▼
                                          ┌─────────────┐
                                          │  Enhanced   │
                                          │  Confirm    │
                                          │  Modal      │
                                          │  (⚠️ REAL   │
                                          │   MONEY)    │
                                          └──────┬──────┘
                                                 │
                                                 ▼
                                          ┌─────────────┐
                                          │  Trade      │
                                          │  Executed   │
                                          │  Success    │
                                          └─────────────┘
```

---

## State Designs

### Empty States

| Feature | Empty State Content |
|---------|---------------------|
| Paper Trading | "Start Paper Trading" CTA, $100K demo balance |
| Positions | Empty table with "No positions yet" message |
| Sentiment | Search bar with placeholder "Enter symbol (e.g., AAPL)" |
| Social Feed | "No posts yet" or filter selection message |
| Broker Connect | Broker selection grid |

### Loading States

| Feature | Loading State |
|---------|---------------|
| Paper Trading | Skeleton cards, shimmer effect |
| Sentiment | Skeleton gauge, skeleton chart |
| Social Feed | Skeleton post cards |
| Broker Connect | Spinner during connection |

### Error States

| Feature | Error State |
|---------|------------|
| Order Form | Inline error messages, red border, error toast |
| Broker Connect | Error toast with retry option |
| API Error | Full-page error with retry button |

### Success States

| Feature | Success State |
|---------|---------------|
| Order Executed | Green toast, portfolio updated |
| Position Closed | Green toast, position removed |
| Broker Connected | Success toast, dashboard updated |
| Added to Watchlist | Toast notification |

---

**"Less is more."**

*MIES - UI/UX Designer*
