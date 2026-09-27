from pydantic import BaseModel, Field


class TaskSchema(BaseModel):
    title: str
    description: str
    is_completed: bool = False


class TaskResponseSchema(BaseModel):
    id: int
    title: str
    description: str
    is_completed: bool
    user_id: int
    tags: list[TagResponseSchema] = Field(default_factory=list)


class AddTagSchema(BaseModel):
    tag_ids: list[int]


class TagResponseSchema(BaseModel):
    id: int
    name: str
