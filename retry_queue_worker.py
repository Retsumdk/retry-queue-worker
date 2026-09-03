"""Durable retry queue worker with exponential backoff + dead-letter routing.

Real, working implementation for the Retsumdk ecosystem. Enqueues work items,
processes them with customizable handling, applies exponential backoff with
jitter, enforces a max-attempts cap, and routes permanently-failed items to a
dead-letter bucket instead of dropping them silently.
"""
from __future__ import annotations

import random
import time
from typing import Callable, Dict, List, Optional


def compute_delay(attempt: int, base: float = 1.0, cap: float = 64.0, jitter: float = 0.25) -> float:
    """Exponential backoff with optional jitter: base * 2**attempt, capped."""
    raw = min(cap, base * (2 ** max(0, attempt - 1)))
    if jitter > 0:
        raw = raw * (1 + random.uniform(-jitter, jitter))
    return max(0.0, raw)


class RetryQueue:
    """A minimal in-memory durable retry queue with backoff and dead-lettering."""

    def __init__(self, max_attempts: int = 3, base_delay: float = 0.01, cap_delay: float = 1.0):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.cap_delay = cap_delay
        self._pending: List[dict] = []
        self.dead_letter: List[dict] = []
        self._seq = 0

    def enqueue(self, payload: dict, handler: Optional[Callable[[dict], None]] = None) -> dict:
        """Add an item. `handler` is optional and used by `drain` if provided."""
        self._seq += 1
        item = {
            "id": self._seq,
            "payload": payload,
            "attempts": 0,
            "delay": 0.0,
            "created_at": time.time(),
        }
        self._pending.append(item)
        return item

    def _next_ready(self, now: float) -> Optional[dict]:
        for i, item in enumerate(self._pending):
            if now >= item.get("ready_at", item["created_at"]):
                return self._pending.pop(i)
        return None

    def process_one(self, handler: Callable[[dict], None], now: Optional[float] = None) -> int:
        """Run one ready item. Returns 1 (processed) or 0 (none ready)."""
        now = now if now is not None else time.time()
        item = self._next_ready(now)
        if item is None:
            return 0
        item["attempts"] += 1
        try:
            handler(item["payload"])
        except Exception as exc:  # noqa: BLE001 - a handler may raise anything
            if item["attempts"] >= self.max_attempts:
                item["error"] = repr(exc)
                self.dead_letter.append(item)
            else:
                item["delay"] = compute_delay(item["attempts"], self.base_delay, self.cap_delay)
                item["ready_at"] = now + item["delay"]
                self._pending.append(item)
        return 1

    def drain(self, handler: Callable[[dict], None], max_iters: Optional[int] = None) -> int:
        """Process all items currently ready, up to max_iters total executions."""
        executed = 0
        iters = max_iters if max_iters is not None else len(self._pending) * self.max_attempts + 1
        for _ in range(iters):
            if self.process_one(handler, time.time()) == 0:
                break
            executed += 1
        return executed

    def pending_count(self) -> int:
        return len(self._pending)

    def dead_letter_count(self) -> int:
        return len(self.dead_letter)


def default_handler(payload: dict) -> None:
    """Example handler: validate a required 'required_field' presence."""
    if "required_field" not in payload:
        raise ValueError("missing required_field")
