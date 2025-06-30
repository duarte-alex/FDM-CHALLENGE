from fastapi import FastAPI
from .api.routes import router
from .database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Steel Production API",
    description="""
## 🏭 Steel Plant Analysis & Forecasting System

A simple API and database schema implemented for a steel plant's production plans.

### 📋 Getting Started

1. **Upload Product Groups**: **[FIRST STEP]** Use /upload/product-groups to upload product_groups_monthly.xlsx
2. **Import Historical Data**: Use /upload/production-history to upload steel_grade_production.xlsx
3. **Import Scheduled Production**: Use /upload/daily-schedule to upload daily_charge_schedule.xlsx
4. **September's Forecast**: Use /forecast endpoint to predict September's production for selected steel grades and weights

### 🔗 Quick Links

* **[📖 Interactive Documentation](/docs)** - Explore all API endpoints with interactive testing
* **[💓 Health Check](/health)** - Monitor system status and database connectivity
* **[📊 Product Groups](/product-groups)** - View all uploaded product group data
* **[🔩 Steel Grades](/steel-grades)** - Browse all steel grade information
* **[🐙 GitHub Repository](https://github.com/duarte-alex/FDM-CHALLENGE.git)** - View source code and documentation

### 🏗️ Architecture

Built with **FastAPI** + **PostgreSQL** for high-performance, production-ready deployment with Docker support. Useful links:
    """,
    version="1.0.0",
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
            "description": "🔮 September's production forecast in a format ScrapCheft can use",
        },
        {"name": "reference", "description": "📚 Get information on the data uploaded"},
    ],
)

app.include_router(router)
