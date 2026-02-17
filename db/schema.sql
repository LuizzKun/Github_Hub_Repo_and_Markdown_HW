-- db/schema.sql
-- SteelWorks Operations - Physical Data Design (PostgreSQL)

BEGIN;

DROP TABLE IF EXISTS shipment_records;
DROP TABLE IF EXISTS inspection_records;
DROP TABLE IF EXISTS production_records;
DROP TABLE IF EXISTS defect_types;
DROP TABLE IF EXISTS production_lines;
DROP TABLE IF EXISTS lots;

-- =========================
-- Dimension tables
-- =========================

CREATE TABLE lots (
    id BIGSERIAL PRIMARY KEY,
    lot_code TEXT NOT NULL UNIQUE
);

CREATE TABLE production_lines (
    id BIGSERIAL PRIMARY KEY,
    line_code TEXT NOT NULL UNIQUE
);

CREATE TABLE defect_types (
    id BIGSERIAL PRIMARY KEY,
    defect_code TEXT NOT NULL UNIQUE
);

-- =========================
-- Production (Ops_Production_Log)
-- =========================

CREATE TABLE production_records (
    id BIGSERIAL PRIMARY KEY,

    lot_id BIGINT NOT NULL,
    production_line_id BIGINT NOT NULL,

    record_date DATE NOT NULL,

    CONSTRAINT fk_production_records_lot
        FOREIGN KEY (lot_id)
        REFERENCES lots(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_production_records_production_line
        FOREIGN KEY (production_line_id)
        REFERENCES production_lines(id)
        ON DELETE RESTRICT
);

-- =========================
-- Inspection (QE_Inspector logs)
-- =========================

CREATE TABLE inspection_records (
    id BIGSERIAL PRIMARY KEY,

    lot_id BIGINT NOT NULL,
    defect_type_id BIGINT NOT NULL,

    inspection_date DATE NOT NULL,
    qty_defects INTEGER NOT NULL,

    CONSTRAINT fk_inspection_records_lot
        FOREIGN KEY (lot_id)
        REFERENCES lots(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_inspection_records_defect_type
        FOREIGN KEY (defect_type_id)
        REFERENCES defect_types(id)
        ON DELETE RESTRICT,

    CONSTRAINT ck_qty_defects_nonneg CHECK (qty_defects >= 0)
);

-- =========================
-- Shipping (Ops_Shipping_Log)
-- =========================

CREATE TABLE shipment_records (
    id BIGSERIAL PRIMARY KEY,

    lot_id BIGINT NOT NULL UNIQUE,

    is_shipped BOOLEAN NOT NULL,
    ship_date DATE,

    CONSTRAINT fk_shipment_records_lot
        FOREIGN KEY (lot_id)
        REFERENCES lots(id)
        ON DELETE CASCADE,

    CONSTRAINT ck_ship_date_logic
        CHECK (
            (is_shipped IS TRUE AND ship_date IS NOT NULL)
            OR
            (is_shipped IS FALSE AND ship_date IS NULL)
        )
);

-- =========================
-- Indexes to support reporting queries
-- =========================

CREATE INDEX idx_production_records_line_date
    ON production_records(production_line_id, record_date);

CREATE INDEX idx_production_records_lot_date
    ON production_records(lot_id, record_date);

CREATE INDEX idx_inspection_records_date
    ON inspection_records(inspection_date);

CREATE INDEX idx_inspection_records_defect_date
    ON inspection_records(defect_type_id, inspection_date);

CREATE INDEX idx_inspection_records_lot_date
    ON inspection_records(lot_id, inspection_date);

CREATE INDEX idx_shipment_records_is_shipped
    ON shipment_records(is_shipped);

COMMIT;
