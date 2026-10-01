# =============== TEST CREATE TASK ==========================
def test_create_task(client, auth_headers):
    task_response = client.post(
        "/tasks",
        headers=auth_headers,
        json={
            "title": "Test Task",
            "description": "This is a test task",
            "priority": "high",
            "status": "pending",
        },
    )

    assert task_response.status_code == 201
    data = task_response.json()

    assert data["success"] is True
    assert data["message"] == "Task Created Successfully"
    assert data["data"]["title"] == "Test Task"
    assert data["data"]["description"] == "This is a test task"
    assert data["data"]["priority"] == "high"
    assert data["data"]["status"] == "pending"


# ============= TEST GET TASKS =============================
def test_get_tasks(client, auth_headers):
    responnse = client.get("/tasks/", headers=auth_headers)
    assert responnse.status_code == 200
    data = responnse.json()

    assert data["success"] is True
    assert data["message"] == "Tasks Fetched Successfully"


# ============= TEST GET ONE TASK =============================
def test_get_single_task(client, auth_headers):
    create_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Single Task",
            "description": "Testing single task retrieval",
            "priority": "high",
            "status": "pending",
        },
    )

    assert create_response.status_code == 201

    created_task = create_response.json()["data"]
    task_id = created_task["id"]

    response = client.get(f"/tasks/{task_id}", headers=auth_headers)

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["data"]["id"] == task_id
    assert data["data"]["title"] == "Single Task"
    assert data["data"]["description"] == "Testing single task retrieval"


# ============= TEST UPDATE A TASK =============================
def test_update_task(client, auth_headers):
    create_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Original Title",
            "description": "Original description",
            "priority": "low",
            "status": "pending",
        },
    )

    assert create_response.status_code == 201

    task_id = create_response.json()["data"]["id"]

    update_response = client.put(
        f"/tasks/{task_id}",
        headers=auth_headers,
        json={
            "title": "Updated Title",
            "description": "Updated description",
            "priority": "high",
            "status": "in_progress",
        },
    )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["success"] is True
    assert data["data"]["id"] == task_id
    assert data["data"]["title"] == "Updated Title"
    assert data["data"]["description"] == "Updated description"
    assert data["data"]["priority"] == "high"
    assert data["data"]["status"] == "in_progress"


# ============= TEST DELETE A TASK =============================
def test_delete_task(client, auth_headers):
    create_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Task To Delete",
            "description": "This task will be deleted",
            "priority": "medium",
            "status": "pending",
        },
    )

    assert create_response.status_code == 201

    task_id = create_response.json()["data"]["id"]

    delete_response = client.delete(f"/tasks/{task_id}", headers=auth_headers)

    assert delete_response.status_code == 200

    data = delete_response.json()

    assert data["success"] is True
    assert data["message"] == "Task Deleted Successfully"

    get_response = client.get(f"/tasks/{task_id}", headers=auth_headers)

    assert get_response.status_code == 404


# ============= TEST USER CANNOT UPDATE ANOTHER USERS TASK =============================
def test_user_cannot_update_another_users_task(
    client, auth_headers, second_auth_headers
):
    # User A creates the task
    create_response = client.post(
        "/tasks",
        headers=auth_headers,
        json={
            "title": "User A Task",
            "description": "Owned by User A",
            "priority": "medium",
            "status": "pending",
        },
    )

    assert create_response.status_code == 201

    task_id = create_response.json()["data"]["id"]

    # User B tries to update User A's task
    update_response = client.put(
        f"/tasks/{task_id}",
        headers=second_auth_headers,
        json={
            "title": "Hacked Task",
            "description": "User B should not be able to do this",
            "priority": "high",
            "status": "completed",
        },
    )

    assert update_response.status_code == 403


# ============= TEST USER CANNOT DELETE ANOTHER USERS TASK =============================
def test_user_cannot_delete_another_users_task(
    client,
    auth_headers,
    second_auth_headers,
):
    # User A creates the task
    create_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "User A Task",
            "description": "Owned by User A",
            "priority": "medium",
            "status": "pending",
        },
    )

    assert create_response.status_code == 201

    task_id = create_response.json()["data"]["id"]

    # User B tries to delete User A's task
    delete_response = client.delete(
        f"/tasks/{task_id}",
        headers=second_auth_headers,
    )

    assert delete_response.status_code == 403


# ============= TEST TASK NOT FOUND =============================
def test_get_task_not_found(client, auth_headers):
    response = client.get(
        "/tasks/999999",
        headers=auth_headers,
    )

    assert response.status_code == 404

    data = response.json()

    assert data["message"] == "Task not found"
