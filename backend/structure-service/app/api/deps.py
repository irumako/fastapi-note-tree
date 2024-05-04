from typing import Annotated

import neo4j
from fastapi import Depends, HTTPException

from core.db import gc
from core.security import oauth2_scheme, keycloak_openid
from nodes import UserNode
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