from pydantic import BaseModel, Field
from datetime import date
from typing import Dict, List, Optional


class ProductGroupResponse(BaseModel):
    """Response model for product group data."""
    id: int
    name: str
    
    class Config:
        from_attributes = True


class SteelGradeResponse(BaseModel):
    """Response model for steel grade data."""
    id: int
    name: str
    product_group_id: int
    
    class Config:
        from_attributes = True


class HistoricalProductionResponse(BaseModel):
    """Response model for historical production data."""
    id: int
    date: date
    tons: int
    grade_id: int
    
    class Config:
        from_attributes = True


class ForecastRequest(BaseModel):
    """Request model for production forecasting."""
    grade_ids: List[int] = Field(..., description="List of steel grade IDs to forecast")
    forecast_days: int = Field(30, description="Number of days to forecast ahead")
    include_linear_fit: bool = Field(True, description="Include linear regression analysis")


class LinearFitData(BaseModel):
    """Linear regression fit results."""
    slope: float
    intercept: float
    r_value: float
    r_squared: float
    equation: str


class ForecastOutput(BaseModel):
    """Response model for production forecast results."""
    grade_id: int
    grade_name: str
    forecast_date: date
    predicted_tons: float
    confidence_score: float
    linear_fit: Optional[LinearFitData] = None
    historical_data_points: int


class ProductionSummaryResponse(BaseModel):
    """Response model for production summary statistics."""
    grade_id: int
    historical_records: int
    total_historical_tons: int
    forecasted_records: int
    total_forecasted_heats: int
    avg_tons_per_period: Optional[float] = None


class UploadResponse(BaseModel):
    """Response model for file upload operations."""
    message: str
    records_inserted: int
    file_name: str
    processing_time_seconds: float


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: str
    timestamp: str
