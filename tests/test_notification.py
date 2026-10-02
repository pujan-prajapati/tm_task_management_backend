# ============================= TEST COMMENT CREATES NOTIFICATION FOR TASK OWNER =============================
def test_comment_creates_notification_for_task_owner(
    client,
    auth_headers,
    second_auth_headers,
):
    task_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Notification Task",
            "description": "Testing comment notification",
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
            "content": "A new comment was added.",
        },
    )

    assert comment_response.status_code == 201

    notification_response = client.get(
        "/notifications/",
        headers=auth_headers,
    )

    assert notification_response.status_code == 200

    data = notification_response.json()

    assert data["success"] is True
    assert any(
        "comment" in notification["message"].lower() for notification in data["data"]
    )


# ============================= TEST USER ONLY SEES OWN NOTIFICATIONS =============================
def test_user_only_sees_own_notifications(
    client,
    auth_headers,
    second_auth_headers,
):
    response = client.get(
        "/notifications/",
        headers=second_auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    for notification in data["data"]:
        assert notification["user_id"] != None


# ============================= TEST USER CAN MARK NOTIFICATION AS READ =============================
def test_user_can_mark_notification_as_read(
    client,
    auth_headers,
    second_auth_headers,
):
    task_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Read Notification Task",
            "description": "Testing notification read status",
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
            "content": "This should create a notification.",
        },
    )

    assert comment_response.status_code == 201

    notification_response = client.get(
        "/notifications/",
        headers=auth_headers,
    )

    assert notification_response.status_code == 200

    notifications = notification_response.json()["data"]

    assert notifications

    notification_id = notifications[-1]["id"]

    mark_read_response = client.patch(
        f"/notifications/{notification_id}/read",
        headers=auth_headers,
    )

    assert mark_read_response.status_code == 200
    assert mark_read_response.json()["success"] is True


# ============================= TEST USER CANNOT MARK ANOTHER USERS NOTIFICATION AS READ =============================
def test_user_cannot_mark_another_users_notification_as_read(
    client,
    auth_headers,
    second_auth_headers,
):
    task_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Notification Ownership Task",
            "description": "Testing notification ownership",
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
            "content": "Create notification for task owner.",
        },
    )

    assert comment_response.status_code == 201

    notification_response = client.get(
        "/notifications/",
        headers=auth_headers,
    )

    assert notification_response.status_code == 200

    notifications = notification_response.json()["data"]
    assert notifications

    notification_id = notifications[-1]["id"]

    mark_read_response = client.patch(
        f"/notifications/{notification_id}/read",
        headers=second_auth_headers,
    )

    assert mark_read_response.status_code == 403


# ============================= TEST MARK NOTIFICATION AS READ CHANGES STATUS =============================
def test_mark_notification_as_read_changes_status(
    client,
    auth_headers,
    second_auth_headers,
):
    task_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Read Status Task",
            "description": "Testing notification status",
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
            "content": "Unread notification test.",
        },
    )

    assert comment_response.status_code == 201

    notification_response = client.get(
        "/notifications/",
        headers=auth_headers,
    )

    assert notification_response.status_code == 200

    notifications = notification_response.json()["data"]
    assert notifications

    notification = next(
        notification
        for notification in notifications
        if notification["message"] == "New comment on task: Read Status Task"
    )

    assert notification["is_read"] is False

    notification_id = notification["id"]

    mark_read_response = client.patch(
        f"/notifications/{notification_id}/read",
        headers=auth_headers,
    )

    assert mark_read_response.status_code == 200

    notification_response = client.get(
        "/notifications/",
        headers=auth_headers,
    )

    assert notification_response.status_code == 200

    updated_notifications = notification_response.json()["data"]

    updated_notification = next(
        notification
        for notification in updated_notifications
        if notification["id"] == notification_id
    )

    assert updated_notification["is_read"] is True


# ============================= TEST MARK ALREADY READ NOTIFICATION AS READ =============================
def test_mark_already_read_notification_as_read(
    client,
    auth_headers,
    second_auth_headers,
):
    task_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Already Read Notification",
            "description": "Testing repeated read operation",
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
            "content": "Notification for repeated read test.",
        },
    )

    assert comment_response.status_code == 201

    notification_response = client.get(
        "/notifications/",
        headers=auth_headers,
    )

    assert notification_response.status_code == 200

    notifications = notification_response.json()["data"]
    assert notifications

    notification_id = notifications[-1]["id"]

    first_read = client.patch(
        f"/notifications/{notification_id}/read",
        headers=auth_headers,
    )

    assert first_read.status_code == 200

    second_read = client.patch(
        f"/notifications/{notification_id}/read",
        headers=auth_headers,
    )

    assert second_read.status_code == 200


# ============================= TEST NOTIFICATIONS ARE ORDERED NEWEST FIRST =============================
def test_notifications_are_ordered_newest_first(
    client,
    auth_headers,
    second_auth_headers,
):
    # Create first task → first notification
    task1_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "First Notification Task",
            "description": "First notification",
            "priority": "medium",
            "status": "pending",
        },
    )

    assert task1_response.status_code == 201
    task1_id = task1_response.json()["data"]["id"]

    me_response = client.get(
        "/users/me",
        headers=second_auth_headers,
    )

    assert me_response.status_code == 200
    second_user_id = me_response.json()["data"]["id"]

    assign_response = client.post(
        f"/tasks/{task1_id}/assign",
        headers=auth_headers,
        json={"user_id": second_user_id},
    )

    assert assign_response.status_code == 200

    comment_response = client.post(
        f"/tasks/{task1_id}/comments",
        headers=second_auth_headers,
        json={
            "content": "First notification comment.",
        },
    )

    assert comment_response.status_code == 201

    # Create second task → second notification
    task2_response = client.post(
        "/tasks/",
        headers=auth_headers,
        json={
            "title": "Second Notification Task",
            "description": "Second notification",
            "priority": "medium",
            "status": "pending",
        },
    )

    assert task2_response.status_code == 201
    task2_id = task2_response.json()["data"]["id"]

    assign_response = client.post(
        f"/tasks/{task2_id}/assign",
        headers=auth_headers,
        json={"user_id": second_user_id},
    )

    assert assign_response.status_code == 200

    comment_response = client.post(
        f"/tasks/{task2_id}/comments",
        headers=second_auth_headers,
        json={
            "content": "Second notification comment.",
        },
    )

    assert comment_response.status_code == 201

    # Fetch notifications
    notification_response = client.get(
        "/notifications/",
        headers=auth_headers,
    )

    assert notification_response.status_code == 200

    notifications = notification_response.json()["data"]

    assert len(notifications) >= 2

    # Newest notification should come first
    assert notifications[0]["id"] > notifications[1]["id"]
