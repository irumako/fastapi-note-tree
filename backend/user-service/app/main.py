from typing import Optional, Annotated

from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2AuthorizationCodeBearer
from keycloak import KeycloakOpenID, KeycloakAdmin
from pydantic import BaseModel
from starlette import status
from starlette.requests import Request
from jwt import PyJWKClient
import jwt
from fastapi.logger import logger

app = FastAPI()

KEYCLOAK_URL = "http://localhost:8081/"
REALM_NAME = "Basic"

URL_TOKEN = KEYCLOAK_URL + f"realms/{REALM_NAME}/protocol/openid-connect/token"
AUTH_URL = KEYCLOAK_URL + f"realms/{REALM_NAME}/protocol/openid-connect/auth"
URL_CERTS = KEYCLOAK_URL + f"realms/{REALM_NAME}/protocol/openid-connect/certs"

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    tokenUrl=URL_TOKEN,
    authorizationUrl=AUTH_URL,
)

keycloak_openid = KeycloakOpenID(server_url=KEYCLOAK_URL,
                                 client_id="note-client",
                                 realm_name=REALM_NAME,
                                 client_secret_key="dKw2NPqzRVroYom2TFTP5SIJC4IoJ6s5")

admin = KeycloakAdmin(
    server_url=KEYCLOAK_URL,
    realm_name="Basic",
    client_secret_key="EWJbTseehA51ZlX6vliiFnrGk4PR5Njk", )


class RefreshPayload(BaseModel):
    refresh_token: str


class KeycloakToken(BaseModel):
    """Keycloak representation of a token object

    Attributes:
        access_token (str): An access token
        refresh_token (str): An a refresh token, default None
        id_token (str): An issued by the Authorization Server token id, default None
    """

    access_token: str
    refresh_token: Optional[str] = None
    id_token: Optional[str] = None

    def __str__(self):
        """String representation of KeycloakToken"""
        return f"Bearer {self.access_token}"


class User(BaseModel):
    id: str
    username: str
    email: str
    first_name: str
    last_name: str
    realm_roles: list
    client_roles: list


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


@app.get("/")
async def root():
    return "hello"


@app.post('/refresh', response_model=KeycloakToken)
def refresh(token: RefreshPayload):
    token = keycloak_openid.refresh_token(token.refresh_token)
    return token


@app.get("/user")  # Requires logged in
async def current_users(user: User = Depends(valid_access_token)):
    return user


@app.get("/login")
async def login() -> RedirectResponse:
    auth_url = keycloak_openid.auth_url(
        redirect_uri="http://localhost:8000/callback", scope="openid")
    return RedirectResponse(auth_url)


@app.get("/callback", response_model=KeycloakToken)
async def callback(code: str) -> KeycloakToken:
    access_token = keycloak_openid.token(
        grant_type='authorization_code',
        code=code,
        redirect_uri="http://localhost:8000/callback", )
    # idp.exchange_authorization_code(session_state=session_state, code=code)  # This will return an access token
    return access_token


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
