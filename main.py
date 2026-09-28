from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from src.utils.exceptions import http_exception_handler

from src.core.db import Base, engine

from src.tasks.routers import task_routes
from src.users.routers import user_routes
from src.tags.routers import tag_routes
from src.categories.routers import category_routes

Base.metadata.create_all(engine)

app = FastAPI(title="This is my Task Management Application")

# custom exception handler
app.add_exception_handler(HTTPException, http_exception_handler)

# routers -----------------------------------
app.include_router(task_routes)
app.include_router(user_routes)
app.include_router(tag_routes)
app.include_router(category_routes)
