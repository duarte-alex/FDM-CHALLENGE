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

### Environment Variables
The Docker setup automatically configures:
- Database connection: `postgresql://steel:steel@db:5432/steel_db`
- Application port: 8000
- Data volumes for persistence
