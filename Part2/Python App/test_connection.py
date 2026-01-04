"""
Test Database Connection Script
Simple script to verify database connectivity before running the main application.
"""

import sys
from db_connection import get_db_connection


def test_connection():
    """Test database connection and basic queries."""
    print("=" * 60)
    print("Database Connection Test")
    print("=" * 60)
    
    try:
        # Get connection
        print("\n1. Connecting to database...")
        db = get_db_connection()
        db.connect()
        print(f"   ✓ Connected to: {db.database} on {db.host}:{db.port}")
        
        # Test basic query
        print("\n2. Testing basic query...")
        cursor = db.get_cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"   ✓ PostgreSQL version: {version.split(',')[0]}")
        
        # Check if key tables exist
        print("\n3. Checking required tables...")
        required_tables = [
            'Department', 'Student', 'Instructor', 'Course', 
            'Room', 'Reservation', 'Enrollment', 'Marks'
        ]
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        missing_tables = []
        for table in required_tables:
            if table in existing_tables:
                print(f"   ✓ Table '{table}' exists")
            else:
                print(f"   ✗ Table '{table}' NOT FOUND")
                missing_tables.append(table)
        
        # Check sample data
        print("\n4. Checking sample data...")
        if 'Student' in existing_tables:
            cursor.execute("SELECT COUNT(*) FROM Student")
            student_count = cursor.fetchone()[0]
            print(f"   ✓ Students in database: {student_count}")
        
        if 'Department' in existing_tables:
            cursor.execute("SELECT COUNT(*) FROM Department")
            dept_count = cursor.fetchone()[0]
            print(f"   ✓ Departments in database: {dept_count}")
        
        if 'Course' in existing_tables:
            cursor.execute("SELECT COUNT(*) FROM Course")
            course_count = cursor.fetchone()[0]
            print(f"   ✓ Courses in database: {course_count}")
        
        # Check functions
        print("\n5. Checking required functions...")
        required_functions = ['CheckReservation', 'get_instructor_schedule']
        cursor.execute("""
            SELECT routine_name 
            FROM information_schema.routines 
            WHERE routine_schema = 'public' 
            AND routine_type = 'FUNCTION'
        """)
        existing_functions = [row[0] for row in cursor.fetchall()]
        
        for func in required_functions:
            if func in existing_functions:
                print(f"   ✓ Function '{func}' exists")
            else:
                print(f"   ⚠ Function '{func}' not found (will be created automatically)")
        
        # Summary
        print("\n" + "=" * 60)
        if missing_tables:
            print("⚠ WARNING: Some required tables are missing!")
            print(f"   Missing: {', '.join(missing_tables)}")
            print("\n   Please run Part 1 lab scripts:")
            print("   psql -U postgres -d university_db -f \"Part1/Lab 1/Lab1.sql\"")
        else:
            print("✓ All basic tables exist!")
        
        print("\n" + "=" * 60)
        print("Connection test completed successfully!")
        print("You can now run the main application: python App.py")
        print("=" * 60)
        
        db.close()
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: Connection failed!")
        print(f"   {str(e)}")
        print("\n" + "=" * 60)
        print("Troubleshooting:")
        print("1. Verify PostgreSQL is running")
        print("2. Check database name in db_connection.py (should be 'university_db')")
        print("3. Verify credentials (user/password)")
        print("4. Ensure database exists: CREATE DATABASE university_db;")
        print("5. Run Part 1 lab scripts to create tables")
        print("=" * 60)
        return False


if __name__ == '__main__':
    success = test_connection()
    sys.exit(0 if success else 1)

