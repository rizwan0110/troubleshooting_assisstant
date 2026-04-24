import logging
import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        method = request.method
        path = request.url.path

        logger.info(f"request_id={request_id} | Request started {method} {path}")

        start_time = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                f"request_id={request_id} | Unhandled error during {method} {path}"
            )
            raise

        duration = time.perf_counter() - start_time

        logger.info(
            f"request_id={request_id} | Request finished {method} {path} "
            f"status_code={response.status_code} duration={duration:.4f}s"
        )

        response.headers["X-Request-ID"] = request_id
        return response
