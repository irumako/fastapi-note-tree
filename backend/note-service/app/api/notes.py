from bson import ObjectId
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.responses import Response
from pymongo import ReturnDocument

from schemas import (
    NoteModel,
    User,
    UpdateNoteModel,
)
from core.db import collection as note_collection
from .deps import valid_access_token, get_note_by_id

router = APIRouter(
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/",
    response_description="Add new note",
    response_model=NoteModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_note(note: NoteModel = Body(...), user: User = Depends(valid_access_token)):
    note.owner = user.id
    new_note = await note_collection.insert_one(
        note.model_dump(by_alias=True, exclude=["id"])
    )
    created_note = await note_collection.find_one(
        {"_id": new_note.inserted_id}
    )
    return created_note


@router.get(
    "/{id}",
    response_description="Get a single note",
    response_model=NoteModel,
    response_model_by_alias=False,
)
async def show_note(note: NoteModel = Depends(get_note_by_id)):
    return note


@router.put(
    "/{id}",
    response_description="Update a note",
    response_model=NoteModel,
    response_model_by_alias=False,
)
async def update_note(note: NoteModel = Depends(get_note_by_id), new_note: UpdateNoteModel = Body(...)):
    new_note = {
        k: v for k, v in new_note.model_dump(by_alias=True).items() if v is not None
    }

    if len(new_note) >= 1:
        update_result = await note_collection.find_one_and_update(
            {"_id": ObjectId(note["_id"])},
            {"$set": new_note},
            return_document=ReturnDocument.AFTER,
        )

        return update_result

    return note


@router.delete("/{id}", response_description="Delete a note")
async def delete_note(note: NoteModel = Depends(get_note_by_id)):
    delete_result = await note_collection.delete_one({"_id": ObjectId(note["_id"])})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Note {note["_id"]} not found")
