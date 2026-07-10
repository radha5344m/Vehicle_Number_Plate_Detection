"""Run blocking work with a timeout."""

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from typing import TypeVar

from sentinel_anpr.domain.common.errors import AiTimeoutError

T = TypeVar("T")


def run_with_timeout(
    operation: Callable[[], T],
    *,
    timeout_seconds: float,
    service_name: str,
) -> T:
    """Execute a callable and raise AiTimeoutError when it exceeds the limit."""
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(operation)
        try:
            return future.result(timeout=timeout_seconds)
        except FuturesTimeoutError as exc:
            raise AiTimeoutError(service_name) from exc
