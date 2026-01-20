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
        # 1. Connect
        print("\n1. Connecting to database...")
        db = get_db_connection()
        db.connect()
        print(f"   ✓ Connected to: {db.database} on {db.host}:{db.port}")

        # 2. Basic query
        print("\n2. Testing basic query...")
        cursor = db.get_cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"   ✓ PostgreSQL version: {version.split(',')[0]}")

        # 3. Check tables
        print("\n3. Checking required tables...")
        required_tables = [
            "Department",
            "Student",
            "Instructor",
            "Course",
            "Room",
            "Reservation",
            "Enrollment",
            "Marks",
        ]

        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        existing_tables = [row[0] for row in cursor.fetchall()]

        missing_tables = []
        for table in required_tables:
            if table in existing_tables:
                print(f"   ✓ Table '{table}' exists")
            else:
                print(f"   ✗ Table '{table}' NOT FOUND")
                missing_tables.append(table)

        # 4. Sample data
        print("\n4. Checking sample data...")
        if "Student" in existing_tables:
            cursor.execute("SELECT COUNT(*) FROM Student;")
            print(f"   ✓ Students: {cursor.fetchone()[0]}")

        if "Department" in existing_tables:
            cursor.execute("SELECT COUNT(*) FROM Department;")
            print(f"   ✓ Departments: {cursor.fetchone()[0]}")

        if "Course" in existing_tables:
            cursor.execute("SELECT COUNT(*) FROM Course;")
            print(f"   ✓ Courses: {cursor.fetchone()[0]}")

        # 5. Functions
        print("\n5. Checking required functions...")
        required_functions = ["CheckReservation", "get_instructor_schedule"]

        cursor.execute("""
            SELECT routine_name
            FROM information_schema.routines
            WHERE routine_schema = 'public'
              AND routine_type = 'FUNCTION';
        """)
        existing_functions = [row[0] for row in cursor.fetchall()]

        for func in required_functions:
            if func in existing_functions:
                print(f"   ✓ Function '{func}' exists")
            else:
                print(f"   ⚠ Function '{func}' not found")

        # Summary
        print("\n" + "=" * 60)
        if missing_tables:
            print("⚠ WARNING: Some required tables are missing")
            print("   Missing:", ", ".join(missing_tables))
            print("\n   Run your Part 1 SQL scripts to create them.")
        else:
            print("✓ All required tables exist")

        print("=" * 60)
        print("Connection test completed successfully")
        print("=" * 60)

        db.close()
        return True

    except Exception as e:
        print("\n✗ ERROR: Connection failed")
        print(f"   {e}")
        print("=" * 60)
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
