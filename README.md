# FDM-CHALLENGE

In this repository a simple API and database schema are implemented for a steel plant's production plans.

## Repository Structure

FDM-CHALLENGE/
│
├── app/
│   ├── __init__.py
│   ├── main.py              
│   ├── database.py           
│   ├── models.py              
│   ├── schemas.py           
│   ├── logic.py             
│   └── api/
│       ├── __init__.py
│       └── routes.py          
│
├── data/                    
│   ├── daily_charge_schedule.xlsx
│   ├── product_groups_monthly.xlsx
│   ├── steel_grade_production.xlsx
│   └── /processed                     
│
├── example.py
│
├── .github/workflows
├── README.md
└──  requirements.txt

## Project Highlights

- utility/: modular helper functions for preprocessing, plotting and fitting .csv, .xlsx and .xls
- .github/workflows: github actions to ensure code compliant with black formatting
- app/schema.py: used sql alchemy to define schemas in accordance with project description and goals

### Prediction Formula

For the data provided the linear fit coefficients ($A_{fit}$ and $B_{fit}$) were obtained with correlation coefficient $R \approx 1$. The formula used in the prediction API is:

$
P_{Predicted Grade} = (A_{fit} \times X_{product forecast} + B_{fit}) \times G_{Grade \% average} (units: short tons)
$
There aren't enough data points and variables for any complex AI predictive models. The best way to define our forecast logic is by using a linear regression. It's advantages are:

- **interpretability**: results for a linear regression are easy to communicate to client improving their trust and thus model aceptance

- **$R \approx 1$**: there is a near perfect positive linear correlation 

## Local project set up

### UV

1) The recommendable way to install the dependencies is using **uv** (python +3.8):

```
pip install uv
uv pip install -r requirements.txt
```

When running a script use:

```
uv venv exec python main.py
```

### Virtual environments
2) It is also possible to use virtual environment **venv**:

Create virtual environment:
```
python -m venv fdm-challenge
```

Activate virtual environment:

```
source fdm-challenge/bin/activate
```

### Database set up

In this project, I use PostgreSQL because it gives you reliable structure, strong querying, and flexibility. It can be installed with:

```
sudo apt install postgresql postgresql-contrib
```

In ``database.py``` the postgres url for database connection is:

```
POSTGRES_URL = "postgresql://steel:steel@localhost:5432/steel_db"
```

This assumes a database and user of the following type has been set up. To create locally a database and user, fist open PostgreSQL interactive shell (psql): ```sudo -u postgres psql```. Next, run the following code:

```
CREATE DATABASE steel_db;
CREATE USER steel WITH PASSWORD 'steel';
GRANT ALL PRIVILEGES ON DATABASE steel_db TO steel;
\q
```

sudo -u postgres psql -d steel_db -f init.sql

## Docker Setup

The easiest way to run the project is using Docker, which automatically sets up both the application and PostgreSQL database. In this tutorial we assume you docker and docker compose have been installed on your system.

```bash
docker-compose up --build
```

## Database Schema

The database schema is designed to model a steel plant's production workflow with the following entities:

### **Tables Overview**

```sql
-- Core entities
ProductGroup (id, name)
SteelGrade (id, name, product_group_id)

-- Production data
HistoricalProduction (id, date, tons, grade_id)
ForecastedProduction (id, date, heats, grade_id)
DailyProductionSchedule (id, date, start_time, mould_size, grade_id)
```

### **Entity Relationships**

1. **ProductGroup** → **SteelGrade** (One-to-Many)
   - Each product group (e.g., "Rebar", "MBQ") contains multiple steel grades
   - Examples: Rebar group contains B500A, B500B, B500C grades

2. **SteelGrade** → **HistoricalProduction** (One-to-Many)
   - Each steel grade has multiple historical production records
   - Tracks tons produced by date for each grade

3. **SteelGrade** → **ForecastedProduction** (One-to-Many)
   - Each steel grade has forecasted production data
   - Tracks planned heats by date for each grade

4. **SteelGrade** → **DailyProductionSchedule** (One-to-Many)
   - Each steel grade appears in daily production schedules
   - Tracks start times and mould sizes for each grade

### **Schema Details**

#### **ProductGroup Table**
- **Purpose**: Categorizes steel grades into logical groups
- **Fields**: 
  - `id`: Primary key
  - `name`: Unique product group name (e.g., "Rebar", "MBQ", "SBQ", "CHQ")

#### **SteelGrade Table**
- **Purpose**: Defines specific steel grades within product groups
- **Fields**:
  - `id`: Primary key
  - `name`: Unique steel grade name (e.g., "B500A", "A36", "A5888")
  - `product_group_id`: Foreign key to ProductGroup

#### **HistoricalProduction Table**
- **Purpose**: Records actual production data for analysis and forecasting
- **Fields**:
  - `id`: Primary key
  - `date`: Production date
  - `tons`: Amount produced in tons
  - `grade_id`: Foreign key to SteelGrade

#### **ForecastedProduction Table**
- **Purpose**: Stores production forecasts generated by the prediction model
- **Fields**:
  - `id`: Primary key
  - `date`: Forecast date (NOT NULL)
  - `heats`: Number of heats forecasted (NOT NULL)
  - `grade_id`: Foreign key to SteelGrade (NOT NULL)

#### **DailyProductionSchedule Table**
- **Purpose**: Manages daily production scheduling and planning
- **Fields**:
  - `id`: Primary key
  - `date`: Schedule date (NOT NULL)
  - `start_time`: Production start time
  - `mould_size`: Mould size specification
  - `grade_id`: Foreign key to SteelGrade (NOT NULL)

### **Data Flow**

1. **Excel Data Ingestion**: Raw data from Excel files is processed and stored
2. **Historical Analysis**: Historical production data is analyzed using linear regression
3. **Forecasting**: Predictions are generated and stored in ForecastedProduction
4. **Scheduling**: Daily schedules are created based on forecasts and requirements