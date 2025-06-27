from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import crud
from ..models import pydantic
from ..models import schema
import pandas as pd
from utility import preprocess
import io
from datetime import datetime

router = APIRouter()


@router.get("/")
def root():
    """Welcome endpoint for the Steel Production Forecast API."""
    return {
        "message": "Steel Production Forecast API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "forecast": "/forecast",
            "upload_quality_forecast": "/upload/quality-forecast",
            "upload_production_history": "/upload/production-history",
            "upload_group_breakdown": "/upload/group-breakdown",
            "product_groups": "/product-groups",
            "steel_grades": "/steel-grades",
        },
    }


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint for monitoring."""
    try:
        # Test database connection
        product_groups_count = len(crud.get_product_groups(db))
        steel_grades_count = len(crud.get_steel_grades(db, limit=1000))

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected",
            "data_summary": {
                "product_groups": product_groups_count,
                "steel_grades": steel_grades_count,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@router.post("/forecast", response_model=pydantic.ForecastOutput)
def forecast_production(
    request: pydantic.ForecastRequest, db: Session = Depends(get_db)
):
    """
    Generate production forecasts using linear regression analysis.

    Analyzes historical production data to predict future output based on:
    - Historical tons produced per steel grade
    - Linear regression with correlation coefficient R ≈ 1
    - Product group breakdown percentages
    """
    return crud.compute_forecast(request, db)


@router.post("/upload/quality-forecast")
def upload_quality_forecast(
    file: UploadFile = File(...), db: Session = Depends(get_db)
):
    """
    Upload forecasted production data from Excel/CSV files.

    Expected columns: date, grade_name, heats
    Stores data in ForecastedProduction table.
    """
    if not file.filename.endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(
            status_code=400, detail="Only CSV or Excel files are supported"
        )

    df = preprocess.sheet_to_pandas(file)
    records = crud.store_quality_forecast(df, db)
    return {
        "message": f"Quality forecast data uploaded successfully. {records} records inserted."
    }


@router.post("/upload/production-history")
def upload_production_history(
    file: UploadFile = File(...), db: Session = Depends(get_db)
):
    """
    Upload historical production data from Excel/CSV files.

    Expected columns: date, grade_name, tons
    Stores data in HistoricalProduction table for analysis and forecasting.
    """
    if not file.filename.endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(
            status_code=400, detail="Only CSV or Excel files are supported"
        )

    df = preprocess.sheet_to_pandas(file)
    records = crud.store_production_history(df, db)
    return {
        "message": f"Production history uploaded successfully. {records} records inserted."
    }


@router.post("/upload/group-breakdown")
def upload_group_breakdown(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload product groups and steel grade classifications.

    Expected columns: product_group_name, grade_name
    Creates relationships between product groups (Rebar, MBQ, etc.) and steel grades (B500A, A36, etc.).
    """
    if not file.filename.endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(
            status_code=400, detail="Only CSV or Excel files are supported"
        )

    df = preprocess.sheet_to_pandas(file)
    records = crud.store_group_breakdown(df, db)
    return {
        "message": f"Product group breakdown uploaded successfully. {records} records inserted."
    }


@router.get("/product-groups")
def get_product_groups(db: Session = Depends(get_db)):
    """Get all product groups."""
    groups = crud.get_product_groups(db)
    return [{"id": g.id, "name": g.name} for g in groups]


@router.get("/steel-grades")
def get_steel_grades(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get steel grades with pagination."""
    grades = crud.get_steel_grades(db, skip=skip, limit=limit)
    return [
        {"id": g.id, "name": g.name, "product_group_id": g.product_group_id}
        for g in grades
    ]


@router.get("/production-summary/{grade_id}")
def get_production_summary(grade_id: int, db: Session = Depends(get_db)):
    """
    Get comprehensive production summary for a specific steel grade.

    Returns historical production statistics, forecasted data, and total metrics
    for the specified steel grade ID.
    """
    return crud.get_production_summary_by_grade(db, grade_id)
