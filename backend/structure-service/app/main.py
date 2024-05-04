from contextlib import asynccontextmanager

from fastapi import FastAPI
from neontology import BaseNode, BaseRelationship, init_neontology, GraphConnection

from api import api_router
from core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_neontology(
        neo4j_uri=settings.NEO4J_URI,
        neo4j_username=settings.NEO4J_USERNAME,
        neo4j_password=settings.NEO4J_PASSWORD.get_secret_value(),
    )
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    summary="A service for working with projects structure using FastAPI + Neo4j",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
