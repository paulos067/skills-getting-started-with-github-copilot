"""
Tests for the root endpoint of the High School Activities API
"""

import pytest
from fastapi import status


class TestRootEndpoint:
    """Test cases for the root endpoint"""

    def test_root_redirect(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert response.headers["location"] == "/static/index.html"

    def test_root_redirect_follows(self, client):
        """Test that following the redirect leads to the main page"""
        response = client.get("/", follow_redirects=True)
        
        # Should eventually get to the HTML page (may be 404 in tests without static files)
        # but the redirect should work
        assert response.history[0].status_code == status.HTTP_307_TEMPORARY_REDIRECT