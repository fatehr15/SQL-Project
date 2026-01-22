import sqlite3
from pathlib import Path


class CursorWrapper:
    """Wrapper around SQLite cursor to provide PostgreSQL-like interface."""
    
    def __init__(self, cursor):
        self._cursor = cursor
        self._description = None
    
    @property
    def description(self):
        """Return cursor description (column metadata)."""
        # Use the underlying cursor's description
        return self._cursor.description
    
    @description.setter
    def description(self, value):
        """Allow setting description (needed for some operations)."""
        # Store in our wrapper, but this doesn't affect the real cursor
        self._description = value
    
    def execute(self, query, params=None):
        """Execute a query with optional parameters."""
        if params is None:
            return self._cursor.execute(query)
        else:
            # Convert %s style placeholders to ? style for SQLite
            converted_query = query.replace('%s', '?')
            return self._cursor.execute(converted_query, params)
    
    def executemany(self, query, params_list):
        """Execute a query multiple times with different parameters."""
        converted_query = query.replace('%s', '?')
        return self._cursor.executemany(converted_query, params_list)
    
    def fetchone(self):
        """Fetch one row."""
        return self._cursor.fetchone()
    
    def fetchall(self):
        """Fetch all rows."""
        return self._cursor.fetchall()
    
    def fetchmany(self, size=None):
        """Fetch multiple rows."""
        if size is None:
            return self._cursor.fetchmany()
        return self._cursor.fetchmany(size)
    
    @property
    def rowcount(self):
        """Return number of rows affected."""
        return self._cursor.rowcount
    
    @property
    def lastrowid(self):
        """Return last inserted row ID."""
        return self._cursor.lastrowid
    
    def close(self):
        """Close the cursor."""
        return self._cursor.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __iter__(self):
        """Make cursor iterable."""
        return iter(self._cursor)


