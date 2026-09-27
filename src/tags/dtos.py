from pydantic import BaseModel


class TagSchema(BaseModel):
    name: str


class TagResponseSchema(BaseModel):
    id: int
    name: str
