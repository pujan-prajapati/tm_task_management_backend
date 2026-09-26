from src.utils.db import LocalSession
from src.users.models import UserModel
from src.users.controllers import get_password_hash
from src.tasks.models import TaskModel


def seed_database():
    db = LocalSession()

    try:
        # ================ CREATE TEST USER =====================
        username = "testuser"

        # Check if test user already exists
        user = db.query(UserModel).filter(UserModel.username == username).first()

        if not user:
            user = UserModel(
                name="Test User",
                username=username,
                email="test@example.com",
                hash_password=get_password_hash("password123"),
                phone="9800000000",
            )

            db.add(user)
            db.commit()
            db.refresh(user)

            print("Test user created.")
        else:
            print("Test user already exists.")

        # ================ CREATE TASKS ======================
        existing_tasks = (
            db.query(TaskModel).filter(TaskModel.user_id == user.id).count()
        )

        if existing_tasks > 0:
            print(f"User already has {existing_tasks} tasks.")
            return

        tasks = []

        for i in range(1, 21):
            task = TaskModel(
                title=f"Task {i}",
                description=f"This is the description for task {i}",
                is_completed=i % 2 == 0,
                user_id=user.id,
            )

            tasks.append(task)

        db.add_all(tasks)
        db.commit()

        print("20 tasks created successfully.")

    except Exception as e:
        db.rollback()
        print("Error while seeding db : ", e)

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
