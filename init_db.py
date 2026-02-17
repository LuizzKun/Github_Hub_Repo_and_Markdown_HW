#!/usr/bin/env python3
"""
Initialize Render PostgreSQL database with schema and seed data.
"""

import psycopg2
from pathlib import Path

DATABASE_URL = "postgresql://steelworks_db_user:vhzzZhNTsKPofhqBpR8VwBPMPnuFmzES@dpg-d69ujds9c44c738hbfv0-a.ohio-postgres.render.com/steelworks_db?sslmode=require"

def run_sql_file(conn, filepath):
    """Execute SQL from a file."""
    with open(filepath, 'r') as f:
        sql = f.read()
    
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    print(f"✓ Executed {filepath}")

def main():
    try:
        print("Connecting to Render PostgreSQL...")
        conn = psycopg2.connect(DATABASE_URL)
        
        # Load schema
        schema_file = Path(__file__).parent / 'db' / 'schema.sql'
        print(f"Loading schema from {schema_file}...")
        run_sql_file(conn, schema_file)
        
        # Load seed data
        seed_file = Path(__file__).parent / 'db' / 'seed.sql'
        print(f"Loading seed data from {seed_file}...")
        run_sql_file(conn, seed_file)
        
        conn.close()
        print("\n✓ Database initialization complete!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        exit(1)

if __name__ == '__main__':
    main()
