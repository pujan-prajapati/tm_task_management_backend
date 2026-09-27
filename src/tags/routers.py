from typing import List

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
def create_tag(
    body: TagSchema,
    db: Session = Depends(get_db),
):
    return controllers.create_tag(body, db)


# ================ GET ALL TAG ==================
@tag_routes.get(
    "/", response_model=List[TagResponseSchema], status_code=status.HTTP_200_OK
)
def get_tag(db: Session = Depends(get_db)):
    return controllers.get_all_tags(db)


# ================ GET ONE TAG ==================
@tag_routes.get(
    "/{tag_id}", response_model=TagResponseSchema, status_code=status.HTTP_200_OK
)
def get_one_tag(tag_id: int, db: Session = Depends(get_db)):
    return controllers.get_one_tag(tag_id, db)


# ================ UPDATE TAG ==================
@tag_routes.put(
    "/{tag_id}",
    response_model=TagResponseSchema,
    status_code=status.HTTP_200_OK,
)
def update_tag(tag_id: int, body: TagSchema, db: Session = Depends(get_db)):
    return controllers.update_tag(tag_id, body, db)


# ================ DELETE TAG ==================
@tag_routes.delete(
    "/{tag_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    return controllers.delete_tag(tag_id, db)
