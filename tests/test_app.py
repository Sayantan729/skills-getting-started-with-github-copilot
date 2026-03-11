"""
Tests for the FastAPI activities management API using AAA (Arrange-Act-Assert) pattern.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Fixture to provide a FastAPI TestClient instance."""
    return TestClient(app)


@pytest.fixture
def sample_activity():
    """Fixture to provide a sample activity name for testing."""
    return "Chess Club"


@pytest.fixture
def sample_email():
    """Fixture to provide a sample email for testing."""
    return "test@mergington.edu"


class TestGetActivities:
    """Test cases for GET /activities endpoint."""

    def test_get_activities_success(self, client):
        # Arrange
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class",
            "Basketball Team", "Tennis Club", "Art Studio",
            "Theater Club", "Debate Team", "Science Club"
        ]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9
        for activity in expected_activities:
            assert activity in data
            assert "description" in data[activity]
            assert "schedule" in data[activity]
            assert "max_participants" in data[activity]
            assert "participants" in data[activity]
            assert isinstance(data[activity]["participants"], list)


class TestSignupForActivity:
    """Test cases for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client, sample_activity, sample_email):
        # Arrange
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[sample_activity]["participants"]
        assert sample_email not in initial_participants

        # Act
        response = client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": sample_email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert sample_email in data["message"]
        assert sample_activity in data["message"]

        # Verify the email was added
        updated_response = client.get("/activities")
        updated_participants = updated_response.json()[sample_activity]["participants"]
        assert sample_email in updated_participants

    def test_signup_activity_not_found(self, client, sample_email):
        # Arrange
        nonexistent_activity = "Nonexistent Activity"

        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": sample_email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_email(self, client, sample_activity, sample_email):
        # Arrange
        # First signup
        client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": sample_email}
        )

        # Act
        # Second signup with same email
        response = client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": sample_email}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Student already signed up" in data["detail"]


class TestUnregisterFromActivity:
    """Test cases for DELETE /activities/{activity_name}/signup endpoint."""

    def test_unregister_success(self, client, sample_activity, sample_email):
        # Arrange
        # First sign up
        client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": sample_email}
        )

        # Act
        response = client.delete(
            f"/activities/{sample_activity}/signup",
            params={"email": sample_email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert sample_email in data["message"]
        assert sample_activity in data["message"]

        # Verify the email was removed
        updated_response = client.get("/activities")
        updated_participants = updated_response.json()[sample_activity]["participants"]
        assert sample_email not in updated_participants

    def test_unregister_activity_not_found(self, client, sample_email):
        # Arrange
        nonexistent_activity = "Nonexistent Activity"

        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": sample_email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_unregister_email_not_signed_up(self, client, sample_activity, sample_email):
        # Arrange
        # Ensure email is not signed up
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[sample_activity]["participants"]
        assert sample_email not in initial_participants

        # Act
        response = client.delete(
            f"/activities/{sample_activity}/signup",
            params={"email": sample_email}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Student not signed up for this activity" in data["detail"]