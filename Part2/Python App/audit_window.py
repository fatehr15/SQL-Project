"""
Audit Window
Interface for viewing audit logs from Marks and Attendance tables using statement triggers.
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QTableWidget, QTableWidgetItem, 
                             QMessageBox, QGroupBox, QTabWidget, QHeaderView,
                             QComboBox, QDateEdit, QDateTimeEdit)
from PyQt5.QtCore import Qt, QDate, QDateTime
from PyQt5.QtGui import QFont
from db_connection import get_db_connection
import os


class AuditWindow(QMainWindow):
    """Window for viewing audit logs from Marks and Attendance tables."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Try to get connection from parent (MainWindow) if available
        if parent and hasattr(parent, 'db_connection') and parent.db_connection is not None:
            self.db_connection = parent.db_connection
        else:
            self.db_connection = get_db_connection()
            if self.db_connection is None:
                raise Exception("No database connection available. Please check your database setup.")
        self.db_connection.connect()
        self.init_ui()
        self.setup_audit_tables()
        self.setup_triggers()
        self.load_audit_logs()
    
    def setup_audit_tables(self):
        """Create audit tables for Marks and Attendance if they don't exist."""
        try:
            cursor = self.db_connection.get_cursor()
            # Create audit tables (use SQLite-compatible definitions when in demo mode)
            if os.getenv('USE_DEMO_DB', '0') == '1':
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Marks_Audit_Log (
                        LogID INTEGER PRIMARY KEY AUTOINCREMENT,
                        OperationType VARCHAR(50) NOT NULL,
                        OperationTime TEXT NOT NULL,
                        Description TEXT,
                        RowsAffected INTEGER DEFAULT 0
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Attendance_Audit_Log (
                        LogID INTEGER PRIMARY KEY AUTOINCREMENT,
                        OperationType VARCHAR(50) NOT NULL,
                        OperationTime TEXT NOT NULL,
                        Description TEXT,
                        RowsAffected INTEGER DEFAULT 0
                    )
                """)
                self.db_connection.commit()
            else:
                # Create Marks_Audit_Log table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Marks_Audit_Log (
                        LogID SERIAL PRIMARY KEY,
                        OperationType VARCHAR(50) NOT NULL,
                        OperationTime TIMESTAMP NOT NULL,
                        Description TEXT,
                        RowsAffected INTEGER DEFAULT 0
                    )
                """)

                # Create Attendance_Audit_Log table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Attendance_Audit_Log (
                        LogID SERIAL PRIMARY KEY,
                        OperationType VARCHAR(50) NOT NULL,
                        OperationTime TIMESTAMP NOT NULL,
                        Description TEXT,
                        RowsAffected INTEGER DEFAULT 0
                    )
                """)

                self.db_connection.commit()
        except Exception as e:
            print(f"Note: Audit tables setup: {e}")
    
    def setup_triggers(self):
        """Create trigger functions and triggers for Marks and Attendance tables."""
        try:
            cursor = self.db_connection.get_cursor()
            # Triggers and functions are Postgres-specific; for demo mode skip creating PL/pgSQL functions
            if os.getenv('USE_DEMO_DB', '0') == '1':
                # Skip function/trigger creation on SQLite demo — triggers are optional for demo
                return

            # Function for Marks audit (Postgres)
            cursor.execute("""
                CREATE OR REPLACE FUNCTION audit_marks_changes_statement()
                RETURNS TRIGGER 
                LANGUAGE plpgsql AS $$
                BEGIN
                    INSERT INTO Marks_Audit_Log (OperationType, OperationTime, Description, RowsAffected)
                    VALUES (
                        TG_OP, 
                        CURRENT_TIMESTAMP, 
                        'A statement-level DML operation occurred on Marks table.',
                        0
                    );
                    
                    RETURN NULL;
                END;
                $$;
            """)

            # Function for Attendance audit
            cursor.execute("""
                CREATE OR REPLACE FUNCTION audit_attendance_changes_statement()
                RETURNS TRIGGER 
                LANGUAGE plpgsql AS $$
                BEGIN
                    INSERT INTO Attendance_Audit_Log (OperationType, OperationTime, Description, RowsAffected)
                    VALUES (
                        TG_OP, 
                        CURRENT_TIMESTAMP, 
                        'A statement-level DML operation occurred on Attendance table.',
                        0
                    );
                    
                    RETURN NULL;
                END;
                $$;
            """)

            # Drop existing triggers if they exist (to avoid errors on recreation)
            cursor.execute("""
                DROP TRIGGER IF EXISTS trg_audit_marks_statement ON Marks;
            """)
            cursor.execute("""
                DROP TRIGGER IF EXISTS trg_audit_attendance_statement ON Attendance;
            """)

            # Create trigger for Marks table
            cursor.execute("""
                CREATE TRIGGER trg_audit_marks_statement 
                AFTER INSERT OR UPDATE OR DELETE ON Marks
                FOR EACH STATEMENT 
                EXECUTE FUNCTION audit_marks_changes_statement();
            """)

            # Create trigger for Attendance table
            cursor.execute("""
                CREATE TRIGGER trg_audit_attendance_statement 
                AFTER INSERT OR UPDATE OR DELETE ON Attendance
                FOR EACH STATEMENT 
                EXECUTE FUNCTION audit_attendance_changes_statement();
            """)

            self.db_connection.connection.commit()
        except Exception as e:
            print(f"Note: Triggers setup: {e}")
            # Try to continue even if triggers already exist
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('Audit Logs - Marks & Attendance')
        self.setGeometry(50, 50, 1400, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Title
        title = QLabel('Audit Logs - Marks & Attendance')
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Info label
        info_label = QLabel('This module displays audit logs for INSERT, UPDATE, and DELETE operations on Marks and Attendance tables.')
        info_label.setWordWrap(True)
        info_label.setStyleSheet("padding: 10px; background-color: #e8f4f8; border-radius: 5px;")
        main_layout.addWidget(info_label)
        
        # Tab widget for different audit logs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Marks Audit Tab
        marks_tab = QWidget()
        marks_layout = QVBoxLayout()
        marks_tab.setLayout(marks_layout)
        
        # Filter controls for Marks
        marks_filter_group = QGroupBox('Filter Marks Audit Log')
        marks_filter_layout = QHBoxLayout()
        marks_filter_group.setLayout(marks_filter_layout)
        
        marks_filter_layout.addWidget(QLabel('Operation Type:'))
        self.marks_operation_filter = QComboBox()
        self.marks_operation_filter.addItems(['All', 'INSERT', 'UPDATE', 'DELETE'])
        self.marks_operation_filter.currentIndexChanged.connect(self.load_marks_audit)
        marks_filter_layout.addWidget(self.marks_operation_filter)
        
        marks_filter_layout.addStretch()
        
        self.btn_refresh_marks = QPushButton('Refresh')
        self.btn_refresh_marks.clicked.connect(self.load_marks_audit)
        self.btn_refresh_marks.setStyleSheet("background-color: #3498db; color: white; padding: 8px;")
        marks_filter_layout.addWidget(self.btn_refresh_marks)
        
        marks_layout.addWidget(marks_filter_group)
        
        # Marks audit table
        marks_table_label = QLabel('Marks Audit Log')
        marks_table_label.setFont(QFont('Arial', 12, QFont.Bold))
        marks_layout.addWidget(marks_table_label)
        
        self.marks_audit_table = QTableWidget()
        self.marks_audit_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.marks_audit_table.horizontalHeader().setStretchLastSection(True)
        self.marks_audit_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        marks_layout.addWidget(self.marks_audit_table)
        
        self.tabs.addTab(marks_tab, 'Marks Audit Log')
        
        # Attendance Audit Tab
        attendance_tab = QWidget()
        attendance_layout = QVBoxLayout()
        attendance_tab.setLayout(attendance_layout)
        
        # Filter controls for Attendance
        attendance_filter_group = QGroupBox('Filter Attendance Audit Log')
        attendance_filter_layout = QHBoxLayout()
        attendance_filter_group.setLayout(attendance_filter_layout)
        
        attendance_filter_layout.addWidget(QLabel('Operation Type:'))
        self.attendance_operation_filter = QComboBox()
        self.attendance_operation_filter.addItems(['All', 'INSERT', 'UPDATE', 'DELETE'])
        self.attendance_operation_filter.currentIndexChanged.connect(self.load_attendance_audit)
        attendance_filter_layout.addWidget(self.attendance_operation_filter)
        
        attendance_filter_layout.addStretch()
        
        self.btn_refresh_attendance = QPushButton('Refresh')
        self.btn_refresh_attendance.clicked.connect(self.load_attendance_audit)
        self.btn_refresh_attendance.setStyleSheet("background-color: #3498db; color: white; padding: 8px;")
        attendance_filter_layout.addWidget(self.btn_refresh_attendance)
        
        attendance_layout.addWidget(attendance_filter_group)
        
        # Attendance audit table
        attendance_table_label = QLabel('Attendance Audit Log')
        attendance_table_label.setFont(QFont('Arial', 12, QFont.Bold))
        attendance_layout.addWidget(attendance_table_label)
        
        self.attendance_audit_table = QTableWidget()
        self.attendance_audit_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.attendance_audit_table.horizontalHeader().setStretchLastSection(True)
        self.attendance_audit_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        attendance_layout.addWidget(self.attendance_audit_table)
        
        self.tabs.addTab(attendance_tab, 'Attendance Audit Log')
        
        # Summary Tab
        summary_tab = QWidget()
        summary_layout = QVBoxLayout()
        summary_tab.setLayout(summary_layout)
        
        summary_label = QLabel('Audit Summary')
        summary_label.setFont(QFont('Arial', 12, QFont.Bold))
        summary_layout.addWidget(summary_label)
        
        self.summary_table = QTableWidget()
        self.summary_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.summary_table.horizontalHeader().setStretchLastSection(True)
        self.summary_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        summary_layout.addWidget(self.summary_table)
        
        btn_refresh_summary = QPushButton('Refresh Summary')
        btn_refresh_summary.clicked.connect(self.load_summary)
        btn_refresh_summary.setStyleSheet("background-color: #27ae60; color: white; padding: 8px;")
        summary_layout.addWidget(btn_refresh_summary)
        
        self.tabs.addTab(summary_tab, 'Summary')
    
    def load_audit_logs(self):
        """Load all audit logs."""
        self.load_marks_audit()
        self.load_attendance_audit()
        self.load_summary()
    
    def load_marks_audit(self):
        """Load Marks audit log."""
        try:
            operation_filter = self.marks_operation_filter.currentText()
            
            if operation_filter == 'All':
                query = """
                    SELECT LogID, OperationType, OperationTime, Description, RowsAffected
                    FROM Marks_Audit_Log
                    ORDER BY OperationTime DESC
                """
                params = ()
            else:
                query = """
                    SELECT LogID, OperationType, OperationTime, Description, RowsAffected
                    FROM Marks_Audit_Log
                    WHERE OperationType = %s
                    ORDER BY OperationTime DESC
                """
                params = (operation_filter,)
            
            cursor = self.db_connection.get_cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            column_names = ['Log ID', 'Operation Type', 'Operation Time', 'Description', 'Rows Affected']
            
            self.marks_audit_table.setRowCount(len(results))
            self.marks_audit_table.setColumnCount(len(column_names))
            self.marks_audit_table.setHorizontalHeaderLabels(column_names)
            
            for row_idx, row in enumerate(results):
                for col_idx, value in enumerate(row):
                    item = QTableWidgetItem(str(value) if value is not None else '')
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    
                    # Color code by operation type
                    if col_idx == 1:  # OperationType column
                        if value == 'INSERT':
                            item.setBackground(Qt.green)
                        elif value == 'UPDATE':
                            item.setBackground(Qt.yellow)
                        elif value == 'DELETE':
                            item.setBackground(Qt.red)
                    
                    self.marks_audit_table.setItem(row_idx, col_idx, item)
            
            self.marks_audit_table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to load Marks audit log:\n{str(e)}')
    
    def load_attendance_audit(self):
        """Load Attendance audit log."""
        try:
            operation_filter = self.attendance_operation_filter.currentText()
            
            if operation_filter == 'All':
                query = """
                    SELECT LogID, OperationType, OperationTime, Description, RowsAffected
                    FROM Attendance_Audit_Log
                    ORDER BY OperationTime DESC
                """
                params = ()
            else:
                query = """
                    SELECT LogID, OperationType, OperationTime, Description, RowsAffected
                    FROM Attendance_Audit_Log
                    WHERE OperationType = %s
                    ORDER BY OperationTime DESC
                """
                params = (operation_filter,)
            
            cursor = self.db_connection.get_cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            column_names = ['Log ID', 'Operation Type', 'Operation Time', 'Description', 'Rows Affected']
            
            self.attendance_audit_table.setRowCount(len(results))
            self.attendance_audit_table.setColumnCount(len(column_names))
            self.attendance_audit_table.setHorizontalHeaderLabels(column_names)
            
            for row_idx, row in enumerate(results):
                for col_idx, value in enumerate(row):
                    item = QTableWidgetItem(str(value) if value is not None else '')
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    
                    # Color code by operation type
                    if col_idx == 1:  # OperationType column
                        if value == 'INSERT':
                            item.setBackground(Qt.green)
                        elif value == 'UPDATE':
                            item.setBackground(Qt.yellow)
                        elif value == 'DELETE':
                            item.setBackground(Qt.red)
                    
                    self.attendance_audit_table.setItem(row_idx, col_idx, item)
            
            self.attendance_audit_table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to load Attendance audit log:\n{str(e)}')
    
    def load_summary(self):
        """Load audit summary statistics."""
        try:
            query = """
                SELECT 
                    'Marks' as Table_Name,
                    OperationType,
                    COUNT(*) as Operation_Count,
                    SUM(RowsAffected) as Total_Rows_Affected,
                    MAX(OperationTime) as Last_Operation_Time
                FROM Marks_Audit_Log
                GROUP BY OperationType
                
                UNION ALL
                
                SELECT 
                    'Attendance' as Table_Name,
                    OperationType,
                    COUNT(*) as Operation_Count,
                    SUM(RowsAffected) as Total_Rows_Affected,
                    MAX(OperationTime) as Last_Operation_Time
                FROM Attendance_Audit_Log
                GROUP BY OperationType
                
                ORDER BY Table_Name, OperationType
            """
            
            cursor = self.db_connection.get_cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            column_names = ['Table Name', 'Operation Type', 'Operation Count', 
                          'Total Rows Affected', 'Last Operation Time']
            
            self.summary_table.setRowCount(len(results))
            self.summary_table.setColumnCount(len(column_names))
            self.summary_table.setHorizontalHeaderLabels(column_names)
            
            for row_idx, row in enumerate(results):
                for col_idx, value in enumerate(row):
                    item = QTableWidgetItem(str(value) if value is not None else '')
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.summary_table.setItem(row_idx, col_idx, item)
            
            self.summary_table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to load audit summary:\n{str(e)}')

