# trade-pnl-attribution-pipeline
End-to-end financial data pipeline for trade ingestion, EOD position building, PnL attribution, reconciliation, and tolerance-based exception reporting using Python, pandas, SQL, PostgreSQL, and pytest.

A Python and PostgreSQL-based **Trade PnL Attribution Pipeline** that processes trades and market data to calculate daily positions, realized PnL, unrealized PnL, total PnL, and PnL attribution.

The project is designed as a small data-engineering / financial-data pipeline demonstrating:

* CSV data ingestion
* PostgreSQL database integration
* Docker-based PostgreSQL environment
* Position calculation
* Weighted-average cost calculation
* Realized and unrealized PnL calculation
* PnL attribution
* SQL reporting views
* Automated testing with pytest

---

## Project Architecture

```text
CSV Files
   │
   ├── instruments.csv
   ├── trades.csv
   └── market_prices.csv
          │
          ▼
   Data Ingestion Layer
          │
          ▼
      PostgreSQL
          │
          ├── dim_instrument
          ├── fct_trade
          └── fct_market_price
          │
          ▼
   Position Calculation
          │
          ▼
      fct_position
          │
          ▼
      PnL Calculation
          │
          ▼
        fct_pnl
          │
          ▼
   PnL Attribution
          │
          ▼
   fct_pnl_attribution
          │
          ▼
     Reporting Views
```

---

# 1. Prerequisites

Before running the project, install the following:

* Python 3.10+
* Git
* Docker Desktop
* PostgreSQL is **not required locally** because PostgreSQL runs inside Docker.

Verify the installations:

```powershell
python --version
git --version
docker --version
docker compose version
```

---

# 2. Clone the Repository

Clone the repository:

```powershell
git clone https://github.com/AmberVats/trade-pnl-attribution-pipeline.git
```

Move into the project directory:

```powershell
cd trade-pnl-attribution-pipeline
```

---

# 3. Create a Python Virtual Environment

Create the virtual environment:

```powershell
python -m venv .venv
```

Activate it in PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

After activation, the terminal should show:

```text
(.venv)
```

For example:

```text
(.venv) PS D:\...\trade-pnl-attribution-pipeline>
```

---

# 4. Install Python Dependencies

Install the project dependencies:

```powershell
pip install -r requirements.txt
```

The project uses Python libraries for:

* SQLAlchemy
* PostgreSQL connectivity
* Pandas
* PyYAML
* Pytest

To verify the environment:

```powershell
pip list
```

---

# 5. Start PostgreSQL Using Docker

Start the PostgreSQL container using Docker Compose:

```powershell
docker compose up -d
```

Check that the container is running:

```powershell
docker ps
```

You should see the PostgreSQL container running.

The project uses the PostgreSQL database:

```text
Database: trade_pnl
User: trade_user
```

---

# 6. Initialize the Database Schema

The database schema is stored in:

```text
sql/01_schema.sql
```

Apply the schema to PostgreSQL:

```powershell
Get-Content sql\01_schema.sql | docker exec -i trade_pnl_postgres psql -U trade_user -d trade_pnl
```

Verify the tables:

```powershell
docker exec -it trade_pnl_postgres psql -U trade_user -d trade_pnl -c "\dt"
```

The database should contain tables similar to:

```text
dim_instrument
fct_trade
fct_market_price
fct_position
fct_pnl
fct_pnl_attribution
```

---

# 7. Create Reporting Views

The project contains SQL reporting views in:

```text
sql/02_views.sql
```

Apply the views:

```powershell
Get-Content sql\02_views.sql | docker exec -i trade_pnl_postgres psql -U trade_user -d trade_pnl
```

Verify the views:

```powershell
docker exec -it trade_pnl_postgres psql -U trade_user -d trade_pnl -c "\dv"
```

Expected views:

```text
vw_daily_book_pnl
vw_daily_pnl_attribution
vw_instrument_pnl
```

---

# 8. Sample Data

Sample CSV files are located under:

```text
data/sample/
```

Files:

```text
data/sample/instruments.csv
data/sample/trades.csv
data/sample/market_prices.csv
```

The sample dataset contains:

### Instruments

```text
AAPL
MSFT
GOOGL
```

### Trades

The sample data contains:

* AAPL BUY
* MSFT BUY
* AAPL SELL
* GOOGL BUY

The pipeline calculates positions and PnL from these trades.

---

# 9. Run the Complete Pipeline

The recommended way to run the project is:

```powershell
python -m src.pipeline
```

The pipeline performs the following steps:

```text
[1/5] Loading instruments
[2/5] Loading trades
[3/5] Loading market prices
[4/5] Calculating positions
[5/5] Calculating PnL and attribution
```

