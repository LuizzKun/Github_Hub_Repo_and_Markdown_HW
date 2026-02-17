"""
src/__init__.py
Package initialization for SteelWorks Operations module.

Exports primary classes for easy imports:
    from src import models, repository, service
"""

from src.models import (
    Lot, ProductionLine, DefectType, ProductionRecord,
    InspectionRecord, ShipmentRecord, create_session
)
from src.repository import (
    ProductionRepository, InspectionRepository,
    ShipmentRepository, LotRepository
)
from src.service import OperationsReportingService

__version__ = '1.0.0'
__author__ = 'SteelWorks Operations Team'
__all__ = [
    'Lot', 'ProductionLine', 'DefectType', 'ProductionRecord',
    'InspectionRecord', 'ShipmentRecord', 'create_session',
    'ProductionRepository', 'InspectionRepository',
    'ShipmentRepository', 'LotRepository',
    'OperationsReportingService'
]
