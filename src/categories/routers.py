from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.core.db import get_db

from src.users.models import UserModel

from src.categories.dtos import CategorySchema, CategoryResponseSchema
from src.categories import controllers

from src.dependencies.is_authenticated import is_authenticated

from src.utils.dtos import SuccessResponse

category_routes = APIRouter(prefix="/categories")


# ================== CREATE CATEGORY ===========================
@category_routes.post(
    "/",
    response_model=SuccessResponse[CategoryResponseSchema],
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    body: CategorySchema,
    db: Session = Depends(get_db),
    user: UserModel = Depends(is_authenticated),
):
    return controllers.create_category(body, db, user)


# ================== GET CATEGORY ===========================
@category_routes.get(
    "/",
    response_model=SuccessResponse[list[CategoryResponseSchema]],
    status_code=status.HTTP_200_OK,
)
def get_all_categories(
    db: Session = Depends(get_db), user: UserModel = Depends(is_authenticated)
):
    return controllers.get_all_categories(db, user)


# ================== GET ONE CATEGORY ===========================
@category_routes.get(
    "/{category_id}",
    response_model=SuccessResponse[CategoryResponseSchema],
    status_code=status.HTTP_200_OK,
)
def get_one_category(
    category_id: int,
    db: Session = Depends(get_db),
    user: UserModel = Depends(is_authenticated),
):
    return controllers.get_one_category(category_id, db, user)


# ================== UPDATE CATEGORY ===========================
@category_routes.put(
    "/{category_id}",
    response_model=SuccessResponse[CategoryResponseSchema],
    status_code=status.HTTP_200_OK,
)
def update_category(
    body: CategorySchema,
    category_id: int,
    db: Session = Depends(get_db),
    user: UserModel = Depends(is_authenticated),
):
    return controllers.update_category(body, category_id, db, user)


# ================== DELETE CATEGORY ===========================
@category_routes.delete(
    "/{category_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    user: UserModel = Depends(is_authenticated),
):
    return controllers.delete_category(category_id, db, user)
