from fastapi import FastAPI
from src.utils.db import Base, engine
from src.tasks.routers import task_routes

Base.metadata.create_all(engine)

app = FastAPI(title="This is my Task Management Application")

# routers -----------------------------------
app.include_router(task_routes)
