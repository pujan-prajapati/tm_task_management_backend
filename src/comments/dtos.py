from pydantic import BaseModel, ConfigDict


class CommentSchema(BaseModel):
    content: str


class CommentResponseSchema(BaseModel):
    id: int
    content: str
    task_id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)
