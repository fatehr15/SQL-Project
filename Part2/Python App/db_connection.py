"""
Database Connection Module
Handles PostgreSQL database connection and cursor creation.
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os


class DatabaseConnection:
    """Manages PostgreSQL database connections and cursors."""
    
    def __init__(self, host='localhost', port=5432, database='university_db', user='postgres', password=''):
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
    
    def commit(self):
        """Commit the current transaction."""
        if self.connection and not self.connection.closed:
            self.connection.commit()
    
    def rollback(self):
        """Rollback the current transaction."""
        if self.connection and not self.connection.closed:
            self.connection.rollback()
    
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
    Loads settings from config file if available, otherwise uses environment variables or defaults.
    
    Returns:
        DatabaseConnection: Configured database connection object
    """
    import json
    from pathlib import Path
    
    config_file = Path(__file__).parent / "db_config.json"
    settings = {}
    
    # Load from config file if it exists
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                settings = json.load(f)
        except Exception:
            pass
    
    # Check if demo mode is requested
    use_demo = settings.get('use_demo', False) or os.getenv('USE_DEMO_DB', '0') == '1'
    
    if use_demo:
        try:
            from db_connection_demo import get_demo_db_connection
            return get_demo_db_connection()
        except Exception:
            # Fall back to PostgreSQL connection if demo import fails
            pass

    # Use settings from config file, environment variables, or defaults
    return DatabaseConnection(
        host=settings.get('host') or os.getenv('DB_HOST', 'localhost'),
        port=int(settings.get('port') or os.getenv('DB_PORT', 5432)),
        database=settings.get('database') or os.getenv('DB_NAME', 'university_db'),
        user=settings.get('user') or os.getenv('DB_USER', 'postgres'),
        password=settings.get('password') or os.getenv('DB_PASSWORD', '')
    )

