from enum import Enum
from typing import Optional, List, Any, Annotated

from bson import ObjectId
from pydantic import ConfigDict, BaseModel, Field, UUID4
from pydantic.functional_validators import BeforeValidator

PyObjectId = Annotated[str, BeforeValidator(str)]


class ToolTypeEnum(str, Enum):
    paragraph = "paragraph"
    embed = "embed"
    table = "table"
    list = "list"
    warning = "warning"
    code = "code"
    linkTool = "linktool"
    image = "image"
    raw = "raw"
    header = "header"
    quote = "quote"
    marker = "marker"
    checklist = "checklist"
    delimiter = "delimiter"
    inlineCode = "inlinecode"
    simpleImage = "simpleimage"


class BlockModel(BaseModel):
    id: str = Field(...)
    type: ToolTypeEnum = ToolTypeEnum.paragraph
    data: Optional[Any] = None
    tunes: Optional[Any] = None


class NoteModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    owner: Optional[UUID4] = None
    time: int = Field(...)
    version: str = Field(...)
    blocks: Optional[List[BlockModel]] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "owner": "d89f57da-8009-4649-9002-09ca96ee6489",
                "time": 1550476186479,
                "blocks": [
                    {
                        "type": "header",
                        "data": {
                            "text": "Editor.js",
                            "level": 2
                        }
                    },
                    {
                        "type": "paragraph",
                        "data": {
                            "text": "Hey. Meet the new Editor. On this page you can see it in action — try to edit this"
                                    "text. Source code of the page contains the example of connection and "
                                    "configuration."
                        }
                    },
                    {
                        "type": "header",
                        "data": {
                            "text": "Key features",
                            "level": 3
                        }
                    }
                ],
                "version": "2.8.1",
            }
        },
    )


class UpdateNoteModel(BaseModel):
    time: Optional[int] = None
    version: Optional[str] = None
    blocks: Optional[List[BlockModel]] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "owner": "d89f57da-8009-4649-9002-09ca96ee6489",
                "time": 1550476186479,
                "blocks": [
                    {
                        "type": "header",
                        "data": {
                            "text": "Editor.js",
                            "level": 2
                        }
                    },
                    {
                        "type": "paragraph",
                        "data": {
                            "text": "Hey. Meet the new Editor. On this page you can see it in action — try to edit this"
                                    "text. Source code of the page contains the example of connection and "
                                    "configuration."
                        }
                    },
                    {
                        "type": "header",
                        "data": {
                            "text": "Key features",
                            "level": 3
                        }
                    }
                ],
                "version": "2.8.1",
            }
        },
    )


class NoteCollection(BaseModel):
    notes: List[NoteModel]


class User(BaseModel):
    id: str
    username: str
    email: str
    first_name: str
    last_name: str
    realm_roles: list
    client_roles: list
