import time
import asyncio

class ExpiringCache:
    """
    A simple short-lived cache to prevent processing duplicate messages or challenges.
    """
    def __init__(self, ttl: float = 3600.0):
        self.cache: dict[str, float] = {}
        self.ttl = ttl
        self._lock = asyncio.Lock()

    async def add(self, key: str):
        async with self._lock:
            self.cache[key] = time.time()
            self._cleanup()

    async def contains(self, key: str) -> bool:
        async with self._lock:
            self._cleanup()
            return key in self.cache

    def _cleanup(self):
        now = time.time()
        self.cache = {k: v for k, v in self.cache.items() if now - v < self.ttl}

# Global instance for tracking processed challenges
message_cache = ExpiringCache(ttl=3600)
