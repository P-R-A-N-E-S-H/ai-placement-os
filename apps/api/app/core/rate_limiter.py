from __future__ import annotations

import time
from typing import Dict, List, Optional, Tuple
from fastapi import HTTPException, Request, status


class SlidingWindowRateLimiter:
    """Thread-safe in-memory sliding window rate limiter."""

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.window_seconds = 60.0
        self._history: Dict[str, List[float]] = {}

    def is_allowed(self, key: str) -> Tuple[bool, int, float]:
        """
        Check if request is allowed under the sliding window limit.
        Returns: (is_allowed, remaining_requests, reset_seconds)
        """
        now = time.time()
        window_start = now - self.window_seconds

        if key not in self._history:
            self._history[key] = []

        # Filter out timestamps older than the sliding window
        valid_timestamps = [t for t in self._history[key] if t > window_start]
        self._history[key] = valid_timestamps

        current_count = len(valid_timestamps)
        if current_count < self.requests_per_minute:
            self._history[key].append(now)
            remaining = self.requests_per_minute - (current_count + 1)
            reset_seconds = max(1.0, (valid_timestamps[0] + self.window_seconds - now) if valid_timestamps else 60.0)
            return True, remaining, round(reset_seconds, 1)

        # Rate limit exceeded
        oldest_ts = valid_timestamps[0]
        reset_seconds = max(1.0, oldest_ts + self.window_seconds - now)
        return False, 0, round(reset_seconds, 1)

    def reset_key(self, key: str) -> None:
        """Reset history for a specific key (useful for unit tests)."""
        self._history.pop(key, None)


# Default global rate limiters
global_rate_limiter = SlidingWindowRateLimiter(requests_per_minute=120)
auth_rate_limiter = SlidingWindowRateLimiter(requests_per_minute=20)
sandbox_rate_limiter = SlidingWindowRateLimiter(requests_per_minute=30)


class RateLimitDependency:
    """FastAPI dependency for rate limiting specific route handlers."""

    def __init__(self, requests_per_minute: int = 60):
        self.limiter = SlidingWindowRateLimiter(requests_per_minute=requests_per_minute)

    async def __call__(self, request: Request):
        # Extract client identifier: X-Forwarded-For, client host, or generic
        client_ip = request.headers.get("x-forwarded-for") or (request.client.host if request.client else "unknown_ip")
        key = f"{client_ip}:{request.url.path}"

        allowed, remaining, reset_time = self.limiter.is_allowed(key)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Please retry in {reset_time} seconds.",
                headers={
                    "X-RateLimit-Limit": str(self.limiter.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(reset_time)),
                    "Retry-After": str(int(reset_time)),
                },
            )
        return True
