from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from ..database import get_db
from .. import crud
from ..models import pydantic
import pandas as pd
from utility import preprocess
from datetime import datetime

router = APIRouter()


def create_error_response(
    error: str, detail: str, status_code: int = 500
) -> JSONResponse:
    """Create a structured error response using the ErrorResponse model."""
    error_data = pydantic.ErrorResponse(
        error=error, detail=detail, timestamp=datetime.now().isoformat()
    )
    return JSONResponse(status_code=status_code, content=error_data.model_dump())


@router.get("/", tags=["root"])
def root():
    """
    Welcome to the Steel Production Forecast API

    This is the main entry point for the Steel Production Planning & Forecasting System.
    Navigate to `/docs` for interactive API documentation.
    """
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


@router.get("/health", tags=["health"])
def health_check(db: Session = Depends(get_db)):
    """
    ## System Health Check

    Monitor the API and database connectivity status.

    Returns system health information including:
    - Database connection status
    - Current data summary (product groups and steel grades count)
    - System timestamp
    """
    try:
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
        return create_error_response(
            error="Service Unhealthy",
            detail=f"Service unhealthy: {str(e)}",
            status_code=503,
        )


@router.post("/forecast", response_model=pydantic.ForecastOutput, tags=["forecasting"])
def forecast_production(
    request: pydantic.ForecastRequest, db: Session = Depends(get_db)
):
    """
    ## Generate Production Forecasts

    User interface for generating production forecasts for specified steel grades.
    """
    try:
        return crud.compute_forecast(request, db)
    except Exception as e:
        return create_error_response(
            error="Service Unhealthy",
            detail=f"Service unhealthy: {str(e)}",
            status_code=503,
        )
    

@router.post(
    "/upload/product-groups",
    response_model=pydantic.UploadResponse,
    tags=["data-upload"],
)
def upload_product_groups(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    ## Upload product_groups_monthly file

    **Accepted Formats:** `.xlsx`, `.xls`, `.csv`

    **Creates:** ProductGroup table and ForecastedProduction (if not exists)
    """
    if not file.filename.endswith((".csv", ".xlsx", ".xls")):
        return create_error_response(
            error="Invalid File Type",
            detail="Only CSV or Excel files are supported",
            status_code=400,
        )

    try:
        df = preprocess.sheet_to_pandas(file)

        df_transformed = df.melt(
            id_vars="Quality:", var_name="date", value_name="heats"
        )
        df_transformed = df_transformed.rename(
            columns={"Quality:": "product_group_name"}
        )

        records = crud.store_product_groups(df_transformed, db)
        return pydantic.UploadResponse(
            message=f"Product groups and forecasted production uploaded successfully. {records} records inserted.",
            records_inserted=records,
        )
    except Exception as e:
        return create_error_response(
            error="File Processing Error",
            detail=f"Error processing file: {str(e)}",
            status_code=500,
        )


@router.post(
    "/upload/production-history",
    response_model=pydantic.UploadResponse,
    tags=["data-upload"],
)
def upload_production_history(
    file: UploadFile = File(...), db: Session = Depends(get_db)
):
    """
    ## Upload steel_grade_production file

    Upload product-groups first!

    **Accepted Formats:** `.xlsx`, `.xls`, `.csv`
    """
    if not file.filename.endswith((".csv", ".xlsx", ".xls")):
        return create_error_response(
            error="Invalid File Type",
            detail="Only CSV or Excel files are supported",
            status_code=400,
        )

    try:
        df = preprocess.process_steel_grade(file)
        records = crud.store_production_history(df, db)

        return pydantic.UploadResponse(
            message=f"Production history uploaded successfully. {records} records inserted.",
            records_inserted=records,
        )
    except Exception as e:
        return create_error_response(
            error="File Processing Error",
            detail=f"Error processing file: {str(e)}",
            status_code=500,
        )



@router.post(
    "/upload/daily-schedule",
    response_model=pydantic.UploadResponse,
    tags=["data-upload"],
)
def upload_daily_schedule(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    ## Upload Daily Production Schedule

    **Accepted Formats:** `.xlsx`, `.xls`, `.csv`
    """
    if not file.filename.endswith((".csv", ".xlsx", ".xls")):
        return create_error_response(
            error="Invalid File Type",
            detail="Only CSV or Excel files are supported",
            status_code=400,
        )

    try:
        df = preprocess.sheet_to_pandas(file)
        records = crud.store_daily_schedule(df, db)
        return pydantic.UploadResponse(
            message=f"Daily schedule uploaded successfully. {records} records inserted.",
            records_inserted=records,
        )
    except Exception as e:
        return create_error_response(
            error="File Processing Error",
            detail=f"Error processing file: {str(e)}",
            status_code=500,
        )


@router.get("/product-groups", tags=["reference"])
def get_product_groups(db: Session = Depends(get_db)):
    """
    Get all product groups

    Retrieve a complete list of steel product group classifications
    used for organizing and categorizing steel grades.
    """
    groups = crud.get_product_groups(db)
    return [{"id": g.id, "name": g.name} for g in groups]


@router.get("/steel-grades", tags=["reference"])
def get_steel_grades(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get steel grades with pagination

    Retrieve steel grade definitions with their associated product groups.
    Supports pagination for large datasets.
    """
    grades = crud.get_steel_grades(db, skip=skip, limit=limit)
    return [
        {"id": g.id, "name": g.name, "product_group_id": g.product_group_id}
        for g in grades
    ]


@router.get("/forecasted-production", tags=["reference"])
def get_forecasted_production(db: Session = Depends(get_db)):
    """
    Get all forecasted production data

    Retrieve all forecasted production records from the ForecastedProduction table.
    Returns date, heats, and associated product group information.
    """
    forecasted_data = crud.get_forecasted_production(db)
    return [
        {
            "id": f.id,
            "date": f.date,
            "heats": f.heats,
            "product_group_id": f.product_group_id,
            "product_group_name": f.product_group.name if f.product_group else None,
        }
        for f in forecasted_data
    ]


@router.get("/historical-production", tags=["reference"])
def get_historical_production(db: Session = Depends(get_db)):
    """
    Get HistoricalProduction table.

    Retrieve all historical production records from the HistoricalProduction table.
    Returns date, tons, and associated steel grade information.
    """
    historical_data = crud.get_historical_production(db, limit=1000)  # Get more records
    return [
        {
            "id": h.id,
            "date": h.date,
            "tons": h.tons,
            "grade_id": h.grade_id,
            "grade_name": h.grade.name if h.grade else None,
        }
        for h in historical_data
    ]


@router.get("/daily-schedules", tags=["reference"])
def get_daily_schedules(db: Session = Depends(get_db)):
    """
    Get all daily production schedules

    Retrieve all daily production schedule records from the DailyProductionSchedule table.
    Returns date, start time, mould size, and associated steel grade information.
    """
    schedule_data = crud.get_daily_schedule(db, limit=1000)  # Get more records
    return [
        {
            "id": s.id,
            "date": s.date,
            "start_time": s.start_time,
            "mould_size": s.mould_size,
            "grade_id": s.grade_id,
            "grade_name": s.grade.name if s.grade else None,
        }
        for s in schedule_data
    ]
