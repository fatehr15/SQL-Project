"""
Quick script to create university_db database if it doesn't exist.
Run this before starting the application.
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import sys

def create_database():
    """Create university_db database if it doesn't exist."""
    
    # Get connection parameters from environment or use defaults
    host = os.getenv('DB_HOST', 'localhost')
    port = int(os.getenv('DB_PORT', 5432))
    user = os.getenv('DB_USER', 'postgres')
    password = os.getenv('DB_PASSWORD', 'raidblack')
    
    print("=" * 50)
    print("Creating university_db Database")
    print("=" * 50)
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"User: {user}")
    print("")
    
    try:
        # Connect to PostgreSQL server (connect to 'postgres' database to create new database)
        print("Connecting to PostgreSQL server...")
        conn = psycopg2.connect(
            host=host,
            port=port,
            database='postgres',  # Connect to default database
            user=user,
            password=password if password else None
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        print("Checking if database exists...")
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'university_db'")
        exists = cursor.fetchone()
        
        if exists:
            print("✓ Database 'university_db' already exists.")
        else:
            # Create the database
            print("Creating database 'university_db'...")
            cursor.execute('CREATE DATABASE university_db')
            print("✓ Database 'university_db' created successfully!")
        
        cursor.close()
        conn.close()
        
        print("")
        print("=" * 50)
        print("Database Setup Complete!")
        print("=" * 50)
        print("")
        print("Next steps:")
        print("1. Run the lab scripts to create tables:")
        print("   - Run setup_database.ps1 (PowerShell)")
        print("   - OR run the SQL scripts manually from Part1/Lab folders")
        print("")
        print("2. Test connection: python test_connection.py")
        print("3. Run application: python App.py")
        print("")
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"✗ Error connecting to PostgreSQL: {e}")
        print("")
        print("Troubleshooting:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check your connection settings:")
        print(f"   - Host: {host}")
        print(f"   - Port: {port}")
        print(f"   - User: {user}")
        print("3. Verify your password is correct")
        print("4. You can set environment variables:")
        print("   $env:DB_PASSWORD = 'your_password'")
        return False
        
    except psycopg2.Error as e:
        print(f"✗ Database error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

if __name__ == '__main__':
    success = create_database()
    sys.exit(0 if success else 1)

