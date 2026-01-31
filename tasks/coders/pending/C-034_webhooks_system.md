# #️⃣ TASK: C-034 - Webhooks System

**Task ID:** C-034
**Created:** February 1, 2026
**Assigned To:** Backend Coder (Guido)
**Status:** ⏳ PENDING
**Priority:** P2 MEDIUM
**Estimated Time:** 12-16 hours
**Deadline:** February 28, 2026 5:00 PM

---

## 🎯 OBJECTIVE

Create a webhooks system that allows users to receive real-time notifications:
- Price alerts delivered to external endpoints
- Portfolio change notifications
- Trading signals
- Custom event triggers
- Webhook authentication and retry logic

---

## 📋 REQUIREMENTS

### 1. Webhook Models

```python
# apps/backend/src/notifications/models/webhooks.py
class Webhook(models.Model):
    user = ForeignKey(User, on_delete=models.CASCADE)
    name = CharField()  # e.g., "My Discord Bot"
    url = URLField()  # Endpoint to POST to
    secret = CharField(max_length=64)  # For HMAC signature
    events = JSONField()  # List of events to subscribe to
    is_active = BooleanField(default=True)
    last_triggered = DateTimeField(null=True)
    success_count = IntegerField(default=0)
    failure_count = IntegerField(default=0)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

class WebhookEvent(models.Model):
    webhook = ForeignKey(Webhook)
    event_type = CharField()  # 'price_alert', 'portfolio_change', etc.
    payload = JSONField()
    status_code = IntegerField(null=True)
    response_body = TextField(blank=True)
    success = BooleanField()
    attempts = IntegerField(default=0)
    created_at = DateTimeField(auto_now_add=True)

class WebhookEventType(models.TextChoices):
    PRICE_ABOVE = 'price_above', 'Price Above Target'
    PRICE_BELOW = 'price_below', 'Price Below Target'
    PORTFOLIO_CHANGE = 'portfolio_change', 'Portfolio Value Change'
    POSITION_ADDED = 'position_added', 'Position Added'
    POSITION_REMOVED = 'position_removed', 'Position Removed'
    DIVIDEND_PAYMENT = 'dividend_payment', 'Dividend Payment'
    TRADE_EXECUTED = 'trade_executed', 'Trade Executed'
    CUSTOM = 'custom', 'Custom Event'
```

### 2. Webhook Service

```python
# apps/backend/src/notifications/services/webhook_service.py
import requests
import hmac
import hashlib
import json
from datetime import datetime

class WebhookService:
    def register_webhook(self, user_id: int, name: str, url: str,
                        events: List[str]) -> Webhook:
        """
        Create new webhook subscription
        Generate secret for HMAC signature
        """
        secret = self._generate_secret()
        webhook = Webhook.objects.create(
            user_id=user_id,
            name=name,
            url=url,
            secret=secret,
            events=events
        )
        return webhook

    def trigger_event(self, event_type: str, payload: dict):
        """
        Trigger webhook event:
        - Find all webhooks subscribed to this event
        - Send POST request to each webhook URL
        - Include HMAC signature for verification
        - Retry on failure
        - Log attempts
        """
        webhooks = Webhook.objects.filter(
            is_active=True,
            events__contains=event_type
        )

        for webhook in webhooks:
            self._send_webhook(webhook, event_type, payload)

    def _send_webhook(self, webhook: Webhook, event_type: str, payload: dict):
        """
        Send webhook with retry logic:
        - Attempt 1: Immediate
        - Attempt 2: 1 minute later
        - Attempt 3: 5 minutes later
        """
        signature = self._generate_signature(webhook.secret, payload)

        headers = {
            'Content-Type': 'application/json',
            'X-Webhook-Signature': signature,
            'X-Webhook-Event': event_type,
            'X-Webhook-Timestamp': str(int(datetime.now().timestamp())),
            'X-Webhook-ID': str(uuid.uuid4())
        }

        for attempt in range(3):
            try:
                response = requests.post(
                    webhook.url,
                    json=payload,
                    headers=headers,
                    timeout=10
                )

                # Log event
                WebhookEvent.objects.create(
                    webhook=webhook,
                    event_type=event_type,
                    payload=payload,
                    status_code=response.status_code,
                    success=response.status_code == 200,
                    attempts=attempt + 1
                )

                if response.status_code == 200:
                    webhook.success_count += 1
                    webhook.last_triggered = datetime.now()
                    webhook.save()
                    return True

            except Exception as e:
                if attempt == 2:  # Last attempt failed
                    webhook.failure_count += 1
                    webhook.save()

        return False

    def _generate_signature(self, secret: str, payload: dict) -> str:
        """Generate HMAC SHA256 signature"""
        message = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"

    def _generate_secret(self) -> str:
        """Generate random secret for webhook"""
        import secrets
        return secrets.token_urlsafe(32)

    def test_webhook(self, webhook_id: int):
        """
        Send test event to webhook
        Useful for user to verify setup
        """
        webhook = Webhook.objects.get(id=webhook_id)
        test_payload = {
            'test': True,
            'message': 'Webhook configuration verified',
            'timestamp': datetime.now().isoformat()
        }
        return self._send_webhook(webhook, 'test', test_payload)

    def get_webhook_logs(self, webhook_id: int, limit: int = 50):
        """Get recent webhook delivery logs"""
        return WebhookEvent.objects.filter(
            webhook_id=webhook_id
        ).order_by('-created_at')[:limit]
```

