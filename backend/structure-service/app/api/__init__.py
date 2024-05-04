from fastapi import APIRouter

from .endpoints import notes, projects, structure

api_router = APIRouter()
api_router.include_router(notes.router, prefix="/notes", tags=["notes"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(structure.router, prefix="/structure", tags=["structure"])
