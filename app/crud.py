from utility.linear_fit import get_linear_fit
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta
import pandas as pd
from fastapi import HTTPException
from .models import schema
from .models import pydantic


def store_production_history(df: pd.DataFrame, db: Session) -> int:
    """
    Store historical production data from DataFrame into HistoricalProduction table.

    Args:
        df (pd.DataFrame): DataFrame with columns: date, grade_name, tons
        db (Session): Database session

    Returns:
        int: Number of records inserted
    """
    records_inserted = 0

    for _, row in df.iterrows():
        # Find the steel grade
        steel_grade = (
            db.query(schema.SteelGrade)
            .filter(schema.SteelGrade.name == str(row["grade_name"]))
            .first()
        )

        if steel_grade:
            # Convert date if needed
            production_date = (
                pd.to_datetime(row["date"]).date()
                if isinstance(row["date"], str)
                else row["date"]
            )

            # Check if record already exists
            existing = (
                db.query(schema.HistoricalProduction)
                .filter(
                    schema.HistoricalProduction.date == production_date,
                    schema.HistoricalProduction.grade_id == steel_grade.id,
                )
                .first()
            )

            if not existing:
                production_record = schema.HistoricalProduction(
                    date=production_date, tons=int(row["tons"]), grade_id=steel_grade.id
                )
                db.add(production_record)
                records_inserted += 1

    db.commit()
    return records_inserted


def store_product_groups(df: pd.DataFrame, db: Session) -> int:
    """
    Store product groups and forecasted production data from DataFrame.

    Args:
        df (pd.DataFrame): DataFrame with columns: product_group_name, date, heats
        db (Session): Database session

    Returns:
        int: Number of records inserted (groups + forecasted production)
    """

    records_inserted = 0
    
    # First, store unique product groups
    unique_groups = df["product_group_name"].dropna().unique()

    for group_name in unique_groups:
        existing_group = (
            db.query(schema.ProductGroup)
            .filter(schema.ProductGroup.name == str(group_name))
            .first()
        )

        if not existing_group:
            product_group = schema.ProductGroup(name=str(group_name))
            db.add(product_group)
            records_inserted += 1

    db.commit()  # Commit product groups first
    
    # Now store forecasted production data
    for _, row in df.iterrows():
        if pd.isna(row["product_group_name"]) or pd.isna(row["date"]) or pd.isna(row["heats"]):
            continue
            
        # Find the product group
        product_group = (
            db.query(schema.ProductGroup)
            .filter(schema.ProductGroup.name == str(row["product_group_name"]))
            .first()
        )
        
        if product_group:
            steel_grade = (
                db.query(schema.SteelGrade)
                .filter(schema.SteelGrade.name == str(row["product_group_name"]))
                .first()
            )
            
            if not steel_grade:
                steel_grade = schema.SteelGrade(
                    name=str(row["product_group_name"]),
                    product_group_id=product_group.id
                )
                db.add(steel_grade)
                db.commit()
                db.refresh(steel_grade)
            
            # Convert date if needed
            forecast_date = (
                pd.to_datetime(row["date"]).date()
                if isinstance(row["date"], str)
                else row["date"]
            )
            
            # Check if forecasted production record already exists
            existing_forecast = (
                db.query(schema.ForecastedProduction)
                .filter(
                    schema.ForecastedProduction.date == forecast_date,
                    schema.ForecastedProduction.product_group_id == product_group.id,
                )
                .first()
            )
            
            if not existing_forecast:
                forecasted_production = schema.ForecastedProduction(
                    date=forecast_date,
                    heats=int(row["heats"]) if not pd.isna(row["heats"]) else 0,
                    product_group_id=product_group.id
                )
                db.add(forecasted_production)
                records_inserted += 1

    db.commit()
    return records_inserted


def get_product_groups(db: Session) -> List[schema.ProductGroup]:
    """Get all product groups."""
    return db.query(schema.ProductGroup).all()


def get_product_group_by_name(db: Session, name: str) -> Optional[schema.ProductGroup]:
    """Get a product group by name."""
    return (
        db.query(schema.ProductGroup).filter(schema.ProductGroup.name == name).first()
    )


def create_product_group(db: Session, name: str) -> schema.ProductGroup:
    """Create a new product group."""
    db_product_group = schema.ProductGroup(name=name)
    db.add(db_product_group)
    db.commit()
    db.refresh(db_product_group)
    return db_product_group


def get_steel_grades(
    db: Session, skip: int = 0, limit: int = 100
) -> List[schema.SteelGrade]:
    """Get steel grades with pagination."""
    return db.query(schema.SteelGrade).offset(skip).limit(limit).all()


def get_steel_grade_by_name(db: Session, name: str) -> Optional[schema.SteelGrade]:
    """Get a steel grade by name."""
    return db.query(schema.SteelGrade).filter(schema.SteelGrade.name == name).first()


def create_steel_grade(
    db: Session, name: str, product_group_id: int
) -> schema.SteelGrade:
    """Create a new steel grade."""
    db_steel_grade = schema.SteelGrade(name=name, product_group_id=product_group_id)
    db.add(db_steel_grade)
    db.commit()
    db.refresh(db_steel_grade)
    return db_steel_grade