### 3. API Endpoints

```python
# apps/backend/src/notifications/api/webhooks.py
from ninja import Router

router = Router()

@router.post("/webhooks")
def create_webhook(request, name: str, url: str, events: List[str]):
    """Create new webhook subscription"""
    pass

@router.get("/webhooks")
def list_webhooks(request):
    """List user's webhooks"""
    pass

@router.get("/webhooks/{webhook_id}")
def get_webhook(request, webhook_id: int):
    """Get webhook details"""
    pass

@router.put("/webhooks/{webhook_id}")
def update_webhook(request, webhook_id: int, **kwargs):
    """Update webhook configuration"""
    pass

@router.delete("/webhooks/{webhook_id}")
def delete_webhook(request, webhook_id: int):
    """Delete webhook"""
    pass

@router.post("/webhooks/{webhook_id}/test")
def test_webhook(request, webhook_id: int):
    """Send test event to webhook"""
    pass

@router.get("/webhooks/{webhook_id}/logs")
def get_webhook_logs(request, webhook_id: int):
    """Get webhook delivery logs"""
    pass

@router.get("/webhooks/events")
def list_available_events(request):
    """List available webhook event types"""
    return {
        'events': [
            {'value': 'price_above', 'label': 'Price Above Target'},
            {'value': 'price_below', 'label': 'Price Below Target'},
            {'value': 'portfolio_change', 'label': 'Portfolio Value Change'},
            # ... more events
        ]
    }
```

### 4. Frontend Components

```typescript
// apps/frontend/src/components/webhooks/WebhookList.tsx
export function WebhookList() {
  // List all webhooks
  // Show status (active/inactive)
  // Show success/failure counts
  // Create new webhook button
  // Test webhook button
  // View logs button
}

// apps/frontend/src/components/webhooks/WebhookForm.tsx
export function WebhookForm({ webhook }: Props) {
  // Name input
  // URL input
  // Event type multi-select
  // Secret display (masked)
  // Active toggle
  // Save button
}

// apps/frontend/src/components/webhooks/WebhookLogs.tsx
export function WebhookLogs({ webhookId }: Props) {
  // Table of webhook delivery attempts
  // Show status code, success/failure
  // Show payload (collapsible)
  - Show timestamp
  - Retry failed webhooks
}

// apps/frontend/src/components/webhooks/WebhookTestDialog.tsx
export function WebhookTestDialog({ webhookId }: Props) {
  // Send test event
  - Show response status
  // Display response body
}
```

### 5. Event Triggers

**Integrate with existing systems:**

```python
# Price Alert Trigger
def on_price_alert(alert: PriceAlert):
    if alert.condition_met:
        WebhookService().trigger_event('price_alert', {
            'symbol': alert.symbol,
            'price': alert.current_price,
            'target': alert.target_price,
            'condition': alert.condition,
            'timestamp': alert.triggered_at.isoformat()
        })

# Portfolio Change Trigger
def on_portfolio_value_change(portfolio: Portfolio):
    WebhookService().trigger_event('portfolio_change', {
        'portfolio_id': portfolio.id,
        'portfolio_name': portfolio.name,
        'previous_value': str(portfolio.previous_value),
        'current_value': str(portfolio.current_value),
        'change_percent': str(portfolio.change_percent),
        'timestamp': datetime.now().isoformat()
    })

# Trade Execution Trigger
def on_trade_executed(trade: Trade):
    WebhookService().trigger_event('trade_executed', {
        'symbol': trade.symbol,
        'side': trade.side,
        'quantity': str(trade.quantity),
        'price': str(trade.price),
        'timestamp': trade.executed_at.isoformat()
    })
```

