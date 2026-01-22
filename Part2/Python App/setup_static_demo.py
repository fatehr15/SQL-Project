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
        -- Department table (matching PostgreSQL schema)
        CREATE TABLE IF NOT EXISTS Department (
            Department_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );
        
        -- Student table (matching PostgreSQL schema)
        CREATE TABLE IF NOT EXISTS Student (
            Student_ID INTEGER PRIMARY KEY,
            Last_Name TEXT NOT NULL,
            First_Name TEXT NOT NULL,
            DOB TEXT NOT NULL,
            Address TEXT,
            City TEXT,
            Zip_Code TEXT,
            Phone TEXT,
            Fax TEXT,
            Email TEXT,
            group_id INTEGER DEFAULT 1,
            section_id INTEGER DEFAULT 1
        );
        
        -- Instructor table (matching PostgreSQL schema)
        CREATE TABLE IF NOT EXISTS Instructor (
            Instructor_ID INTEGER PRIMARY KEY,
            Department_ID INTEGER NOT NULL,
            Last_Name TEXT NOT NULL,
            First_Name TEXT NOT NULL,
            Rank TEXT CHECK (Rank IN ('Substitute','MCB', 'MCA', 'PROF')),
            Phone TEXT,
            Fax TEXT,
            Email TEXT,
            FOREIGN KEY (Department_ID) REFERENCES Department(Department_id)
        );
        
        -- Course table (matching PostgreSQL schema)
        CREATE TABLE IF NOT EXISTS Course (
            Course_ID INTEGER NOT NULL,
            Department_ID INTEGER NOT NULL,
            name TEXT NOT NULL,
            Description TEXT,
            passing_grade REAL DEFAULT 10.0,
            PRIMARY KEY (Course_ID, Department_ID),
            FOREIGN KEY (Department_ID) REFERENCES Department(Department_id)
        );
        
        -- Room table
        CREATE TABLE IF NOT EXISTS Room (
            Building TEXT,
            RoomNo TEXT,
            Capacity INTEGER,
            PRIMARY KEY (Building, RoomNo)
        );
        
        -- Reservation table (matching PostgreSQL schema)
        CREATE TABLE IF NOT EXISTS Reservation (
            Reservation_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Building TEXT NOT NULL,
            RoomNo TEXT NOT NULL,
            Reserv_Date TEXT NOT NULL,
            Start_Time TEXT NOT NULL,
            End_Time TEXT NOT NULL,
            Course_ID INTEGER NOT NULL,
            Department_ID INTEGER NOT NULL,
            Instructor_ID INTEGER NOT NULL,
            Hours_Number INTEGER,
            FOREIGN KEY (Building, RoomNo) REFERENCES Room(Building, RoomNo),
            FOREIGN KEY (Course_ID, Department_ID) REFERENCES Course(Course_ID, Department_ID),
            FOREIGN KEY (Department_ID) REFERENCES Department(Department_id),
            FOREIGN KEY (Instructor_ID) REFERENCES Instructor(Instructor_ID)
        );
        
        -- Enrollment table (matching PostgreSQL schema)
        CREATE TABLE IF NOT EXISTS Enrollment (
            Student_ID INTEGER NOT NULL,
            Course_ID INTEGER NOT NULL,
            Department_ID INTEGER NOT NULL,
            Enrollment_Date TEXT,
            PRIMARY KEY (Student_ID, Course_ID, Department_ID),
            FOREIGN KEY (Student_ID) REFERENCES Student(Student_ID),
            FOREIGN KEY (Course_ID, Department_ID) REFERENCES Course(Course_ID, Department_ID)
        );
        
        -- Marks table (matching PostgreSQL schema)
        CREATE TABLE IF NOT EXISTS Marks (
            mark_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            dept_id INTEGER NOT NULL,
            mark REAL NOT NULL CHECK (mark >= 0 AND mark <= 20),
            mark_date TEXT NOT NULL DEFAULT (date('now')),
            FOREIGN KEY (student_id) REFERENCES Student(Student_ID),
            FOREIGN KEY (course_id, dept_id) REFERENCES Course(Course_ID, Department_ID)
        );
        
        -- Attendance table (matching PostgreSQL schema)
        CREATE TABLE IF NOT EXISTS Attendance (
            attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            dept_id INTEGER NOT NULL,
            attendance_date TEXT NOT NULL DEFAULT (date('now')),
            status TEXT NOT NULL CHECK (status IN ('Present', 'Absent', 'Late', 'Excused')),
            notes TEXT,
            FOREIGN KEY (student_id) REFERENCES Student(Student_ID),
            FOREIGN KEY (course_id, dept_id) REFERENCES Course(Course_ID, Department_ID)
        );
        
        """)
        
        # Insert sample data
        cursor.executescript("""
        -- Departments (matching PostgreSQL schema)
        INSERT INTO Department (Department_id, name) VALUES
        (1, 'Computer Science'),
        (2, 'Mathematics'),
        (3, 'Physics'),
        (4, 'Engineering');
        
        -- Students (matching PostgreSQL schema)
        INSERT INTO Student (Student_ID, Last_Name, First_Name, DOB, City, Address, group_id, section_id) VALUES
        (1, 'Doe', 'John', '2000-01-15', 'Algiers', '123 Main St', 1, 1),
        (2, 'Smith', 'Jane', '2001-03-20', 'Oran', '456 Oak Ave', 1, 1),
        (3, 'Ali', 'Ahmed', '1999-11-10', 'Constantine', '789 Pine Rd', 1, 2),
        (4, 'Hassan', 'Fatima', '2000-07-05', 'Algiers', '321 Elm St', 2, 1),
        (5, 'Khalil', 'Mohamed', '2001-09-18', 'Oran', '654 Maple Dr', 2, 2);
        
        -- Instructors (matching PostgreSQL schema)
        INSERT INTO Instructor (Instructor_ID, Department_ID, Last_Name, First_Name, Rank) VALUES
        (1, 1, 'Johnson', 'Sarah', 'PROF'),
        (2, 2, 'Brown', 'Michael', 'PROF'),
        (3, 3, 'Davis', 'Emily', 'MCA'),
        (4, 4, 'Wilson', 'David', 'PROF');
        
        -- Courses (matching PostgreSQL schema - composite key)
        INSERT INTO Course (Course_ID, Department_ID, name, Description, passing_grade) VALUES
        (1, 1, 'Introduction to Programming', 'Basic programming concepts', 10.0),
        (2, 1, 'Data Structures', 'Advanced data structures and algorithms', 10.0),
        (3, 2, 'Calculus I', 'Differential and integral calculus', 10.0),
        (4, 3, 'Physics I', 'Mechanics and thermodynamics', 10.0),
        (5, 4, 'Engineering Fundamentals', 'Basic engineering principles', 10.0);
        
        -- Rooms
        INSERT INTO Room (Building, RoomNo, Capacity) VALUES
        ('A', '101', 30),
        ('A', '102', 25),
        ('A', '201', 40),
        ('B', '301', 35),
        ('B', '302', 30),
        ('C', '101', 50);
        
        -- Reservations (matching PostgreSQL schema)
        INSERT INTO Reservation (Building, RoomNo, Reserv_Date, Start_Time, End_Time, Course_ID, Department_ID, Instructor_ID, Hours_Number) VALUES
        ('A', '101', '2024-01-15', '09:00:00', '11:00:00', 1, 1, 1, 2),
        ('A', '102', '2024-01-15', '14:00:00', '16:00:00', 2, 1, 1, 2),
        ('B', '301', '2024-01-16', '10:00:00', '12:00:00', 3, 2, 2, 2);
        
        -- Enrollments (matching PostgreSQL schema)
        INSERT INTO Enrollment (Student_ID, Course_ID, Department_ID, Enrollment_Date) VALUES
        (1, 1, 1, '2024-01-01'),
        (1, 2, 1, '2024-01-01'),
        (2, 1, 1, '2024-01-01'),
        (3, 3, 2, '2024-01-01'),
        (4, 4, 3, '2024-01-01'),
        (5, 5, 4, '2024-01-01');
        
        -- Marks (matching PostgreSQL schema)
        INSERT INTO Marks (student_id, course_id, dept_id, mark, mark_date) VALUES
        (1, 1, 1, 15.5, '2024-02-01'),
        (1, 2, 1, 18.0, '2024-02-15'),
        (2, 1, 1, 12.5, '2024-02-01'),
        (3, 3, 2, 16.0, '2024-02-10'),
        (4, 4, 3, 14.5, '2024-02-05');
        
        -- Attendance (matching PostgreSQL schema)
        INSERT INTO Attendance (student_id, course_id, dept_id, attendance_date, status) VALUES
        (1, 1, 1, '2024-01-10', 'Present'),
        (1, 1, 1, '2024-01-17', 'Present'),
        (2, 1, 1, '2024-01-10', 'Present'),
        (2, 1, 1, '2024-01-17', 'Absent'),
        (3, 3, 2, '2024-01-11', 'Present');
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
        print(f"Static demo database created successfully at: {db_path}")
        return str(db_path)
        
    except Exception as e:
        conn.rollback()
        print(f"Error creating demo database: {e}")
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    create_static_demo_database()

