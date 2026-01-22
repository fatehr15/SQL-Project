"""
Base Window Helper Module
Provides common functionality for all window modules.
"""

from PyQt5.QtWidgets import QMessageBox


def get_connection_from_parent(parent):
    """
    Get database connection from parent MainWindow.
    
    Args:
        parent: Parent window (should be MainWindow)
    
    Returns:
        Database connection object
    
    Raises:
        Exception: If no connection available
    """
    if parent is None:
        raise Exception("No parent window provided. Cannot access database connection.")
    
    # Check if parent has conn_manager (MainWindow)
    if hasattr(parent, 'conn_manager'):
        try:
            return parent.conn_manager.get_connection()
        except Exception as e:
            raise Exception(f"Could not get connection from parent: {e}")
    
    # Fallback: check if parent has db_connection directly
    if hasattr(parent, 'db_connection') and parent.db_connection is not None:
        return parent.db_connection
    
    raise Exception("Parent window does not have a database connection")


def is_demo_mode(db_connection):
    """
    Check if connection is using demo database (SQLite).
    
    Args:
        db_connection: Database connection object
    
    Returns:
        bool: True if demo mode, False otherwise
    """
    try:
        from db_connection_demo import DemoDatabaseConnection
        return isinstance(db_connection, DemoDatabaseConnection)
    except:
        return False


def safe_execute(cursor, query, params=None, default=None):
    """
    Execute query safely and return result or default.
    
    Args:
        cursor: Database cursor
        query: SQL query string
        params: Query parameters (optional)
        default: Default value if query fails
    
    Returns:
        Query result or default value
    """
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"Query failed: {query} - {e}")
        return default if default is not None else []


def show_error(parent, title, message):
    """Show error message dialog."""
    QMessageBox.critical(parent, title, message)


def show_warning(parent, title, message):
    """Show warning message dialog."""
    QMessageBox.warning(parent, title, message)


def show_info(parent, title, message):
    """Show information message dialog."""
    QMessageBox.information(parent, title, message)


def show_question(parent, title, message):
    """Show question dialog and return user choice."""
    reply = QMessageBox.question(
        parent, title, message,
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
    )
    return reply == QMessageBox.Yes