Example output:

```text
Trade PnL Attribution Pipeline

Resetting previous input data...
Input tables cleared

[1/5] Loading instruments...
Loaded 3 instruments

[2/5] Loading trades...
Loaded 4 trades

[3/5] Loading market prices...
Loaded 8 market prices

[4/5] Calculating positions...
Calculated 4 positions

[5/5] Calculating PnL and attribution...
Calculated 4 PnL records
Calculated 4 attribution records
```

---

# 10. Run Individual Pipeline Components

The project components can also be executed independently.

## Calculate Positions

```powershell
python -c "from src.position import calculate_positions; print(calculate_positions())"
```

This calculates:

* Daily quantity
* Cumulative position
* Market price
* Market value
* Average price

---

## Calculate PnL

```powershell
python -c "from src.pnl import calculate_pnl; print(calculate_pnl())"
```

This calculates:

* Realized PnL
* Unrealized PnL
* Total PnL

The PnL calculation uses a **weighted-average cost** approach.

---

## Calculate PnL Attribution

```powershell
python -c "from src.attribution import calculate_attribution; print(calculate_attribution())"
```

This calculates:

* Trading PnL
* Price PnL
* Realized PnL
* Unrealized PnL
* Total PnL

---

# 11. Run Tests

Run the complete test suite:

```powershell
python -m pytest -v
```

The project currently contains tests covering:

```text
Position calculation
PnL calculation
PnL attribution
Database connection
```

Expected result:

```text
7 passed
```

Example:

```text
tests/test_attribution.py::test_calculate_attribution PASSED
tests/test_attribution.py::test_aapl_attribution PASSED
tests/test_db.py::test_database_connection PASSED
tests/test_pnl.py::test_calculate_pnl PASSED
tests/test_pnl.py::test_aapl_realized_pnl PASSED
tests/test_position.py::test_calculate_positions PASSED
tests/test_position.py::test_aapl_cumulative_position PASSED

7 passed
```

---

# 12. Verify Database Results

After running the pipeline, you can inspect the generated data directly from PostgreSQL.

## Positions

```powershell
docker exec -it trade_pnl_postgres psql -U trade_user -d trade_pnl -c "SELECT * FROM fct_position ORDER BY position_date, instrument_id;"
```

---

## PnL

```powershell
docker exec -it trade_pnl_postgres psql -U trade_user -d trade_pnl -c "SELECT * FROM fct_pnl ORDER BY pnl_date, instrument_id;"
```

---

## PnL Attribution

```powershell
docker exec -it trade_pnl_postgres psql -U trade_user -d trade_pnl -c "SELECT * FROM fct_pnl_attribution ORDER BY attribution_date, instrument_id;"
```

---

# 13. Reporting Views

The project provides three reporting views.

## Daily PnL Attribution

```powershell
docker exec -it trade_pnl_postgres psql -U trade_user -d trade_pnl -c "SELECT * FROM vw_daily_pnl_attribution;"
```

This provides PnL attribution by:

```text
Date
Book
Instrument
Trading PnL
Price PnL
Realized PnL
Unrealized PnL
Total PnL
Currency
```

---

## Daily Book PnL

```powershell
docker exec -it trade_pnl_postgres psql -U trade_user -d trade_pnl -c "SELECT * FROM vw_daily_book_pnl;"
```

This aggregates PnL at the book level.

Example:

```text
2026-08-03 | EQUITY_BOOK | 0
2026-08-04 | EQUITY_BOOK | 500
```

---

## Instrument PnL

```powershell
docker exec -it trade_pnl_postgres psql -U trade_user -d trade_pnl -c "SELECT * FROM vw_instrument_pnl;"
```

This provides PnL by instrument.

Example result:

```text
AAPL  | EQUITY_BOOK | 500
GOOGL | EQUITY_BOOK | 0
MSFT  | EQUITY_BOOK | 0
```

---

# 14. Example PnL Result

For the included sample data, AAPL produces the following PnL on 2026-08-04:

```text
Realized PnL     = 125
Unrealized PnL   = 375
Total PnL        = 500
```

The calculation is based on:

```text
AAPL BUY:
100 shares @ $200

AAPL SELL:
25 shares @ $205

Remaining position:
75 shares

Market price:
$205
```

### Realized PnL

```text
25 × (205 - 200)
= $125
```

### Unrealized PnL

```text
75 × (205 - 200)
= $375
```

### Total PnL

```text
125 + 375
= $500
```

---

# 15. Project Structure

