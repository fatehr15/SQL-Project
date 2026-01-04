"""
Setup Demo Database
Creates a SQLite database with sample data for testing/demo purposes.
"""

import sqlite3
from pathlib import Path
from db_connection_demo import get_demo_db_connection


def create_demo_database():
    """Create demo database with schema and sample data."""
    print("=" * 60)
    print("Setting up Demo Database (SQLite)")
    print("=" * 60)
    
    db = get_demo_db_connection()
    db.connect()
    cursor = db.get_cursor()
    
    try:
        print("\n1. Creating tables...")
        
        # Department table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Department(
                Department_id INTEGER PRIMARY KEY,
                name VARCHAR(25) NOT NULL UNIQUE
            )
        """)
        
        # Student table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Student(
                Student_ID INTEGER PRIMARY KEY,
                Last_Name VARCHAR(25) NOT NULL,
                First_Name VARCHAR(25) NOT NULL,
                DOB DATE NOT NULL,
                Address VARCHAR(50),
                City VARCHAR(25),
                Zip_Code VARCHAR(9),
                Phone VARCHAR(10),
                Fax VARCHAR(10),
                Email VARCHAR(100),
                group_id INTEGER DEFAULT 1,
                section_id INTEGER DEFAULT 1
            )
        """)
        
        # Instructor table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Instructor(
                Instructor_ID INTEGER PRIMARY KEY,
                Department_ID INTEGER NOT NULL,
                Last_Name VARCHAR(25) NOT NULL,
                First_Name VARCHAR(25) NOT NULL,
                Rank VARCHAR(25),
                Phone VARCHAR(10),
                Fax VARCHAR(10),
                Email VARCHAR(100),
                FOREIGN KEY (Department_ID) REFERENCES Department(Department_id)
            )
        """)
        
        # Course table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Course(
                Course_ID INTEGER NOT NULL,
                Department_ID INTEGER NOT NULL,
                name VARCHAR(60) NOT NULL,
                Description VARCHAR(1000),
                passing_grade NUMERIC(4,2) DEFAULT 10.0,
                PRIMARY KEY (Course_ID, Department_ID),
                FOREIGN KEY (Department_ID) REFERENCES Department(Department_id)
            )
        """)
        
        # Room table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Room(
                Building VARCHAR(1),
                RoomNo VARCHAR(10),
                Capacity INTEGER CHECK (Capacity > 1),
                PRIMARY KEY (Building, RoomNo)
            )
        """)
        
        # Reservation table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Reservation(
                Reservation_ID INTEGER PRIMARY KEY,
                Building VARCHAR(1) NOT NULL,
                RoomNo VARCHAR(10) NOT NULL,
                Course_ID INTEGER NOT NULL,
                Department_ID INTEGER NOT NULL,
                Instructor_ID INTEGER NOT NULL,
                Reserv_Date DATE NOT NULL DEFAULT (date('now')),
                Start_Time TIME NOT NULL DEFAULT (time('now')),
                End_Time TIME NOT NULL DEFAULT '23:00:00',
                Hours_Number INTEGER NOT NULL,
                FOREIGN KEY (Building, RoomNo) REFERENCES Room(Building, RoomNo),
                FOREIGN KEY (Course_ID, Department_ID) REFERENCES Course(Course_ID, Department_ID),
                FOREIGN KEY (Instructor_ID) REFERENCES Instructor(Instructor_ID)
            )
        """)
        
        # Enrollment table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Enrollment(
                Student_ID INTEGER,
                Course_ID INTEGER,
                Dept_ID INTEGER,
                Enroll_Date DATE DEFAULT (date('now')),
                PRIMARY KEY (Student_ID, Course_ID, Dept_ID),
                FOREIGN KEY (Student_ID) REFERENCES Student(Student_ID),
                FOREIGN KEY (Course_ID, Dept_ID) REFERENCES Course(Course_ID, Department_ID)
            )
        """)
        
        # Marks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Marks(
                mark_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                dept_id INTEGER NOT NULL,
                mark NUMERIC NOT NULL CHECK (mark BETWEEN 0 AND 20),
                mark_date DATE NOT NULL DEFAULT (date('now')),
                FOREIGN KEY(student_id) REFERENCES Student(student_id),
                FOREIGN KEY(course_id, dept_id) REFERENCES Course(course_id, Department_ID)
            )
        """)
        
        # Attendance table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Attendance(
                attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                dept_id INTEGER NOT NULL,
                attendance_date DATE NOT NULL DEFAULT (date('now')),
                status VARCHAR(20) NOT NULL CHECK (status IN ('Present', 'Absent', 'Late', 'Excused')),
                notes TEXT,
                FOREIGN KEY(student_id) REFERENCES Student(student_id),
                FOREIGN KEY(course_id, dept_id) REFERENCES Course(course_id, Department_ID)
            )
        """)
        
        # Audit tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Marks_Audit_Log(
                LogID INTEGER PRIMARY KEY AUTOINCREMENT,
                OperationType VARCHAR(50) NOT NULL,
                OperationTime TIMESTAMP NOT NULL DEFAULT (datetime('now')),
                Description TEXT,
                RowsAffected INTEGER DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Attendance_Audit_Log(
                LogID INTEGER PRIMARY KEY AUTOINCREMENT,
                OperationType VARCHAR(50) NOT NULL,
                OperationTime TIMESTAMP NOT NULL DEFAULT (datetime('now')),
                Description TEXT,
                RowsAffected INTEGER DEFAULT 0
            )
        """)
        
        db.connection.commit()
        print("   [OK] Tables created successfully!")
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM Department")
        if cursor.fetchone()[0] > 0:
            print("\n2. Sample data already exists. Skipping data insertion.")
            print("   (Delete demo/university_demo.db to recreate)")
        else:
            print("\n2. Inserting sample data...")
            
            # Insert departments
            departments = [
                (1, 'SADS'),
                (2, 'CCS'),
                (3, 'GRC'),
                (4, 'INS')
            ]
            cursor.executemany("INSERT INTO Department VALUES (?, ?)", departments)
            
            # Insert students
            students = [
                (1, 'Ali', 'Ben Ali', '1979-02-18', '50, 1st street', 'Algiers', '16000', '0143567890', None, 'A1@yahoo.fr', 1, 1),
                (2, 'Amar', 'Ben Ammar', '1980-08-23', '10, Avenue b', 'BATNA', '05000', '0678567801', None, 'pt@yahoo.fr', 1, 1),
                (3, 'Ameur', 'Ben Ameur', '1978-05-12', '25, 2nd street', 'Oran', '31000', '0145678956', '0145678956', 'o@yahoo.fr', 1, 2),
                (4, 'Aissa', 'Ben Aissa', '1979-07-15', '56, Road', 'Annaba', '23000', '0678905645', None, 'd@hotmail.com', 2, 1),
                (5, 'Fatima', 'Ben Abdedallah', '1979-08-15', '45, Faubourg', 'Constantine', '25000', None, None, None, 2, 2)
            ]
            cursor.executemany("""
                INSERT INTO Student VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, students)
            
            # Insert instructors
            instructors = [
                (1, 1, 'Abbas', 'BenAbbes', 'MCA', '4185', '4091', 'Ab@yahoo.fr'),
                (2, 1, 'Mokhtar', 'BenMokhtar', 'Substitute', None, None, None),
                (3, 1, 'Djemaa', 'Ben Mohamed', 'MCB', None, None, None),
                (4, 1, 'Lahlou', 'Mohamed', 'PROF', None, None, None),
                (5, 1, 'Abla', 'Chad', 'MCA', None, None, 'ab@lgmail.com')
            ]
            cursor.executemany("""
                INSERT INTO Instructor VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, instructors)
            
            # Insert courses
            courses = [
                (1, 1, 'Databases', 'Licence(L3) : Modeling E/A and UML, Relational Model, SQL', 10.0),
                (2, 1, 'C++ progr.', 'Level Master 1', 10.0),
                (3, 1, 'Advanced DBs', 'Level Master 2', 10.0),
                (4, 4, 'English', '', 10.0)
            ]
            cursor.executemany("""
                INSERT INTO Course VALUES (?, ?, ?, ?, ?)
            """, courses)
            
            # Insert rooms
            rooms = [
                ('B', '020', 15),
                ('B', '022', 15),
                ('A', '301', 45),
                ('C', 'Hall 1', 500),
                ('C', 'Hall 2', 200)
            ]
            cursor.executemany("INSERT INTO Room VALUES (?, ?, ?)", rooms)
            
            # Insert enrollments
            enrollments = [
                (1, 1, 1, '2024-01-01'),
                (2, 1, 1, '2024-01-01'),
                (3, 1, 1, '2024-01-01'),
                (1, 2, 1, '2024-01-01')
            ]
            cursor.executemany("INSERT INTO Enrollment VALUES (?, ?, ?, ?)", enrollments)
            
            # Insert sample marks
            marks = [
                (1, 1, 1, 15.5, '2024-01-15'),
                (2, 1, 1, 12.0, '2024-01-15'),
                (3, 1, 1, 18.0, '2024-01-15'),
                (1, 2, 1, 14.5, '2024-01-20')
            ]
            cursor.executemany("""
                INSERT INTO Marks (student_id, course_id, dept_id, mark, mark_date) 
                VALUES (?, ?, ?, ?, ?)
            """, marks)
            
            db.connection.commit()
            print("   [OK] Sample data inserted successfully!")
        
        print("\n" + "=" * 60)
        print("Demo database setup complete!")
        print(f"Database location: {db.db_path}")
        print("=" * 60)
        
        db.close()
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error setting up demo database: {e}")
        db.close()
        return False


if __name__ == '__main__':
    create_demo_database()

