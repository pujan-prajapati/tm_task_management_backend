from pydantic import BaseModel, ConfigDict


class CategorySchema(BaseModel):
    name: str


class CategoryResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
