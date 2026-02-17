"""
tests/test_models.py
Unit tests for SQLAlchemy ORM models

Tests:
    - Model instantiation
    - Relationships
    - Constraints

Coverage: All model classes and their key attributes

Author: SteelWorks Operations Team
Date: 2024-02-16
"""

import pytest
from src.models import (
    Lot, ProductionLine, DefectType, ProductionRecord,
    InspectionRecord, ShipmentRecord
)


class TestLotModel:
    """Test Lot entity model."""
    
    def test_lot_creation(self):
        """Test instantiating a Lot."""
        lot = Lot(lot_code='LOT-2024-01-001')
        
        assert lot.lot_code == 'LOT-2024-01-001'
        assert lot.production_records == []
        assert lot.inspection_records == []
        assert lot.shipment_record is None
    
    def test_lot_repr(self):
        """Test Lot string representation."""
        lot = Lot(id=1, lot_code='LOT-2024-01-001')
        
        assert "LOT-2024-01-001" in repr(lot)
        assert "Lot" in repr(lot)


class TestProductionLineModel:
    """Test ProductionLine entity model."""
    
    def test_production_line_creation(self):
        """Test instantiating a ProductionLine."""
        line = ProductionLine(line_code='LINE-A')
        
        assert line.line_code == 'LINE-A'
        assert line.production_records == []
    
    def test_production_line_repr(self):
        """Test ProductionLine string representation."""
        line = ProductionLine(id=1, line_code='LINE-A')
        
        assert "LINE-A" in repr(line)
        assert "ProductionLine" in repr(line)


class TestDefectTypeModel:
    """Test DefectType entity model."""
    
    def test_defect_type_creation(self):
        """Test instantiating a DefectType."""
        defect = DefectType(defect_code='SURFACE-SCRATCH')
        
        assert defect.defect_code == 'SURFACE-SCRATCH'
        assert defect.inspection_records == []
    
    def test_defect_type_repr(self):
        """Test DefectType string representation."""
        defect = DefectType(id=1, defect_code='SURFACE-SCRATCH')
        
        assert "SURFACE-SCRATCH" in repr(defect)
        assert "DefectType" in repr(defect)


class TestProductionRecord:
    """Test ProductionRecord entity model."""
    
    def test_production_record_creation(self):
        """Test instantiating a ProductionRecord."""
        from datetime import date
        
        record = ProductionRecord(
            lot_id=1,
            production_line_id=1,
            record_date=date(2024, 1, 1)
        )
        
        assert record.lot_id == 1
        assert record.production_line_id == 1
        assert record.record_date == date(2024, 1, 1)
    
    def test_production_record_repr(self):
        """Test ProductionRecord string representation."""
        from datetime import date
        
        record = ProductionRecord(
            id=1,
            lot_id=1,
            production_line_id=1,
            record_date=date(2024, 1, 1)
        )
        
        assert "ProductionRecord" in repr(record)
        assert "lot_id=1" in repr(record)


class TestInspectionRecord:
    """Test InspectionRecord entity model."""
    
    def test_inspection_record_creation(self):
        """Test instantiating an InspectionRecord."""
        from datetime import date
        
        record = InspectionRecord(
            lot_id=1,
            defect_type_id=1,
            inspection_date=date(2024, 1, 2),
            qty_defects=3
        )
        
        assert record.lot_id == 1
        assert record.defect_type_id == 1
        assert record.inspection_date == date(2024, 1, 2)
        assert record.qty_defects == 3
    
    def test_inspection_record_zero_defects(self):
        """Test InspectionRecord with zero defects (valid state)."""
        from datetime import date
        
        record = InspectionRecord(
            lot_id=1,
            defect_type_id=1,
            inspection_date=date(2024, 1, 2),
            qty_defects=0
        )
        
        assert record.qty_defects == 0
    
    def test_inspection_record_repr(self):
        """Test InspectionRecord string representation."""
        from datetime import date
        
        record = InspectionRecord(
            id=1,
            lot_id=1,
            defect_type_id=2,
            inspection_date=date(2024, 1, 2),
            qty_defects=3
        )
        
        assert "InspectionRecord" in repr(record)
        assert "qty=3" in repr(record)


class TestShipmentRecord:
    """Test ShipmentRecord entity model."""
    
    def test_shipment_record_shipped(self):
        """Test ShipmentRecord for shipped lot."""
        from datetime import date
        
        record = ShipmentRecord(
            lot_id=1,
            is_shipped=True,
            ship_date=date(2024, 1, 8)
        )
        
        assert record.lot_id == 1
        assert record.is_shipped is True
        assert record.ship_date == date(2024, 1, 8)
    
    def test_shipment_record_pending(self):
        """Test ShipmentRecord for not-yet-shipped lot."""
        record = ShipmentRecord(
            lot_id=2,
            is_shipped=False,
            ship_date=None
        )
        
        assert record.lot_id == 2
        assert record.is_shipped is False
        assert record.ship_date is None
    
    def test_shipment_record_repr(self):
        """Test ShipmentRecord string representation."""
        from datetime import date
        
        record = ShipmentRecord(
            id=1,
            lot_id=1,
            is_shipped=True,
            ship_date=date(2024, 1, 8)
        )
        
        assert "ShipmentRecord" in repr(record)
        assert "lot_id=1" in repr(record)


# Integration: Verify database schema constraints

class TestModelConstraints:
    """
    Test model constraint definitions.
    
    Note: These tests verify constraint definitions are present
    in models. Actual database constraint enforcement is tested
    at the integration level (with a live database).
    """
    
    def test_lot_unique_constraint(self):
        """Verify Lot.lot_code uniqueness is defined."""
        lot_columns = Lot.__table__.columns
        lot_code_col = lot_columns['lot_code']
        
        # Check unique constraint is set
        assert lot_code_col.unique is True
    
    def test_production_line_unique_constraint(self):
        """Verify ProductionLine.line_code uniqueness."""
        line_columns = ProductionLine.__table__.columns
        line_code_col = line_columns['line_code']
        
        assert line_code_col.unique is True
    
    def test_defect_type_unique_constraint(self):
        """Verify DefectType.defect_code uniqueness."""
        defect_columns = DefectType.__table__.columns
        defect_code_col = defect_columns['defect_code']
        
        assert defect_code_col.unique is True
    
    def test_shipment_record_lot_unique_constraint(self):
        """Verify ShipmentRecord.lot_id is unique (1:1 relationship)."""
        shipment_columns = ShipmentRecord.__table__.columns
        lot_id_col = shipment_columns['lot_id']
        
        assert lot_id_col.unique is True
    
    def test_foreign_keys_defined(self):
        """Verify foreign key relationships are defined."""
        # ProductionRecord → Lot
        prod_record_fks = [fk for fk in ProductionRecord.__table__.foreign_keys]
        assert len(prod_record_fks) > 0
        
        # InspectionRecord → Lot, DefectType
        insp_record_fks = [fk for fk in InspectionRecord.__table__.foreign_keys]
        assert len(insp_record_fks) > 0
        
        # ShipmentRecord → Lot
        shipment_fks = [fk for fk in ShipmentRecord.__table__.foreign_keys]
        assert len(shipment_fks) > 0
