from fastapi import FastAPI
import uvicorn
from config import settings

main_app = FastAPI()


if __name__ == "__main__":
    uvicorn.run(
        app='main:main_app',
        port=settings.run.port,
        host=settings.run.host,
        reload=True
)