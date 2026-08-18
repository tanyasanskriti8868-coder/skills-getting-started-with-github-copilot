"""
Test cases for Mergington High School Activities API

Tests are structured using the AAA (Arrange-Act-Assert) testing pattern.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Provide a test client for the API."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to a known state before each test."""
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        }
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for getting activities list."""
    
    def test_get_activities_returns_200(self, client):
        """Arrange: Client is ready
           Act: Make GET request to /activities
           Assert: Response status code is 200"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self, client):
        """Arrange: Client is ready
           Act: Make GET request to /activities
           Assert: Response contains a dictionary of activities"""
        response = client.get("/activities")
        data = response.json()
        assert isinstance(data, dict)
    
    def test_get_activities_contains_known_activities(self, client):
        """Arrange: Client is ready
           Act: Make GET request to /activities
           Assert: Response contains expected activities"""
        response = client.get("/activities")
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_get_activities_has_required_fields(self, client):
        """Arrange: Client is ready
           Act: Make GET request to /activities
           Assert: Each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_details in data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details


class TestSignupForActivity:
    """Tests for signing up for an activity."""
    
    def test_signup_success(self, client, reset_activities):
        """Arrange: Client and test email
           Act: POST to /activities/{activity}/signup
           Assert: Response is 200 and contains success message"""
        email = "newstudent@mergington.edu"
        activity = "Chess Club"
        
        response = client.post(
            f"/activities/{activity}/signup?email={email}",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    def test_signup_adds_participant(self, client, reset_activities):
        """Arrange: Client and test email not yet signed up
           Act: POST to /activities/{activity}/signup
           Assert: Student is added to participants list"""
        email = "newstudent@mergington.edu"
        activity = "Chess Club"
        
        client.post(f"/activities/{activity}/signup?email={email}")
        
        response = client.get("/activities")
        data = response.json()
        assert email in data[activity]["participants"]
    
    def test_signup_to_nonexistent_activity_fails(self, client):
        """Arrange: Client and test email
           Act: POST to /activities/NonExistent/signup
           Assert: Response is 404"""
        email = "student@mergington.edu"
        
        response = client.post(
            f"/activities/NonExistent/signup?email={email}"
        )
        
        assert response.status_code == 404
    
    def test_duplicate_signup_fails(self, client, reset_activities):
        """Arrange: Student already signed up for activity
           Act: Try to signup again
           Assert: Response is 400 with error message"""
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()


class TestUnregisterFromActivity:
    """Tests for unregistering from an activity."""
    
    def test_unregister_success(self, client, reset_activities):
        """Arrange: Student is signed up for activity
           Act: DELETE /activities/{activity}/unregister
           Assert: Response is 200 and student is removed"""
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Arrange: Student is signed up for activity
           Act: DELETE /activities/{activity}/unregister
           Assert: Student is removed from participants list"""
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        client.delete(f"/activities/{activity}/unregister?email={email}")
        
        response = client.get("/activities")
        data = response.json()
        assert email not in data[activity]["participants"]
    
    def test_unregister_from_nonexistent_activity_fails(self, client):
        """Arrange: Client and test email
           Act: DELETE to /activities/NonExistent/unregister
           Assert: Response is 404"""
        email = "student@mergington.edu"
        
        response = client.delete(
            f"/activities/NonExistent/unregister?email={email}"
        )
        
        assert response.status_code == 404
    
    def test_unregister_not_signed_up_fails(self, client, reset_activities):
        """Arrange: Student not signed up for activity
           Act: Try to unregister
           Assert: Response is 400 with error message"""
        email = "notstudent@mergington.edu"
        activity = "Chess Club"
        
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"].lower()


class TestRootEndpoint:
    """Tests for the root endpoint."""
    
    def test_root_redirects_to_static(self, client):
        """Arrange: Client is ready
           Act: Make GET request to /
           Assert: Response redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code in [301, 302, 303, 307, 308]
