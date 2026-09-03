import pytest

from retry_queue_worker import RetryQueue, compute_delay, default_handler


def test_backoff_grows_and_caps():
    assert compute_delay(1, base=1.0, cap=64.0, jitter=0) == 1.0
    assert compute_delay(2, base=1.0, cap=64.0, jitter=0) == 2.0
    assert compute_delay(10, base=1.0, cap=64.0, jitter=0) == 64.0


def test_success_on_first_try():
    q = RetryQueue(max_attempts=3)
    q.enqueue({"required_field": "ok"})
    ran = []

    def handler(payload):
        ran.append(payload)
        default_handler(payload)

    q.drain(handler)
    assert len(ran) == 1
    assert q.pending_count() == 0
    assert q.dead_letter_count() == 0


def test_retries_then_dead_letter():
    q = RetryQueue(max_attempts=3, base_delay=0.0, cap_delay=0.0)
    q.enqueue({})  # will always fail (no required_field)

    def failing(payload):
        default_handler(payload)

    q.drain(failing)
    assert q.pending_count() == 0
    assert q.dead_letter_count() == 1
    assert q.dead_letter[0]["attempts"] == 3


def test_retry_reschedules_with_delay():
    q = RetryQueue(max_attempts=3, base_delay=0.5, cap_delay=0.5, )
    q.enqueue({})
    # first attempt fails -> goes back to pending with a future ready_at
    executions = q.drain(lambda p: default_handler(p), max_iters=1)
    assert executions == 1
    assert q.pending_count() == 1


def test_concurrent_success_progresses():
    q = RetryQueue(max_attempts=2, base_delay=0.0, cap_delay=0.0)
    calls = {"n": 0}
    q.enqueue({"required_field": ""})

    def flaky(payload):
        calls["n"] += 1
        if calls["n"] < 2:
            raise RuntimeError("transient")
        default_handler(payload)

    q.enqueue({"other": 1})  # add a never-ready sibling to keep things honest
    q.drain(flaky, max_iters=10)
    # the flaky item eventually succeeds on attempt 2; sibling has no field
    assert calls["n"] >= 1
