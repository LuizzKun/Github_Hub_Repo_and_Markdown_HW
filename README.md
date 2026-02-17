# SteelWorks Operations Reporting Tool

## Project Description

SteelWorks Operations Reporting Tool is a Python-based application designed to help operations teams review and summarize production, quality, and shipment information for manufacturing batches (lots). The system integrates data from multiple sources—production records, inspection logs, and shipment databases—into a unified PostgreSQL data warehouse that supports analytical reporting and operational decision-making.

### Key Features

- **Production Line Analytics**: Identify which production lines had the most defects within a given time period
- **Defect Aggregation**: Aggregate defect counts by lot, production line, and date
- **Trend Analysis**: Track defect trends over time to identify patterns
- **Shipment Tracking**: Determine whether a lot has been shipped and review shipment dates
- **Data Validation**: Cross-validate production, inspection, and shipment records for data consistency
- **Referential Integrity**: Enforce relationships between lots, production lines, defects, and shipments

### Technology Stack

- **Database**: PostgreSQL (Render.com hosted)
- **Language**: Python 3.12+
- **Framework**: Streamlit (interactive web UI)
- **ORM**: SQLAlchemy 2.x
- **Package Manager**: Poetry
- **Visualization**: Matplotlib
- **Testing**: pytest

### Architecture

```
Data Sources (Excel, Operations Logs)
    ↓
seed.sql (Sample Data Load)
    ↓
PostgreSQL Database on Render.com (Schema: db/schema.sql)
    ↓
Python ORM Layer (SQLAlchemy models)
    ↓
Service Layer (Business Logic)
    ↓
Streamlit Web Dashboard (Interactive UI)
```

---

## How to Run / Build the Code

### Prerequ12 or higher
- Poetry (Python package manager)
- Render.com PostgreSQL instance (or local PostgreSQL)
- Git

### Quick Start

#### 1. Clone & Install Dependencies

```bash
git clone <your-repo-url>
cd Github_Hub_Repo_and_Markdown_HW
poetry install
```

#### 2. Configure Database

Create a `.env` file in the project root with your Render PostgreSQL connection string:

```env
DATABASE_URL=postgresql://username:password@dpg-xxxxx.render.com/steelworks_db?sslmode=require
```

#### 3. Initialize Database

```bash
poetry run python init_db.py
```

This script will:
- Connect to your Render PostgreSQL database
- Create all tables (schema.sql)
- Load sample data (seed.sql)

#### 4. Run the Streamlit Dashboard

```bash
poetry run streamlit run src/ui.py
```

The dashboard will open at `http://localhost:8501`

---

## Dashboard Features

### Pages Available

1. **Dashboard (Overview)** - Summary metrics:
   - Production lines with most defects
   - Defect trends over time (Last 30 days)
   - Shipment status (shipped vs pending)

2. **Production Line Quality** - AC 1:
   - Identify which production lines had the most defects in the selected period
   - Rank lines by defect count

3. **Defect Trends** - AC 2 & 3:
   - Daily defect trend visualization
   - Defect aggregation by type with percentages

4. **Shipment Status** - AC 4:
   - View all lots and their shipment status
   - Filter by shipped/pending status

5. **Lot Details (Drill-down)** - AC 5:
   - Search for specific lots
## Database Schema

### Tables

- **lots** - Production batches (lot_code UNIQUE)
- **production_lines** - Factory lines (line_code UNIQUE)
- **defect_types** - Quality defect categories (defect_code UNIQUE)
- **production_records** - Production events linking lots to lines and dates
- **inspection_records** - Quality inspection with defect counts
- **shipment_records** - Shipment status (one per lot, with date validation)

### Views & Indexes

All tables include indexes on:
- Date ranges (for reporting queries)
- Foreign keys (for referential integrity)
- Unique constraints (for data consistency)

---

## Architecture

### Code Structure

```
src/
├── __init__.py
├── models.py              # SQLAlchemy ORM definitions
├── repository.py          # Data access layer
├── service.py             # Business logic & reporting
├── ui.py                  # Streamlit dashboard
└── __pycache__/

db/
├── schema.sql             # Database schema (tables, indexes)
├── seed.sql               # Sample data
└── sample_queries.sql     # Useful SQL queries

tests/
├── __init__.py
├── test_models.py
├── test_service.py
├── __init__.py

init_db.py                 # Database initialization script
```

### Data Flow

```
.env (Database URL)
    ↓
models.py (load_dotenv, get_db_connection_string)
    ↓
Render PostgreSQL
    ↓
repository.py (queries)
    ↓
service.py (business logic)
    ↓
ui.py (Streamlit dashboard displays resultsects).label('total_qty')
).filter(
    InspectionRecord.inspection_date >= start_date
).group_by(
    InspectionRecord.defect_type_id
).all()

for defect_id, count, qty in defect_summary:
    print(f"Defect {defect_id}: {count} records, {qty} units")
```

### Example 3: Check Shipment Status

