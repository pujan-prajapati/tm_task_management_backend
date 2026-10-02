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


# ============= TEST ASSIGN TASK =============================
def test_assign_task(client, auth_headers, second_auth_headers):
    # User A creates a task
    create_response = client.post(
        "/tasks",
        headers=auth_headers,
        json={
            "title": "Task To Assign",
            "description": "Testing task assignment",
            "priority": "medium",
            "status": "pending",
        },
    )

    assert create_response.status_code == 201

    task_id = create_response.json()["data"]["id"]

    # Get User B's ID
    me_response = client.get(
        "/users/me",
        headers=second_auth_headers,
    )

    assert me_response.status_code == 200

    second_user_id = me_response.json()["data"]["id"]

    # User A assigns the task to User B
    assign_response = client.post(
        f"/tasks/{task_id}/assign",
        headers=auth_headers,
        json={
            "user_id": second_user_id,
        },
    )

    assert assign_response.status_code == 200

    data = assign_response.json()

    assert data["success"] is True


# ============= TEST ASSIGN USER CAN VIEW TASK =============================
def test_assigned_user_can_view_task(client, auth_headers, second_auth_headers):
    # User A creates a task
    create_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Shared Task",
            "description": "Testing task assignment visibility",
            "priority": "medium",
            "status": "pending",
        },
    )

    assert create_response.status_code == 201

    task_id = create_response.json()["data"]["id"]

    # Get User B's ID
    me_response = client.get("/users/me", headers=second_auth_headers)

    assert me_response.status_code == 200

    second_user_id = me_response.json()["data"]["id"]

    # User A assigns the task to User B
    assign_response = client.post(
        f"/tasks/{task_id}/assign",
        headers=auth_headers,
        json={
            "user_id": second_user_id,
        },
    )

    assert assign_response.status_code == 200

    # user B views that task
    task_response = client.get(f"/tasks/{task_id}", headers=second_auth_headers)

    assert task_response.status_code == 200

    data = task_response.json()

    assert data["success"] is True
    assert data["data"]["id"] == task_id
    assert data["data"]["title"] == "Shared Task"


# ============= TEST ASSIGN USER CANNOT DELETE TASK =============================
def test_assigned_user_cannot_delete_task(
    client,
    auth_headers,
    second_auth_headers,
):
    create_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Shared Task",
            "description": "User B should not delete this",
            "priority": "medium",
            "status": "pending",
        },
    )

    assert create_response.status_code == 201
    task_id = create_response.json()["data"]["id"]

    me_response = client.get(
        "/users/me",
        headers=second_auth_headers,
    )

    assert me_response.status_code == 200
    second_user_id = me_response.json()["data"]["id"]

    assign_response = client.post(
        f"/tasks/{task_id}/assign",
        headers=auth_headers,
        json={"user_id": second_user_id},
    )

    assert assign_response.status_code == 200

    delete_response = client.delete(
        f"/tasks/{task_id}",
        headers=second_auth_headers,
    )

    assert delete_response.status_code == 403


# ============= TEST ASSIGN USER CAN UPDATE TASK =============================
def test_assigned_user_can_update_task(
    client,
    auth_headers,
    second_auth_headers,
):
    create_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Shared Task",
            "description": "Original description",
            "priority": "medium",
            "status": "pending",
        },
    )

    assert create_response.status_code == 201
    task_id = create_response.json()["data"]["id"]

    me_response = client.get(
        "/users/me",
        headers=second_auth_headers,
    )

    assert me_response.status_code == 200
    second_user_id = me_response.json()["data"]["id"]

    assign_response = client.post(
        f"/tasks/{task_id}/assign",
        headers=auth_headers,
        json={"user_id": second_user_id},
    )

    assert assign_response.status_code == 200

    update_response = client.put(
        f"/tasks/{task_id}",
        headers=second_auth_headers,
        json={
            "title": "Updated By Assignee",
            "description": "Assignee updated this task",
            "priority": "high",
            "status": "in_progress",
        },
    )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["success"] is True
    assert data["data"]["id"] == task_id
    assert data["data"]["title"] == "Updated By Assignee"
    assert data["data"]["description"] == "Assignee updated this task"
    assert data["data"]["priority"] == "high"
    assert data["data"]["status"] == "in_progress"


