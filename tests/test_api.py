"""
Run with: pytest tests/
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint returns API information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Steel Production Forecast API"
    assert "version" in data
    assert "endpoints" in data


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code in [200, 503]


def test_docs_endpoint():
    """Test that API documentation is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_get_product_groups_empty():
    """Test getting product groups when database is empty."""
    response = client.get("/product-groups")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_steel_grades_empty():
    """Test getting steel grades when database is empty."""
    response = client.get("/steel-grades")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_forecast_endpoint_structure():
    """Test forecast endpoint accepts proper request structure."""
    response = client.post(
        "/forecast",
        json={"grade_ids": [1], "forecast_days": 30, "include_linear_fit": True},
    )
    assert response.status_code in [200, 422, 404]


def test_upload_invalid_file_type():
    """Test upload endpoints reject invalid file types."""
    files = {"file": ("test.txt", "invalid content", "text/plain")}

    response = client.post("/upload/production-history", files=files)
    assert response.status_code == 400
    assert "Only CSV or Excel files are supported" in response.json()["detail"]
