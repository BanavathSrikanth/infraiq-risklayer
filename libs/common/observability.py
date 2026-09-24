"""Small framework-neutral observability helpers shared by services."""

from contextvars import ContextVar
import logging
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        value = request.headers.get("x-correlation-id") or str(uuid4())
        token = correlation_id.set(value)
        try:
            response = await call_next(request)
            response.headers["x-correlation-id"] = value
            return response
        finally:
            correlation_id.reset(token)


class CorrelationIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = correlation_id.get()
        return True
