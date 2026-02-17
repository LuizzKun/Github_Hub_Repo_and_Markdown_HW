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

- **Database**: PostgreSQL (Render.com for deployment)
- **Language**: Python 3.9+
- **ORM**: SQLAlchemy
- **API**: Flask (optional, for web interface)
- **Testing**: pytest
- **Data Validation**: Pydantic

### Architecture

```
Data Sources (Excel) 
    ↓
seed.sql (Initial Data Load)
    ↓
PostgreSQL Database (Schema defined in db/schema.sql)
    ↓
Python ORM Layer (SQLAlchemy models)
    ↓
Operations API / CLI Interface
```

---

## How to Run / Build the Code

### Prerequisites

- Python 3.9 or higher
- PostgreSQL (or access to Render.com PostgreSQL instance)
- pip (Python package manager)
- Git

### Setup Instructions

#### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd Github_Hub_Repo_and_Markdown_HW
```

#### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Configure Database

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://username:password@hostname:port/dbname
RENDER_DB_URL=postgresql://user:password@dpg-xxxx.render.com:5432/steelworks_db
ENV=development
LOG_LEVEL=INFO
```

Or use Render.com's provided connection string directly.

#### 5. Initialize Database

```bash
# Create schema in your PostgreSQL database
psql -h hostname -U username -d dbname -f db/schema.sql

# Load sample data
psql -h hostname -U username -d dbname -f db/seed.sql
```

#### 6. Run the Application

```bash
# CLI Mode
python -m src.main --help

# API Mode (if Flask is configured)
python -m src.api.app
```

---

## Usage Examples

### Example 1: Retrieve Production Records by Lot

```python
from src.models import ProductionRecord
from src.database import get_session

session = get_session()

# Get all production records for a specific lot
lot_id = 1
records = session.query(ProductionRecord).filter(
    ProductionRecord.lot_id == lot_id
).all()

for record in records:
    print(f"Lot {record.lot_id} - Line {record.production_line_id} - Date {record.record_date}")
```

### Example 2: Aggregate Defects by Production Line

```python
from src.models import InspectionRecord
from src.database import get_session
from sqlalchemy import func
from datetime import datetime, timedelta

session = get_session()

# Get defect counts by production line in the last 30 days
days_back = 30
start_date = datetime.now() - timedelta(days=days_back)

defect_summary = session.query(
    InspectionRecord.defect_type_id,
    func.count(InspectionRecord.id).label('defect_count'),
    func.sum(InspectionRecord.qty_defects).label('total_qty')
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

## Project Structure

```
Github_Hub_Repo_and_Markdown_HW/
├── src/
│   ├── __init__.py
│   ├── main.py                 # CLI entry point
│   ├── database.py             # Database connection and session management
│   ├── models.py               # SQLAlchemy ORM models
│   ├── config.py               # Configuration management
│   ├── services/
│   │   ├── __init__.py
│   │   ├── report_service.py   # Reporting and analytics
│   │   ├── data_service.py     # Data operations
│   │   └── validation_service.py
│   ├── api/                    # Flask API (optional)
│   │   ├── __init__.py
│   │   ├── app.py
│   │   └── routes.py
│   └── utils/
│       ├── __init__.py
│       ├── excel_parser.py
│       └── validators.py
├── db/
│   ├── schema.sql              # PostgreSQL schema definition
│   ├── seed.sql                # Sample data
│   └── sample_queries.sql      # Common reporting queries
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_services.py
│   ├── test_integration.py
│   └── conftest.py             # pytest configuration
├── docs/
│   ├── assumptions_scope.md
│   ├── architecture_decision_records.md
│   ├── data_design.md
│   └── tech_stack_decision_records.md
├── data/
│   └── sample/                 # Sample Excel files
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore
└── README.md
```

---

## Acceptance Criteria & Coverage

All Acceptance Criteria (ACs) are covered by automated tests:

- ✅ AC1: Defect aggregation by production line and date
- ✅ AC2: Shipment status tracking and validation
- ✅ AC3: Cross-validation of production, inspection, and shipment records
- ✅ AC4: Data consistency and referential integrity
- ✅ AC5: Performance with large datasets (indexed queries)

---

## Database Connection

### Local PostgreSQL

```bash
psql -h localhost -U postgres -d steelworks
```

### Render.com PostgreSQL

Connection details are provided in the Render dashboard. Use the `DATABASE_URL` in your `.env` file.

### Verify Connection

```python
from src.database import get_session
session = get_session()
print("Database connection successful!")
```

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

For issues, questions, or contributions, please open an issue on GitHub or contact the operations team.