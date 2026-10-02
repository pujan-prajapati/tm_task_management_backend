# =================== TEST TASK OWNER CAN CREATE COMMENT =============================
def test_task_owner_can_create_comment(
    client,
    auth_headers,
):
    task_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Commented Task",
            "description": "Testing comments",
            "priority": "medium",
            "status": "pending",
        },
    )

    assert task_response.status_code == 201
    task_id = task_response.json()["data"]["id"]

    comment_response = client.post(
        f"/tasks/{task_id}/comments",
        headers=auth_headers,
        json={
            "content": "This is my first comment.",
        },
    )

    assert comment_response.status_code == 201

    data = comment_response.json()

    assert data["success"] is True
    assert data["data"]["content"] == "This is my first comment."
    assert data["data"]["task_id"] == task_id


# =================== TEST ASSIGNED USER CAN CREATE COMMENT =============================
def test_assigned_user_can_create_comment(
    client,
    auth_headers,
    second_auth_headers,
):
    task_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Shared Comment Task",
            "description": "Testing assignee comments",
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

    comment_response = client.post(
        f"/tasks/{task_id}/comments",
        headers=second_auth_headers,
        json={
            "content": "Comment from the assigned user.",
        },
    )

    assert comment_response.status_code == 201

    data = comment_response.json()

    assert data["success"] is True
    assert data["data"]["content"] == "Comment from the assigned user."
    assert data["data"]["task_id"] == task_id


# =================== TEST UNASSIGNED USER CANNOT CREATE COMMENT =============================
def test_unassigned_user_cannot_create_comment(
    client,
    auth_headers,
    second_auth_headers,
):
    task_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Private Comment Task",
            "description": "Testing comment permissions",
            "priority": "medium",
            "status": "pending",
        },
    )

    assert task_response.status_code == 201
    task_id = task_response.json()["data"]["id"]

    comment_response = client.post(
        f"/tasks/{task_id}/comments",
        headers=second_auth_headers,
        json={
            "content": "This should not be allowed.",
        },
    )

    assert comment_response.status_code == 403


# =================== TEST COMMENT AUTHOR CAN UPDATE COMMENT =============================
def test_comment_author_can_update_comment(
    client,
    auth_headers,
):
    task_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Comment Update Task",
            "description": "Testing comment updates",
            "priority": "medium",
            "status": "pending",
        },
    )

    assert task_response.status_code == 201
    task_id = task_response.json()["data"]["id"]

    comment_response = client.post(
        f"/tasks/{task_id}/comments",
        headers=auth_headers,
        json={
            "content": "Original comment",
        },
    )

    assert comment_response.status_code == 201
    comment_id = comment_response.json()["data"]["id"]

    update_response = client.put(
        f"/tasks/{task_id}/comments/{comment_id}",
        headers=auth_headers,
        json={
            "content": "Updated comment",
        },
    )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["success"] is True
    assert data["data"]["id"] == comment_id
    assert data["data"]["content"] == "Updated comment"


# =================== TEST USER CANNOT UPDATE ANOTHER USERS COMMENT =============================
def test_user_cannot_update_another_users_comment(
    client,
    auth_headers,
    second_auth_headers,
):
    task_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Comment Permission Task",
            "description": "Testing comment ownership",
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

    comment_response = client.post(
        f"/tasks/{task_id}/comments",
        headers=auth_headers,
        json={
            "content": "Comment owned by User A",
        },
    )

    assert comment_response.status_code == 201
    comment_id = comment_response.json()["data"]["id"]

    update_response = client.put(
        f"/tasks/{task_id}/comments/{comment_id}",
        headers=second_auth_headers,
        json={
            "content": "User B trying to edit User A's comment",
        },
    )

    assert update_response.status_code == 404


