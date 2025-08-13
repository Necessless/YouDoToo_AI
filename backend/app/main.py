from fastapi import FastAPI
import uvicorn
from config import settings
from api.user_router import router as user_router


main_app = FastAPI()

main_app.include_router(user_router)

if __name__ == "__main__":
    uvicorn.run(
        app='main:main_app',
        port=settings.run.port,
        host=settings.run.host,
        reload=True
)