# ============= TEST OWNER CAN REMOVE ASSIGNEE =============================
def test_owner_can_remove_assignee(
    client,
    auth_headers,
    second_auth_headers,
):
    create_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Task With Assignee",
            "description": "Testing assignee removal",
            "priority": "medium",
            "status": "pending",
        },
    )

    assert create_response.status_code == 201
    task_id = create_response.json()["data"]["id"]

    me_response = client.get(
        "/users/me",
        headers=second_auth_headers,
    )

    assert me_response.status_code == 200
    second_user_id = me_response.json()["data"]["id"]

    assign_response = client.post(
        f"/tasks/{task_id}/assign",
        headers=auth_headers,
        json={"user_id": second_user_id},
    )

    assert assign_response.status_code == 200

    remove_response = client.delete(
        f"/tasks/{task_id}/assign/{second_user_id}",
        headers=auth_headers,
    )

    assert remove_response.status_code == 200

    data = remove_response.json()

    assert data["success"] is True


# ================== TEST REMOVED ASSIGNEE CANNOT VIEW TASK =============================
def test_removed_assignee_cannot_view_task(
    client,
    auth_headers,
    second_auth_headers,
):
    create_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Task To Unassign",
            "description": "Testing removed assignee access",
            "priority": "medium",
            "status": "pending",
        },
    )

    assert create_response.status_code == 201
    task_id = create_response.json()["data"]["id"]

    me_response = client.get(
        "/users/me",
        headers=second_auth_headers,
    )

    assert me_response.status_code == 200
    second_user_id = me_response.json()["data"]["id"]

    assign_response = client.post(
        f"/tasks/{task_id}/assign",
        headers=auth_headers,
        json={"user_id": second_user_id},
    )

    assert assign_response.status_code == 200

    remove_response = client.delete(
        f"/tasks/{task_id}/assign/{second_user_id}",
        headers=auth_headers,
    )

    assert remove_response.status_code == 200

    task_response = client.get(
        f"/tasks/{task_id}",
        headers=second_auth_headers,
    )

    assert task_response.status_code == 403


# ================== TEST CANNOT ASSIGN SAME USER TWICE =============================
def test_cannot_assign_same_user_twice(
    client,
    auth_headers,
    second_auth_headers,
):
    create_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Duplicate Assignment Test",
            "description": "Testing duplicate assignment",
            "priority": "medium",
            "status": "pending",
        },
    )

    assert create_response.status_code == 201
    task_id = create_response.json()["data"]["id"]

    me_response = client.get(
        "/users/me",
        headers=second_auth_headers,
    )

    assert me_response.status_code == 200
    second_user_id = me_response.json()["data"]["id"]

    first_assign = client.post(
        f"/tasks/{task_id}/assign",
        headers=auth_headers,
        json={"user_id": second_user_id},
    )

    assert first_assign.status_code == 200

    second_assign = client.post(
        f"/tasks/{task_id}/assign",
        headers=auth_headers,
        json={"user_id": second_user_id},
    )

    assert second_assign.status_code in [400, 409]


# ================== TEST CANNOT ASSIGN NONEXISTENT USER =============================
def test_cannot_assign_nonexistent_user(
    client,
    auth_headers,
):
    create_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Invalid Assignment Test",
            "description": "Testing nonexistent user assignment",
            "priority": "medium",
            "status": "pending",
        },
    )

    assert create_response.status_code == 201
    task_id = create_response.json()["data"]["id"]

    assign_response = client.post(
        f"/tasks/{task_id}/assign",
        headers=auth_headers,
        json={"user_id": 999999},
    )

    assert assign_response.status_code == 404


# ================== TEST CANNOT ASSIGN SELF =============================
def test_cannot_assign_task_to_self(
    client,
    auth_headers,
):
    create_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Self Assignment Test",
            "description": "Testing self assignment",
            "priority": "medium",
            "status": "pending",
        },
    )

    assert create_response.status_code == 201
    task_id = create_response.json()["data"]["id"]

    me_response = client.get(
        "/users/me",
        headers=auth_headers,
    )

    assert me_response.status_code == 200
    current_user_id = me_response.json()["data"]["id"]

    assign_response = client.post(
        f"/tasks/{task_id}/assign",
        headers=auth_headers,
        json={"user_id": current_user_id},
    )

    assert assign_response.status_code in [400, 409]


