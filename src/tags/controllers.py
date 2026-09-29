from fastapi import HTTPException, status

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.tags.dtos import TagSchema
from src.tags.models import TagModel
from src.utils.helpers import success_response


# ============== CREATE TAG ==================
def create_tag(body: TagSchema, db: Session):
    query = select(TagModel).where(TagModel.name == body.name)

    existing_tag = db.scalar(query)

    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag with this name already exists.",
        )

    new_tag = TagModel(name=body.name)

    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)

    return success_response(new_tag, "Tag created successfully")


# ============== GET ALL TAGS ==================
def get_all_tags(db: Session):
    query = select(TagModel)
    tags = db.execute(query).scalars().all()

    return success_response(tags, "Tags fetched successfully")


# =============== GET ONE TAG =================
def get_one_tag(tag_id: int, db: Session):
    tag = db.get(TagModel, tag_id)

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag Not Found"
        )

    return success_response(tag, "Tag fetched successfully")


# ============= UPDATE TAG ====================
def update_tag(tag_id: int, body: TagSchema, db: Session):
    tag = db.get(TagModel, tag_id)

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag Not Found"
        )

    tag.name = body.name

    db.add(tag)
    db.commit()
    db.refresh(tag)

    return success_response(tag, "Tag updated successfully")


# ============= DELETE TAG ====================
def delete_tag(tag_id: int, db: Session):
    tag = db.get(TagModel, tag_id)

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag Not Found"
        )

    db.delete(tag)
    db.commit()

    return success_response(None, "Tag deleted successfully")
