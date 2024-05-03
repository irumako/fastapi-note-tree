from typing import Annotated

from bson import ObjectId
from fastapi import Depends, HTTPException

from core.db import collection as note_collection
from core.security import oauth2_scheme, keycloak_openid
from schemas import User


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


async def get_note_by_id(id: str, user: User = Depends(valid_access_token)):
    if (
            note := await note_collection.find_one({"_id": ObjectId(id)})
    ) is not None:
        if note["owner"] == user.id:
            return note

    raise HTTPException(status_code=404, detail=f"Note {id} not found")
