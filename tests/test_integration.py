"""
Integration tests for the High School Activities API

These tests verify that the API endpoints work together correctly
and test realistic user scenarios.
"""

import pytest
from fastapi import status
from urllib.parse import quote


class TestAPIIntegration:
    """Integration test cases that test multiple endpoints working together"""

    def test_complete_user_journey(self, client, reset_activities):
        """Test a complete user journey: view activities, sign up, then leave"""
        email = "journey@mergington.edu"
        activity_name = "Chess Club"
        
        # 1. Get all activities
        response = client.get("/activities")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        initial_participants = len(data[activity_name]["participants"])
        
        # 2. Sign up for an activity
        response = client.post(
            f"/activities/{quote(activity_name)}/signup",
            params={"email": email}
        )
        assert response.status_code == status.HTTP_200_OK
        
        # 3. Verify signup by checking activities again
        response = client.get("/activities")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert email in data[activity_name]["participants"]
        assert len(data[activity_name]["participants"]) == initial_participants + 1
        
        # 4. Leave the activity
        response = client.delete(
            f"/activities/{quote(activity_name)}/participants/{quote(email)}"
        )
        assert response.status_code == status.HTTP_200_OK
        
        # 5. Verify removal
        response = client.get("/activities")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert email not in data[activity_name]["participants"]
        assert len(data[activity_name]["participants"]) == initial_participants

    def test_multiple_activities_signup(self, client, reset_activities):
        """Test signing up for multiple activities"""
        email = "multi@mergington.edu"
        activities = ["Chess Club", "Programming Class", "Art Club"]
        
        # Sign up for multiple activities
        for activity in activities:
            response = client.post(
                f"/activities/{quote(activity)}/signup",
                params={"email": email}
            )
            assert response.status_code == status.HTTP_200_OK
        
        # Verify user is in all activities
        response = client.get("/activities")
        data = response.json()
        
        for activity in activities:
            assert email in data[activity]["participants"]

    def test_activity_capacity_management(self, client, reset_activities):
        """Test that we can track how many spots are left in activities"""
        # Get initial state
        response = client.get("/activities")
        data = response.json()
        
        activity_name = "Chess Club"
        max_participants = data[activity_name]["max_participants"]
        current_participants = len(data[activity_name]["participants"])
        spots_left = max_participants - current_participants
        
        # Add participants until we approach capacity
        emails_to_add = [f"student{i}@mergington.edu" for i in range(min(spots_left, 5))]
        
        for email in emails_to_add:
            response = client.post(
                f"/activities/{quote(activity_name)}/signup",
                params={"email": email}
            )
            assert response.status_code == status.HTTP_200_OK
        
        # Verify all participants were added
        response = client.get("/activities")
        data = response.json()
        participants = data[activity_name]["participants"]
        
        for email in emails_to_add:
            assert email in participants

    def test_error_handling_consistency(self, client, reset_activities):
        """Test that error responses are consistent across endpoints"""
        fake_activity = "Nonexistent Activity"
        fake_email = "fake@mergington.edu"
        
        # Test 404 responses are consistent
        signup_response = client.post(
            f"/activities/{quote(fake_activity)}/signup",
            params={"email": fake_email}
        )
        
        delete_response = client.delete(
            f"/activities/{quote(fake_activity)}/participants/{quote(fake_email)}"
        )
        
        assert signup_response.status_code == status.HTTP_404_NOT_FOUND
        assert delete_response.status_code == status.HTTP_404_NOT_FOUND
        
        # Both should have detail field
        assert "detail" in signup_response.json()
        assert "detail" in delete_response.json()

    def test_data_persistence_across_requests(self, client, reset_activities):
        """Test that data changes persist across multiple requests"""
        email = "persist@mergington.edu"
        activity_name = "Programming Class"
        
        # Make a change
        response = client.post(
            f"/activities/{quote(activity_name)}/signup",
            params={"email": email}
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Verify persistence across multiple GET requests
        for _ in range(3):
            response = client.get("/activities")
            data = response.json()
            assert email in data[activity_name]["participants"]

    def test_concurrent_operations_simulation(self, client, reset_activities):
        """Test simulating concurrent operations on the same activity"""
        activity_name = "Gym Class"
        emails = [f"concurrent{i}@mergington.edu" for i in range(5)]
        
        # Simulate multiple users signing up "simultaneously"
        responses = []
        for email in emails:
            response = client.post(
                f"/activities/{quote(activity_name)}/signup",
                params={"email": email}
            )
            responses.append((email, response))
        
        # All should succeed (since we don't have true concurrency in tests)
        for email, response in responses:
            assert response.status_code == status.HTTP_200_OK
        
        # Verify all users were added
        response = client.get("/activities")
        data = response.json()
        participants = data[activity_name]["participants"]
        
        for email in emails:
            assert email in participants

    def test_edge_case_empty_activity_operations(self, client, reset_activities):
        """Test operations on an activity with no participants"""
        # First, create an activity with no participants by removing all
        activity_name = "Science Olympiad"
        
        # Get current participants
        response = client.get("/activities")
        data = response.json()
        participants = data[activity_name]["participants"].copy()
        
        # Remove all participants
        for email in participants:
            response = client.delete(
                f"/activities/{quote(activity_name)}/participants/{quote(email)}"
            )
            assert response.status_code == status.HTTP_200_OK
        
        # Verify activity is empty
        response = client.get("/activities")
        data = response.json()
        assert len(data[activity_name]["participants"]) == 0
        
        # Test operations on empty activity
        new_email = "first@mergington.edu"
        
        # Should be able to add to empty activity
        response = client.post(
            f"/activities/{quote(activity_name)}/signup",
            params={"email": new_email}
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Should be able to remove from activity with one participant
        response = client.delete(
            f"/activities/{quote(activity_name)}/participants/{quote(new_email)}"
        )
        assert response.status_code == status.HTTP_200_OK