"""
Setup Static Demo Database
Creates a SQLite database with sample data that always works.
"""

import sqlite3
from pathlib import Path


def create_static_demo_database():
    """Create a static demo database with sample data."""
    # Create demo directory
    project_root = Path(__file__).parent.parent.parent
    demo_dir = project_root / "demo"
    demo_dir.mkdir(exist_ok=True)
    
    db_path = demo_dir / "university_demo.db"
    
    # Remove existing database if it exists to start fresh
    if db_path.exists():
        db_path.unlink()
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Create tables
        cursor.executescript("""
        -- Department table
        CREATE TABLE IF NOT EXISTS Department (
            Dept_ID TEXT PRIMARY KEY,
            Dept_Name TEXT NOT NULL,
            Location TEXT
        );
        
        -- Student table
        CREATE TABLE IF NOT EXISTS Student (
            Student_ID TEXT PRIMARY KEY,
            Fname TEXT NOT NULL,
            Lname TEXT NOT NULL,
            City TEXT,
            Address TEXT,
            Birth_Date TEXT,
            Gender TEXT,
            Dept_ID TEXT,
            FOREIGN KEY (Dept_ID) REFERENCES Department(Dept_ID)
        );
        
        -- Instructor table
        CREATE TABLE IF NOT EXISTS Instructor (
            Instructor_ID TEXT PRIMARY KEY,
            Fname TEXT NOT NULL,
            Lname TEXT NOT NULL,
            Dept_ID TEXT,
            FOREIGN KEY (Dept_ID) REFERENCES Department(Dept_ID)
        );
        
        -- Course table
        CREATE TABLE IF NOT EXISTS Course (
            Course_ID TEXT PRIMARY KEY,
            Course_Name TEXT NOT NULL,
            Credits INTEGER,
            Dept_ID TEXT,
            Instructor_ID TEXT,
            Passing_Grade REAL DEFAULT 10.0,
            FOREIGN KEY (Dept_ID) REFERENCES Department(Dept_ID),
            FOREIGN KEY (Instructor_ID) REFERENCES Instructor(Instructor_ID)
        );
        
        -- Room table
        CREATE TABLE IF NOT EXISTS Room (
            Building TEXT,
            RoomNo TEXT,
            Capacity INTEGER,
            PRIMARY KEY (Building, RoomNo)
        );
        
        -- Reservation table
        CREATE TABLE IF NOT EXISTS Reservation (
            Reservation_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Building TEXT NOT NULL,
            RoomNo TEXT NOT NULL,
            Reserv_Date TEXT NOT NULL,
            Start_Time TEXT NOT NULL,
            End_Time TEXT NOT NULL,
            Course_ID TEXT,
            Department_ID TEXT,
            Instructor_ID TEXT,
            Hours_Number INTEGER,
            FOREIGN KEY (Building, RoomNo) REFERENCES Room(Building, RoomNo),
            FOREIGN KEY (Course_ID) REFERENCES Course(Course_ID),
            FOREIGN KEY (Department_ID) REFERENCES Department(Dept_ID),
            FOREIGN KEY (Instructor_ID) REFERENCES Instructor(Instructor_ID)
        );
        
        -- Enrollment table
        CREATE TABLE IF NOT EXISTS Enrollment (
            Student_ID TEXT,
            Course_ID TEXT,
            Enrollment_Date TEXT,
            PRIMARY KEY (Student_ID, Course_ID),
            FOREIGN KEY (Student_ID) REFERENCES Student(Student_ID),
            FOREIGN KEY (Course_ID) REFERENCES Course(Course_ID)
        );
        
        -- Marks table
        CREATE TABLE IF NOT EXISTS Marks (
            Mark_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Student_ID TEXT NOT NULL,
            Course_ID TEXT NOT NULL,
            Mark_Value REAL,
            Mark_Date TEXT,
            FOREIGN KEY (Student_ID) REFERENCES Student(Student_ID),
            FOREIGN KEY (Course_ID) REFERENCES Course(Course_ID)
        );
        
        -- Attendance table
        CREATE TABLE IF NOT EXISTS Attendance (
            Attendance_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Student_ID TEXT NOT NULL,
            Course_ID TEXT NOT NULL,
            Attendance_Date TEXT NOT NULL,
            Status TEXT,
            FOREIGN KEY (Student_ID) REFERENCES Student(Student_ID),
            FOREIGN KEY (Course_ID) REFERENCES Course(Course_ID)
        );
        
        -- Student_Audit_Log table
        CREATE TABLE IF NOT EXISTS Student_Audit_Log (
            Log_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Student_ID TEXT,
            Operation TEXT,
            Old_Value TEXT,
            New_Value TEXT,
            Change_Date TEXT,
            Changed_By TEXT
        );
        """)
        
        # Insert sample data
        cursor.executescript("""
        -- Departments
        INSERT INTO Department (Dept_ID, Dept_Name, Location) VALUES
        ('CS', 'Computer Science', 'Building A'),
        ('MATH', 'Mathematics', 'Building B'),
        ('PHYS', 'Physics', 'Building C'),
        ('ENG', 'Engineering', 'Building D');
        
        -- Students
        INSERT INTO Student (Student_ID, Fname, Lname, City, Address, Birth_Date, Gender, Dept_ID) VALUES
        ('S001', 'John', 'Doe', 'Algiers', '123 Main St', '2000-01-15', 'M', 'CS'),
        ('S002', 'Jane', 'Smith', 'Oran', '456 Oak Ave', '2001-03-20', 'F', 'CS'),
        ('S003', 'Ahmed', 'Ali', 'Constantine', '789 Pine Rd', '1999-11-10', 'M', 'MATH'),
        ('S004', 'Fatima', 'Hassan', 'Algiers', '321 Elm St', '2000-07-05', 'F', 'PHYS'),
        ('S005', 'Mohamed', 'Khalil', 'Oran', '654 Maple Dr', '2001-09-18', 'M', 'ENG');
        
        -- Instructors
        INSERT INTO Instructor (Instructor_ID, Fname, Lname, Dept_ID) VALUES
        ('I001', 'Dr. Sarah', 'Johnson', 'CS'),
        ('I002', 'Prof. Michael', 'Brown', 'MATH'),
        ('I003', 'Dr. Emily', 'Davis', 'PHYS'),
        ('I004', 'Prof. David', 'Wilson', 'ENG');
        
        -- Courses
        INSERT INTO Course (Course_ID, Course_Name, Credits, Dept_ID, Instructor_ID, Passing_Grade) VALUES
        ('C001', 'Introduction to Programming', 3, 'CS', 'I001', 10.0),
        ('C002', 'Data Structures', 4, 'CS', 'I001', 10.0),
        ('C003', 'Calculus I', 4, 'MATH', 'I002', 10.0),
        ('C004', 'Physics I', 3, 'PHYS', 'I003', 10.0),
        ('C005', 'Engineering Fundamentals', 3, 'ENG', 'I004', 10.0);
        
        -- Rooms
        INSERT INTO Room (Building, RoomNo, Capacity) VALUES
        ('A', '101', 30),
        ('A', '102', 25),
        ('A', '201', 40),
        ('B', '301', 35),
        ('B', '302', 30),
        ('C', '101', 50);
        
        -- Reservations
        INSERT INTO Reservation (Building, RoomNo, Reserv_Date, Start_Time, End_Time, Course_ID) VALUES
        ('A', '101', '2024-01-15', '09:00', '11:00', 'C001'),
        ('A', '102', '2024-01-15', '14:00', '16:00', 'C002'),
        ('B', '301', '2024-01-16', '10:00', '12:00', 'C003');
        
        -- Enrollments
        INSERT INTO Enrollment (Student_ID, Course_ID, Enrollment_Date) VALUES
        ('S001', 'C001', '2024-01-01'),
        ('S001', 'C002', '2024-01-01'),
        ('S002', 'C001', '2024-01-01'),
        ('S003', 'C003', '2024-01-01'),
        ('S004', 'C004', '2024-01-01'),
        ('S005', 'C005', '2024-01-01');
        
        -- Marks
        INSERT INTO Marks (Student_ID, Course_ID, Mark_Value, Mark_Date) VALUES
        ('S001', 'C001', 15.5, '2024-02-01'),
        ('S001', 'C002', 18.0, '2024-02-15'),
        ('S002', 'C001', 12.5, '2024-02-01'),
        ('S003', 'C003', 16.0, '2024-02-10'),
        ('S004', 'C004', 14.5, '2024-02-05');
        
        -- Attendance
        INSERT INTO Attendance (Student_ID, Course_ID, Attendance_Date, Status) VALUES
        ('S001', 'C001', '2024-01-10', 'Present'),
        ('S001', 'C001', '2024-01-17', 'Present'),
        ('S002', 'C001', '2024-01-10', 'Present'),
        ('S002', 'C001', '2024-01-17', 'Absent'),
        ('S003', 'C003', '2024-01-11', 'Present');
        """)
        
        # Create CheckReservation function for SQLite
        def check_reservation(building, roomno, reserv_date, start_time, end_time):
            """Check if a reservation conflicts with existing reservations."""
            cur = conn.cursor()
            query = """
                SELECT COUNT(*) FROM Reservation
                WHERE Building = ? AND RoomNo = ? AND Reserv_Date = ?
                  AND NOT (End_Time <= ? OR Start_Time >= ?)
            """
            cur.execute(query, (building, roomno, reserv_date, start_time, end_time))
            result = cur.fetchone()
            return result[0] if result else 0
        
        conn.create_function('CheckReservation', 5, check_reservation)
        
        conn.commit()
        print(f"✓ Static demo database created successfully at: {db_path}")
        return str(db_path)
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Error creating demo database: {e}")
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    create_static_demo_database()

