from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class SteelGradeResponse(BaseModel):
    """Response model for steel grade data."""

    id: int
    name: str
    product_group_id: int

    class Config:
        from_attributes = True


class LinearFitData(BaseModel):
    """Linear regression fit results."""

    slope: float
    intercept: float


class ForecastOutput(BaseModel):
    """Response model for production forecast results."""

    grade_id: int
    grade_name: str
    forecast_date: date
    predicted_tons: float
    confidence_score: float
    linear_fit: Optional[LinearFitData] = None
    historical_data_points: int


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str
    detail: str
    timestamp: str
