"""
src/repository.py
Data Access Layer (Repository Pattern) for SteelWorks Operations Database

This module provides database query methods for reporting operations:
- Production line analysis
- Defect trend identification
- Shipment status tracking
- Lot-level reporting

All methods follow the repository pattern to abstract database queries and ensure
consistent transaction handling.

Time Complexity Notes:
    - Date range queries: O(log n) with indexes (idx_*_date)
    - Aggregation queries: O(n) table scans, optimized by indexes
    - Drill-down queries: O(log n) + O(m) where m = result rows

Space Complexity: O(m) where m = number of result rows

Author: SteelWorks Operations Team
Date: 2024-02-16
"""

from typing import List, Dict, Tuple, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from src.models import (
    Lot, ProductionRecord, InspectionRecord, DefectType, 
    ProductionLine, ShipmentRecord
)


class ProductionRepository:
    """
    Repository for production-related queries.
    
    Time Complexity: See individual methods
    Space Complexity: O(m) where m = result rows
    """
    
    def __init__(self, session: Session):
        """
        Initialize repository with database session.
        
        Args:
            session (Session): SQLAlchemy session for database access
            
        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        self.session = session
    
    def get_production_record_by_lot(self, lot_id: int) -> List[ProductionRecord]:
        """
        Retrieve all production records for a specific lot.
        
        Args:
            lot_id (int): Lot identifier
            
        Returns:
            List[ProductionRecord]: Production records for the lot
            
        Time Complexity: O(log n) with index + O(m) result rows
        Space Complexity: O(m) where m = records returned
        """
        return self.session.query(ProductionRecord).filter(
            ProductionRecord.lot_id == lot_id
        ).all()
    
    def get_production_by_date_range(
        self, start_date: date, end_date: date
    ) -> List[Tuple[str, str, date]]:
        """
        Get production records within a date range with lot and line codes.
        
        Args:
            start_date (date): Start date (inclusive)
            end_date (date): End date (inclusive)
            
        Returns:
            List[Tuple]: (lot_code, line_code, record_date) tuples
            
        Time Complexity: O(log n) index lookup + O(m) result scan
        Space Complexity: O(m)
        
        Query Strategy:
            - Uses idx_production_records_record_date index for range scan
            - Joins with lots and production_lines for human-readable codes
        """
        records = self.session.query(
            Lot.lot_code,
            ProductionLine.line_code,
            ProductionRecord.record_date
        ).join(Lot, ProductionRecord.lot_id == Lot.id).join(
            ProductionLine, ProductionRecord.production_line_id == ProductionLine.id
        ).filter(
            and_(
                ProductionRecord.record_date >= start_date,
                ProductionRecord.record_date <= end_date
            )
        ).order_by(ProductionRecord.record_date).all()
        
        return records


class InspectionRepository:
    """
    Repository for inspection/quality-related queries.
    
    Supports defect trend analysis, line-level quality metrics, and lot drill-down.
    
    Time Complexity: O(log n) index + O(m) scan
    Space Complexity: O(m)
    """
    
    def __init__(self, session: Session):
        """
        Initialize inspection repository.
        
        Args:
            session (Session): SQLAlchemy session
            
        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        self.session = session
    
    def get_inspection_records_by_lot(self, lot_id: int) -> List[InspectionRecord]:
        """
        Retrieve all inspection records for a specific lot.
        
        Args:
            lot_id (int): Lot identifier
            
        Returns:
            List[InspectionRecord]: All defect records for the lot
            
        Time Complexity: O(log n) with idx_inspection_records_lot_date + O(m)
        Space Complexity: O(m)
        """
        return self.session.query(InspectionRecord).filter(
            InspectionRecord.lot_id == lot_id
        ).order_by(InspectionRecord.inspection_date).all()
    
    def get_defect_count_by_type(
        self, start_date: date, end_date: date
    ) -> List[Tuple[str, int]]:
        """
        Aggregate defects by type within date range.
        
        Answer: "Which defect types are most common in a date period?"
        
        Args:
            start_date (date): Range start
            end_date (date): Range end
            
        Returns:
            List[Tuple]: (defect_code, total_qty) sorted by quantity descending
            
        Time Complexity: O(n) full scan with GROUP BY, O(m log m) sorting
        Space Complexity: O(m) where m = number of distinct defect types
        
        Optimization:
            - Uses GROUP BY with SUM aggregation
            - idx_inspection_records_defect_date index speeds date filter
        """
        results = self.session.query(
            DefectType.defect_code,
            func.sum(InspectionRecord.qty_defects).label('total_defects')
        ).join(
            DefectType, InspectionRecord.defect_type_id == DefectType.id
        ).filter(
            and_(
                InspectionRecord.inspection_date >= start_date,
                InspectionRecord.inspection_date <= end_date
            )
        ).group_by(DefectType.defect_code).order_by(
            func.sum(InspectionRecord.qty_defects).desc()
        ).all()
        
        return results
    
    def get_defect_count_by_line(
        self, start_date: date, end_date: date
    ) -> List[Tuple[str, int]]:
        """
        Aggregate defects by production line within date range.
        
        Answer: "Which production lines have the most defects in a period?"
        
        Args:
            start_date (date): Range start
            end_date (date): Range end
            
        Returns:
            List[Tuple]: (line_code, total_defects) sorted descending
            
        Time Complexity: O(n) with multi-table join + GROUP BY
        Space Complexity: O(m) where m = number of lines
        
        Optimization:
            - Joins inspect→lot→production records→lines
            - Uses idx_production_records_line_date for production range scan
            - Groups by line_code for aggregation
        """
        results = self.session.query(
            ProductionLine.line_code,
            func.sum(InspectionRecord.qty_defects).label('total_defects')
        ).join(
            ProductionRecord,
            ProductionRecord.production_line_id == ProductionLine.id
        ).join(
            InspectionRecord,
            InspectionRecord.lot_id == ProductionRecord.lot_id
        ).filter(
            and_(
                InspectionRecord.inspection_date >= start_date,
                InspectionRecord.inspection_date <= end_date
            )
        ).group_by(ProductionLine.line_code).order_by(
            func.sum(InspectionRecord.qty_defects).desc()
        ).all()
        
        return results
    
    def get_defect_trend(
        self, start_date: date, end_date: date
    ) -> List[Tuple[date, int]]:
        """
        Track defect counts over time (daily aggregation).
        
        Answer: "How do defect counts change day-by-day over a period?"
        
        Args:
            start_date (date): Range start
            end_date (date): Range end
            
        Returns:
            List[Tuple]: (inspection_date, total_defects) chronological order
            
        Time Complexity: O(n) table scan + GROUP BY on date
        Space Complexity: O(d) where d = number of inspection dates
        
        Optimization:
            - Uses idx_inspection_records_date index
            - GROUP BY date for daily aggregation
        """
        results = self.session.query(
            InspectionRecord.inspection_date,
            func.sum(InspectionRecord.qty_defects).label('daily_defects')
        ).filter(
            and_(
                InspectionRecord.inspection_date >= start_date,
                InspectionRecord.inspection_date <= end_date
            )
        ).group_by(InspectionRecord.inspection_date).order_by(
            InspectionRecord.inspection_date
        ).all()
        
        return results


