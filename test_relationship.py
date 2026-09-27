from src.utils.db import LocalSession
from src.tasks.models import TaskModel
from src.tags.models import TagModel
from src.users.models import UserModel

db = LocalSession()

task = db.get(TaskModel, 16)
tag = db.get(TagModel, 1)

task.tags.append(tag)

db.commit()

print("Task tags:", task.tags)
print("Tag tasks:", tag.tasks)

db.close()
