from fastapi import FastAPI

from core.config import settings
from api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    summary="A service for working with notes using FastAPI + MongoDB.",
    debug=settings.DEBUG,
)

app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
