from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List


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
    linear_fit: Optional[LinearFitData] = None
    historical_data_points: int


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str
    detail: str
    timestamp: str


class ForecastRequest(BaseModel):
    """Request model for production forecast."""

    grade_ids: List[str] = Field(..., description="List of steel grades to forecast")
    forecast_days: str = Field(
        default="September", description="Month to be forecasted"
    )
    include_linear_fit: bool = Field(
        default=True, description="Include linear regression analysis in response"
    )
