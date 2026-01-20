"""
Connection Validator with Threading
Handles database connection validation in a separate thread to prevent UI freezing.
"""

from PyQt5.QtCore import QThread, pyqtSignal
import psycopg2
from pathlib import Path


class ConnectionValidatorThread(QThread):
    """Thread for validating database connection without freezing the UI."""
    
    # Signals
    connection_success = pyqtSignal(dict)  # Emits connection info on success
    connection_error = pyqtSignal(str)     # Emits error message on failure
    
    def __init__(self, host, port, database, user, password):
        super().__init__()
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self._connection = None
    
    def run(self):
        """Run the connection validation in the thread."""
        try:
            # Build connection parameters
            connect_params = {
                'host': self.host,
                'port': self.port,
                'database': self.database,
                'user': self.user,
            }
            
            if self.password:
                connect_params['password'] = self.password
            
            # Attempt connection
            self._connection = psycopg2.connect(**connect_params)
            
            # Test with a simple query
            cursor = self._connection.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            cursor.close()
            
            # Check if key tables exist
            cursor = self._connection.cursor()
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                AND table_name IN ('Department', 'Student', 'Instructor', 'Course', 'Room', 'Reservation')
            """)
            tables = [row[0] for row in cursor.fetchall()]
            cursor.close()
            
            # Emit success with connection info
            self.connection_success.emit({
                'version': version,
                'tables': tables,
                'has_schema': len(tables) > 0
            })
            
        except psycopg2.OperationalError as e:
            error_msg = str(e)
            if "password authentication failed" in error_msg.lower():
                self.connection_error.emit("Invalid username or password. Please check your credentials.")
            elif "could not connect to server" in error_msg.lower() or "connection refused" in error_msg.lower():
                self.connection_error.emit(f"Cannot connect to server at {self.host}:{self.port}. Please check if PostgreSQL is running.")
            elif "does not exist" in error_msg.lower():
                self.connection_error.emit(f"Database '{self.database}' does not exist. Please create it first.")
            else:
                self.connection_error.emit(f"Connection error: {error_msg}")
        except Exception as e:
            self.connection_error.emit(f"Unexpected error: {str(e)}")
        finally:
            if self._connection:
                try:
                    self._connection.close()
                except Exception:
                    pass
    
    def get_connection(self):
        """Get the connection object (for reuse if needed)."""
        return self._connection


def check_schema_exists(connection):
    """Check if the required schema exists in the database."""
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            AND table_name IN ('Department', 'Student', 'Instructor', 'Course', 'Room', 'Reservation')
        """)
        count = cursor.fetchone()[0]
        cursor.close()
        return count >= 6  # At least 6 core tables should exist
    except Exception:
        return False


def initialize_database_schema(connection, lab_scripts_path):
    """Initialize database schema by running lab scripts."""
    import psycopg2
    try:
        cursor = connection.cursor()
        
        # Lab 1: Create tables and insert data
        lab1_path = Path(lab_scripts_path) / "Part1" / "Lab 1" / "Lab1.sql"
        if lab1_path.exists():
            with open(lab1_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()
                # Execute each statement separately
                # Split by semicolon but keep statement context
                statements = [s.strip() for s in sql_script.split(';') if s.strip() and not s.strip().startswith('--')]
                for statement in statements:
                    if statement:
                        try:
                            cursor.execute(statement)
                        except psycopg2.ProgrammingError as e:
                            # Ignore errors like "table already exists", "function already exists", etc.
                            if 'already exists' not in str(e).lower():
                                raise
        
        # Lab 3: Functions
        lab3_path = Path(lab_scripts_path) / "Part1" / "Lab 3" / "lab3.sql"
        if lab3_path.exists():
            with open(lab3_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()
                statements = [s.strip() for s in sql_script.split(';') if s.strip() and not s.strip().startswith('--')]
                for statement in statements:
                    if statement:
                        try:
                            cursor.execute(statement)
                        except psycopg2.ProgrammingError as e:
                            if 'already exists' not in str(e).lower():
                                raise
        
        # Lab 4: Triggers
        lab4_path = Path(lab_scripts_path) / "Part1" / "Lab 4" / "Lab4.sql"
        if lab4_path.exists():
            with open(lab4_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()
                statements = [s.strip() for s in sql_script.split(';') if s.strip() and not s.strip().startswith('--')]
                for statement in statements:
                    if statement:
                        try:
                            cursor.execute(statement)
                        except psycopg2.ProgrammingError as e:
                            if 'already exists' not in str(e).lower():
                                raise
        
        connection.commit()
        cursor.close()
        return True
    except Exception as e:
        try:
            connection.rollback()
        except Exception:
            pass
        raise Exception(f"Failed to initialize database schema: {str(e)}")

