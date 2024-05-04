from contextlib import asynccontextmanager
from typing import ClassVar, Optional, List, Annotated
from uuid import uuid4

import neo4j
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.responses import Response
from neontology import BaseNode, BaseRelationship, init_neontology, GraphConnection
from pydantic import UUID4, Field

from core.config import settings


class UserNode(BaseNode):
    __primaryproperty__: ClassVar[str] = "id"
    __primarylabel__: ClassVar[str] = "User"
    id: Optional[UUID4] = None


class ProjectNode(BaseNode):
    __primaryproperty__: ClassVar[str] = "id"
    __primarylabel__: ClassVar[str] = "Project"
    id: UUID4 = Field(default_factory=uuid4)
    name: str
    desc: Optional[str] = None


class NoteNode(BaseNode):
    __primaryproperty__: ClassVar[str] = "id"
    __primarylabel__: ClassVar[str] = "Note"
    id: str


class BelongsTo(BaseRelationship):
    __relationshiptype__: ClassVar[str] = "BELONGS_TO"

    source: ProjectNode
    target: UserNode


class IncludeInProject(BaseRelationship):
    __relationshiptype__: ClassVar[str] = "INCLUDE_IN"

    source: NoteNode
    target: ProjectNode


class IncludeInNote(BaseRelationship):
    __relationshiptype__: ClassVar[str] = "INCLUDE_IN"

    source: NoteNode
    target: NoteNode


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_neontology(
        neo4j_uri=settings.NEO4J_URI,
        neo4j_username=settings.NEO4J_USERNAME,
        neo4j_password=settings.NEO4J_PASSWORD.get_secret_value(),
    )
    yield


gc = GraphConnection(
    neo4j_uri=settings.NEO4J_URI,
    neo4j_username=settings.NEO4J_USERNAME,
    neo4j_password=settings.NEO4J_PASSWORD.get_secret_value(),
)

app = FastAPI(lifespan=lifespan)


async def valid_access_token(
        access_token: Annotated[str, Depends(oauth2_scheme)]
) -> User:
    try:
        data = keycloak_openid.decode_token(access_token, validate=True)
        return User(
            id=data.get("sub"),
            username=data.get("preferred_username"),
            email=data.get("email"),
            first_name=data.get("given_name"),
            last_name=data.get("family_name"),
            realm_roles=data.get("realm_access", {}).get("roles", []),
            client_roles=data.get("realm_access", {}).get("roles", [])
        )

    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


async def project_permission(project_id: str, user: User = Depends(valid_access_token)):
    cypher_query = f"""
        MATCH p = (n:Project {{id: '{project_id}'}}) <-[:BELONGS_TO]-(u)
        RETURN u
        """

    result = gc.driver.execute_query(cypher_query, result_transformer_=neo4j.Result.single)

    if result:
        if user.id == UserNode(**dict(result)).id:
            return project_id

    raise HTTPException(status_code=404, detail=f"Project {project_id} not found")


@app.post("/projects/")
async def create_project(project: ProjectNode) -> ProjectNode:
    user = UserNode.match("4937c07b-2713-4503-81e0-260e101aafa1")
    if user is None:
        user = UserNode(id='4937c07b-2713-4503-81e0-260e101aabbb')
        user.merge()
    project.merge()
    rel = BelongsTo(source=project, target=user)
    rel.merge()

    return project


@app.get("/projects/{project_id}")
async def get_project(pp: str = Depends(project_permission)) -> ProjectNode:
    project = ProjectNode.match(pp)

    return project


@app.put("/projects/{project_id}")
async def update_project(new_project: ProjectNode, pp: str = Depends(project_permission)) -> ProjectNode:
    project = ProjectNode.match(pp)

    new_project.id = project.id
    new_project.merge()

    return new_project


@app.delete("/projects/{project_id}")
async def delete_project(pp: str = Depends(project_permission)):
    ProjectNode.delete(pp)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/projects/")
async def get_projects(user: User = Depends(valid_access_token)) -> List[ProjectNode]:
    cypher_query = f"""
    MATCH (u: User {{id: '{user.id}'}})<-[:BELONGS_TO]-(p: Project) 
    RETURN p 
    """

    response = []
    result = gc.driver.execute_query(cypher_query, result_transformer_=neo4j.Result.single)

    if result:
        response = [ProjectNode(**dict(r)) for r in result]

    return response


# TODO: Сделать проверку на принадлежность target_id пользователю
@app.post("/notes/")
async def create_note(note: NoteNode, target_id: str) -> NoteNode:
    if target_id == note.id:
        raise HTTPException(status_code=404, detail=f"Target {target_id} doesn't exist")

    project = ProjectNode.match(target_id)
    target_note = NoteNode.match(target_id)

    if project:
        NoteNode.delete(note.id)
        note.merge()
        rel = IncludeInProject(source=note, target=project)
        rel.merge()
        return note
    if target_note:
        NoteNode.delete(note.id)
        note.merge()
        rel = IncludeInNote(source=note, target=target_note)
        rel.merge()
        return note

    raise HTTPException(status_code=404, detail=f"Target {target_id} doesn't exist")


# TODO: Сделать проверку на принадлежность заметки пользователю
@app.delete("/notes/{note_id}")
async def delete_project(note_id):
    NoteNode.delete(note_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/structure/{project_id}")
async def get_structure(pp: str = Depends(project_permission)):
    cypher_query = f"""
    MATCH p=(n:Project {{id: "{pp}"}})<-[:INCLUDE_IN*]-(m)
    WITH COLLECT(p) AS ps
    CALL apoc.convert.toTree(ps, true, 
    {{nodes: {{Project: ['id', 'desc', 'name'], Note: ['id']}}, rels:  {{include_in: ['_elementId']}}}}) yield value
    RETURN value;
    """

    result = gc.driver.execute_query(cypher_query, result_transformer_=neo4j.Result.single)

    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
