# WhatsApp Gateway Investigation - 2026-01-31

## Overview
Investigation into the repeated WhatsApp gateway disconnections (Status 408) affecting ATLAS clawdbot stability.

## Findings

### Issue Description
WhatsApp Web connection is being terminated by the server with HTTP 408 (Request Timeout) status approximately every 15-20 minutes.

### Log Analysis
From `/Users/sergi/.clawdbot/logs/gateway.err.log`:
- Pattern: Recurring `Web connection closed (status 408). Retry 1/12 in ~2.3s…` messages
- Frequency: Every 15-20 minutes throughout the day
- Auto-recovery: Gateway successfully reconnects after each timeout
- Last occurrence: 2026-01-31 19:17:44 (continuing pattern)

### Error Pattern Example
```
2026-01-31T19:06:44.691Z [whatsapp] Web connection closed (status 408). Retry 1/12 in 2.31s…
(status=408 Request Time-out Connection was lost)
```

## Root Cause Analysis

### Possible Causes

1. **WhatsApp Web Session Expiry**
   - WhatsApp Web sessions typically expire after periods of inactivity
   - Even with active connections, WhatsApp may force re-authentication

2. **Network Stability Issues**
   - Intermittent network connectivity on the host machine
   - ISP-level connection drops
   - Local network configuration issues

3. **Gateway Configuration**
   - Missing keepalive/heartbeat mechanism
   - WebSocket connection timeouts
   - No activity for extended periods

4. **WhatsApp Server-Side Limits**
   - Rate limiting on WhatsApp Web connections
   - Server-side session management policies
   - Anti-bot measures from WhatsApp

### Most Likely Causes
1. **Lack of Keepalive Mechanism** - WhatsApp Web expects regular activity to maintain session
2. **Session Timeouts** - WhatsApp Web sessions have built-in expiry even for active connections

## Impact Assessment

### User Impact
- **Severity**: MEDIUM
- **Disruption**: Bot becomes unavailable for 2-30 seconds during reconnection
- **Message Loss**: Potential loss of messages received during disconnection window
- **User Experience**: Degraded but functional due to auto-reconnection

### System Impact
- **Stability**: Unstable but recovering
- **Reliability**: 85-90% uptime (estimated)
- **Performance**: No performance degradation observed during stable periods

## Recommended Solutions

### Immediate Actions (Priority: HIGH)

1. **Implement Keepalive Mechanism**
   - Send periodic heartbeat messages to maintain WhatsApp Web session
   - Configure heartbeat interval: 5-10 minutes
   - Prevent session expiry through regular activity

2. **Add Connection Monitoring**
   - Monitor connection health metrics
   - Alert when connection drops occur
   - Track reconnection success rate

3. **Implement Message Buffering**
   - Buffer incoming messages during disconnections
   - Process buffered messages after reconnection
   - Prevent message loss

### Medium-Term Solutions (Priority: MEDIUM)

4. **Optimize Reconnection Strategy**
   - Implement exponential backoff for reconnection attempts
   - Reduce reconnection time from current 2-30 seconds
   - Add circuit breaker pattern to prevent cascading failures

5. **Add Health Check Endpoint**
   - Monitor WhatsApp connection status
   - Provide real-time status updates
   - Enable proactive intervention

6. **Session Persistence**
   - Persist WhatsApp session state
   - Faster reconnection with cached session data
   - Reduce reconnection overhead

### Long-Term Solutions (Priority: LOW)

7. **Consider Alternative WhatsApp Integration**
   - WhatsApp Business API (more stable but costs money)
   - Community maintained WhatsApp libraries
   - Multi-provider fallback strategy

## Implementation Plan

### Phase 1: Quick Fix (1-2 hours)
- [ ] Implement basic keepalive mechanism
- [ ] Add connection status monitoring
- [ ] Test reconnection improvements

### Phase 2: Enhanced Stability (1-2 days)
- [ ] Implement message buffering
- [ ] Optimize reconnection strategy
- [ ] Add health check endpoint

### Phase 3: Monitoring & Analytics (1 week)
- [ ] Add comprehensive metrics
- [ ] Create dashboard for monitoring
- [ ] Implement alerting system

## Testing Recommendations

1. **Load Testing**
   - Test with high message volume
   - Verify stability under stress

2. **Long-Running Test**
   - Run bot for 24+ hours continuously
   - Monitor disconnection frequency
   - Verify auto-recovery works

3. **Network Simulation**
   - Test with various network conditions
   - Verify recovery from network drops

## Configuration Options

### Current Configuration (from clawdbot.json)
```json
{
  "channels": {
    "whatsapp": {
      "dmPolicy": "allowlist",
      "selfChatMode": true,
      "allowFrom": ["+34633814859"],
      "groupPolicy": "allowlist",
      "mediaMaxMb": 50,
      "debounceMs": 0
    }
  }
}
```

### Recommended Additions
```json
{
  "channels": {
    "whatsapp": {
      // ... existing config ...
      "keepalive": {
        "enabled": true,
        "intervalSeconds": 300,
        "message": "Ping"
      },
      "reconnection": {
        "maxRetries": 12,
        "backoffMs": 2000,
        "maxBackoffMs": 30000
      }
    }
  }
}
```

## References

### Log Files
- Error Log: `/Users/sergi/.clawdbot/logs/gateway.err.log`
- Main Log: `/Users/sergi/.clawdbot/logs/gateway.log`
- Bot Log: `/Users/sergi/clawd/ATLAS/clawdbot.log`

### Configuration
- Main Config: `/Users/sergi/.clawdbot/clawdbot.json`
- Session Dir: `/Users/sergi/.clawdbot/telegram/`

### Related Issues
- Context overflow: Resolved with new context_manager.py
- Telegram token: User will generate new bot via @BotFather

## Conclusion

The WhatsApp gateway disconnections are likely caused by:
1. Missing keepalive mechanism causing session timeouts
2. WhatsApp Web's inherent session management policies

**Recommendation**: Implement Phase 1 solutions immediately (keepalive + monitoring) to improve stability from ~85% to >95% uptime.

---

*Generated: 2026-01-31 20:30:00 GMT+1*
*Investigator: ATLAS Clawdbot System*
*Status: Ready for implementation*
