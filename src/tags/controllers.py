from fastapi import HTTPException, status

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.tags.dtos import TagSchema
from src.tags.models import TagModel


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

    return new_tag
