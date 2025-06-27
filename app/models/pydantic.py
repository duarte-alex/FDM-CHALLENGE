from pydantic import BaseModel
from datetime import date
from typing import Dict


class ForecastRequest(BaseModel):
    date: date
    forecast: Dict[str, int]


class ForecastOutput(BaseModel):
    forecast: Dict[str, int]
