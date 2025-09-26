import logging
from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.exception_handlers import http_exception_handler
from fastapi import HTTPException as HttpException

from asgi_correlation_id import CorrelationIdMiddleware
from storeapi.database import database
from storeapi.logging_conf import configure_logging
from storeapi.routers.post import router as post_router
from storeapi.routers.upload import router as upload_router
from storeapi.routers.user import router as user_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    await database.connect()
    logger.info("FASTAPI startup complete.")
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)

# Configure logging as early as possible so libraries that log during
# startup (for example the `databases` package when connecting) are
# formatted through our Rich handler.
configure_logging()

# Quick startup test to validate filters (will be obfuscated by EmailObfuscationFilter
# when the filter is registered in the logging config). We add it here as a
# smoke-check; it intentionally logs a sample email which should be masked
# when the filter is active.
test_logger = logging.getLogger(__name__)
test_logger.info("Startup test: contact admin at admin@example.com for help")

# Install correlation id ASGI middleware so every HTTP request has an id.
# The middleware will set X-Correlation-ID on the response and expose the
# id in a contextvar consumed by the logging filter.
app.add_middleware(CorrelationIdMiddleware)

print("Hi this is environ variable", os.environ.get('DATABASE_URL'))

# Include routers at root to match tests
app.include_router(post_router, tags=["posts"])
app.include_router(upload_router, tags=["upload"])
app.include_router(user_router, tags=["users"])


@app.exception_handler(HttpException)
async def http_exception_handle_logging(request, exc):
    logger.error(f"HTTPException: {exc.status_code} {exc.detail}")
    return await http_exception_handler(request, exc)


@app.get("/")
def read_root():
    raise HttpException(status_code=501, detail="Not Implemented")
