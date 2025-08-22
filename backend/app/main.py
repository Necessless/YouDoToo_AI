from fastapi import FastAPI
import uvicorn
from config import settings
from api.user_router import router as user_router
from contextlib import asynccontextmanager
from redis_client import redis_startup, redis_shutdown


@asynccontextmanager 
async def lifespan(app: FastAPI):
    await redis_startup()
    yield
    await redis_shutdown()

main_app = FastAPI(lifespan=lifespan)

main_app.include_router(user_router)

if __name__ == "__main__":
    uvicorn.run(
        app='main:main_app',
        port=settings.run.port,
        host=settings.run.host,
        reload=True
)