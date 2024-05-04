import neo4j
from fastapi import APIRouter, Depends, status
from fastapi.responses import Response

from schemas import User
from nodes import ProjectNode, UserNode, BelongsTo
from core.db import gc
from ..deps import valid_access_token, project_permission

router = APIRouter(
    responses={404: {"description": "Not found"}},
)


# TODO: Добавить зависимость пользователя
@router.post("/")
async def create_project(project: ProjectNode) -> ProjectNode:
    user = UserNode.match("4937c07b-2713-4503-81e0-260e101aafa1")
    if user is None:
        user = UserNode(id='4937c07b-2713-4503-81e0-260e101aabbb')
        user.merge()
    project.merge()
    rel = BelongsTo(source=project, target=user)
    rel.merge()

    return project


@router.get("/{project_id}")
async def get_project(pp: str = Depends(project_permission)) -> ProjectNode:
    project = ProjectNode.match(pp)

    return project


@router.put("/{project_id}")
async def update_project(new_project: ProjectNode, pp: str = Depends(project_permission)) -> ProjectNode:
    project = ProjectNode.match(pp)

    new_project.id = project.id
    new_project.merge()

    return new_project


@router.delete("/{project_id}")
async def delete_project(pp: str = Depends(project_permission)):
    ProjectNode.delete(pp)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/")
async def get_projects(user: User = Depends(valid_access_token)) -> list[ProjectNode]:
    cypher_query = f"""
    MATCH (u: User {{id: '{user.id}'}})<-[:BELONGS_TO]-(p: Project) 
    RETURN p 
    """

    response = []
    result = gc.driver.execute_query(cypher_query, result_transformer_=neo4j.Result.single)

    if result:
        response = [ProjectNode(**dict(r)) for r in result]

    return response
