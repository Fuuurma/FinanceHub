# Paper Trading API Documentation

**For:** Turing (Frontend Developer)
**By:** Linus (Backend Developer)
**Date:** February 1, 2026

---

## Overview

The Paper Trading API provides endpoints for managing virtual trading portfolios, executing orders, and tracking performance. All endpoints require JWT authentication via `Authorization: Bearer <token>` header.

**Base URL:** `/api/paper-trading/`

---

## Endpoints

### 1. Get Account Summary

**GET** `/api/paper-trading/account`

**Response:**
```json
{
  "account": {
    "cash_balance": 100000.00,
    "starting_balance": 100000.00,
    "total_trades": 15,
    "win_rate": 60.0,
    "reset_count": 0
  },
  "summary": {
    "cash_balance": 100000.00,
    "portfolio_value": 12500.00,
    "total_value": 112500.00,
    "total_return": 12.5,
    "positions": [],
    "total_trades": 15,
    "win_rate": 60.0,
    "winning_trades": 9,
    "losing_trades": 6
  }
}
```

---

### 2. List Positions

**GET** `/api/paper-trading/positions`

**Response:**
```json
[
  {
    "id": "uuid-string",
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "quantity": 10,
    "avg_price": 150.00,
    "current_price": 175.00,
    "market_value": 1750.00,
    "pl": 250.00,
    "pl_percent": 16.67
  },
  {
    "id": "uuid-string",
    "symbol": "GOOGL",
    "name": "Alphabet Inc.",
    "quantity": 5,
    "avg_price": 2800.00,
    "current_price": 2950.00,
    "market_value": 14750.00,
    "pl": 750.00,
    "pl_percent": 5.36
  }
]
```

---

### 3. List Orders

**GET** `/api/paper-trading/orders?limit=100`

**Response:**
```json
[
  {
    "id": "uuid-string",
    "symbol": "AAPL",
    "order_type": "market",
    "side": "buy",
    "quantity": 10,
    "price": null,
    "stop_price": null,
    "filled_price": 175.50,
    "status": "filled",
    "created_at": "2026-02-01T10:30:00Z",
    "filled_at": "2026-02-01T10:30:01Z"
  },
  {
    "id": "uuid-string",
    "symbol": "MSFT",
    "order_type": "limit",
    "side": "buy",
    "quantity": 5,
    "price": 380.00,
    "stop_price": null,
    "filled_price": null,
    "status": "pending",
    "created_at": "2026-02-01T11:00:00Z",
    "filled_at": null
  }
]
```

---

### 4. Execute Market Order

**POST** `/api/paper-trading/orders/market`

**Request Body:**
```json
{
  "asset": "AAPL",
  "order_type": "market",
  "side": "buy",
  "quantity": 10
}
```

**Success Response (200):**
```json
{
  "success": true,
  "trade_id": "uuid-string",
  "asset": "AAPL",
  "quantity": 10,
  "price": 175.50,
  "total_value": 1755.00,
  "remaining_cash": 98245.00
}
```

**Error Response (400):**
```json
{
  "success": false,
  "error": "Insufficient funds" | "Quantity must be positive" | "Price not available"
}
```

---

### 5. Execute Limit Order

**POST** `/api/paper-trading/orders/limit`

**Request Body:**
```json
{
  "asset": "AAPL",
  "side": "buy",
  "quantity": 5,
  "price": 170.00
}
```

**Success Response (200):**
```json
{
  "success": true,
  "trade_id": "uuid-string",
  "asset": "AAPL",
  "quantity": 5,
  "price": 170.00,
  "total_value": null,
  "profit_loss": null,
  "remaining_cash": 100000.00
}
```

**Note:** Limit orders are created with `pending` status and will be executed when the market price reaches the limit price.

---

### 6. Cancel Order

**POST** `/api/paper-trading/orders/{order_id}/cancel`

**Success Response (200):**
```json
{
  "success": true,
  "message": "Order cancelled successfully"
}
```

**Error Response (400):**
```json
{
  "success": false,
  "message": "Order not found or cannot be cancelled"
}
```

---

### 7. Execute Buy Order (Legacy)