```text
trade-pnl-attribution-pipeline/
│
├── config/
│   └── tolerances.yaml
│
├── data/
│   └── sample/
│       ├── instruments.csv
│       ├── market_prices.csv
│       └── trades.csv
│
├── sql/
│   ├── 01_schema.sql
│   └── 02_views.sql
│
├── src/
│   ├── __init__.py
│   ├── db.py
│   ├── ingestion.py
│   ├── position.py
│   ├── pnl.py
│   ├── attribution.py
│   └── pipeline.py
│
├── tests/
│   ├── test_attribution.py
│   ├── test_db.py
│   ├── test_pnl.py
│   └── test_position.py
│
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

# 16. Stopping the Docker Container

When finished working with the project:

```powershell
docker compose down
```

This stops and removes the running containers.

To start the environment again:

```powershell
docker compose up -d
```

---

# 17. Resetting the Project

The pipeline resets previously loaded input/calculated data when it runs.

To completely remove Docker containers and associated volumes:

```powershell
docker compose down -v
```

Then start again:

```powershell
docker compose up -d
```

Recreate the database schema:

```powershell
Get-Content sql\01_schema.sql | docker exec -i trade_pnl_postgres psql -U trade_user -d trade_pnl
```

Recreate the reporting views:

```powershell
Get-Content sql\02_views.sql | docker exec -i trade_pnl_postgres psql -U trade_user -d trade_pnl
```

Then run:

```powershell
python -m src.pipeline
```

---

# 18. Troubleshooting

## Docker container is not running

Check:

```powershell
docker ps
```

If the PostgreSQL container is not running:

```powershell
docker compose up -d
```

---

## Check PostgreSQL container logs

```powershell
docker logs trade_pnl_postgres
```

---

## Check database connection

```powershell
docker exec -it trade_pnl_postgres psql -U trade_user -d trade_pnl -c "SELECT version();"
```

---

## Check database tables

```powershell
docker exec -it trade_pnl_postgres psql -U trade_user -d trade_pnl -c "\dt"
```

---

## Check reporting views

```powershell
docker exec -it trade_pnl_postgres psql -U trade_user -d trade_pnl -c "\dv"
```

---

## If PowerShell output is too long

Save query output to a file:

```powershell
docker exec -it trade_pnl_postgres psql -U trade_user -d trade_pnl -c "SELECT * FROM vw_daily_pnl_attribution;" > pnl_report.txt
```

Then open it:

```powershell
notepad pnl_report.txt
```

---

# 19. Complete Setup — Quick Start

For someone cloning this project for the first time:

```powershell
git clone https://github.com/AmberVats/trade-pnl-attribution-pipeline.git

cd trade-pnl-attribution-pipeline

python -m venv .venv

.venv\Scripts\Activate.ps1

pip install -r requirements.txt

docker compose up -d

Get-Content sql\01_schema.sql | docker exec -i trade_pnl_postgres psql -U trade_user -d trade_pnl

Get-Content sql\02_views.sql | docker exec -i trade_pnl_postgres psql -U trade_user -d trade_pnl

python -m src.pipeline

python -m pytest -v
```

Expected final test result:

```text
7 passed
```

---

# 20. Technology Stack

| Technology | Purpose                 |
| ---------- | ----------------------- |
| Python     | Pipeline implementation |
| PostgreSQL | Relational database     |
| SQLAlchemy | Database connectivity   |
| psycopg2   | PostgreSQL driver       |
| Pandas     | CSV/data processing     |
| PyYAML     | Configuration           |
| Pytest     | Automated testing       |
| Docker     | PostgreSQL environment  |
| PowerShell | Command-line execution  |
| Git/GitHub | Version control         |

---

# 21. Key Financial Calculations

### Position

```text
BUY  → increases position
SELL → decreases position
```

### Market Value

```text
Market Value = Quantity × Market Price
```

### Realized PnL

```text
Realized PnL =
Sold Quantity × (Sell Price − Average Cost)
```

### Unrealized PnL

```text
Unrealized PnL =
Closing Quantity × (Market Price − Average Cost)
```

### Total PnL

```text
Total PnL =
Realized PnL + Unrealized PnL
```

### PnL Attribution

```text
Total PnL =
Trading PnL + Price PnL
```

---

# 22. Current Validation

The current implementation has been validated with:

```text
7 automated tests
7 passed
0 failed
```

The complete pipeline successfully produces:

```text
4 positions
4 PnL records
4 attribution records
```

The sample AAPL result is:

```text
Realized PnL    : $125
Unrealized PnL  : $375
Total PnL       : $500
```

---

# 23. Author

**Amber Vats**

GitHub:

https://github.com/AmberVats

Repository:

https://github.com/AmberVats/trade-pnl-attribution-pipeline
