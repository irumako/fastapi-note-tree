import neo4j
from fastapi import APIRouter, Depends

from core.db import gc
from ..deps import project_permission


router = APIRouter(
    responses={404: {"description": "Not found"}},
)


@router.get("/{project_id}")
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
