-- db/seed.sql
-- SteelWorks Operations - Sample Data Seed Script
-- This script populates the database with realistic sample data from operations Excel files
-- Execution: psql -h <host> -U <user> -d <database> -f seed.sql

BEGIN;

-- ======================================================
-- Clear existing data (optional - comment out if not needed)
-- ======================================================
-- TRUNCATE TABLE shipment_records CASCADE;
-- TRUNCATE TABLE inspection_records CASCADE;
-- TRUNCATE TABLE production_records CASCADE;
-- TRUNCATE TABLE defect_types CASCADE;
-- TRUNCATE TABLE production_lines CASCADE;
-- TRUNCATE TABLE lots CASCADE;

-- ======================================================
-- SEED: Lots (from Ops_Production_Log and Ops_Shipping_Log)
-- ======================================================
INSERT INTO lots (lot_code) VALUES
('LOT-2024-01-001'),
('LOT-2024-01-002'),
('LOT-2024-01-003'),
('LOT-2024-01-004'),
('LOT-2024-01-005'),
('LOT-2024-01-006'),
('LOT-2024-01-007'),
('LOT-2024-01-008'),
('LOT-2024-01-009'),
('LOT-2024-01-010'),
('LOT-2024-02-001'),
('LOT-2024-02-002'),
('LOT-2024-02-003'),
('LOT-2024-02-004'),
('LOT-2024-02-005')
ON CONFLICT (lot_code) DO NOTHING;

-- ======================================================
-- SEED: Production Lines (from operations logs)
-- ======================================================
INSERT INTO production_lines (line_code) VALUES
('LINE-A'),
('LINE-B'),
('LINE-C'),
('LINE-D'),
('LINE-E')
ON CONFLICT (line_code) DO NOTHING;

-- ======================================================
-- SEED: Defect Types (from QE_Inspector daily/weekly logs)
-- ======================================================
INSERT INTO defect_types (defect_code) VALUES
('SURFACE-SCRATCH'),
('DIMENSION-OOT'),
('MATERIAL-FLAW'),
('WELDING-DEFECT'),
('SEAL-FAILURE'),
('CORROSION-SPOT'),
('PAINT-CHIP'),
('ASSEMBLY-MISALIGN')
ON CONFLICT (defect_code) DO NOTHING;

-- ======================================================
-- SEED: Production Records (from Ops_Production_Log)
-- Time Period: January - February 2024
-- ======================================================
INSERT INTO production_records (lot_id, production_line_id, record_date) VALUES
-- January 2024 Production
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-01-001'), (SELECT id FROM production_lines WHERE line_code = 'LINE-A'), '2024-01-01'),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-01-002'), (SELECT id FROM production_lines WHERE line_code = 'LINE-B'), '2024-01-01'),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-01-003'), (SELECT id FROM production_lines WHERE line_code = 'LINE-C'), '2024-01-02'),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-01-004'), (SELECT id FROM production_lines WHERE line_code = 'LINE-D'), '2024-01-02'),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-01-005'), (SELECT id FROM production_lines WHERE line_code = 'LINE-E'), '2024-01-03'),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-01-006'), (SELECT id FROM production_lines WHERE line_code = 'LINE-A'), '2024-01-04'),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-01-007'), (SELECT id FROM production_lines WHERE line_code = 'LINE-B'), '2024-01-05'),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-01-008'), (SELECT id FROM production_lines WHERE line_code = 'LINE-C'), '2024-01-08'),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-01-009'), (SELECT id FROM production_lines WHERE line_code = 'LINE-D'), '2024-01-09'),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-01-010'), (SELECT id FROM production_lines WHERE line_code = 'LINE-E'), '2024-01-10'),
-- February 2024 Production
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-02-001'), (SELECT id FROM production_lines WHERE line_code = 'LINE-A'), '2024-02-01'),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-02-002'), (SELECT id FROM production_lines WHERE line_code = 'LINE-B'), '2024-02-02'),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-02-003'), (SELECT id FROM production_lines WHERE line_code = 'LINE-C'), '2024-02-03'),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-02-004'), (SELECT id FROM production_lines WHERE line_code = 'LINE-D'), '2024-02-05'),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-02-005'), (SELECT id FROM production_lines WHERE line_code = 'LINE-E'), '2024-02-06')
ON CONFLICT (lot_id, production_line_id, record_date) DO NOTHING;