class ShipmentRepository:
    """
    Repository for shipment-related queries.
    
    Time Complexity: O(log n) index + O(m) scan
    Space Complexity: O(m)
    """
    
    def __init__(self, session: Session):
        """
        Initialize shipment repository.
        
        Args:
            session (Session): SQLAlchemy session
            
        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        self.session = session
    
    def get_shipment_status(self, lot_id: int) -> Optional[ShipmentRecord]:
        """
        Retrieve shipment status for a specific lot.
        
        Args:
            lot_id (int): Lot identifier
            
        Returns:
            ShipmentRecord: Shipment info (None if no record exists)
            
        Time Complexity: O(1) unique constraint lookup
        Space Complexity: O(1)
        """
        return self.session.query(ShipmentRecord).filter(
            ShipmentRecord.lot_id == lot_id
        ).first()
    
    def get_shipped_lots(self) -> List[Tuple[str, date]]:
        """
        Get all lots that have been shipped with their dates.
        
        Answer: "Which lots have shipped and when?"
        
        Returns:
            List[Tuple]: (lot_code, ship_date) ordered by date descending
            
        Time Complexity: O(log n) with idx_shipment_records_is_shipped + O(m)
        Space Complexity: O(m)
        """
        results = self.session.query(
            Lot.lot_code,
            ShipmentRecord.ship_date
        ).join(ShipmentRecord, Lot.id == ShipmentRecord.lot_id).filter(
            ShipmentRecord.is_shipped == True
        ).order_by(ShipmentRecord.ship_date.desc()).all()
        
        return results
    
    def get_pending_shipments(self) -> List[str]:
        """
        Get list of lots not yet shipped (pending).
        
        Answer: "Which lots are waiting to be shipped?"
        
        Returns:
            List[str]: Lot codes of unshipped lots
            
        Time Complexity: O(log n) index scan + O(m)
        Space Complexity: O(m)
        """
        results = self.session.query(Lot.lot_code).join(
            ShipmentRecord, Lot.id == ShipmentRecord.lot_id
        ).filter(
            ShipmentRecord.is_shipped == False
        ).order_by(Lot.lot_code).all()
        
        return [row[0] for row in results]


class LotRepository:
    """
    Repository for lot-related queries and cross-functional lot analysis.
    
    Supports drill-down by lot: pulls production, inspection, and shipment data together.
    
    Time Complexity: O(log n) index + O(m) results
    Space Complexity: O(m)
    """
    
    def __init__(self, session: Session):
        """
        Initialize lot repository.
        
        Args:
            session (Session): SQLAlchemy session
            
        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        self.session = session
    
    def get_lot_by_code(self, lot_code: str) -> Optional[Lot]:
        """
        Retrieve lot by its code identifier.
        
        Args:
            lot_code (str): Lot code to look up
            
        Returns:
            Lot: Lot object (None if not found)
            
        Time Complexity: O(1) unique constraint
        Space Complexity: O(1)
        """
        return self.session.query(Lot).filter(
            Lot.lot_code == lot_code
        ).first()
    
    def get_lot_summary(self, lot_id: int) -> Dict:
        """
        Get comprehensive summary: production, inspection, and shipment data for a lot.
        
        Answer: "What's the full history of a lot from production to shipment?"
        
        Args:
            lot_id (int): Lot identifier
            
        Returns:
            Dict: {
                'lot_code': str,
                'production_info': [(line_code, date), ...],
                'defects': [{'defect_code': str, 'qty': int, 'date': date}, ...],
                'total_defects': int,
                'shipment_status': bool,
                'ship_date': Optional[date]
            }
            
        Time Complexity: O(log n) lookups + O(m) scanning related records
        Space Complexity: O(m) result dictionary
        """
        lot = self.session.query(Lot).filter(Lot.id == lot_id).first()
        if not lot:
            return {}
        
        # Production records for lot
        production = self.session.query(
            ProductionLine.line_code,
            ProductionRecord.record_date
        ).join(
            ProductionRecord, ProductionRecord.production_line_id == ProductionLine.id
        ).filter(ProductionRecord.lot_id == lot_id).all()
        
        # Inspection records (defects) for lot
        inspections = self.session.query(
            DefectType.defect_code,
            InspectionRecord.qty_defects,
            InspectionRecord.inspection_date
        ).join(
            InspectionRecord, InspectionRecord.defect_type_id == DefectType.id
        ).filter(InspectionRecord.lot_id == lot_id).all()
        
        total_defects = sum(rec[1] for rec in inspections)
        
        # Shipment status
        shipment = self.session.query(ShipmentRecord).filter(
            ShipmentRecord.lot_id == lot_id
        ).first()
        
        return {
            'lot_code': lot.lot_code,
            'production_info': [(p[0], p[1]) for p in production],
            'defects': [{'defect_code': i[0], 'qty': i[1], 'date': i[2]} for i in inspections],
            'total_defects': total_defects,
            'shipment_status': shipment.is_shipped if shipment else None,
            'ship_date': shipment.ship_date if shipment else None
        }
    
    def get_all_lots(self) -> List[Lot]:
        """
        Retrieve all lots in the system.
        
        Returns:
            List[Lot]: All lot objects
            
        Time Complexity: O(n) table scan
        Space Complexity: O(n)
        """
        return self.session.query(Lot).order_by(Lot.lot_code).all()
