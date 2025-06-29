from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List, Dict


class ForecastOutput(BaseModel):
    """Response model for production forecast results - steel grade breakdown."""

    forecast_date: date = Field(
        ..., 
        description="Date for the forecast", 
        example="2024-09-01"
    )
    grade_breakdown: Dict[str, int] = Field(
        ...,
        description="Steel grade breakdown showing number of heats for each grade",
        example={
            "B500A": 15,
            "B500B": 10, 
            "B500C": 25,
            "A36": 8,
            "1010": 5
        }
    )
    total_heats: int = Field(
        ...,
        description="Total number of heats forecasted",
        example=63
    )


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(
        ..., 
        description="Error type or category", 
        example="File Processing Error"
    )
    detail: str = Field(
        ..., 
        description="Detailed error message", 
        example="Error processing file: Missing required columns"
    )
    timestamp: str = Field(
        ..., 
        description="Timestamp when error occurred", 
        example="2024-08-30T14:30:25.123456"
    )


class ForecastRequest(BaseModel):
    """Request model for production forecast."""

    grade_percentages: Dict = Field(
        ..., 
        description="List of steel grade IDs to forecast and respective percentages",
        example={"B500A": 25, "B500B": 25, "B500C": 50}
    )


class UploadResponse(BaseModel):
    """Response model for file upload endpoints."""

    message: str = Field(
        ..., 
        description="Success message describing the upload result", 
        example="Product groups and forecasted production uploaded successfully. 25 records inserted."
    )
    records_inserted: int = Field(
        ..., 
        description="Number of records successfully inserted into the database", 
        example=25
    )
