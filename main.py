from fastapi import FastAPI
from contextlib import asynccontextmanager
import os

from database import database
from routers.post import router as posts_router
from logging_conf import configure_logging
import logging
from fastapi import HTTPException as HttpException
from correlation import CorrelationIdMiddleware
from logging_filters import EmailObfuscationFilter


# Do not call logging.basicConfig() here — dictConfig in logging_conf
# will configure handlers. calling basicConfig() may add the default
# StreamHandler and cause duplicate output.
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
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

# Include the posts router
app.include_router(posts_router, prefix="/posts", tags=["posts"])

@app.get("/")
def read_root():
    raise HttpException(status_code=501, detail="Not Implemented")
