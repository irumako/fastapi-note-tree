from neontology import GraphConnection

from .config import settings

gc = GraphConnection(
    neo4j_uri=settings.NEO4J_URI,
    neo4j_username=settings.NEO4J_USERNAME,
    neo4j_password=settings.NEO4J_PASSWORD.get_secret_value(),
)