---

## ✅ ACCEPTANCE CRITERIA

- [ ] Create webhook subscription with URL and events
- [ ] Generate secret for HMAC signature
- [ ] Send POST request to webhook URL on event trigger
- [ ] Include HMAC SHA256 signature in headers
- [ ] Retry failed webhooks (3 attempts with backoff)
- [ ] Log all webhook delivery attempts
- [ ] Test webhook functionality
- [ ] View webhook delivery logs
- [ ] Success/failure tracking
- [ ] Multiple event type subscriptions
- [ ] Webhook authentication verification
- [ ] API endpoints for all operations
- [ ] Frontend webhook management UI
- [ ] Tests for webhook service
- [ ] Rate limiting (prevent webhook spam)

---

## 📁 FILES TO CREATE/MODIFY

### Create:
- `apps/backend/src/notifications/models/webhooks.py`
- `apps/backend/src/notifications/services/webhook_service.py`
- `apps/backend/src/notifications/api/webhooks.py`
- `apps/backend/src/notifications/tests/test_webhooks.py`
- `apps/frontend/src/components/webhooks/WebhookList.tsx`
- `apps/frontend/src/components/webhooks/WebhookForm.tsx`
- `apps/frontend/src/components/webhooks/WebhookLogs.tsx`
- `apps/frontend/src/components/webhooks/WebhookTestDialog.tsx`

---

## 🔗 DEPENDENCIES

**Prerequisites:**
- User authentication
- Alerts system (for price alerts)
- Portfolio tracking

**Related Tasks:**
- None (standalone feature)

---

## 🔒 SECURITY CONSIDERATIONS

**Charo (Security) must review:**
- Webhook URL validation (prevent SSRF)
- Secret storage and generation
- Rate limiting per webhook
- HTTPS requirement for webhook URLs
- HMAC signature verification
- Payload size limits
- Timeout handling
- User notification on repeated failures

---

## 📊 WEBHOOK PAYLOAD FORMAT

**Standard Payload Structure:**
```json
{
  "id": "evt_abc123",
  "event": "price_alert",
  "timestamp": "2026-02-01T10:30:00Z",
  "data": {
    "symbol": "AAPL",
    "price": 185.50,
    "target": 180.00,
    "condition": "above"
  },
  "signature": "sha256=abc123..."
}
```

**Headers:**
```
Content-Type: application/json
X-Webhook-Signature: sha256=abc123...
X-Webhook-Event: price_alert
X-Webhook-Timestamp: 1738384200
X-Webhook-ID: evt_abc123
```

---

## 📊 DELIVERABLES

1. **Models:** Webhook, WebhookEvent
2. **Service:** WebhookService with signature, retry, logging
3. **API:** CRUD operations for webhooks
4. **Frontend:** Webhook management UI
5. **Integration:** Event triggers in existing systems
6. **Tests:** Unit tests for service
7. **Documentation:** Webhook guide for users

---

## 💬 NOTES

**Implementation Approach:**
- Use `requests` library for HTTP calls
- Background task queue (Dramatiq) for async webhook delivery
- Store webhook logs for 30 days
- Disable webhooks after 10 consecutive failures
- Notify users of webhook failures

**Common Use Cases:**
- **Discord:** Send price alerts to Discord channel
- **Slack:** Portfolio updates to Slack
- **Telegram:** Trade signals to Telegram bot
- **Custom Apps:** Push notifications to custom app
- **Trading Bots:** Trigger automated trades

**Rate Limiting:**
- Max 100 webhooks per user
- Max 10 events per minute per webhook
- Retry with exponential backoff (1m, 5m, 15m)

**Libraries:**
- Backend: `requests`, `hmac` (built-in)
- Frontend: None (standard forms)

---

**Status:** ⏳ READY TO START
**Assigned To:** Backend Coder (Guido)
**User Value:** MEDIUM - power users want external integrations

---

#️⃣ *C-034: Webhooks System*
*Real-time notifications to external endpoints - Discord, Slack, custom apps*
