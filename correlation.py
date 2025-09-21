import contextvars
import uuid
import logging
from typing import Optional

# Context var that holds the correlation id for the current request
_correlation_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("correlation_id", default=None)


def get_correlation_id() -> Optional[str]:
    return _correlation_id_var.get()


def set_correlation_id(value: str) -> None:
    _correlation_id_var.set(value)


class CorrelationIdFilter(logging.Filter):
    """Logging filter that injects a correlation_id attribute into LogRecord.

    The filter can be configured via dictConfig by providing `uuid_length`
    and `default_value`.
    """

    def __init__(self, uuid_length: int = 32, default_value: str = ""):
        super().__init__()
        self.uuid_length = int(uuid_length)
        self.default_value = default_value or ""

    def filter(self, record: logging.LogRecord) -> bool:
        cid = get_correlation_id()
        if not cid:
            # If no correlation id in context, use default (or empty string)
            cid = self.default_value
        record.correlation_id = cid
        return True


class CorrelationIdMiddleware:
    """ASGI middleware that ensures each HTTP request has a correlation id.

    It looks for an incoming header 'X-Correlation-ID' and uses that value if
    present. Otherwise it generates a UUID and truncates it to `uuid_length`.

    The middleware also sets the response header 'X-Correlation-ID'.
    """

    def __init__(self, app, header_name: str = "X-Correlation-ID", uuid_length: int = 32, default_value: str = ""):
        self.app = app
        self.header_name = header_name.lower().encode()
        self.uuid_length = int(uuid_length)
        self.default_value = default_value or ""

    async def __call__(self, scope, receive, send):
        # Only handle HTTP requests
        if scope.get("type") != "http":
            return await self.app(scope, receive, send)

        # Extract header if present
        headers = dict(scope.get("headers", []))
        raw = headers.get(self.header_name)
        if raw:
            try:
                cid = raw.decode()
            except Exception:
                cid = self.default_value
        else:
            # generate a uuid and truncate as configured
            cid = uuid.uuid4().hex[: self.uuid_length]

        # set in contextvar for this request
        set_correlation_id(cid)

        # wrap send to inject response header
        async def send_wrapper(event):
            if event.get("type") == "http.response.start":
                headers = event.setdefault("headers", [])
                # append the correlation id header
                headers.append((b"x-correlation-id", cid.encode()))
            await send(event)

        return await self.app(scope, receive, send_wrapper)
