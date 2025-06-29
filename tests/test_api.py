"""
Run with: pytest tests/
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db
from app.models.schema import Base

# Create an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency with test database."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

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
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data
    assert "timestamp" in data


def test_docs_endpoint():
    """Test that API documentation is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_get_product_groups_empty():
    """Test getting product groups when database is empty."""
    response = client.get("/product-groups")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 0


def test_get_steel_grades_empty():
    """Test getting steel grades when database is empty."""
    response = client.get("/steel-grades")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 0


def test_get_forecasted_production_empty():
    """Test getting forecasted production when database is empty."""
    response = client.get("/forecasted-production")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 0


def test_get_historical_production_empty():
    """Test getting historical production when database is empty."""
    response = client.get("/historical-production")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 0


def test_get_daily_schedules_empty():
    """Test getting daily schedules when database is empty."""
    response = client.get("/daily-schedules")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 0


def test_forecast_endpoint_with_empty_request():
    """Test forecast endpoint with empty grade percentages."""
    response = client.post("/forecast", json={"grade_percentages": {}})
    assert response.status_code == 400
    assert "No grade percentages provided" in response.json()["detail"]


def test_forecast_endpoint_with_valid_request():
    """Test forecast endpoint with valid but non-existent grades."""
    response = client.post(
        "/forecast", 
        json={"grade_percentages": {"B500A": 50, "B500B": 50}}
    )
    assert response.status_code == 200
    data = response.json()
    assert "forecast_date" in data
    assert "grade_breakdown" in data
    # Should return zeros since no data exists
    assert data["grade_breakdown"]["B500A"] == 0
    assert data["grade_breakdown"]["B500B"] == 0


def test_upload_invalid_file_type():
    """Test upload endpoints reject invalid file types."""
    files = {"file": ("test.txt", "invalid content", "text/plain")}

    response = client.post("/upload/production-history", files=files)
    assert response.status_code == 400
    assert "Only CSV or Excel files are supported" in response.json()["detail"]

    response = client.post("/upload/product-groups", files=files)
    assert response.status_code == 400
    assert "Only CSV or Excel files are supported" in response.json()["detail"]

    response = client.post("/upload/daily-schedule", files=files)
    assert response.status_code == 400
    assert "Only CSV or Excel files are supported" in response.json()["detail"]


def test_openapi_endpoint():
    """Test that OpenAPI JSON is accessible."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert data["info"]["title"] == "Steel Production Planning & Forecasting API"
    assert "paths" in data
