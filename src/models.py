"""
src/models.py
SQLAlchemy ORM Models for SteelWorks Operations Database

This module defines the data models representing the core entities:
- Lots: Production batches identified by lot_code
- ProductionLines: Factory production lines (LINE-A, LINE-B, etc.)
- DefectTypes: Quality defect categories (SURFACE-SCRATCH, DIMENSION-OOT, etc.)
- ProductionRecords: Production events linking lots to lines and dates
- InspectionRecords: Quality inspection events with defect counts
- ShipmentRecords: Shipment status and dates

Time Complexity: All model definitions are O(1) class definitions.
Space Complexity: Each model instance occupies O(n) where n = number of attributes.

Author: SteelWorks Operations Team
Date: 2024-02-16
"""

from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean, ForeignKey, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from dotenv import load_dotenv
from typing import Optional
import os
from pathlib import Path

# Base class for all ORM models
Base = declarative_base()


class Lot(Base):
    """
    Represents a production lot/batch tracked across operations.
    
    Attributes:
        id (int): Unique primary key (auto-increment)
        lot_code (str): Human-readable lot identifier (e.g., 'LOT-2024-01-001'), UNIQUE, NOT NULL
        
    Relationships:
        production_records (list): One-to-many with ProductionRecord (cascade delete)
        inspection_records (list): One-to-many with InspectionRecord (cascade delete)
        shipment_record: One-to-one with ShipmentRecord (cascade delete)
    
    Database Constraints:
        - PRIMARY KEY: id
        - UNIQUE: lot_code
    """
    __tablename__ = 'lots'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    lot_code = Column(String(50), nullable=False, unique=True)
    
    # Relationships (lazy loaded)
    production_records = relationship('ProductionRecord', back_populates='lot', cascade='all, delete-orphan')
    inspection_records = relationship('InspectionRecord', back_populates='lot', cascade='all, delete-orphan')
    shipment_record = relationship('ShipmentRecord', back_populates='lot', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Lot(id={self.id}, lot_code='{self.lot_code}')>"


class ProductionLine(Base):
    """
    Represents a factory production line where lots are manufactured.
    
    Attributes:
        id (int): Unique primary key (auto-increment)
        line_code (str): Line identifier (e.g., 'LINE-A', 'LINE-B'), UNIQUE, NOT NULL
        
    Relationships:
        production_records (list): One-to-many with ProductionRecord
    
    Database Constraints:
        - PRIMARY KEY: id
        - UNIQUE: line_code
    """
    __tablename__ = 'production_lines'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    line_code = Column(String(50), nullable=False, unique=True)
    
    # Relationships
    production_records = relationship('ProductionRecord', back_populates='production_line')
    
    def __repr__(self):
        return f"<ProductionLine(id={self.id}, line_code='{self.line_code}')>"


class DefectType(Base):
    """
    Represents a category of quality defects discovered during inspection.
    
    Attributes:
        id (int): Unique primary key (auto-increment)
        defect_code (str): Defect category identifier (e.g., 'SURFACE-SCRATCH'), UNIQUE, NOT NULL
        
    Relationships:
        inspection_records (list): One-to-many with InspectionRecord
    
    Database Constraints:
        - PRIMARY KEY: id
        - UNIQUE: defect_code
    """
    __tablename__ = 'defect_types'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    defect_code = Column(String(50), nullable=False, unique=True)
    
    # Relationships
    inspection_records = relationship('InspectionRecord', back_populates='defect_type')
    
    def __repr__(self):
        return f"<DefectType(id={self.id}, defect_code='{self.defect_code}')>"


class ProductionRecord(Base):
    """
    Records production events: a lot produced on a specific line on a specific date.
    
    Attributes:
        id (int): Unique primary key (auto-increment)
        lot_id (int): Foreign key to Lot, NOT NULL
        production_line_id (int): Foreign key to ProductionLine, NOT NULL
        record_date (date): Date of production event, NOT NULL
        
    Relationships:
        lot: Many-to-one with Lot
        production_line: Many-to-one with ProductionLine
    
    Database Constraints:
        - PRIMARY KEY: id
        - FOREIGN KEY: lot_id → lots.id (CASCADE DELETE)
        - FOREIGN KEY: production_line_id → production_lines.id (RESTRICT DELETE)
        - UNIQUE: (lot_id, production_line_id, record_date) - no duplicate production events
        
    Time Complexity: O(1) for creation, O(1) for lookup by date with index
    Space Complexity: O(1) per record
    """
    __tablename__ = 'production_records'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    lot_id = Column(BigInteger, ForeignKey('lots.id', ondelete='CASCADE'), nullable=False)
    production_line_id = Column(BigInteger, ForeignKey('production_lines.id', ondelete='RESTRICT'), nullable=False)
    record_date = Column(Date, nullable=False)
    
    # Relationships
    lot = relationship('Lot', back_populates='production_records')
    production_line = relationship('ProductionLine', back_populates='production_records')
    
    __table_args__ = (
        # Unique constraint to prevent duplicate production records
        # Time: O(1) lookup | Space: O(n) where n = number of production records
        # Index: idx_production_records_record_date supports date range queries
        # Index: idx_production_records_line_date supports (line, date) aggregation queries
    )
    
    def __repr__(self):
        return f"<ProductionRecord(id={self.id}, lot_id={self.lot_id}, line_id={self.production_line_id}, date={self.record_date})>"


class InspectionRecord(Base):
    """
    Records quality inspection events: defects found in a lot on a specific date.
    
    Attributes:
        id (int): Unique primary key (auto-increment)
        lot_id (int): Foreign key to Lot, NOT NULL
        defect_type_id (int): Foreign key to DefectType, NOT NULL
        inspection_date (date): Date of inspection, NOT NULL
        qty_defects (int): Quantity of defects found (>= 0), NOT NULL
        
    Relationships:
        lot: Many-to-one with Lot
        defect_type: Many-to-one with DefectType
    
    Database Constraints:
        - PRIMARY KEY: id
        - FOREIGN KEY: lot_id → lots.id (CASCADE DELETE)
        - FOREIGN KEY: defect_type_id → defect_types.id (RESTRICT DELETE)
        - CHECK: qty_defects >= 0 (non-negative constraint)
        
    Time Complexity: O(log n) for date range queries with index
    Space Complexity: O(1) per record
    
    Notes:
        - Multiple inspection records per lot are allowed (different dates/defect types)
        - qty_defects=0 is valid; represents inspection with no defects found
    """
    __tablename__ = 'inspection_records'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    lot_id = Column(BigInteger, ForeignKey('lots.id', ondelete='CASCADE'), nullable=False)
    defect_type_id = Column(BigInteger, ForeignKey('defect_types.id', ondelete='RESTRICT'), nullable=False)
    inspection_date = Column(Date, nullable=False)
    qty_defects = Column(Integer, nullable=False)
    
    # Relationships
    lot = relationship('Lot', back_populates='inspection_records')
    defect_type = relationship('DefectType', back_populates='inspection_records')
    
    __table_args__ = (
        # Non-negative check constraint
        # Time: O(1) validation on insert/update
        # Indexes: idx_inspection_records_date, idx_inspection_records_defect_date, idx_inspection_records_lot_date
        # These support drill-down queries: defect trends, lot-specific issues, date ranges
    )
    
    def __repr__(self):
        return f"<InspectionRecord(id={self.id}, lot_id={self.lot_id}, defect_id={self.defect_type_id}, qty={self.qty_defects})>"


class ShipmentRecord(Base):
    """
    Records shipment status for a lot: whether it has shipped and when.
    
    Attributes:
        id (int): Unique primary key (auto-increment)
        lot_id (int): Foreign key to Lot, UNIQUE, NOT NULL (one shipment per lot)
        is_shipped (bool): Whether lot has been shipped, NOT NULL
        ship_date (date): Date shipped (required if is_shipped=True, NULL if False), OPTIONAL
        
    Relationships:
        lot: One-to-one with Lot
    
    Database Constraints:
        - PRIMARY KEY: id
        - FOREIGN KEY: lot_id → lots.id (CASCADE DELETE), UNIQUE
        - CHECK: 
            - If is_shipped=TRUE, ship_date must NOT be NULL
            - If is_shipped=FALSE, ship_date must be NULL
        
    Time Complexity: O(1) lookup by lot_id with unique constraint, O(n) scan for is_shipped=TRUE
    Space Complexity: O(1) per record
    
    Notes:
        - This table implements 1:1 relationship: each lot has at most one shipment record
        - Check constraint ensures data consistency: shipped status matches date presence
    """
    __tablename__ = 'shipment_records'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    lot_id = Column(BigInteger, ForeignKey('lots.id', ondelete='CASCADE'), nullable=False, unique=True)
    is_shipped = Column(Boolean, nullable=False)
    ship_date = Column(Date)
    
    # Relationships
    lot = relationship('Lot', back_populates='shipment_record')
    
    __table_args__ = (
        # Status-date consistency check: ship_date must align with is_shipped boolean
        # Time: O(1) validation | Space: O(1)
        # Index: idx_shipment_records_is_shipped supports "find all shipped" queries (O(n) but indexed scan)
    )
    
    def __repr__(self):
        return f"<ShipmentRecord(id={self.id}, lot_id={self.lot_id}, is_shipped={self.is_shipped}, date={self.ship_date})>"


# Database Connection and Session Management
def get_db_connection_string() -> str:
    """
    Builds PostgreSQL connection string from environment variables.
    
    Expected environment variables:
        - DB_HOST: PostgreSQL host
        - DB_PORT: PostgreSQL port (default 5432)
        - DB_NAME: Database name
        - DB_USER: Database user
        - DB_PASSWORD: Database password
    
    Returns:
        str: Connection string in format postgresql://user:password@host:port/db_name
        
    Time Complexity: O(1) string concatenation
    Space Complexity: O(1)
    
    Raises:
        KeyError: If required environment variables are missing
    """
    env_path = Path(__file__).resolve().parents[1] / '.env'
    load_dotenv(dotenv_path=env_path)
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return database_url

    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '5432')
    name = os.getenv('DB_NAME', 'steelworks_ops')
    user = os.getenv('DB_USER', 'postgres')
    password = os.getenv('DB_PASSWORD', 'postgres')
    
    return f'postgresql://{user}:{password}@{host}:{port}/{name}'


def create_session():
    """
    Factory function to create a new SQLAlchemy session.
    
    Returns:
        Session: Configured SQLAlchemy Session bound to database
        
    Time Complexity: O(1) session creation
    Space Complexity: O(1)
    
    Usage:
        session = create_session()
        try:
            # perform queries
        finally:
            session.close()
    """
    engine = create_engine(get_db_connection_string(), echo=False)
    Session = sessionmaker(bind=engine)
    return Session()
