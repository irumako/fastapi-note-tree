from fastapi.security import OAuth2AuthorizationCodeBearer
from keycloak import KeycloakOpenID

from .config import settings

keycloak_openid = KeycloakOpenID(server_url=str(settings.KEYCLOAK_URL),
                                 realm_name=settings.KEYCLOAK_REALM,
                                 client_id=settings.KEYCLOAK_CLIENT,
                                 client_secret_key=settings.KEYCLOAK_CLIENT_SECRET.get_secret_value(),
                                 )

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    tokenUrl=settings.KEYCLOAK_TOKEN_URL,
    authorizationUrl=settings.KEYCLOAK_AUTHORIZATION_URL,
)