# =================== TEST COMMENT AUTHOR CAN DELETE COMMENT =============================
def test_comment_author_can_delete_comment(
    client,
    auth_headers,
):
    task_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Comment Delete Task",
            "description": "Testing comment deletion",
            "priority": "medium",
            "status": "pending",
        },
    )

    assert task_response.status_code == 201
    task_id = task_response.json()["data"]["id"]

    comment_response = client.post(
        f"/tasks/{task_id}/comments",
        headers=auth_headers,
        json={
            "content": "Comment to delete",
        },
    )

    assert comment_response.status_code == 201
    comment_id = comment_response.json()["data"]["id"]

    delete_response = client.delete(
        f"/tasks/{task_id}/comments/{comment_id}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 200

    data = delete_response.json()

    assert data["success"] is True


# =================== TEST USER CANNOT DELETE ANOTHER USERS COMMENT =============================
def test_user_cannot_delete_another_users_comment(
    client,
    auth_headers,
    second_auth_headers,
):
    task_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Comment Delete Permission",
            "description": "Testing comment delete ownership",
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

    comment_response = client.post(
        f"/tasks/{task_id}/comments",
        headers=auth_headers,
        json={
            "content": "User A's comment",
        },
    )

    assert comment_response.status_code == 201
    comment_id = comment_response.json()["data"]["id"]

    delete_response = client.delete(
        f"/tasks/{task_id}/comments/{comment_id}",
        headers=second_auth_headers,
    )

    assert delete_response.status_code == 404


# ==================== TEST TASK OWNER CAN LIST COMMENTS =============================
def test_task_owner_can_list_comments(
    client,
    auth_headers,
):
    task_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Comment List Task",
            "description": "Testing comment listing",
            "priority": "medium",
            "status": "pending",
        },
    )

    assert task_response.status_code == 201
    task_id = task_response.json()["data"]["id"]

    first_comment = client.post(
        f"/tasks/{task_id}/comments",
        headers=auth_headers,
        json={"content": "First comment"},
    )

    second_comment = client.post(
        f"/tasks/{task_id}/comments",
        headers=auth_headers,
        json={"content": "Second comment"},
    )

    assert first_comment.status_code == 201
    assert second_comment.status_code == 201

    response = client.get(
        f"/tasks/{task_id}/comments",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert len(data["data"]) >= 2


# ==================== TEST UNASSIGNED USER CANNOT LIST COMMENTS =============================
def test_unassigned_user_cannot_list_comments(
    client,
    auth_headers,
    second_auth_headers,
):
    task_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Private Comment List",
            "description": "Testing comment list permissions",
            "priority": "medium",
            "status": "pending",
        },
    )

    assert task_response.status_code == 201
    task_id = task_response.json()["data"]["id"]

    comment_response = client.post(
        f"/tasks/{task_id}/comments",
        headers=auth_headers,
        json={
            "content": "Private comment",
        },
    )

    assert comment_response.status_code == 201

    response = client.get(
        f"/tasks/{task_id}/comments",
        headers=second_auth_headers,
    )

    assert response.status_code == 403


# ============================= TEST CANNOT UPDATE COMMENT FROM WRONG TASK =============================
def test_cannot_update_comment_from_wrong_task(
    client,
    auth_headers,
):
    first_task_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "First Task",
            "description": "Task containing the comment",
            "priority": "medium",
            "status": "pending",
        },
    )

    assert first_task_response.status_code == 201
    first_task_id = first_task_response.json()["data"]["id"]

    second_task_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Second Task",
            "description": "Different task",
            "priority": "medium",
            "status": "pending",
        },
    )

    assert second_task_response.status_code == 201
    second_task_id = second_task_response.json()["data"]["id"]

    comment_response = client.post(
        f"/tasks/{first_task_id}/comments",
        headers=auth_headers,
        json={
            "content": "Comment belongs to first task",
        },
    )

    assert comment_response.status_code == 201
    comment_id = comment_response.json()["data"]["id"]

    update_response = client.put(
        f"/tasks/{second_task_id}/comments/{comment_id}",
        headers=auth_headers,
        json={
            "content": "Trying to move comment to another task",
        },
    )

    assert update_response.status_code == 404


# ============================= TEST CANNOT DELETE COMMENT FROM WRONG TASK =============================
def test_cannot_delete_comment_from_wrong_task(
    client,
    auth_headers,
):
    first_task_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "First Task",
            "description": "Task containing the comment",
            "priority": "medium",
            "status": "pending",
        },
    )

    assert first_task_response.status_code == 201
    first_task_id = first_task_response.json()["data"]["id"]

    second_task_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Second Task",
            "description": "Different task",
            "priority": "medium",
            "status": "pending",
        },
    )

    assert second_task_response.status_code == 201
    second_task_id = second_task_response.json()["data"]["id"]

    comment_response = client.post(
        f"/tasks/{first_task_id}/comments",
        headers=auth_headers,
        json={
            "content": "Comment belongs to first task",
        },
    )

    assert comment_response.status_code == 201
    comment_id = comment_response.json()["data"]["id"]

    delete_response = client.delete(
        f"/tasks/{second_task_id}/comments/{comment_id}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 404
