"""
Demo Database Connection Module
Uses SQLite for local testing without PostgreSQL setup.
"""

import sqlite3
import os
from pathlib import Path


class DemoDatabaseConnection:
    """Manages SQLite database connections for demo/testing."""
    
    def __init__(self, db_path=None):
        """
        Initialize SQLite database connection.
        
        Args:
            db_path: Path to SQLite database file (default: demo/university_demo.db)
        """
        if db_path is None:
            # Create demo directory in project root
            project_root = Path(__file__).parent.parent.parent
            demo_dir = project_root / "demo"
            demo_dir.mkdir(exist_ok=True)
            db_path = demo_dir / "university_demo.db"
        
        self.db_path = db_path
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """
        Establish connection to SQLite database.
        
        Returns:
            sqlite3.Connection: Database connection object
        """
        try:
            self.connection = sqlite3.connect(str(self.db_path))
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
            return self.connection
        except Exception as e:
            print(f"Error connecting to demo database: {e}")
            raise
    
    def get_cursor(self):
        """
        Get a cursor for executing SQL queries.
        
        Returns:
            sqlite3.Cursor: Database cursor object
        """
        if self.connection is None:
            self.connect()
        
        if self.cursor is None:
            self.cursor = self.connection.cursor()
        
        return self.cursor
    
    def execute_query(self, query, params=None):
        """
        Execute a SQL query and return results.
        
        Args:
            query: SQL query string (PostgreSQL syntax adapted for SQLite)
            params: Optional parameters for parameterized queries
            
        Returns:
            list: Query results (for SELECT queries)
        """
        # Adapt PostgreSQL syntax to SQLite
        query = self._adapt_query(query)

        # Convert psycopg2-style '%s' parameter placeholders to SQLite '?'
        if params is not None:
            query = query.replace('%s', '?')

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
        except Exception as e:
            self.connection.rollback()
            print(f"Error executing query: {e}")
            raise
    
    def _adapt_query(self, query):
        """Adapt PostgreSQL syntax to SQLite."""
        # Replace PostgreSQL-specific syntax
        query = query.replace('SERIAL', 'INTEGER')
        query = query.replace('::date', '')
        query = query.replace('::time', '')
        query = query.replace('::numeric', '')
        query = query.replace('::integer', '')
        query = query.replace('::text', '')
        query = query.replace('CURRENT_TIMESTAMP', "datetime('now')")
        query = query.replace('CURRENT_DATE', "date('now')")
        query = query.replace('CURRENT_TIME', "time('now')")
        # Remove type casts in function calls
        import re
        query = re.sub(r'::\w+', '', query)
        return query
    
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


def get_demo_db_connection():
    """
    Get a demo database connection instance (SQLite).
    
    Returns:
        DemoDatabaseConnection: Configured demo database connection
    """
    return DemoDatabaseConnection()

