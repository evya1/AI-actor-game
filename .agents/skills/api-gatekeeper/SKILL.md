---
name: api-gatekeeper
description: Implement centralized API gatekeeper with rate limiting, queuing, retry logic, and monitoring. All external API calls must flow through this gatekeeper. Use when making external API calls or managing rate limits.
---

# API Gatekeeper & Rate Limiting

All external API calls must go through a centralized gatekeeper that handles rate limiting, queuing, retries, and monitoring.

## Gatekeeper Requirements

- No direct API calls that bypass the gatekeeper
- Rate limits enforced before every call
- Overflow requests queued (never rejected or crashed)
- All calls logged for monitoring

## Gatekeeper Interface

```python
class ApiGatekeeper:
    """Centralized API call manager."""

    def __init__(self, config: RateLimitConfig):
        """Initialize with rate limit config."""
        ...

    def execute(self, api_call, *args, **kwargs):
        """Execute API call through gatekeeper.
        - Check rate limits before execution
        - Queue if limit reached
        - Retry on transient failures
        - Log all calls
        """
        ...

    def get_queue_status(self) -> QueueStatus:
        """Return queue depth and stats."""
        ...
```

## Rate Limit Configuration

All rate limits must come from configuration files, never hardcoded:

```json
{
  "rate_limits": {
    "version": "1.00",
    "services": {
      "default": {
        "requests_per_minute": 30,
        "requests_per_hour": 500,
        "concurrent_max": 5,
        "retry_after_seconds": 30,
        "max_retries": 3
      }
    }
  }
}
```

## Queue Management

When rate limits are reached, the gatekeeper must queue requests instead of rejecting them:

- FIFO queue for pending requests
- Maximum queue depth defined in configuration
- Backpressure alert when queue is full
- Drain mechanism that processes requests when rate windows reset

## Implementation Checklist

1. Create `src/<package>/shared/gatekeeper.py` with `ApiGatekeeper` class
2. Load rate limits from `config/rate_limits.json`
3. All external API calls go through `gatekeeper.execute()`
4. Implement FIFO queue for overflow
5. Add retry logic with configurable max retries
6. Log all API calls with timestamps
7. Implement backpressure when queue is full
8. Provide `get_queue_status()` for monitoring
