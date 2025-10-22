"""
Test configuration and fixtures for the High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the src directory to the path so we can import the app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset the activities database to its initial state before each test"""
    # Store the original state
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
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball training and tournaments",
            "schedule": "Mondays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu", "jordan@mergington.edu"]
        },
        "Track and Field": {
            "description": "Running, jumping, and throwing events training",
            "schedule": "Tuesdays and Fridays, 3:30 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["maya@mergington.edu", "ethan@mergington.edu"]
        },
        "Art Club": {
            "description": "Painting, drawing, and sculpture workshops",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["lily@mergington.edu", "noah@mergington.edu"]
        },
        "Drama Club": {
            "description": "Theater performances and acting workshops",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 22,
            "participants": ["grace@mergington.edu", "lucas@mergington.edu"]
        },
        "Debate Team": {
            "description": "Competitive debating and public speaking skills",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["ava@mergington.edu", "william@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "STEM competitions and scientific research projects",
            "schedule": "Saturdays, 9:00 AM - 12:00 PM",
            "max_participants": 20,
            "participants": ["isabella@mergington.edu", "james@mergington.edu"]
        }
    }
    
    # Reset activities to original state
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Clean up after test (reset again in case test modified state)
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def sample_email():
    """Provide a sample email for testing"""
    return "test@mergington.edu"


@pytest.fixture
def sample_activity_name():
    """Provide a sample activity name for testing"""
    return "Chess Club"