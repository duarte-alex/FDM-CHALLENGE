# FDM-CHALLENGE

In this repository a simple API and database schema are implemented for a steel plant's production plans.

## Repository Structure

```
FDM-CHALLENGE/
│
├── app/                     # Main application code
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── crud.py              # Database operations
│   ├── database.py          # Database connection setup
│   │         
│   └── models/              # Data models
│   │   ├── pydantic.py      # API request/response models
│   │   └── schema.py        # SQLAlchemy database models
│   │             
│   └── api/                 # API routes
│       ├── __init__.py
│       └── routes.py        # Endpoint definitions
│
├── data/                    # Sample data files
│   ├── daily_charge_schedule.xlsx
│   ├── product_groups_monthly.xlsx
│   ├── steel_grade_production.xlsx
│   └── /processed           # Processed data output
│
├── tests/                   # Unit tests
│   ├── __init__.py
│   └── test_api.py          # API endpoint tests
│
├── utility/                 # Helper functions
│   ├── preprocess.py        # Data preprocessing
│   └── linear_fit.py        # Forecasting logic
│
├── .github/workflows        # CI/CD automation
├── docker-compose.yml       # Container orchestration
├── Dockerfile               # Container build instructions
├── init.sql                 # Database schema setup
├── README.md                # Project documentation
├── forecast_logic.ipynb     # Linear fits plots
└── requirements.txt         # Python dependencies
```

## Project Highlights

### **Production-Ready Steel Plant API**
- **FastAPI + PostgreSQL**: Modern, high-performance API with robust database integration
- **Dockerized Deployment**: One-command setup with `docker-compose up --build`
- **Interactive Documentation**: Auto-generated OpenAPI docs at `/docs` for easy API exploration

### **Forecasting Engine**
- **Linear Regression Model**: Achieves near-perfect correlation (R ≈ 1) for production predictions
- **Real-Time Predictions**: RESTful endpoint for generating forecasts for any month

### **Robust Data Processing Pipeline**
- **Multi-Format Data Ingestion**: Seamlessly processes non-tabular data and Excel (.xlsx, .xls) and CSV files
- **Data Validation**: Pydantic models ensure data integrity throughout the pipeline

### **API Design**
- **Modular Design**
- **Comprehensive CRUD Operations**
- **Scalable Schema**

### **Quality Assurance**
- **Automated Testing**: pytest-based unittest suite
- **CI/CD Pipeline**: GitHub Actions ensuring code quality with Black formatting

## Forecasting logic

The forecasting endpoint, runs a linear fit based on historical data
For the data provided the linear fit coefficients ($A_{fit}$ and $B_{fit}$) were obtained with correlation coefficient $R \approx 1$. The formula used in the prediction API is:

<p>
P<sub>Predicted Grade</sub> = (A<sub>fit</sub> × X<sub>product forecast</sub> + B<sub>fit</sub>) × G<sub>Grade % average</sub> (units: short tons)
</p>



- **interpretability**: results for a linear regression are easy to communicate to client increasing their trust

- **$R \approx 1$**: near perfect historical correlation plotted in ```forecast_logic.ipynb```

## Running the API

### Using Docker (Recommended)

The easiest way to run the project is using Docker, which automatically sets up both the application and PostgreSQL database. Assuming docker and docker compose have been installed on your system, the project can be set up with a single line:

```bash
docker-compose up --build
```

### Locally (Harder set up)

#### Install dependencies
1) The recommendable way to install the dependencies is using **uv**:

```
pip install uv
uv pip install -r requirements.txt
```

2) It is also possible to use virtual environment **venv**:

```
python -m venv fdm-challenge
source fdm-challenge/bin/activate
```

#### Database commands

When running locally since we are not using docker we need to install postgres:
```
sudo apt install postgresql postgresql-contrib
```
Then open the PostgreSQL interactive shell (psql): ```sudo -u postgres psql``` and create the database and users:

