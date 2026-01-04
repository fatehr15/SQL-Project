"""
Database Connection Module
Handles PostgreSQL database connection and cursor creation.
"""

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os


class DatabaseConnection:
    """Manages PostgreSQL database connections and cursors."""
    
    def __init__(self, host='localhost', port=5432, database='university', user='postgres', password=''):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        # Normalize empty passwords to empty string
        self.password = '' if password is None else str(password)
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """
        Establish connection to PostgreSQL database.
        
        Returns:
            psycopg2.connection: Database connection object
            
        Raises:
            psycopg2.Error: If connection fails
        """
        try:
            connect_kwargs = {
                'host': self.host,
                'port': self.port,
                'database': self.database,
                'user': self.user,
            }
            # Only include password if it's non-empty; some PostgreSQL setups fail when given empty password
            if self.password:
                connect_kwargs['password'] = self.password

            self.connection = psycopg2.connect(**connect_kwargs)
            self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            return self.connection
        except psycopg2.Error as e:
            print(f"Error connecting to database: {e}")
            raise
    
    def get_cursor(self):
        """
        Get a cursor for executing SQL queries.
        
        Returns:
            psycopg2.cursor: Database cursor object
            
        Raises:
            psycopg2.Error: If connection is not established
        """
        if self.connection is None or self.connection.closed:
            self.connect()
        
        if self.cursor is None or self.cursor.closed:
            self.cursor = self.connection.cursor()
        
        return self.cursor
    
    def execute_query(self, query, params=None):
        """
        Execute a SQL query and return results.
        
        Args:
            query: SQL query string
            params: Optional parameters for parameterized queries
            
        Returns:
            list: Query results (for SELECT queries)
        """
        cursor = self.get_cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # For SELECT queries, fetch results
            if query.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            else:
                self.connection.commit()
                return cursor.rowcount
        except psycopg2.Error as e:
            self.connection.rollback()
            print(f"Error executing query: {e}")
            raise
    
    def close(self):
        """Close database connection and cursor."""
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Default connection instance
def get_db_connection():
    """
    Get a default database connection instance.
    
    Returns:
        DatabaseConnection: Configured database connection object
    """
    # If demo mode is enabled via environment variable, return the SQLite demo connection
    if os.getenv('USE_DEMO_DB', '0') == '1':
        try:
            from db_connection_demo import get_demo_db_connection
            return get_demo_db_connection()
        except Exception:
            # Fall back to PostgreSQL connection if demo import fails
            pass

    # You can modify these defaults or load from environment variables
    # Default database name matches Part 1: university_db
    return DatabaseConnection(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 5432)),
        database=os.getenv('DB_NAME', 'university_db'),  # Changed to match Part 1 database
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', ' ')  # Empty password for PostgreSQL
    )

