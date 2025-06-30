-- Grant schema-level permissions to create tables and sequences
GRANT CREATE ON SCHEMA public TO steel;
GRANT USAGE ON SCHEMA public TO steel;

-- Grant privileges on all existing tables and sequences
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO steel;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO steel;

-- Grant privileges on future tables and sequences (important for auto-created sequences)
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO steel;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO steel;

-- Create product groups
CREATE TABLE product_groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL
);

-- Create steel grades
CREATE TABLE steel_grades (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    product_group_id INTEGER REFERENCES product_groups(id)
);

-- Create historical production
CREATE TABLE historical_production (
    id SERIAL PRIMARY KEY,
    date DATE,
    tons INTEGER,
    grade_id INTEGER REFERENCES steel_grades(id)
);

-- Create forecasted production
CREATE TABLE forecasted_production (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    heats INTEGER NOT NULL,
    product_group_id INTEGER NOT NULL REFERENCES product_groups(id)
);

-- Create daily production schedule
CREATE TABLE daily_production_schedule (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    start_time VARCHAR,
    mould_size VARCHAR,
    grade_id INTEGER NOT NULL REFERENCES steel_grades(id)
);

-- simple index for date-based queries on historical production
CREATE INDEX idx_historical_production_date ON historical_production(date);
