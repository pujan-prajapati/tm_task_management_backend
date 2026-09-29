from typing import Generic, TypeVar

from pydantic import BaseModel

ResponseData = TypeVar("ResponseData")


class ResponseSchema(BaseModel, Generic[ResponseData]):
    data: ResponseData | None
    success: bool
    message: str