```python
from src.models import Lot, ShipmentRecord
from src.database import get_session

session = get_session()

# Get shipment status for all lots
shipments = session.query(Lot, ShipmentRecord).outerjoin(
    ShipmentRecord, Lot.id == ShipmentRecord.lot_id
).all()

for lot, shipment in shipments:
    if shipment and shipment.is_shipped:
        print(f"Lot {lot.lot_code}: Shipped on {shipment.ship_date}")
    else:
        print(f"Lot {lot.lot_code}: Not yet shipped")
```

### Example 4: Identify Problem Production Lines

```python
from sqlalchemy import func
from src.models import ProductionRecord, InspectionRecord
from src.database import get_session

session = get_session()

# Find production lines with highest defect counts
problem_lines = session.query(
    ProductionRecord.production_line_id,
    func.count(InspectionRecord.id).label('defect_count')
).join(
    InspectionRecord, ProductionRecord.lot_id == InspectionRecord.lot_id
).group_by(
    ProductionRecord.production_line_id
).order_by(
    func.count(InspectionRecord.id).desc()
).limit(5).all()

print("Top 5 Problem Production Lines:")
for line_id, defect_count in problem_lines:
    print(f"  Line {line_id}: {defect_count} defect records")
```

### Example 5: Generate Defect Trend Report

```python
from src.services.report_service import DefectTrendReporter

reporter = DefectTrendReporter()
trend_data = reporter.get_monthly_defect_trends(
    months_back=6,
    defect_type_id=None  # None = all defects
)

for month, count in trend_data:
    print(f"{month}: {count} defects")
```

---

## How to Run Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test Module

```bash
pytest tests/test_models.py -v
```

### Run Tests with Coverage Report

```bash
pytest --cov=src --cov-report=html
```

### Run Tests by Marker

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests (requires database)
pytest -m integration
```

### Example Test Output

```
tests/test_models.py::test_lot_creation PASSED                    [ 10%]
tests/test_models.py::test_production_record_foreign_key PASSED   [ 20%]
tests/test_services.py::test_defect_aggregation PASSED            [ 30%]
tests/test_services.py::test_shipment_status PASSED               [ 40%]
tests/test_integration.py::test_end_to_end_workflow PASSED        [ 50%]

============================== 50 passed in 2.34s ==============================
```

### Viewing Test Coverage

After running tests with coverage, open the HTML report:

```bash
# Windows
start htmlcov/index.html

# macOS
open htmlcov/index.html

# Linux
xdg-open htmlcov/index.html
```

---

## Acceptance Criteria Coverage

All acceptance criteria are supported by the Streamlit dashboard:

- ✅ **AC 1**: Identify production lines with most defects (Production Line Quality page)
- ✅ **AC 2**: Defect trends over time (Defect Trends page - Daily Trend chart)
- ✅ **AC 3**: Aggregate defects by type (Defect Trends page - By Type section)
- ✅ **AC 4**: Determine shipped lots (Shipment Status page)
- ✅ **AC 5**: Lot drill-down with cross-functional data (Lot Details page)
- ✅ **AC 6**: Production summary by date and line (Production Summary page)

---

## Troubleshooting

### Issue: ModuleNotFoundError

**Solution**: Ensure virtual environment is activated and dependencies are installed.

```bash
pip install -r requirements.txt
```

### Issue: Database connection refused

**Solution**: Check `.env` file and verify database server is running.

```bash
# Test connection
psql -h hostname -U username -d dbname
```

### Issue: Schema not found

**Solution**: Initialize the database schema.

```bash
psql -h hostname -U username -d dbname -f db/schema.sql
```

---

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and write tests
3. Run tests: `pytest`
4. Commit: `git commit -am 'Add feature'`
5. Push: `git push origin feature/your-feature`
6. Create Pull Request

---

## License

MIT License - See LICENSE file for details

---

## Contact & Support

For issues, questions, or contributions, please open an issue on GitHub or contact the operations team.`ModuleNotFoundError: No module named 'matplotlib'`

**Solution**: Install matplotlib

```bash
poetry add matplotlib
# or
pip install matplotlib
```

### Issue: Database connection failed

**Solution**: Verify `.env` file has correct `DATABASE_URL`

```bash
# Check .env exists and has DATABASE_URL
cat .env
```

### Issue: `psycopg2.OperationalError: connection failed`

**Solution**: Ensure DATABASE_URL has correct credentials and `sslmode=require`

```env
DATABASE_URL=postgresql://user:password@host/database?sslmode=require
```

### Issue: Tables don't exist after `init_db.py`

**Solution**: Re-run initialization (it drops and recreates tables)

```bash
poetry run python init_db.py
```

### Issue: Streamlit cache issues

**Solution**: Clear Streamlit cache

```bash
# Windows
rmdir /s %userprofile%\.streamlit\cache

# macOS/Linux
rm -rf ~/.streamlit/cache
```

Then restart the app:

```bash
poetry run streamlit run src/ui.py