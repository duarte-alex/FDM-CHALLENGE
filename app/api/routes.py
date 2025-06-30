from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import crud
from ..models import pydantic
import pandas as pd
from utility import preprocess
from datetime import datetime
import glob

router = APIRouter()


@router.get("/", tags=["root"])
def root():
    """
    Welcome to the Steel Production API

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
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


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
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@router.post(
    "/upload/product-groups",
    response_model=pydantic.UploadResponse,
    tags=["data-upload"],
)
def upload_product_groups(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    ## Upload product_groups_monthly file

    **Accepted Formats:** `.xlsx`, `.xls`, `.csv`

    This function stores records on the ProductGroup table and ForecastedProduction.
    """
    if not file.filename.endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(
            status_code=400, detail="Only CSV or Excel files are supported"
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
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


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

    Upload product-groups first! This function stores records on HistoricalProduction table.

    **Accepted Formats:** `.xlsx`, `.xls`, `.csv`
    """
    if not file.filename.endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(
            status_code=400, detail="Only CSV or Excel files are supported"
        )

    try:
        df = preprocess.process_steel_grade(file)
        records = crud.store_production_history(df, db)

        return pydantic.UploadResponse(
            message=f"Production history uploaded successfully. {records} records inserted.",
            records_inserted=records,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.post(
    "/upload/daily-schedule",
    response_model=pydantic.UploadResponse,
    tags=["data-upload"],
)
def upload_daily_schedule(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    ## Upload Daily Production Schedule

    **Accepted Formats:** `.xlsx`, `.xls`, `.csv`

    This function processes non-tabular data with triplet format.
    It stores records on the DailyProductionSchedule table.
    """
    if not file.filename.endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(
            status_code=400, detail="Only CSV or Excel files are supported"
        )

    try:
        # Process the non-tabular file and save CSV files
        success = preprocess.handle_non_tabular(file)

        if not success:
            raise HTTPException(
                status_code=500, detail="Failed to process the daily schedule file"
            )

        processed_files = glob.glob("data/processed/charge_schedule_*.csv")

        total_records = 0
        for csv_file in processed_files:
            df = pd.read_csv(csv_file)
            # Add date column based on filename
            date_str = csv_file.split("_")[-1].replace(".csv", "")
            df["date"] = date_str
            # Rename columns to match expected format
            df = df.rename(columns={"grade": "grade_name"})

            # Clean up start_time to remove the 1900-01-01 date part
            if "start_time" in df.columns:
                df["start_time"] = df["start_time"].apply(
                    lambda x: (
                        pd.to_datetime(str(x)).strftime("%H:%M:%S")
                        if pd.notna(x) and str(x) != "nan"
                        else str(x)
                    )
                )

            records = crud.store_daily_schedule(df, db)
            total_records += records

        return pydantic.UploadResponse(
            message=f"Daily schedule uploaded successfully. {total_records} records inserted from {len(processed_files)} dates.",
            records_inserted=total_records,
        )

    except HTTPException:
        raise  # Re-raise HTTPExceptions as-is
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


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
