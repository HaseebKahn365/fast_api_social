from fastapi import FastAPI

from routers.post import router as posts_router

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

app.include_router(posts_router)