from pydantic import BaseModel, ConfigDict


class TagSchema(BaseModel):
    name: str


class TagResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
