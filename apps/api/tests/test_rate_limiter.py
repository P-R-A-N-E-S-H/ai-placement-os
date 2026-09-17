import time
import pytest
from app.core.rate_limiter import SlidingWindowRateLimiter


def test_sliding_window_rate_limiter_allows_under_threshold():
    """Verify rate limiter permits requests within capacity."""
    limiter = SlidingWindowRateLimiter(requests_per_minute=5)
    key = "test_user_ip_1"
    limiter.reset_key(key)

    for i in range(5):
        allowed, remaining, reset_sec = limiter.is_allowed(key)
        assert allowed is True
        assert remaining == 5 - (i + 1)
        assert reset_sec > 0.0


def test_sliding_window_rate_limiter_blocks_above_threshold():
    """Verify rate limiter blocks when threshold is exceeded."""
    limiter = SlidingWindowRateLimiter(requests_per_minute=3)
    key = "test_user_ip_2"
    limiter.reset_key(key)

    # 3 allowed requests
    for _ in range(3):
        allowed, _, _ = limiter.is_allowed(key)
        assert allowed is True

    # 4th request must be rejected
    allowed, remaining, reset_sec = limiter.is_allowed(key)
    assert allowed is False
    assert remaining == 0
    assert reset_sec > 0.0
