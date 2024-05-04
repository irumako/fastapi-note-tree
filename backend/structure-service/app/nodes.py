from typing import ClassVar, Optional
from uuid import uuid4

from neontology import BaseNode, BaseRelationship
from pydantic import UUID4, Field


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