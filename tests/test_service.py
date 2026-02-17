"""
tests/test_service.py
Unit tests for OperationsReportingService business logic

Tests cover:
    - AC 1: Production line quality analysis
    - AC 2: Defect trends
    - AC 3: Defect aggregation by type
    - AC 4: Shipment status
    - AC 5: Lot drill-down
    - AC 6: Production summary
    - Utility functions

Note: These tests use mocking to avoid database dependency.
Integration tests with a real database are in test_repository_integration.py

Author: SteelWorks Operations Team
Date: 2024-02-16
"""

import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch
from src.service import OperationsReportingService
from src.models import ShipmentRecord


class TestOperationsReportingService:
    """Test suite for OperationsReportingService."""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return MagicMock()
    
    @pytest.fixture
    def service(self, mock_session):
        """Create service instance with mocked session."""
        return OperationsReportingService(session=mock_session)
    
    # ===== AC 1: Lines with most defects =====
    
    def test_get_lines_with_most_defects(self, service):
        """
        AC 1: Test retrieving production lines with most defects.
        
        Coverage: AC 1 requirement
        """
        # Mock repository response
        mock_data = [
            ('LINE-A', 15),
            ('LINE-C', 8),
            ('LINE-B', 5)
        ]
        service.inspection_repo.get_defect_count_by_line = MagicMock(
            return_value=mock_data
        )
        
        start = date(2024, 1, 1)
        end = date(2024, 1, 31)
        
        result = service.get_lines_with_most_defects(start, end)
        
        assert len(result) == 3
        assert result[0] == ('LINE-A', 15)  # Most defects first
        assert result[1] == ('LINE-C', 8)
        service.inspection_repo.get_defect_count_by_line.assert_called_once_with(
            start, end
        )
    
    def test_get_lines_with_most_defects_empty(self, service):
        """AC 1: Test with no data available."""
        service.inspection_repo.get_defect_count_by_line = MagicMock(
            return_value=[]
        )
        
        result = service.get_lines_with_most_defects(
            date(2024, 1, 1), date(2024, 1, 31)
        )
        
        assert result == []
    
    # ===== AC 2: Defect trends =====
    
    def test_get_defect_trend_over_time(self, service):
        """
        AC 2: Test defect trend calculation.
        
        Coverage: AC 2 requirement - trend indicators
        """
        mock_data = [
            (date(2024, 1, 1), 5),
            (date(2024, 1, 2), 8),
            (date(2024, 1, 3), 6),
            (date(2024, 1, 4), 6)
        ]
        service.inspection_repo.get_defect_trend = MagicMock(
            return_value=mock_data
        )
        
        result = service.get_defect_trend_over_time(
            date(2024, 1, 1), date(2024, 1, 4)
        )
        
        assert len(result) == 4
        assert result[0]['total_defects'] == 5
        assert result[0]['trend_indicator'] == 'baseline'
        assert result[1]['trend_indicator'] == 'increasing'  # 5 → 8
        assert result[2]['trend_indicator'] == 'decreasing'   # 8 → 6
        assert result[3]['trend_indicator'] == 'stable'       # 6 → 6
    
    def test_get_defect_trend_empty(self, service):
        """AC 2: Test with no trend data."""
        service.inspection_repo.get_defect_trend = MagicMock(return_value=[])
        
        result = service.get_defect_trend_over_time(
            date(2024, 1, 1), date(2024, 1, 31)
        )
        
        assert result == []
    
    # ===== AC 3: Defects by type =====
    
    def test_get_defects_by_type(self, service):
        """
        AC 3: Test aggregating defects by type with percentages.
        
        Coverage: AC 3 requirement
        """
        mock_data = [
            ('SURFACE-SCRATCH', 10),
            ('DIMENSION-OOT', 5),
            ('MATERIAL-FLAW', 3)
        ]
        service.inspection_repo.get_defect_count_by_type = MagicMock(
            return_value=mock_data
        )
        
        result = service.get_defects_by_type(
            date(2024, 1, 1), date(2024, 1, 31)
        )
        
        assert len(result) == 3
        assert result[0]['defect_code'] == 'SURFACE-SCRATCH'
        assert result[0]['total_qty'] == 10
        assert result[0]['percentage'] == 55.56  # 10/(10+5+3) = 55.56%
        assert result[1]['percentage'] == 27.78
        assert result[2]['percentage'] == 16.67
    
    def test_get_defects_by_type_empty(self, service):
        """AC 3: Test with zero defects."""
        service.inspection_repo.get_defect_count_by_type = MagicMock(return_value=[])
        
        result = service.get_defects_by_type(
            date(2024, 1, 1), date(2024, 1, 31)
        )
        
        assert result == []
    
    # ===== AC 4: Shipment status =====
    
    def test_get_shipped_lots_summary(self, service):
        """
        AC 4: Test shipment status summary for all lots.
        
        Coverage: AC 4 requirement
        """
        mock_lots_summary = [
            {
                'lot_code': 'LOT-2024-01-001',
                'is_shipped': True,
                'ship_date': date(2024, 1, 8),
                'total_defects': 2
            },
            {
                'lot_code': 'LOT-2024-01-002',
                'is_shipped': False,
                'ship_date': None,
                'total_defects': 5
            }
        ]
        
        # Mock the lot repo methods
        lot1 = MagicMock()
        lot1.id = 1
        lot1.lot_code = 'LOT-2024-01-001'
        
        lot2 = MagicMock()
        lot2.id = 2
        lot2.lot_code = 'LOT-2024-01-002'
        
        service.lot_repo.get_all_lots = MagicMock(return_value=[lot1, lot2])
        
        service.lot_repo.get_lot_summary = MagicMock(
            side_effect=[
                {'lot_code': 'LOT-2024-01-001', 'total_defects': 2},
                {'lot_code': 'LOT-2024-01-002', 'total_defects': 5}
            ]
        )
        
        ship1 = MagicMock(is_shipped=True, ship_date=date(2024, 1, 8))
        ship2 = MagicMock(is_shipped=False, ship_date=None)
        
        service.shipment_repo.get_shipment_status = MagicMock(
            side_effect=[ship1, ship2]
        )
        
        result = service.get_shipped_lots_summary()
        
        assert len(result) == 2
        assert result[0]['is_shipped'] is True
        assert result[1]['is_shipped'] is False
    
    # ===== AC 5: Lot drill-down =====
    
    def test_get_lot_report(self, service):
        """
        AC 5: Test lot drill-down with complete history.
        
        Coverage: AC 5 requirement
        """
        lot_summary = {
            'lot_code': 'LOT-2024-01-001',
            'production_info': [('LINE-A', date(2024, 1, 1))],
            'defects': [
                {'defect_code': 'SURFACE-SCRATCH', 'qty': 2, 'date': date(2024, 1, 2)}
            ],
            'total_defects': 2
        }
        
        service.lot_repo.get_lot_by_code = MagicMock(return_value=MagicMock(id=1))
        service.lot_repo.get_lot_summary = MagicMock(return_value=lot_summary)
        
        shipment = MagicMock(
            is_shipped=True,
            ship_date=date(2024, 1, 8)
        )
        service.shipment_repo.get_shipment_status = MagicMock(return_value=shipment)
        
        result = service.get_lot_report('LOT-2024-01-001')
        
        assert result['lot_code'] == 'LOT-2024-01-001'
        assert result['production_info'][0]['line'] == 'LINE-A'
        assert result['quality_info']['total_defects'] == 2
        assert result['shipment_info']['is_shipped'] is True
        assert result['shipment_info']['days_to_ship'] == 7
    
    def test_get_lot_report_not_found(self, service):
        """AC 5: Test lot not found."""
        service.lot_repo.get_lot_by_code = MagicMock(return_value=None)
        
        result = service.get_lot_report('LOT-NONEXISTENT')
        
        assert result is None
    
    # ===== AC 6: Production summary =====
    
    def test_get_production_summary(self, service):
        """
        AC 6: Test production record aggregation.
        
        Coverage: AC 6 requirement
        """
        mock_data = [
            ('LOT-2024-01-001', 'LINE-A', date(2024, 1, 1)),
            ('LOT-2024-01-002', 'LINE-B', date(2024, 1, 2))
        ]
        service.production_repo.get_production_by_date_range = MagicMock(
            return_value=mock_data
        )
        
        result = service.get_production_summary(
            date(2024, 1, 1), date(2024, 1, 31)
        )
        
        assert len(result) == 2
        assert result[0]['lot_code'] == 'LOT-2024-01-001'
        assert result[0]['line_code'] == 'LINE-A'
    
    # ===== Utility methods =====
    
    def test_get_pending_shipments(self, service):
        """Test retrieving lots waiting to ship."""
        mock_data = ['LOT-2024-02-004', 'LOT-2024-02-005']
        service.shipment_repo.get_pending_shipments = MagicMock(return_value=mock_data)
        
        result = service.get_pending_shipments()
        
        assert len(result) == 2
        assert 'LOT-2024-02-004' in result
    
    def test_get_shipped_lots(self, service):
        """Test retrieving all shipped lots."""
        mock_data = [
            ('LOT-2024-01-001', date(2024, 1, 8)),
            ('LOT-2024-01-002', date(2024, 1, 9))
        ]
        service.shipment_repo.get_shipped_lots = MagicMock(return_value=mock_data)
        
        result = service.get_shipped_lots()
        
        assert len(result) == 2
        assert result[0] == ('LOT-2024-01-001', date(2024, 1, 8))
    
    # ===== Context manager =====
    
    def test_context_manager(self, mock_session):
        """Test service as context manager."""
        with OperationsReportingService(session=mock_session) as svc:
            assert svc is not None
        
        # Session should be closed on exit
        mock_session.close.assert_called_once()
