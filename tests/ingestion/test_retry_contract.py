from __future__ import annotations

import pytest

from src.ingestion.retry import RetryPolicy

pytestmark = pytest.mark.unit


class TransientProviderFailure(Exception):
    pass


class NonRetryableProviderFailure(Exception):
    pass


def test_retry_policy_bounds_retries_for_transient_failure() -> None:
    attempts = 0
    sleeps: list[float] = []

    def flaky_provider_call() -> str:
        nonlocal attempts
        attempts += 1
        raise TransientProviderFailure("temporary provider outage")

    policy = RetryPolicy(
        max_attempts=3,
        backoff_seconds=0.25,
        retryable_exceptions=(TransientProviderFailure,),
        sleep=sleeps.append,
    )

    with pytest.raises(TransientProviderFailure):
        policy.execute(flaky_provider_call)

    assert attempts == 3
    assert sleeps == [0.25, 0.25]


def test_retry_policy_does_not_retry_non_retryable_failure() -> None:
    attempts = 0

    def bad_response() -> None:
        nonlocal attempts
        attempts += 1
        raise NonRetryableProviderFailure("malformed returned data")

    policy = RetryPolicy(
        max_attempts=3,
        backoff_seconds=0,
        retryable_exceptions=(TransientProviderFailure,),
    )

    with pytest.raises(NonRetryableProviderFailure):
        policy.execute(bad_response)

    assert attempts == 1
