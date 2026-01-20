"""
PostgreSQL Database Connection Module
Provides connection to the university database.
"""

import psycopg2
from pathlib import Path
import json


class DatabaseConnection:
    """Wrapper for PostgreSQL database connection."""
    
    def __init__(self, host=None, port=None, database=None, user=None, password=None):
        """
        Initialize database connection parameters.
        
        Args:
            host: Database host (default: load from config)
            port: Database port (default: load from config)
            database: Database name (default: load from config)
            user: Database user (default: load from config)
            password: Database password (default: load from config)
        """
        # Load from config file if parameters not provided
        if host is None:
            config = self._load_config()
            host = config.get('host', 'localhost')
            port = config.get('port', 5432)
            database = config.get('database', 'university_db')
            user = config.get('user', 'postgres')
            password = config.get('password', '')
        
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
    
    def _load_config(self):
        """Load configuration from db_config.json."""
        config_file = Path(__file__).parent / "db_config.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load config: {e}")
        
        return {}
    
    def connect(self):
        """Establish connection to PostgreSQL database."""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            print(f"Connected to PostgreSQL database '{self.database}' at {self.host}:{self.port}")
            return self.connection
        except psycopg2.Error as e:
            raise Exception(f"Could not connect to PostgreSQL: {e}")
    
    def cursor(self):
        """Get a database cursor."""
        if self.connection is None:
            raise Exception("Database not connected. Call connect() first.")
        return self.connection.cursor()
    
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


def get_db_connection():
    """
    Get a database connection using settings from config file.
    
    Returns:
        DatabaseConnection: Connected database instance
    """
    conn = DatabaseConnection()
    # Don't auto-connect here - let caller do it
    # This matches the expected pattern
    return conn


# For compatibility
__all__ = ['DatabaseConnection', 'get_db_connection']