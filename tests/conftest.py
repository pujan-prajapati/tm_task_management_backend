import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from src.core.db import Base, get_db
from src.core.settings import settings

test_engine = create_engine(settings.TEST_DB_CONNECTION)
TestSession = sessionmaker(bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def db():
    session = TestSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def auth_headers(client):
    user_data = {
        "name": "Test User",
        "username": "authuser",
        "password": "testpassword",
        "email": "authuser@gmail.com",
        "phone": "9800000200",
    }

    client.post(
        "/users/register",
        json=user_data,
    )

    response = client.post(
        "/users/login",
        json={
            "username": user_data["username"],
            "password": user_data["password"],
        },
    )

    token = response.json()["data"]["token"]

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def second_auth_headers(client):
    user_data = {
        "name": "Second User",
        "username": "seconduser",
        "password": "testpassword",
        "email": "seconduser@gmail.com",
        "phone": "9800000201",
    }

    client.post(
        "/users/register",
        json=user_data,
    )

    response = client.post(
        "/users/login",
        json={
            "username": user_data["username"],
            "password": user_data["password"],
        },
    )

    token = response.json()["data"]["token"]

    return {"Authorization": f"Bearer {token}"}
