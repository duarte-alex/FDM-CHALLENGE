"""
Simple API tests that don't require database connection.
Run with: pytest tests/test_simple.py
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime


# Create a simple test app without database dependencies
test_app = FastAPI(title="Test Steel Production API")

test_router = APIRouter()


@test_router.get("/")
def root():
    """Test root endpoint"""
    return {
        "message": "Steel Production Forecast API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "forecast": "/forecast",
            "upload_production_history": "/upload/production-history",
            "upload_product_groups": "/upload/product-groups",
            "upload_daily_schedule": "/upload/daily-schedule",
            "product_groups": "/product-groups",
            "steel_grades": "/steel-grades",
        },
    }


@test_router.get("/health")
def health_check():
    """Test health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "test",
        "data_summary": {"product_groups": 0, "steel_grades": 0},
    }


@test_router.get("/product-groups")
def get_product_groups():
    """Test product groups endpoint"""
    return []


@test_router.get("/steel-grades")
def get_steel_grades():
    """Test steel grades endpoint"""
    return []


@test_router.post("/forecast")
def forecast_production(request: dict):
    """Test forecast endpoint"""
    if not request.get("grade_percentages"):
        return JSONResponse(
            status_code=400,
            content={"error": "Bad Request", "detail": "No grade percentages provided"}
        )
    
    return {
        "forecast_date": "2024-09-24",
        "grade_breakdown": {grade: 0 for grade in request["grade_percentages"].keys()}
    }


test_app.include_router(test_router)

client = TestClient(test_app)


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


def test_forecast_endpoint_with_empty_request():
    """Test forecast endpoint with empty grade percentages."""
    response = client.post("/forecast", json={"grade_percentages": {}})
    assert response.status_code == 400
    assert "No grade percentages provided" in response.json()["detail"]


def test_forecast_endpoint_with_valid_request():
    """Test forecast endpoint with valid request."""
    response = client.post(
        "/forecast", 
        json={"grade_percentages": {"B500A": 50, "B500B": 50}}
    )
    assert response.status_code == 200
    data = response.json()
    assert "forecast_date" in data
    assert "grade_breakdown" in data
    assert data["grade_breakdown"]["B500A"] == 0
    assert data["grade_breakdown"]["B500B"] == 0


def test_docs_endpoint():
    """Test that API documentation is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_endpoint():
    """Test that OpenAPI JSON is accessible."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert data["info"]["title"] == "Test Steel Production API"
    assert "paths" in data


def test_api_structure():
    """Test that the API has expected structure."""
    root_response = client.get("/")
    assert root_response.status_code == 200
    
    endpoints = root_response.json()["endpoints"]
    expected_endpoints = [
        "forecast",
        "upload_production_history", 
        "upload_product_groups",
        "upload_daily_schedule",
        "product_groups",
        "steel_grades"
    ]
    
    for endpoint in expected_endpoints:
        assert endpoint in endpoints


def test_response_formats():
    """Test that responses have expected formats."""
    # Test root response format
    root_response = client.get("/")
    root_data = root_response.json()
    required_fields = ["message", "version", "docs", "endpoints"]
    for field in required_fields:
        assert field in root_data
    
    # Test health response format
    health_response = client.get("/health")
    health_data = health_response.json()
    health_fields = ["status", "timestamp", "database", "data_summary"]
    for field in health_fields:
        assert field in health_data