def get_historical_production(
    db: Session,
    grade_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[schema.HistoricalProduction]:
    """Get historical production with optional filters."""
    query = db.query(schema.HistoricalProduction)

    if grade_id:
        query = query.filter(schema.HistoricalProduction.grade_id == grade_id)
    if start_date:
        query = query.filter(schema.HistoricalProduction.date >= start_date)
    if end_date:
        query = query.filter(schema.HistoricalProduction.date <= end_date)

    return query.offset(skip).limit(limit).all()


def get_forecasted_production(db: Session, product_group_id: Optional[int] = None) -> List[schema.ForecastedProduction]:
    """
    Get forecasted production data, optionally filtered by product group.

    Args:
        db (Session): Database session
        product_group_id (Optional[int]): Filter by specific product group ID

    Returns:
        List[schema.ForecastedProduction]: List of forecasted production records
    """
    query = db.query(schema.ForecastedProduction)
    
    if product_group_id:
        query = query.filter(schema.ForecastedProduction.product_group_id == product_group_id)
    
    return query.all()


def get_forecasted_production(
    db: Session
) -> List[schema.ForecastedProduction]:
    """
    Get ForecastedProduction table

    Args:
        db (Session): Database session

    Returns:
        List[schema.ForecastedProduction]: List of forecasted production records
    """
    return (
        db.query(schema.ForecastedProduction).all()
    )


def get_daily_schedule(
    db: Session,
    schedule_date: Optional[date] = None,
    grade_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[schema.DailyProductionSchedule]:
    """Get daily production schedule with optional filters."""
    query = db.query(schema.DailyProductionSchedule)

    if schedule_date:
        query = query.filter(schema.DailyProductionSchedule.date == schedule_date)
    if grade_id:
        query = query.filter(schema.DailyProductionSchedule.grade_id == grade_id)

    return query.offset(skip).limit(limit).all()


def store_daily_schedule(df: pd.DataFrame, db: Session) -> int:
    """
    Store daily production schedule from DataFrame.

    Args:
        df (pd.DataFrame): DataFrame with columns: date, grade_name, start_time, mould_size
        db (Session): Database session

    Returns:
        int: Number of records inserted
    """
    records_inserted = 0

    for _, row in df.iterrows():
        # Find the steel grade
        steel_grade = (
            db.query(schema.SteelGrade)
            .filter(schema.SteelGrade.name == str(row["grade_name"]))
            .first()
        )

        if steel_grade:
            # Convert date if needed
            schedule_date = (
                pd.to_datetime(row["date"]).date()
                if isinstance(row["date"], str)
                else row["date"]
            )

            schedule_record = schema.DailyProductionSchedule(
                date=schedule_date,
                start_time=str(row.get("start_time", "")),
                mould_size=str(row.get("mould_size", "")),
                grade_id=steel_grade.id,
            )
            db.add(schedule_record)
            records_inserted += 1

    db.commit()
    return records_inserted


def calculate_production_forecast_with_linear_fit(db: Session, grade_id: int) -> dict:
    """
    Calculate production forecast using linear regression on historical data.

    Args:
        db (Session): Database session
        grade_id (int): Steel grade ID

    Returns:
        dict: Linear fit parameters and forecast data
    """
    # Get historical production data
    historical_data = (
        db.query(schema.HistoricalProduction)
        .filter(schema.HistoricalProduction.grade_id == grade_id)
        .order_by(schema.HistoricalProduction.date)
        .all()
    )

    if len(historical_data) < 2:
        return {"error": "Insufficient historical data for linear fit"}

    # Prepare data for linear regression
    dates = [record.date for record in historical_data]
    tons = [record.tons for record in historical_data]

    # Convert dates to numeric values (days since first date)
    first_date = dates[0]
    x_values = [(date - first_date).days for date in dates]

    # Calculate linear fit
    linear_fit_result = get_linear_fit(x_values, tons)

    return {
        "grade_id": grade_id,
        "linear_fit": linear_fit_result,
        "data_points": len(historical_data),
        "date_range": {"start": first_date, "end": dates[-1]},
    }


def compute_forecast(
    request: pydantic.ForecastRequest, db: Session
) -> pydantic.ForecastOutput:
    """
    Compute production forecast based on request parameters.

    Args:
        request (ForecastRequest): Request parameters
        db (Session): Database session

    Returns:
        ForecastOutput: Forecast results
    """

    # For now, return a properly structured response for the first grade_id
    # This is a placeholder implementation that returns valid data structure
    if not request.grade_ids:
        raise HTTPException(status_code=400, detail="No grade IDs provided")

    grade_id = request.grade_ids[0]

    # Get steel grade info
    steel_grade = (
        db.query(schema.SteelGrade).filter(schema.SteelGrade.id == grade_id).first()
    )
    if not steel_grade:
        raise HTTPException(
            status_code=404, detail=f"Steel grade with ID {grade_id} not found"
        )

    # Calculate forecast date
    forecast_date = date.today() + timedelta(days=request.forecast_days)

    # Placeholder linear fit data
    linear_fit = None
    if request.include_linear_fit:
        linear_fit = pydantic.LinearFitData(slope=1.2, intercept=100.0)

    return pydantic.ForecastOutput(
        grade_id=grade_id,
        grade_name=steel_grade.name,
        forecast_date=forecast_date,
        predicted_tons=250.5,
        confidence_score=0.95,
        linear_fit=linear_fit,
        historical_data_points=12,
    )