**POST** `/api/paper-trading/buy`

**Request Body:**
```json
{
  "asset": "AAPL",
  "quantity": 10
}
```

---

### 8. Execute Sell Order (Legacy)

**POST** `/api/paper-trading/sell`

**Request Body:**
```json
{
  "asset": "AAPL",
  "quantity": 5
}
```

**Success Response (200):**
```json
{
  "success": true,
  "trade_id": "uuid-string",
  "asset": "AAPL",
  "quantity": 5,
  "price": 178.00,
  "total_value": 890.00,
  "profit_loss": 125.00,
  "remaining_cash": 99135.00
}
```

---

### 9. Get Trade History

**GET** `/api/paper-trading/history?limit=100`

**Response:**
```json
{
  "trades": [
    {
      "id": "uuid-string",
      "asset": "AAPL",
      "type": "BUY",
      "quantity": 10,
      "price": 175.50,
      "total_value": 1755.00,
      "executed_at": "2026-02-01T10:30:00Z",
      "profit_loss": null
    }
  ]
}
```

---

### 10. Get Performance

**GET** `/api/paper-trading/performance`

**Response:**
```json
{
  "total_return": 12.5,
  "win_rate": 60.0,
  "total_trades": 15,
  "winning_trades": 9,
  "losing_trades": 6
}
```

---

### 11. Reset Portfolio

**POST** `/api/paper-trading/reset` (Legacy)
**POST** `/api/paper-trading/portfolio/reset` (New)

**Response:**
```json
{
  "success": true,
  "message": "Account reset successfully",
  "new_balance": 100000.00
}
```

**Warning:** This will delete all positions and orders!

---

## WebSocket Connection

**Endpoint:** `ws://localhost:8000/ws/paper-trading/`

**Authentication:** Include JWT token in query string or cookies.

**Message Format:**
```json
{
  "type": "portfolio_update",
  "data": {
    "cash_balance": 100000.00,
    "portfolio_value": 12500.00,
    "total_return": 12.5
  }
}
```

**Event Types:**
- `portfolio_update` - Portfolio value changed
- `order_update` - Order status changed
- `position_update` - Position changed

**Example Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/paper-trading/');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message.type, message.data);
};
```

---

## Order Status Values

| Status | Description |
|--------|-------------|
| `pending` | Order created but not yet filled |
| `filled` | Order successfully executed |
| `cancelled` | Order was cancelled by user |
| `rejected` | Order rejected (insufficient funds, etc.) |

---

## Order Types

| Type | Description |
|------|-------------|
| `market` | Execute immediately at current market price |
| `limit` | Execute only when price reaches specified limit |
| `stop` | Trigger market order when stop price is reached |

---

## Error Codes

| Error | HTTP Status | Description |
|-------|-------------|-------------|
| `Asset not found` | 400 | Symbol doesn't exist |
| `Insufficient funds` | 400 | Not enough cash |
| `Insufficient position` | 400 | Not enough shares to sell |
| `Price not available` | 400 | Can't get current price |
| `Quantity must be positive` | 400 | Invalid quantity |
| `Order not found` | 404 | Order ID doesn't exist |
| `Only pending orders can be cancelled` | 400 | Can't cancel filled order |

---

## Frontend Integration Notes

1. **Auto-create account:** Calling `/account` will automatically create a paper trading account if one doesn't exist.

2. **Real-time updates:** Connect to WebSocket to receive instant updates when orders execute or positions change.

3. **Decimal precision:** All monetary values use 2 decimal places, quantities use 4 decimal places (for fractional shares/crypto).

4. **Authentication:** Use JWT from `ninja-jwt` library for authentication.

5. **Rate limiting:** No specific rate limits yet, but be reasonable with requests.

---

## Code References

| Component | File Path |
|-----------|-----------|
| API Views | `apps/backend/src/trading/api/paper_trading.py` |
| Engine | `apps/backend/src/trading/services/paper_trading_engine.py` |
| Models | `apps/backend/src/trading/models/` |
| WebSocket | `apps/backend/src/trading/consumers/paper_trading.py` |

---

**Questions?** Check COMMUNICATION_HUB.md or message Linus directly.
