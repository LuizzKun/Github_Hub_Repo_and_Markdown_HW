-- db/sample_queries.sql
-- SteelWorks Operations - Sample Queries (PostgreSQL)

-- ======================================================
-- 1) Which production lines had the most issues this week?
-- Interpretation: "issues" = total defects found in inspections
-- (joined to production line via production_records)
-- ======================================================

SELECT
    pl.line_code AS production_line,
    SUM(ir.qty_defects) AS total_defects
FROM production_records pr
JOIN production_lines pl ON pl.id = pr.production_line_id
JOIN inspection_records ir ON ir.lot_id = pr.lot_id
WHERE ir.inspection_date >= (CURRENT_DATE - INTERVAL '7 days')
GROUP BY pl.line_code
ORDER BY total_defects DESC;


-- ======================================================
-- 2) What defect types are trending (last 90 days, weekly buckets)?
-- ======================================================

SELECT
    dt.defect_code,
    DATE_TRUNC('week', ir.inspection_date)::date AS week_start,
    SUM(ir.qty_defects) AS defects_in_week
FROM inspection_records ir
JOIN defect_types dt ON dt.id = ir.defect_type_id
WHERE ir.inspection_date >= (CURRENT_DATE - INTERVAL '90 days')
GROUP BY dt.defect_code, week_start
ORDER BY week_start ASC, defects_in_week DESC;


-- ======================================================
-- 3) Has a problematic batch already shipped? (look up by lot_code)
-- ======================================================

SELECT
    l.lot_code,
    sr.is_shipped,
    sr.ship_date
FROM lots l
LEFT JOIN shipment_records sr ON sr.lot_id = l.id
WHERE l.lot_code = 'LOT-123';


-- ======================================================
-- 4) Compare production, quality, and shipping info for one lot
-- (one view to avoid reconciling spreadsheets)
-- ======================================================

SELECT
    l.lot_code,
    pr.record_date AS production_date,
    pl.line_code AS production_line,
    ir.inspection_date,
    dt.defect_code,
    ir.qty_defects,
    sr.is_shipped,
    sr.ship_date
FROM lots l
LEFT JOIN production_records pr ON pr.lot_id = l.id
LEFT JOIN production_lines pl ON pl.id = pr.production_line_id
LEFT JOIN inspection_records ir ON ir.lot_id = l.id
LEFT JOIN defect_types dt ON dt.id = ir.defect_type_id
LEFT JOIN shipment_records sr ON sr.lot_id = l.id
WHERE l.lot_code = 'LOT-123'
ORDER BY pr.record_date, ir.inspection_date;


-- ======================================================
-- 5) Defect totals by production line for a date range (report-style)
-- ======================================================

SELECT
    pl.line_code AS production_line,
    SUM(ir.qty_defects) AS total_defects
FROM production_records pr
JOIN production_lines pl ON pl.id = pr.production_line_id
JOIN inspection_records ir ON ir.lot_id = pr.lot_id
WHERE ir.inspection_date BETWEEN DATE '2026-01-01' AND DATE '2026-01-31'
GROUP BY pl.line_code
ORDER BY total_defects DESC;


-- ======================================================
-- 6) Top defect types for a date range (what is trending recently?)
-- ======================================================

SELECT
    dt.defect_code,
    SUM(ir.qty_defects) AS total_defects
FROM inspection_records ir
JOIN defect_types dt ON dt.id = ir.defect_type_id
WHERE ir.inspection_date BETWEEN DATE '2026-01-01' AND DATE '2026-01-31'
GROUP BY dt.defect_code
ORDER BY total_defects DESC;


-- ======================================================
-- 7) Lots with defects that have already shipped (risk check)
-- ======================================================

SELECT
    l.lot_code,
    SUM(ir.qty_defects) AS total_defects,
    sr.ship_date
FROM lots l
JOIN inspection_records ir ON ir.lot_id = l.id
JOIN shipment_records sr ON sr.lot_id = l.id
WHERE sr.is_shipped = TRUE
GROUP BY l.lot_code, sr.ship_date
HAVING SUM(ir.qty_defects) > 0
ORDER BY sr.ship_date DESC, total_defects DESC;
