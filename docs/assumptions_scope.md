# Assumptions and Scope
SteelWorks Operations Internal Tool

---

## Assumptions

1. The system is an internal tool used only by SteelWorks employees (operations, quality, and production teams).

2. Each production batch is identified by a unique lot code.

3. A lot may be produced on one production line per production record, but a production line can produce many lots.

4. Quality inspections are recorded by lot and defect type.

5. Defects are categorized into predefined defect types.

6. A lot may be inspected multiple times.

7. A lot may or may not be shipped. If shipped, it will have one shipment record.

8. Operations primarily need summary-level information (e.g., defects by line, defect trends over time, shipment status).

9. Data is originally sourced from spreadsheets maintained by production, quality, and shipping teams.

10. The system focuses on structured reporting and does not include advanced analytics or predictive modeling.

---

## Scope

### In Scope

- Storing production records by lot and production line.
- Storing inspection records by lot and defect type.
- Tracking shipment status of each lot.
- Supporting queries for:
  - Production line issue summaries
  - Defect trends over time
  - Shipment status lookup by lot
  - Combined reporting across production, inspection, and shipment data
- Enforcing data integrity through constraints and foreign keys.

### Out of Scope

- User authentication and role management.
- Real-time IoT integration from production machines.
- Advanced analytics or machine learning models.
- Financial tracking or cost analysis.
- Inventory management beyond lot-level tracking.
- Detailed employee or inspector management.
- External customer-facing functionality.

---

## Constraints

- PostgreSQL is used as the database.
- All tables use surrogate primary keys.
- Data types follow best practices (DATE, INTEGER, BOOLEAN).
- Naming conventions follow snake_case and plural table names.
- Referential integrity is enforced with foreign keys.

