from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
import logging

logger = logging.getLogger(__name__)


def retry_on_api_failure(max_attempts: int = 3, min_wait: int = 1, max_wait: int = 10):
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=min_wait, max=max_wait),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
