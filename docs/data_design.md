# Data Design — Operations User Story (SteelWorks)

---

## 1. Source: Operations User Story

### User Story

As an operations team member,  
I want to review and summarize production, quality, and shipment information by lot ID and date,  
So that I can answer report questions about line issues, defect trends, and shipped batches without manually combining spreadsheets.

---

## 2. AI #1 Result (Normalized Manufacturing Model)

### Entities and Attributes

#### Lot
- **lot_id** (PK)

#### ProductionLine
- **line_id** (PK)

#### ProductionRecord
- **production_record_id** (PK)
- **lot_id** (FK → Lot.lot_id)
- **line_id** (FK → ProductionLine.line_id)
- record_date

#### DefectType
- **defect_code** (PK)

#### InspectionRecord
- **inspection_record_id** (PK)
- **lot_id** (FK → Lot.lot_id)
- inspection_date
- **defect_code** (FK → DefectType.defect_code)
- qty_defects

#### ShipmentRecord
- **shipment_id** (PK)
- **lot_id** (FK → Lot.lot_id)
- ship_date
- shipment_status

---

## 3. AI #2 Result (Activity / Timeline Model)

### Entities and Attributes

#### Lot
- **lot_id** (PK)

#### ProductionLine
- **line_id** (PK)

#### LotActivity
- **activity_id** (PK)
- **lot_id** (FK → Lot.lot_id)
- activity_date
- activity_type (production / inspection / shipment)
- line_id (FK → ProductionLine.line_id)

#### DefectObservation
- **defect_obs_id** (PK)
- **lot_id** (FK → Lot.lot_id)
- defect_code
- observed_date
- qty_defects

#### Shipment
- **shipment_id** (PK)
- **lot_id** (FK → Lot.lot_id)
- ship_date
- shipment_status

---

## 4. Comparison of AI Results

### What AI #1 Did Better
- Clear separation of production, inspection, and shipment data.
- Easier to query for operations questions (line issues, defect trends, shipment status).
- Cleaner and more traditional ERD structure.

### What AI #1 Did Worse
- Slightly more tables than necessary for a basic reporting tool.

### What AI #2 Did Better
- Models workflow as activities over time.
- Flexible when spreadsheet formats differ.

### What AI #2 Did Worse
- "LotActivity" entity is vague.
- Harder to enforce consistency for reporting.
- Less clear separation of responsibilities.

---

## 5. Final Merged Data Design (Chosen Model)

I selected the normalized structure from AI #1 because it is clearer, easier to query, and better supports reporting needs described in the user story.

### Final Entities and Attributes

#### Lot
- **lot_id** (PK)

#### ProductionLine
- **line_id** (PK)

#### ProductionRecord
- **production_record_id** (PK)
- **lot_id** (FK → Lot.lot_id)
- **line_id** (FK → ProductionLine.line_id)
- record_date

#### DefectType
- **defect_code** (PK)

#### InspectionRecord
- **inspection_record_id** (PK)
- **lot_id** (FK → Lot.lot_id)
- inspection_date
- **defect_code** (FK → DefectType.defect_code)
- qty_defects

#### ShipmentRecord
- **shipment_id** (PK)
- **lot_id** (FK → Lot.lot_id)
- ship_date
- shipment_status

---

## 6. Final Relationships (Business Meaning)

- One **Lot** can have many **ProductionRecords**.
- One **ProductionLine** can produce many **ProductionRecords**.
- One **Lot** can have many **InspectionRecords**.
- One **DefectType** can appear in many **InspectionRecords**.
- One **Lot** can have zero or one **ShipmentRecord**.

---

## 7. Mermaid ERD

```mermaid
erDiagram
  LOT ||--o{ PRODUCTION_RECORD : has
  PRODUCTION_LINE ||--o{ PRODUCTION_RECORD : runs_on
  LOT ||--o{ INSPECTION_RECORD : has
  DEFECT_TYPE ||--o{ INSPECTION_RECORD : categorized_as
  LOT ||--o| SHIPMENT_RECORD : ships_as

  LOT {
    string lot_id PK
  }

  PRODUCTION_LINE {
    string line_id PK
  }

  PRODUCTION_RECORD {
    string production_record_id PK
    string lot_id FK
    string line_id FK
    date record_date
  }

  DEFECT_TYPE {
    string defect_code PK
  }

  INSPECTION_RECORD {
    string inspection_record_id PK
    string lot_id FK
    date inspection_date
    string defect_code FK
    int qty_defects
  }

  SHIPMENT_RECORD {
    string shipment_id PK
    string lot_id FK
    date ship_date
    string shipment_status
  }

