from fastapi import FastAPI
from contextlib import asynccontextmanager
import os

from database import database
from routers.post import router as posts_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()

app = FastAPI(lifespan=lifespan)

print("Hi this is environ variable", os.environ.get('DATABASE_URL'))

# Include the posts router
app.include_router(posts_router, prefix="/posts", tags=["posts"])

@app.get("/")
def read_root():
    return {"Hello": "World"}