"""Bounded retry behaviour for retryable provider failures."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


class RetryPolicy:
    def __init__(self, max_attempts: int, backoff_seconds: float) -> None:
        raise NotImplementedError

    def execute(self, fn: F, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError
