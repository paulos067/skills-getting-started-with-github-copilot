"""
Tests for the signup endpoint of the High School Activities API
"""

import pytest
from fastapi import status
from urllib.parse import quote


class TestSignupEndpoint:
    """Test cases for the /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client, reset_activities, sample_email, sample_activity_name):
        """Test successful signup for an activity"""
        # First, verify the user is not already signed up
        response = client.get("/activities")
        data = response.json()
        initial_participants = data[sample_activity_name]["participants"].copy()
        assert sample_email not in initial_participants

        # Sign up the user
        response = client.post(
            f"/activities/{quote(sample_activity_name)}/signup",
            params={"email": sample_email}
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        response_data = response.json()
        assert "message" in response_data
        assert sample_email in response_data["message"]
        assert sample_activity_name in response_data["message"]

        # Verify the user was added to the activity
        response = client.get("/activities")
        data = response.json()
        updated_participants = data[sample_activity_name]["participants"]
        assert sample_email in updated_participants
        assert len(updated_participants) == len(initial_participants) + 1

    def test_signup_duplicate_user(self, client, reset_activities, sample_activity_name):
        """Test that signing up a user who is already registered fails"""
        # Use an existing participant
        existing_email = "michael@mergington.edu"  # Already in Chess Club
        
        response = client.post(
            f"/activities/{quote(sample_activity_name)}/signup",
            params={"email": existing_email}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        response_data = response.json()
        assert "detail" in response_data
        assert "already signed up" in response_data["detail"].lower()

    def test_signup_nonexistent_activity(self, client, reset_activities, sample_email):
        """Test signing up for a non-existent activity"""
        fake_activity = "Fake Activity"
        
        response = client.post(
            f"/activities/{quote(fake_activity)}/signup",
            params={"email": sample_email}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        response_data = response.json()
        assert "detail" in response_data
        assert "Activity not found" in response_data["detail"]

    def test_signup_special_characters_in_activity_name(self, client, reset_activities):
        """Test signup with special characters in activity name (URL encoding)"""
        # Create a test with an activity that has spaces (which should be URL encoded)
        activity_name = "Art Club"  # Contains space
        test_email = "artist@mergington.edu"
        
        response = client.post(
            f"/activities/{quote(activity_name)}/signup",
            params={"email": test_email}
        )
        
        assert response.status_code == status.HTTP_200_OK

    def test_signup_special_characters_in_email(self, client, reset_activities, sample_activity_name):
        """Test signup with special characters in email (URL encoding)"""
        special_email = "test+user@mergington.edu"
        
        response = client.post(
            f"/activities/{quote(sample_activity_name)}/signup",
            params={"email": special_email}
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify the email was properly stored
        response = client.get("/activities")
        data = response.json()
        participants = data[sample_activity_name]["participants"]
        assert special_email in participants

    def test_signup_empty_email(self, client, reset_activities, sample_activity_name):
        """Test signup with empty email"""
        response = client.post(
            f"/activities/{quote(sample_activity_name)}/signup",
            params={"email": ""}
        )
        
        # Should still work (empty string is valid), but might want to add validation later
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_signup_multiple_users_same_activity(self, client, reset_activities, sample_activity_name):
        """Test signing up multiple different users for the same activity"""
        emails = ["user1@mergington.edu", "user2@mergington.edu", "user3@mergington.edu"]
        
        # Get initial participant count
        response = client.get("/activities")
        initial_count = len(response.json()[sample_activity_name]["participants"])
        
        # Sign up multiple users
        for email in emails:
            response = client.post(
                f"/activities/{quote(sample_activity_name)}/signup",
                params={"email": email}
            )
            assert response.status_code == status.HTTP_200_OK
        
        # Verify all users were added
        response = client.get("/activities")
        data = response.json()
        participants = data[sample_activity_name]["participants"]
        
        for email in emails:
            assert email in participants
        
        assert len(participants) == initial_count + len(emails)