"""
src/service.py
Service Layer (Business Logic) for SteelWorks Operations Reporting

This module provides high-level reporting functions that answer operations questions:
- Production line quality analysis
- Defect trend identification
- Shipment tracking
- Lot-level drill-down

The service layer abstracts repository queries and implements business rules
to support the operations user story.

Time Complexity Notes:
    - Most aggregation queries: O(n) where n = total records in date range
    - With proper indexes: Effective O(log n) index lookup + O(m) result scan
    
Space Complexity: O(m) where m = result rows

Author: SteelWorks Operations Team
Date: 2024-02-16
"""

from typing import List, Dict, Tuple, Optional
from datetime import date, timedelta
from sqlalchemy.orm import Session
from src.repository import (
    ProductionRepository, InspectionRepository, 
    ShipmentRepository, LotRepository
)
from src.models import create_session


class OperationsReportingService:
    """
    Main service class for operations reporting operations.
    
    Implements the operations user story: 
    "As an operations team member, I want to review and summarize production,
    quality, and shipment information by lot ID and date, so that I can answer
    report questions about line issues, defect trends, and shipped batches
    without manually combining spreadsheets."
    
    Time Complexity: See individual methods
    Space Complexity: O(m) where m = result rows
    """
    
    def __init__(self, session: Optional[Session] = None):
        """
        Initialize the reporting service with repository layer.
        
        Args:
            session (Optional[Session]): Database session (creates new if None)
            
        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        self.session = session or create_session()
        self.production_repo = ProductionRepository(self.session)
        self.inspection_repo = InspectionRepository(self.session)
        self.shipment_repo = ShipmentRepository(self.session)
        self.lot_repo = LotRepository(self.session)
    
    # ===== AC 1: Identify which production lines had the most defects =====
    
    def get_lines_with_most_defects(
        self, start_date: date, end_date: date
    ) -> List[Tuple[str, int]]:
        """
        AC 1: Identify which production lines had the most defects within a date period.
        
        User Story: Operations team wants to know problem areas by production line.
        
        Args:
            start_date (date): Start of reporting period
            end_date (date): End of reporting period
            
        Returns:
            List[Tuple[str, int]]: [(line_code, total_defects), ...] 
                                   sorted by defects descending
        
        Time Complexity: O(n) where n = inspection records in date range
        Space Complexity: O(p) where p = number of production lines
        
        Coverage: AC 1
        """
        return self.inspection_repo.get_defect_count_by_line(start_date, end_date)
    
    # ===== AC 2: Defect trends over time =====
    
    def get_defect_trend_over_time(
        self, start_date: date, end_date: date
    ) -> List[Dict[str, any]]:
        """
        AC 2: Identify defect trends over time.
        
        Returns daily aggregation of defects to show trends/spikes.
        
        Args:
            start_date (date): Trend period start
            end_date (date): Trend period end
            
        Returns:
            List[Dict]: [{
                'date': date,
                'total_defects': int,
                'trend_indicator': str ('increasing', 'stable', 'decreasing')
            }, ...]
            
        Time Complexity: O(d) where d = days in date range
        Space Complexity: O(d)
        
        Coverage: AC 2
        """
        trend_data = self.inspection_repo.get_defect_trend(start_date, end_date)
        
        result = []
        prev_count = None
        
        for inspection_date, defect_count in trend_data:
            defect_count = defect_count or 0
            
            # Determine trend: up/down/stable vs previous day
            if prev_count is None:
                trend = 'baseline'
            elif defect_count > prev_count:
                trend = 'increasing'
            elif defect_count < prev_count:
                trend = 'decreasing'
            else:
                trend = 'stable'
            
            result.append({
                'date': inspection_date,
                'total_defects': int(defect_count),
                'trend_indicator': trend
            })
            
            prev_count = defect_count
        
        return result
    
    # ===== AC 3: Defect aggregation by defect type =====
    
    def get_defects_by_type(
        self, start_date: date, end_date: date
    ) -> List[Dict[str, any]]:
        """
        AC 3: Aggregate defect counts by type in a date period.
        
        Supports: "Which defect types appear most frequently?"
        
        Args:
            start_date (date): Period start
            end_date (date): Period end
            
        Returns:
            List[Dict]: [{
                'defect_code': str,
                'total_qty': int,
                'percentage': float (of total defects)
            }, ...] sorted by quantity descending
            
        Time Complexity: O(n) table scan + O(m log m) sorting
        Space Complexity: O(m) where m = distinct defect types
        
        Coverage: AC 3
        """
        defect_data = self.inspection_repo.get_defect_count_by_type(
            start_date, end_date
        )
        
        total = sum(qty for _, qty in defect_data)
        
        if total == 0:
            return []
        
        result = []
        for defect_code, qty in defect_data:
            result.append({
                'defect_code': defect_code,
                'total_qty': int(qty),
                'percentage': round((qty / total) * 100, 2)
            })
        
        return result
    
    # ===== AC 4: Lot shipment status and data comparison =====
    
    def get_shipped_lots_summary(self) -> List[Dict[str, any]]:
        """
        AC 4: Determine which lots have been shipped with summary data.
        
        Returns shipment status for all lots with defect counts.
        
        Returns:
            List[Dict]: [{
                'lot_code': str,
                'is_shipped': bool,
                'ship_date': Optional[date],
                'total_defects': int
            }, ...] sorted by lot_code
            
        Time Complexity: O(n) + O(m) where n = lots, m = inspections
        Space Complexity: O(n)
        
        Coverage: AC 4
        """
        lots = self.lot_repo.get_all_lots()
        result = []
        
        for lot in lots:
            lot_summary = self.lot_repo.get_lot_summary(lot.id)
            shipment = self.shipment_repo.get_shipment_status(lot.id)
            
            result.append({
                'lot_code': lot.lot_code,
                'is_shipped': shipment.is_shipped if shipment else False,
                'ship_date': shipment.ship_date if shipment else None,
                'total_defects': lot_summary.get('total_defects', 0)
            })
        
        return sorted(result, key=lambda x: x['lot_code'])
    
    # ===== AC 5: Lot drill-down comparison across departments =====
    
    def get_lot_report(self, lot_code: str) -> Optional[Dict[str, any]]:
        """
        AC 5: Cross-departmental lot data comparison.
        
        Pulls production, inspection, and shipment data for a single lot.
        Enables operations team to answer: "What's the full history of lot X?"
        
        Args:
            lot_code (str): Lot identifier (e.g., 'LOT-2024-01-001')
            
        Returns:
            Dict: {
                'lot_code': str,
                'production_info': [
                    {'line': str, 'date': date}, ...
                ],
                'quality_info': {
                    'total_defects': int,
                    'defects': [
                        {'defect_code': str, 'qty': int, 'date': date}, ...
                    ]
                },
                'shipment_info': {
                    'is_shipped': bool,
                    'ship_date': Optional[date],
                    'days_to_ship': Optional[int]
                }
            }
            or None if lot not found
            
        Time Complexity: O(log n) lookup + O(m) join operations
        Space Complexity: O(m)
        
        Coverage: AC 5
        """
        lot = self.lot_repo.get_lot_by_code(lot_code)
        
        if not lot:
            return None
        
        lot_summary = self.lot_repo.get_lot_summary(lot.id)
        
        if not lot_summary:
            return None
        
        # Build comprehensive report
        shipment = self.shipment_repo.get_shipment_status(lot.id)
        
        # Calculate days to ship if applicable
        days_to_ship = None
        if shipment and shipment.is_shipped and lot_summary['production_info']:
            first_prod_date = min(prod[1] for prod in lot_summary['production_info'])
            days_to_ship = (shipment.ship_date - first_prod_date).days
        
        return {
            'lot_code': lot_summary['lot_code'],
            'production_info': [
                {'line': line, 'date': dt} 
                for line, dt in lot_summary['production_info']
            ],
            'quality_info': {
                'total_defects': lot_summary['total_defects'],
                'defects': lot_summary['defects']
            },
            'shipment_info': {
                'is_shipped': shipment.is_shipped if shipment else False,
                'ship_date': shipment.ship_date if shipment else None,
                'days_to_ship': days_to_ship
            }
        }
    
    # ===== AC 6: Production aggregation by date =====
    
    def get_production_summary(
        self, start_date: date, end_date: date
    ) -> List[Dict[str, any]]:
        """
        AC 6: Aggregate production records by date and line.
        
        Shows production volume and line utilization over time.
        
        Args:
            start_date (date): Period start
            end_date (date): Period end
            
        Returns:
            List[Dict]: [{
                'date': date,
                'line_code': str,
                'lot_code': str
            }, ...] sorted by date, then line
            
        Time Complexity: O(p) where p = production records in range
        Space Complexity: O(p)
        
        Coverage: AC 6
        """
        records = self.production_repo.get_production_by_date_range(
            start_date, end_date
        )
        
        result = []
        for lot_code, line_code, record_date in records:
            result.append({
                'date': record_date,
                'line_code': line_code,
                'lot_code': lot_code
            })
        
        return sorted(result, key=lambda x: (x['date'], x['line_code']))
    
    # ===== Utility methods =====
    
    def get_pending_shipments(self) -> List[str]:
        """
        Get list of lots waiting to ship (not yet shipped).
        
        Returns:
            List[str]: Lot codes of lots with is_shipped=FALSE
            
        Time Complexity: O(log n) index + O(m)
        Space Complexity: O(m)
        """
        return self.shipment_repo.get_pending_shipments()
    
    def get_shipped_lots(self) -> List[Tuple[str, date]]:
        """
        Get all shipped lots with ship dates.
        
        Returns:
            List[Tuple]: [(lot_code, ship_date), ...] most recent first
            
        Time Complexity: O(log n) + O(m)
        Space Complexity: O(m)
        """
        return self.shipment_repo.get_shipped_lots()
    
    def close(self):
        """
        Close database session (cleanup).
        
        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        if self.session:
            self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit (cleanup)."""
        self.close()
