-- db/schema.sql
-- SteelWorks Operations - Final Physical Data Design (PostgreSQL)

BEGIN;

-- Drop in dependency order for safe re-run
DROP TABLE IF EXISTS shipment_records;
DROP TABLE IF EXISTS inspection_records;
DROP TABLE IF EXISTS production_records;
DROP TABLE IF EXISTS defect_types;
DROP TABLE IF EXISTS production_lines;
DROP TABLE IF EXISTS lots;

-- ======================================================
-- Core Dimension Tables
-- ======================================================

CREATE TABLE lots (
    id BIGSERIAL PRIMARY KEY,
    lot_code VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE production_lines (
    id BIGSERIAL PRIMARY KEY,
    line_code VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE defect_types (
    id BIGSERIAL PRIMARY KEY,
    defect_code VARCHAR(50) NOT NULL UNIQUE
);

-- ======================================================
-- Production Records
-- ======================================================

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
        ON DELETE RESTRICT,

    CONSTRAINT uq_production_record_unique
        UNIQUE (lot_id, production_line_id, record_date)
);

-- ======================================================
-- Inspection Records
-- ======================================================

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

    CONSTRAINT ck_qty_defects_nonnegative
        CHECK (qty_defects >= 0)
);

-- ======================================================
-- Shipment Records
-- ======================================================

CREATE TABLE shipment_records (
    id BIGSERIAL PRIMARY KEY,
    lot_id BIGINT NOT NULL UNIQUE,
    is_shipped BOOLEAN NOT NULL,
    ship_date DATE,

    CONSTRAINT fk_shipment_records_lot
        FOREIGN KEY (lot_id)
        REFERENCES lots(id)
        ON DELETE CASCADE,

    CONSTRAINT ck_ship_date_matches_status
        CHECK (
            (is_shipped = TRUE AND ship_date IS NOT NULL)
            OR
            (is_shipped = FALSE AND ship_date IS NULL)
        )
);

-- ======================================================
-- Indexes (Support Reporting Queries)
-- ======================================================

CREATE INDEX idx_production_records_record_date
    ON production_records(record_date);

CREATE INDEX idx_production_records_line_date
    ON production_records(production_line_id, record_date);

CREATE INDEX idx_inspection_records_date
    ON inspection_records(inspection_date);

CREATE INDEX idx_inspection_records_defect_date
    ON inspection_records(defect_type_id, inspection_date);

-- NEW INDEX (lot drill-down support)
CREATE INDEX idx_inspection_records_lot_date
    ON inspection_records(lot_id, inspection_date);

CREATE INDEX idx_shipment_records_is_shipped
    ON shipment_records(is_shipped);

COMMIT;
