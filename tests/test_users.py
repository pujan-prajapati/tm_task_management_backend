# ================ TEST REGISTER USER =========================
def test_register_user(client):
    response = client.post(
        "/users/register",
        json={
            "name": "Test User",
            "username": "testuser",
            "password": "testpassword",
            "email": "testuser@gmail.com",
            "phone": "9800000000",
        },
    )

    assert response.status_code == 201
    data = response.json()

    assert data["success"] is True
    assert data["message"] == "User Registered Successful"


# ================ TEST DUPLICATE REGISTER USERNAME =========================
def test_register_duplicate_username(client):
    user_data = {
        "name": "Duplicate User",
        "username": "duplicateuser",
        "password": "testpassword",
        "email": "duplicate1@gmail.com",
        "phone": "9800000001",
    }

    first_response = client.post(
        "/users/register",
        json=user_data,
    )

    assert first_response.status_code == 201

    duplicate_data = {
        **user_data,
        "email": "duplicate2@gmail.com",
        "phone": "9800000002",
    }

    second_response = client.post(
        "/users/register",
        json=duplicate_data,
    )

    assert second_response.status_code == 400


# ================ TEST DUPLICATE REGISTER EMAIL =========================
def test_register_duplicate_email(client):
    user_data = {
        "name": "Email User",
        "username": "emailuser1",
        "password": "testpassword",
        "email": "sameemail@gmail.com",
        "phone": "9800000010",
    }

    first_response = client.post("/users/register", json=user_data)

    assert first_response.status_code == 201

    duplicate_data = {**user_data, "username": "emailuser2", "phone": "9800000011"}

    second_response = client.post("/users/register", json=duplicate_data)

    assert second_response.status_code == 400


# ================ TEST DUPLICATE REGISTER PHONE =========================
def test_register_duplicate_phone(client):
    user_data = {
        "name": "Phone User",
        "username": "phoneuser1",
        "password": "testpassword",
        "email": "samephone@gmail.com",
        "phone": "9800000021",
    }

    first_response = client.post("/users/register", json=user_data)

    assert first_response.status_code == 201

    duplicate_data = {
        **user_data,
        "username": "phoneuser2",
        "email": "samephone2@gmail.com",
    }

    second_response = client.post("/users/register", json=duplicate_data)
    assert second_response.status_code == 400


# =========== TEST LOGIN ================================
def test_login_success(client):
    login_response = client.post(
        "/users/login", json={"username": "testuser", "password": "testpassword"}
    )

    assert login_response.status_code == 200

    data = login_response.json()

    assert data["success"] is True
    assert data["message"] == "Login Successful"
    assert data["data"]["token"]


# ================ TEST INVALID CREDENTIAL LOGIN  ==========================
def test_invalid_credential_login(client):
    login_response = client.post(
        "/users/login",
        json={"username": "wrongtestuser", "password": "wrongtestpassword"},
    )

    assert login_response.status_code == 401
    data = login_response.json()
    assert data["message"] == "Invalid Credentials"


# ==================== TEST INACTIVE USER LOGIN ==========================
def test_inactive_user_login(client, db):
    from sqlalchemy import select

    from src.users.models import UserModel

    user_data = {
        "name": "Inactive User",
        "username": "inactiveuser",
        "password": "testpassword",
        "email": "inactiveuser@gmail.com",
        "phone": "9800000099",
    }

    register_response = client.post("/users/register", json=user_data)
    assert register_response.status_code == 201

    user = db.scalar(
        select(UserModel).where(UserModel.username == user_data["username"])
    )
    user.is_active = False
    db.commit()

    login_response = client.post(
        "/users/login",
        json={"username": user_data["username"], "password": user_data["password"]},
    )

    assert login_response.status_code == 403
    assert login_response.json()["message"] == "User Account Is Inactive"


# ==================== TEST LOGIN RATE LIMIT ==========================
def test_login_rate_limit(client):
    username = "ratelimituser"
    password = "wrongpassword"

    # Make 5 failed login attempts
    for _ in range(5):
        response = client.post(
            "/users/login", json={"username": username, "password": password}
        )

    # 6th attempt should be rate limited
    response = client.post(
        "/users/login", json={"username": username, "password": password}
    )

    assert response.status_code == 429
    data = response.json()
    assert data["message"] == "Too many login attempts. Please try again later"


