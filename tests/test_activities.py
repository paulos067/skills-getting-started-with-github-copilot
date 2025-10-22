"""
Tests for the activities endpoint of the High School Activities API
"""

import pytest
from fastapi import status


class TestActivitiesEndpoint:
    """Test cases for the /activities endpoint"""

    def test_get_activities_success(self, client, reset_activities):
        """Test successfully retrieving all activities"""
        response = client.get("/activities")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9  # Should have 9 default activities
        
        # Check that specific activities exist
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_get_activities_structure(self, client, reset_activities):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        # Check Chess Club structure as example
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        
        assert isinstance(chess_club["participants"], list)
        assert isinstance(chess_club["max_participants"], int)
        assert chess_club["max_participants"] == 12

    def test_get_activities_participants_content(self, client, reset_activities):
        """Test that activities contain expected participants"""
        response = client.get("/activities")
        data = response.json()
        
        chess_participants = data["Chess Club"]["participants"]
        assert "michael@mergington.edu" in chess_participants
        assert "daniel@mergington.edu" in chess_participants
        
        programming_participants = data["Programming Class"]["participants"]
        assert "emma@mergington.edu" in programming_participants
        assert "sophia@mergington.edu" in programming_participants