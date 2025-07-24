#!/usr/bin/env python3
"""
Database connection and table inspection script
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor

def check_database():
    # Database connection parameters
    DATABASE_URL = "postgresql://counseling_user:G3modmesi@counseling-support-dev-db.ctyimkqc67eb.ap-northeast-1.rds.amazonaws.com:5432/counseling_db"
    
    try:
        # Connect to database
        print("🔗 Connecting to database...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # List all tables
        print("\n📋 Tables in database:")
        cursor.execute("""
            SELECT table_name, table_type 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        for table in tables:
            print(f"  - {table['table_name']} ({table['table_type']})")
        
        # Check alembic version
        print("\n🔄 Migration status:")
        cursor.execute("SELECT version_num FROM alembic_version;")
        version = cursor.fetchone()
        if version:
            print(f"  Current migration: {version['version_num']}")
        
        # Check table record counts
        print("\n📊 Record counts:")
        for table in tables:
            if table['table_type'] == 'BASE TABLE' and table['table_name'] != 'alembic_version':
                cursor.execute(f"SELECT COUNT(*) as count FROM {table['table_name']};")
                count = cursor.fetchone()
                print(f"  {table['table_name']}: {count['count']} records")
        
        # Check counseling_sessions structure if exists
        print("\n🏗️ counseling_sessions structure:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'counseling_sessions' 
            ORDER BY ordinal_position;
        """)
        columns = cursor.fetchall()
        
        if columns:
            for col in columns:
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
                print(f"  {col['column_name']}: {col['data_type']} {nullable}{default}")
        else:
            print("  Table not found")
            
        cursor.close()
        conn.close()
        print("\n✅ Database check completed successfully!")
        
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")

if __name__ == "__main__":
    check_database()