# ==================== TEST CURRENT USER REQUIRES AUTHENTICATION ==========================
def test_current_user_requires_authentication(client):
    response = client.get("/users/me")

    assert response.status_code == 401
    assert response.json()["message"] == "You Are Unauthorized"


# ==================== TEST CURRENT USER REJECTS INVALID TOKEN ==========================
def test_current_user_rejects_invalid_token(client):
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401
    assert response.json()["message"] == "You Are Unauthorized"


# ==================== TEST INACTIVE USER CANNOT ACCESS PROTECTED ENDPOINT ==========================
def test_inactive_user_cannot_access_protected_endpoint(
    client,
    db,
):
    user_data = {
        "name": "Inactive Protected",
        "username": "inactiveprotected",
        "password": "testpassword",
        "email": "inactiveprotected@gmail.com",
        "phone": "9800000300",
    }

    register_response = client.post(
        "/users/register",
        json=user_data,
    )

    assert register_response.status_code == 201

    # Deactivate the user directly in the test database
    from sqlalchemy import select
    from src.users.models import UserModel

    user = db.scalar(
        select(UserModel).where(UserModel.username == user_data["username"])
    )

    assert user is not None

    user.is_active = False
    db.commit()

    # Login should fail because the account is inactive
    login_response = client.post(
        "/users/login",
        json={
            "username": user_data["username"],
            "password": user_data["password"],
        },
    )

    assert login_response.status_code == 403
    assert login_response.json()["message"] == "User Account Is Inactive"


# =================== TEST NORMAL USER CANNOT ACCESS ADMIN USERS ==========================
def test_normal_user_cannot_access_admin_users(
    client,
    auth_headers,
):
    response = client.get(
        "/users/admin/users",
        headers=auth_headers,
    )

    assert response.status_code == 403
    assert response.json()["message"] == "Admin access required"


# =================== TEST ADMIN CAN ACCESS ADMIN USERS ==========================
def test_admin_can_access_admin_users(
    client,
    db,
    auth_headers,
):
    from sqlalchemy import select
    from src.users.models import UserModel

    user = db.scalar(select(UserModel).where(UserModel.username == "authuser"))

    assert user is not None

    user.role = "admin"
    db.commit()

    response = client.get(
        "/users/admin/users",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["success"] is True


# ================== TEST ADMIN CAN UPDATE USER ROLE ==========================
def test_admin_can_update_user_role(
    client,
    db,
    auth_headers,
    second_auth_headers,
):
    from sqlalchemy import select
    from src.users.models import UserModel

    admin_user = db.scalar(select(UserModel).where(UserModel.username == "authuser"))

    assert admin_user is not None

    admin_user.role = "admin"
    db.commit()

    target_user = db.scalar(select(UserModel).where(UserModel.username == "seconduser"))

    assert target_user is not None

    response = client.put(
        f"/users/admin/users/{target_user.id}/role",
        headers=auth_headers,
        json={"role": "admin"},
    )

    assert response.status_code == 200
    assert response.json()["success"] is True


# ================== TEST ADMIN CAN UPDATE USER STATUS ==========================
def test_admin_can_update_user_status(
    client,
    db,
    auth_headers,
    second_auth_headers,
):
    from sqlalchemy import select
    from src.users.models import UserModel

    admin_user = db.scalar(select(UserModel).where(UserModel.username == "authuser"))

    assert admin_user is not None

    admin_user.role = "admin"
    db.commit()

    target_user = db.scalar(select(UserModel).where(UserModel.username == "seconduser"))

    assert target_user is not None
    assert target_user.is_active is True

    response = client.patch(
        f"/users/admin/users/{target_user.id}/status",
        headers=auth_headers,
        json={"is_active": False},
    )

    assert response.status_code == 200
    assert response.json()["success"] is True

    db.refresh(target_user)

    assert target_user.is_active is False


# ================== TEST ADMIN CANNOT CHANGE OWN STATUS ==========================
def test_admin_cannot_change_own_status(
    client,
    db,
    auth_headers,
):
    from sqlalchemy import select
    from src.users.models import UserModel

    admin_user = db.scalar(select(UserModel).where(UserModel.username == "authuser"))

    assert admin_user is not None

    admin_user.role = "admin"
    db.commit()

    response = client.patch(
        f"/users/admin/users/{admin_user.id}/status",
        headers=auth_headers,
        json={"is_active": False},
    )

    assert response.status_code == 400
    assert response.json()["message"] == "You cannot change your own status"
