import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


TEST_ACTIVITY = "Test Activity"
TEST_EMAIL = "student@example.edu"


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def activity(monkeypatch):
    test_activity = {
        "description": "Activity used by API tests",
        "schedule": "Fridays",
        "max_participants": 10,
        "participants": [],
    }
    monkeypatch.setitem(activities, TEST_ACTIVITY, test_activity)
    return test_activity


def test_get_activities_returns_available_activities(client, activity):
    # Arrange
    expected_activity = activity

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json()[TEST_ACTIVITY] == expected_activity


def test_signup_adds_participant(client, activity):
    # Arrange
    email = TEST_EMAIL

    # Act
    response = client.post(
        f"/activities/{TEST_ACTIVITY}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {TEST_ACTIVITY}"}
    assert email in activity["participants"]


def test_signup_rejects_duplicate_participant(client, activity):
    # Arrange
    activity["participants"].append(TEST_EMAIL)

    # Act
    response = client.post(
        f"/activities/{TEST_ACTIVITY}/signup",
        params={"email": TEST_EMAIL},
    )

    # Assert
    assert response.status_code == 400
    assert activity["participants"] == [TEST_EMAIL]


def test_signup_rejects_unknown_activity(client):
    # Arrange
    unknown_activity = "Unknown Activity"

    # Act
    response = client.post(
        f"/activities/{unknown_activity}/signup",
        params={"email": TEST_EMAIL},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client, activity):
    # Arrange
    activity["participants"].extend([TEST_EMAIL, TEST_EMAIL])

    # Act
    response = client.delete(
        f"/activities/{TEST_ACTIVITY}/signup",
        params={"email": TEST_EMAIL},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {TEST_EMAIL} from {TEST_ACTIVITY}"
    }
    assert TEST_EMAIL not in activity["participants"]


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    unknown_activity = "Unknown Activity"

    # Act
    response = client.delete(
        f"/activities/{unknown_activity}/signup",
        params={"email": TEST_EMAIL},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_rejects_unregistered_participant(client, activity):
    # Arrange
    email = TEST_EMAIL

    # Act
    response = client.delete(
        f"/activities/{TEST_ACTIVITY}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
    assert activity["participants"] == []