-- ======================================================
-- SEED: Inspection Records (from QE Inspector daily/weekly logs)
-- Inspector A: Daily logs, Inspector B: Weekly logs
-- ======================================================
INSERT INTO inspection_records (lot_id, defect_type_id, inspection_date, qty_defects) VALUES
-- January Inspections (Inspector A - Daily Log)
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-01-001'), (SELECT id FROM defect_types WHERE defect_code = 'SURFACE-SCRATCH'), '2024-01-02', 2),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-01-001'), (SELECT id FROM defect_types WHERE defect_code = 'DIMENSION-OOT'), '2024-01-02', 0),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-01-002'), (SELECT id FROM defect_types WHERE defect_code = 'WELDING-DEFECT'), '2024-01-03', 1),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-01-003'), (SELECT id FROM defect_types WHERE defect_code = 'SURFACE-SCRATCH'), '2024-01-04', 3),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-01-003'), (SELECT id FROM defect_types WHERE defect_code = 'MATERIAL-FLAW'), '2024-01-04', 1),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-01-004'), (SELECT id FROM defect_types WHERE defect_code = 'PAINT-CHIP'), '2024-01-05', 4),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-01-005'), (SELECT id FROM defect_types WHERE defect_code = 'SEAL-FAILURE'), '2024-01-06', 2),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-01-006'), (SELECT id FROM defect_types WHERE defect_code = 'DIMENSION-OOT'), '2024-01-07', 5),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-01-007'), (SELECT id FROM defect_types WHERE defect_code = 'CORROSION-SPOT'), '2024-01-10', 1),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-01-008'), (SELECT id FROM defect_types WHERE defect_code = 'ASSEMBLY-MISALIGN'), '2024-01-11', 2),
-- January Inspections (Inspector B - Weekly Log)
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-01-009'), (SELECT id FROM defect_types WHERE defect_code = 'SURFACE-SCRATCH'), '2024-01-12', 0),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-01-010'), (SELECT id FROM defect_types WHERE defect_code = 'WELDING-DEFECT'), '2024-01-12', 3),
-- February Inspections
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-02-001'), (SELECT id FROM defect_types WHERE defect_code = 'MATERIAL-FLAW'), '2024-02-02', 2),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-02-002'), (SELECT id FROM defect_types WHERE defect_code = 'PAINT-CHIP'), '2024-02-03', 1),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-02-003'), (SELECT id FROM defect_types WHERE defect_code = 'DIMENSION-OOT'), '2024-02-04', 4),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-02-003'), (SELECT id FROM defect_types WHERE defect_code = 'SURFACE-SCRATCH'), '2024-02-04', 2),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-02-004'), (SELECT id FROM defect_types WHERE defect_code = 'SEAL-FAILURE'), '2024-02-07', 1),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-02-005'), (SELECT id FROM defect_types WHERE defect_code = 'CORROSION-SPOT'), '2024-02-08', 3)
ON CONFLICT DO NOTHING;

-- ======================================================
-- SEED: Shipment Records (from Ops_Shipping_Log)
-- ======================================================
INSERT INTO shipment_records (lot_id, is_shipped, ship_date) VALUES
-- Shipped Lots
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-01-001'), TRUE, '2024-01-08'),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-01-002'), TRUE, '2024-01-09'),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-01-003'), TRUE, '2024-01-10'),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-01-004'), TRUE, '2024-01-15'),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-01-005'), TRUE, '2024-01-16'),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-01-006'), TRUE, '2024-01-17'),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-01-007'), TRUE, '2024-01-22'),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-01-008'), TRUE, '2024-01-23'),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-01-009'), TRUE, '2024-01-25'),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-01-010'), TRUE, '2024-01-29'),
-- Shipped Lots (February)
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-02-001'), TRUE, '2024-02-08'),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-02-002'), TRUE, '2024-02-10'),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-02-003'), TRUE, '2024-02-15'),
-- Not Yet Shipped Lots
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-02-004'), FALSE, NULL),
((SELECT id FROM lots WHERE lot_code = 'LOT-2024-02-005'), FALSE, NULL)
ON CONFLICT (lot_id) DO NOTHING;

COMMIT;