```
CREATE DATABASE steel_db;
CREATE USER steel WITH PASSWORD 'steel';
GRANT ALL PRIVILEGES ON DATABASE steel_db TO steel;
\q
```

Next, intialize the tables and grant permissions:
```
sudo -u postgres psql -d steel_db -f init.sql
```

You can check the tables were creating by running in psql:
```
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';
```

The API can be reached with:
```
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Database Schema

The database schema is designed to model a steel plant's production workflow with the following entities:

### **Tables Overview**

```sql
-- Core entities
ProductGroup (id, name)
SteelGrade (id, name, product_group_id)

-- Production data: corresponding to data files
HistoricalProduction (id, date, tons, grade_id)
ForecastedProduction (id, date, heats, grade_id)
DailyProductionSchedule (id, date, start_time, mould_size, grade_id)
```

### **Entity Relationship Diagram**

```mermaid
erDiagram
    ProductGroup {
        int id PK
        string name UK
    }
    
    SteelGrade {
        int id PK
        string name UK
        int product_group_id FK
    }
    
    HistoricalProduction {
        int id PK
        date date
        int tons
        int grade_id FK
    }
    
    ForecastedProduction {
        int id PK
        date date
        int heats
        int grade_id FK
    }
    
    DailyProductionSchedule {
        int id PK
        date date
        string start_time
        string mould_size
        int grade_id FK
    }
    
   ProductGroup ||--o{ SteelGrade : "contains"
   SteelGrade ||--o{ HistoricalProduction : "produces"
   SteelGrade ||--o{ ForecastedProduction : "forecasts"
   SteelGrade ||--o{ DailyProductionSchedule : "schedules"
```

**Relationship Legend:**
- `||--o{` = One-to-Many relationship
- `||--||` = One-to-One relationship  
- `}o--o{` = Many-to-Many relationship

### **Data Flow**

1. **Excel Data Ingestion**: Raw data from Excel files is processed and stored
2. **Historical Analysis**: Historical production data is analyzed using linear regression
3. **Forecasting**: Predictions are generated and stored in ForecastedProduction
4. **Scheduling**: Daily schedules are created based on forecasts and requirements

## Getting Started

### **Quick Demo (Recommended for Evaluation)**

1. **Start the application:**
   ```bash
   docker-compose up --build
   ```

2. **Generate demo data:**
   ```bash
   python scripts/generate_demo_data.py
   ```

3. **Access the API:**
   - **Interactive Docs**: http://localhost:8000/docs
   - **API Root**: http://localhost:8000

4. **Test the workflow:**
   - Upload `demo_product_groups.csv` via `/upload/group-breakdown`
   - Upload `demo_historical_production.csv` via `/upload/production-history`
   - Upload `demo_quality_forecast.csv` via `/upload/quality-forecast`
   - Test forecasting via `/forecast` endpoint
   - View production summaries via `/production-summary/{grade_id}`

### **API Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information and available endpoints |
| GET | `/docs` | Interactive API documentation |
| POST | `/forecast` | Generate production forecasts using linear regression |
| POST | `/upload/quality-forecast` | Upload forecasted production data |
| POST | `/upload/production-history` | Upload historical production data |
| POST | `/upload/group-breakdown` | Upload product groups and steel grades |
| GET | `/product-groups` | Get all product groups |
| GET | `/steel-grades` | Get all steel grades with pagination |
| GET | `/production-summary/{grade_id}` | Get production summary for specific grade |

### **Example API Usage**

```bash
# Get all product groups
curl -X GET "http://localhost:8000/product-groups"

# Get production summary for grade ID 1
curl -X GET "http://localhost:8000/production-summary/1"

# Upload a file (use the interactive docs for easier file uploads)
curl -X POST "http://localhost:8000/upload/production-history" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@demo_historical_production.csv"
```

## Unit Tests

The project includes a test suite to ensure API reliability. The tests validate core endpoints and error handling. The tests use FastAPI's TestClient for isolated testing without affecting production data. They can be run with:

```bash
pytest tests/
```
