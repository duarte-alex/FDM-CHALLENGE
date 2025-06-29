from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
import pandas as pd
from fastapi import HTTPException
from .models import schema
from .models import pydantic


def store_production_history(df: pd.DataFrame, db: Session) -> int:
    """
    Store historical production data from DataFrame into HistoricalProduction table.
    Also creates SteelGrade and ProductGroup records if they don't exist.

    Args:
        df (pd.DataFrame): DataFrame with columns: date, grade_name, tons, product_group_id
        db (Session): Database session

    Returns:
        int: Number of records inserted
    """
    records_inserted = 0

    for _, row in df.iterrows():
        # Find or create the product group if product_group_id exists
        product_group = None
        if "product_group_id" in row and pd.notna(row["product_group_id"]):
            product_group = (
                db.query(schema.ProductGroup)
                .filter(schema.ProductGroup.name == str(row["product_group_id"]))
                .first()
            )

            if not product_group:
                product_group = schema.ProductGroup(name=str(row["product_group_id"]))
                db.add(product_group)
                db.commit()
                db.refresh(product_group)

        # Find or create the steel grade
        steel_grade = (
            db.query(schema.SteelGrade)
            .filter(schema.SteelGrade.name == str(row["grade_name"]))
            .first()
        )

        if not steel_grade:
            # Create new steel grade
            steel_grade = schema.SteelGrade(
                name=str(row["grade_name"]),
                product_group_id=product_group.id if product_group else None,
            )
            db.add(steel_grade)
            db.commit()
            db.refresh(steel_grade)

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

    db.commit()

    # Now store forecasted production data
    for _, row in df.iterrows():
        if (
            pd.isna(row["product_group_name"])
            or pd.isna(row["date"])
            or pd.isna(row["heats"])
        ):
            continue

        # Find the product group
        product_group = (
            db.query(schema.ProductGroup)
            .filter(schema.ProductGroup.name == str(row["product_group_name"]))
            .first()
        )

        if product_group:

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
                    product_group_id=product_group.id,
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


def get_steel_grade_by_name(db: Session, name: str) -> Optional[schema.SteelGrade]:
    """Get a steel grade by name."""
    return db.query(schema.SteelGrade).filter(schema.SteelGrade.name == name).first()


def get_steel_grades(
    db: Session, skip: int = 0, limit: int = 100
) -> List[schema.SteelGrade]:
    """Get steel grades with pagination."""
    return db.query(schema.SteelGrade).offset(skip).limit(limit).all()


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


def get_forecasted_production(db: Session) -> List[schema.ForecastedProduction]:
    """
    Get ForecastedProduction table

    Args:
        db (Session): Database session

    Returns:
        List[schema.ForecastedProduction]: List of forecasted production records
    """
    return db.query(schema.ForecastedProduction).all()


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


def compute_forecast(
    request: pydantic.ForecastRequest, db: Session
) -> pydantic.ForecastOutput:
    """
    Compute production forecast based on request parameters.

    Reads September forecasted heats from ForecastedProduction table for each product group,
    then distributes heats to specific steel grades based on provided weights.

    Args:
        request (ForecastRequest): Request parameters with grade percentages
        db (Session): Database session

    Returns:
        ForecastOutput: Forecast results with steel grade breakdown
    """

    if not request.grade_percentages:
        raise HTTPException(status_code=400, detail="No grade percentages provided")

    forecast_date = date(2024, 9, 24)

    # get ForecastedProduction table
    forecasted_data = get_forecasted_production(db)

    # return month forecast
    september_heats_by_group = {}
    for forecast in forecasted_data:
        if forecast.date.month == 9 and forecast.date.year == 2024:
            group_name = (
                forecast.product_group.name if forecast.product_group else "Unknown"
            )
            if group_name not in september_heats_by_group:
                september_heats_by_group[group_name] = 0
            september_heats_by_group[group_name] += forecast.heats

    # Calculate heats breakdown based on grade weights
    grade_breakdown = {}
    total_heats = 0

    for grade_name, weight_percentage in request.grade_percentages.items():
        # Find which product group this grade belongs to
        steel_grade = get_steel_grade_by_name(db, grade_name)

        if steel_grade and steel_grade.product_group:
            group_name = steel_grade.product_group.name
            group_total_heats = september_heats_by_group.get(group_name, 0)

            # Calculate heats for this grade: group_heats * (weight / 100)
            grade_heats = int(group_total_heats * (weight_percentage / 100))
            grade_breakdown[grade_name] = grade_heats
            total_heats += grade_heats
        else:
            grade_breakdown[grade_name] = 0

    return pydantic.ForecastOutput(
        forecast_date=forecast_date, grade_breakdown=grade_breakdown
    )
