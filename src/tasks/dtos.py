from enum import Enum
from pydantic import BaseModel, ConfigDict, Field

from src.categories.dtos import CategoryResponseSchema


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIAUM = "medium"
    HIGH = "high"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TagResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class TaskSchema(BaseModel):
    title: str
    description: str
    priority: TaskPriority = TaskPriority.MEDIAUM
    status: TaskStatus = TaskStatus.PENDING
    category_id: int | None = None


class TaskResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    priority: TaskPriority
    status: TaskStatus
    category_id: int | None = None
    category: CategoryResponseSchema | None = None
    user_id: int
    tags: list[TagResponseSchema] = Field(default_factory=list)


class AddTagSchema(BaseModel):
    tag_ids: list[int]


class TagResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class TaskListResponseSchema(BaseModel):
    items: list[TaskResponseSchema]
    page: int
    limit: int
    total: int
    total_pages: int


class AssignTaskSchema(BaseModel):
    user_id: int
