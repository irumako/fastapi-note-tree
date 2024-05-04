from fastapi import status, HTTPException, APIRouter
from fastapi.responses import Response

from nodes import (
    ProjectNode,
    UserNode,
    BelongsTo,
    NoteNode,
    IncludeInProject,
    IncludeInNote,
)


router = APIRouter(
    responses={404: {"description": "Not found"}},
)


# TODO: Сделать проверку на принадлежность target_id пользователю
@router.post("/")
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
@router.delete("/{note_id}")
async def delete_project(note_id):
    NoteNode.delete(note_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