# ================== TEST ASSIGNED USER CAN ADD TAG =============================
def test_assigned_user_can_add_tag(
    client,
    auth_headers,
    second_auth_headers,
):
    tag_response = client.post(
        "/tags/",
        headers=auth_headers,
        json={
            "name": "AssigneeTag",
        },
    )

    assert tag_response.status_code == 201
    tag_id = tag_response.json()["data"]["id"]

    task_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Shared Tagged Task",
            "description": "Testing assignee tag access",
            "priority": "medium",
            "status": "pending",
        },
    )

    assert task_response.status_code == 201
    task_id = task_response.json()["data"]["id"]

    me_response = client.get(
        "/users/me",
        headers=second_auth_headers,
    )

    assert me_response.status_code == 200
    second_user_id = me_response.json()["data"]["id"]

    assign_response = client.post(
        f"/tasks/{task_id}/assign",
        headers=auth_headers,
        json={"user_id": second_user_id},
    )

    assert assign_response.status_code == 200

    add_tag_response = client.post(
        f"/tasks/{task_id}/tags",
        headers=second_auth_headers,
        json={
            "tag_ids": [tag_id],
        },
    )

    assert add_tag_response.status_code == 200
    assert add_tag_response.json()["success"] is True


# ================== TEST UNASSIGNED USER CANNOT ADD TAG =============================
def test_unassigned_user_cannot_add_tag(
    client,
    auth_headers,
    second_auth_headers,
):
    tag_response = client.post(
        "/tags/",
        headers=auth_headers,
        json={
            "name": "UnauthorizedTag",
        },
    )

    assert tag_response.status_code == 201
    tag_id = tag_response.json()["data"]["id"]

    task_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Private Tagged Task",
            "description": "Testing unauthorized tag access",
            "priority": "medium",
            "status": "pending",
        },
    )

    assert task_response.status_code == 201
    task_id = task_response.json()["data"]["id"]

    add_tag_response = client.post(
        f"/tasks/{task_id}/tags",
        headers=second_auth_headers,
        json={
            "tag_ids": [tag_id],
        },
    )

    assert add_tag_response.status_code == 403


# =================== TEST OWNER CAN REMOVE TAG =============================
def test_owner_can_remove_tag(
    client,
    auth_headers,
):
    tag_response = client.post(
        "/tags/",
        headers=auth_headers,
        json={
            "name": "RemoveTag",
        },
    )

    assert tag_response.status_code == 201
    tag_id = tag_response.json()["data"]["id"]

    task_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Task With Removable Tag",
            "description": "Testing tag removal",
            "priority": "medium",
            "status": "pending",
        },
    )

    assert task_response.status_code == 201
    task_id = task_response.json()["data"]["id"]

    add_tag_response = client.post(
        f"/tasks/{task_id}/tags",
        headers=auth_headers,
        json={
            "tag_ids": [tag_id],
        },
    )

    assert add_tag_response.status_code == 200

    remove_tag_response = client.delete(
        f"/tasks/{task_id}/tags/{tag_id}",
        headers=auth_headers,
    )

    assert remove_tag_response.status_code == 200
    assert remove_tag_response.json()["success"] is True


# =================== TEST ASSIGNED USER CAN REMOVE TAG =============================
def test_assigned_user_can_remove_tag(
    client,
    auth_headers,
    second_auth_headers,
):
    tag_response = client.post(
        "/tags/",
        headers=auth_headers,
        json={
            "name": "AssigneeRemoveTag",
        },
    )

    assert tag_response.status_code == 201
    tag_id = tag_response.json()["data"]["id"]

    task_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Shared Tagged Task",
            "description": "Testing assignee tag removal",
            "priority": "medium",
            "status": "pending",
        },
    )

    assert task_response.status_code == 201
    task_id = task_response.json()["data"]["id"]

    me_response = client.get(
        "/users/me",
        headers=second_auth_headers,
    )

    assert me_response.status_code == 200
    second_user_id = me_response.json()["data"]["id"]

    assign_response = client.post(
        f"/tasks/{task_id}/assign",
        headers=auth_headers,
        json={"user_id": second_user_id},
    )

    assert assign_response.status_code == 200

    add_tag_response = client.post(
        f"/tasks/{task_id}/tags",
        headers=auth_headers,
        json={"tag_ids": [tag_id]},
    )

    assert add_tag_response.status_code == 200

    remove_tag_response = client.delete(
        f"/tasks/{task_id}/tags/{tag_id}",
        headers=second_auth_headers,
    )

    assert remove_tag_response.status_code == 200
    assert remove_tag_response.json()["success"] is True