class DemoDatabaseConnection:
    """Demo database connection using SQLite."""
    
    def __init__(self, db_path=None):
        """
        Initialize demo database connection.
        
        Args:
            db_path: Path to SQLite database file. 
                    If None, uses default demo database.
                    If ':memory:', creates in-memory database.
        """
        if db_path is None:
            # Default demo database path
            project_root = Path(__file__).resolve().parent.parent.parent
            self.db_path = project_root / "demo" / "university_demo.db"
        else:
            self.db_path = db_path
        
        self.connection = None
        self._in_memory = (db_path == ':memory:')
    
    def connect(self):
        """Establish connection to SQLite database."""
        if self._in_memory:
            # In-memory database
            self.connection = sqlite3.connect(':memory:')
            # Initialize schema for in-memory database
            self._initialize_in_memory_schema()
        else:
            # File-based database
            db_path_str = str(self.db_path)
            
            # Check if database file exists
            if not Path(db_path_str).exists() and db_path_str != ':memory:':
                raise FileNotFoundError(f"Database file not found: {db_path_str}")
            
            self.connection = sqlite3.connect(db_path_str)
        
        # Enable foreign keys
        self.connection.execute("PRAGMA foreign_keys = ON")
        
        # Set row factory to return Row objects (dict-like access)
        self.connection.row_factory = sqlite3.Row
        
        return self.connection
    
    def _initialize_in_memory_schema(self):
        """Initialize schema and sample data for in-memory database."""
        cursor = self.connection.cursor()
        
        # Create tables with minimal schema
        schema_sql = """
        -- Department table
        CREATE TABLE IF NOT EXISTS Department (
            dept_id INTEGER PRIMARY KEY AUTOINCREMENT,
            dept_name TEXT NOT NULL UNIQUE,
            building TEXT,
            budget REAL
        );
        
        -- Instructor table
        CREATE TABLE IF NOT EXISTS Instructor (
            instructor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            dept_id INTEGER,
            salary REAL,
            FOREIGN KEY (dept_id) REFERENCES Department(dept_id)
        );
        
        -- Student table
        CREATE TABLE IF NOT EXISTS Student (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            dept_id INTEGER,
            tot_cred INTEGER DEFAULT 0,
            FOREIGN KEY (dept_id) REFERENCES Department(dept_id)
        );
        
        -- Course table
        CREATE TABLE IF NOT EXISTS Course (
            course_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            dept_id INTEGER,
            credits INTEGER,
            FOREIGN KEY (dept_id) REFERENCES Department(dept_id)
        );
        
        -- Section table
        CREATE TABLE IF NOT EXISTS Section (
            section_id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER,
            sec_id TEXT,
            semester TEXT,
            year INTEGER,
            building TEXT,
            room_number TEXT,
            FOREIGN KEY (course_id) REFERENCES Course(course_id)
        );
        
        -- Teaches table
        CREATE TABLE IF NOT EXISTS Teaches (
            instructor_id INTEGER,
            section_id INTEGER,
            PRIMARY KEY (instructor_id, section_id),
            FOREIGN KEY (instructor_id) REFERENCES Instructor(instructor_id),
            FOREIGN KEY (section_id) REFERENCES Section(section_id)
        );
        
        -- Takes table
        CREATE TABLE IF NOT EXISTS Takes (
            student_id INTEGER,
            section_id INTEGER,
            grade TEXT,
            PRIMARY KEY (student_id, section_id),
            FOREIGN KEY (student_id) REFERENCES Student(student_id),
            FOREIGN KEY (section_id) REFERENCES Section(section_id)
        );
        
        -- Classroom table
        CREATE TABLE IF NOT EXISTS Classroom (
            building TEXT,
            room_number TEXT,
            capacity INTEGER,
            PRIMARY KEY (building, room_number)
        );
        """
        
        # Execute schema creation
        cursor.executescript(schema_sql)
        
        # Insert sample data
        sample_data = """
        -- Sample departments
        INSERT INTO Department (dept_name, building, budget) VALUES
            ('Computer Science', 'Taylor', 100000),
            ('Mathematics', 'Watson', 80000),
            ('Physics', 'Einstein', 90000);
        
        -- Sample instructors
        INSERT INTO Instructor (name, dept_id, salary) VALUES
            ('Dr. Smith', 1, 75000),
            ('Dr. Johnson', 1, 80000),
            ('Dr. Williams', 2, 70000);
        
        -- Sample students
        INSERT INTO Student (name, dept_id, tot_cred) VALUES
            ('Alice Johnson', 1, 32),
            ('Bob Smith', 1, 45),
            ('Charlie Brown', 2, 28);
        
        -- Sample courses
        INSERT INTO Course (title, dept_id, credits) VALUES
            ('Database Systems', 1, 4),
            ('Algorithms', 1, 4),
            ('Calculus I', 2, 4);
        
        -- Sample classrooms
        INSERT INTO Classroom (building, room_number, capacity) VALUES
            ('Taylor', '101', 50),
            ('Watson', '201', 40),
            ('Einstein', '301', 30);
        """
        
        cursor.executescript(sample_data)
        self.connection.commit()
        cursor.close()
    
    def cursor(self):
        """Get a database cursor wrapped for compatibility."""
        if self.connection is None:
            raise Exception("Database not connected. Call connect() first.")
        return CursorWrapper(self.connection.cursor())
    
    def get_cursor(self):
        """Alias for cursor() method."""
        return self.cursor()
    
    def commit(self):
        """Commit the current transaction."""
        if self.connection:
            self.connection.commit()
    
    def rollback(self):
        """Rollback the current transaction."""
        if self.connection:
            self.connection.rollback()
    
    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute(self, query, params=None):
        """Execute a query directly on the connection."""
        cursor = self.cursor()
        cursor.execute(query, params)
        return cursor
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        self.close()


def get_demo_db_connection():
    """
    Get a demo database connection.
    Uses the default demo database file.
    """
    conn = DemoDatabaseConnection()
    # Don't call connect() here - let the caller do it
    # This matches the pattern of the main db_connection module
    return conn


# For compatibility with modules that import this directly
__all__ = ['DemoDatabaseConnection', 'get_demo_db_connection']