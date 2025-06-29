from fastapi import FastAPI
from .api.routes import router
from .database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Steel Production Forecast API",
    description="""
## 🏭 Steel Plant Production Planning & Forecasting System

A simple API and database schema implemented for a steel plant's production plans.

### 📋 Getting Started

1. **Upload Product Groups**: Use /upload/product-groups to upload product_groups_monthly
2. **Import Historical Data**: Use /upload/production-history to upload steel_grade_production.xslx
3. **Schedule Production**: Use /upload/daily-schedule to upload daily_charge_schedule.xlsx
4. **Generate Forecasts**: Use /forecast endpoint to predict September's production for selected steel grades

### 🔗 Quick Links

* **Interactive Documentation**: Available at /docs
* **Health Check**: Monitor system status at /health
* **Data Endpoints**: View all product groups and steel grades
* **GitHub Repository**: [FDM-Challenge](https://github.com/duarte-alex/FDM-CHALLENGE.git)

### 🏗️ Architecture

Built with **FastAPI** + **PostgreSQL** for high-performance, production-ready deployment with Docker support. Useful links:
    """,
    version="1.0.0",
    license_info={
        "name": "MIT License",
        "url": "https://github.com/duarte-alex/FDM-CHALLENGE/blob/main/LICENSE",
    },
    openapi_tags=[
        {"name": "root", "description": "🏠 Welcome & navigation endpoints"},
        {
            "name": "health",
            "description": "💓 Health check and system monitoring endpoints",
        },
        {
            "name": "data-upload",
            "description": "📤 File upload endpoints for data ingestion (Excel/CSV support)",
        },
        {
            "name": "forecasting",
            "description": "🔮 Production forecasting and predictive analytics with linear regression",
        },
        {"name": "reference", "description": "📚 Get information on the data uploaded"},
    ],
)

app.include_router(router)
