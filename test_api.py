"""
API Integration tests
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

# Mock the data fetcher before importing main
@pytest.fixture(autouse=True)
def mock_data_fetcher():
    """Mock the external API calls."""
    mock_data = {
        "messages": [
            {"id": "1", "user_id": "u1", "user_name": "Alice", "timestamp": "2025-01-01T00:00:00", "message": "I love pizza"},
            {"id": "2", "user_id": "u2", "user_name": "Bob", "timestamp": "2025-01-02T00:00:00", "message": "Buy groceries"}
        ],
        "movies": [
            {"id": "m1", "title": "The Dark Knight", "description": "Batman movie", "image_url": "http://example.com", "rating": 9.0}
        ]
    }

    with patch('data_fetcher.fetch_all_data', new_callable=AsyncMock) as mock:
        mock.return_value = mock_data
        yield mock


@pytest.fixture
def client(mock_data_fetcher):
    """Create test client."""
    from main import app
    return TestClient(app)


def test_root_endpoint(client):
    """Test root endpoint returns API info."""
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "endpoints" in data


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "messages_indexed" in data
    assert "movies_indexed" in data


def test_search_endpoint_basic(client):
    """Test basic search functionality."""
    response = client.get("/search?q=pizza")

    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "pizza"
    assert "results" in data
    assert "query_time_ms" in data


def test_search_messages_only(client):
    """Test searching only messages."""
    response = client.get("/search?q=pizza&type=messages")

    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "messages"
    assert "messages" in data["results"]
    assert "movies" not in data["results"]


def test_search_movies_only(client):
    """Test searching only movies."""
    response = client.get("/search?q=batman&type=movies")

    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "movies"
    assert "movies" in data["results"]
    assert "messages" not in data["results"]


def test_search_pagination(client):
    """Test pagination parameters."""
    response = client.get("/search?q=test&skip=0&limit=1")

    assert response.status_code == 200
    data = response.json()

    # Check that pagination is applied
    if "messages" in data["results"]:
        assert len(data["results"]["messages"]["items"]) <= 1


def test_search_missing_query(client):
    """Test that missing query parameter returns error."""
    response = client.get("/search")

    assert response.status_code == 422  # Validation error


def test_search_empty_query(client):
    """Test that empty query returns error."""
    response = client.get("/search?q=")

    assert response.status_code == 422  # Validation error (min_length=1)


def test_search_invalid_type(client):
    """Test invalid search type."""
    response = client.get("/search?q=test&type=invalid")

    assert response.status_code == 400
    data = response.json()
    assert "error" in data


def test_search_pagination_limits(client):
    """Test pagination limit validation."""
    # Valid limit
    response = client.get("/search?q=test&limit=10")
    assert response.status_code == 200

    # Limit too high (max is 100)
    response = client.get("/search?q=test&limit=1000")
    assert response.status_code == 422


def test_search_performance(client):
    """Test that search completes quickly."""
    response = client.get("/search?q=pizza")

    assert response.status_code == 200
    data = response.json()

    # Should complete in under 100ms
    assert data["query_time_ms"] < 100


def test_search_returns_correct_structure(client):
    """Test response structure."""
    response = client.get("/search?q=pizza")

    assert response.status_code == 200
    data = response.json()

    # Check required fields
    assert "query" in data
    assert "type" in data
    assert "query_time_ms" in data
    assert "results" in data

    # Check results structure
    results = data["results"]
    if "messages" in results:
        assert "total" in results["messages"]
        assert "items" in results["messages"]
        assert isinstance(results["messages"]["items"], list)
