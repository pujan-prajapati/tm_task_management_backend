from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.tags import controllers
from src.tags.dtos import TagSchema, TagResponseSchema
from src.utils.db import get_db

tag_routes = APIRouter(prefix="/tags")


# ================ CREATE TAG ==================
@tag_routes.post(
    "/", response_model=TagResponseSchema, status_code=status.HTTP_201_CREATED
)
def create_tag(body: TagSchema, db: Session = Depends(get_db), ):
    return controllers.create_tag(body, db)
