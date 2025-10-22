"""
Tests for the delete participant endpoint of the High School Activities API
"""

import pytest
from fastapi import status
from urllib.parse import quote


class TestDeleteParticipantEndpoint:
    """Test cases for the DELETE /activities/{activity_name}/participants/{email} endpoint"""

    def test_delete_participant_success(self, client, reset_activities, sample_activity_name):
        """Test successfully removing a participant from an activity"""
        # Use an existing participant
        existing_email = "michael@mergington.edu"  # Already in Chess Club
        
        # Verify the participant exists initially
        response = client.get("/activities")
        data = response.json()
        initial_participants = data[sample_activity_name]["participants"]
        assert existing_email in initial_participants
        initial_count = len(initial_participants)

        # Remove the participant
        response = client.delete(
            f"/activities/{quote(sample_activity_name)}/participants/{quote(existing_email)}"
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        response_data = response.json()
        assert "message" in response_data
        assert existing_email in response_data["message"]
        assert sample_activity_name in response_data["message"]

        # Verify the participant was removed
        response = client.get("/activities")
        data = response.json()
        updated_participants = data[sample_activity_name]["participants"]
        assert existing_email not in updated_participants
        assert len(updated_participants) == initial_count - 1

    def test_delete_nonexistent_participant(self, client, reset_activities, sample_activity_name):
        """Test removing a participant who is not in the activity"""
        non_participant_email = "notregistered@mergington.edu"
        
        response = client.delete(
            f"/activities/{quote(sample_activity_name)}/participants/{quote(non_participant_email)}"
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        response_data = response.json()
        assert "detail" in response_data
        assert "not found" in response_data["detail"].lower()

    def test_delete_from_nonexistent_activity(self, client, reset_activities):
        """Test removing a participant from a non-existent activity"""
        fake_activity = "Nonexistent Activity"
        email = "test@mergington.edu"
        
        response = client.delete(
            f"/activities/{quote(fake_activity)}/participants/{quote(email)}"
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        response_data = response.json()
        assert "detail" in response_data
        assert "Activity not found" in response_data["detail"]

    def test_delete_participant_special_characters(self, client, reset_activities):
        """Test deleting participant with special characters in email"""
        # First, add a participant with special characters
        special_email = "test+user@mergington.edu"
        activity_name = "Art Club"
        
        # Sign them up first
        signup_response = client.post(
            f"/activities/{quote(activity_name)}/signup",
            params={"email": special_email}
        )
        assert signup_response.status_code == status.HTTP_200_OK
        
        # Now delete them
        response = client.delete(
            f"/activities/{quote(activity_name)}/participants/{quote(special_email)}"
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify they were removed
        response = client.get("/activities")
        data = response.json()
        participants = data[activity_name]["participants"]
        assert special_email not in participants

    def test_delete_participant_from_different_activities(self, client, reset_activities):
        """Test deleting the same email from different activities"""
        email = "multi@mergington.edu"
        activities = ["Chess Club", "Art Club"]
        
        # Sign up for multiple activities
        for activity in activities:
            response = client.post(
                f"/activities/{quote(activity)}/signup",
                params={"email": email}
            )
            assert response.status_code == status.HTTP_200_OK
        
        # Remove from one activity
        response = client.delete(
            f"/activities/{quote(activities[0])}/participants/{quote(email)}"
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Verify removed from first activity but still in second
        response = client.get("/activities")
        data = response.json()
        assert email not in data[activities[0]]["participants"]
        assert email in data[activities[1]]["participants"]

    def test_delete_all_participants_from_activity(self, client, reset_activities):
        """Test removing all participants from an activity"""
        activity_name = "Chess Club"
        
        # Get all current participants
        response = client.get("/activities")
        data = response.json()
        participants = data[activity_name]["participants"].copy()
        
        # Remove all participants
        for email in participants:
            response = client.delete(
                f"/activities/{quote(activity_name)}/participants/{quote(email)}"
            )
            assert response.status_code == status.HTTP_200_OK
        
        # Verify activity has no participants
        response = client.get("/activities")
        data = response.json()
        assert len(data[activity_name]["participants"]) == 0

    def test_delete_and_re_add_participant(self, client, reset_activities, sample_activity_name):
        """Test removing a participant and then adding them back"""
        email = "test@mergington.edu"
        
        # Add participant
        response = client.post(
            f"/activities/{quote(sample_activity_name)}/signup",
            params={"email": email}
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Remove participant
        response = client.delete(
            f"/activities/{quote(sample_activity_name)}/participants/{quote(email)}"
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Add participant back
        response = client.post(
            f"/activities/{quote(sample_activity_name)}/signup",
            params={"email": email}
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Verify they're back in the activity
        response = client.get("/activities")
        data = response.json()
        assert email in data[sample_activity_name]["participants"]