# =================== TEST OWNER CAN CREATE CATEGORY AND USE ON TASK =============================
def test_owner_can_create_category_and_use_on_task(
    client,
    auth_headers,
):
    category_response = client.post(
        "/categories/",
        headers=auth_headers,
        json={
            "name": "Work",
        },
    )

    assert category_response.status_code == 201
    category_id = category_response.json()["data"]["id"]

    task_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Categorized Task",
            "description": "Testing task category",
            "priority": "medium",
            "status": "pending",
            "category_id": category_id,
        },
    )

    assert task_response.status_code == 201

    data = task_response.json()

    assert data["success"] is True
    assert data["data"]["category_id"] == category_id


# =================== TEST USER CANNOT USE ANOTHER USERS CATEGORY =============================
def test_user_cannot_use_another_users_category(
    client,
    auth_headers,
    second_auth_headers,
):
    category_response = client.post(
        "/categories/",
        headers=auth_headers,
        json={
            "name": "Private Category",
        },
    )

    assert category_response.status_code == 201
    category_id = category_response.json()["data"]["id"]

    task_response = client.post(
        "/tasks/",
        headers=second_auth_headers,
        json={
            "title": "Unauthorized Category Task",
            "description": "Testing private category access",
            "priority": "medium",
            "status": "pending",
            "category_id": category_id,
        },
    )

    assert task_response.status_code == 403


# =================== TEST ASSIGNED USER CANNOT USE OWNERS CATEGORY =============================
def test_assigned_user_cannot_use_owners_category(
    client,
    auth_headers,
    second_auth_headers,
):
    category_response = client.post(
        "/categories/",
        headers=auth_headers,
        json={
            "name": "Owner Category",
        },
    )

    assert category_response.status_code == 201
    category_id = category_response.json()["data"]["id"]

    task_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Shared Category Task",
            "description": "Testing assignee category access",
            "priority": "medium",
            "status": "pending",
        },
    )

    assert task_response.status_code == 201
    task_id = task_response.json()["data"]["id"]

    me_response = client.get(
        "/users/me",
        headers=second_auth_headers,
    )

    assert me_response.status_code == 200
    second_user_id = me_response.json()["data"]["id"]

    assign_response = client.post(
        f"/tasks/{task_id}/assign",
        headers=auth_headers,
        json={"user_id": second_user_id},
    )

    assert assign_response.status_code == 200

    update_response = client.put(
        f"/tasks/{task_id}",
        headers=second_auth_headers,
        json={
            "title": "Updated Shared Task",
            "description": "Assignee attempting category change",
            "priority": "high",
            "status": "in_progress",
            "category_id": category_id,
        },
    )

    assert update_response.status_code == 403


# =================== TEST DELETE CATEGORY SETS TASK CATEGORY TO NULL =============================
def test_delete_category_sets_task_category_to_null(
    client,
    auth_headers,
):
    category_response = client.post(
        "/categories/",
        headers=auth_headers,
        json={
            "name": "Category To Delete",
        },
    )

    assert category_response.status_code == 201
    category_id = category_response.json()["data"]["id"]

    task_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Task With Category",
            "description": "Testing category deletion",
            "priority": "medium",
            "status": "pending",
            "category_id": category_id,
        },
    )

    assert task_response.status_code == 201
    task_id = task_response.json()["data"]["id"]

    delete_response = client.delete(
        f"/categories/{category_id}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 200

    task_after_delete = client.get(
        f"/tasks/{task_id}",
        headers=auth_headers,
    )

    assert task_after_delete.status_code == 200

    data = task_after_delete.json()

    assert data["data"]["id"] == task_id
    assert data["data"]["category_id"] is None


