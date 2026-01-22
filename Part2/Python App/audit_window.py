from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTableWidget, QTableWidgetItem, QLabel,
                             QMessageBox, QComboBox, QDateEdit, QHeaderView)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
import db_connection


class AuditWindow(QMainWindow):
    """Window for viewing audit logs of database operations."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.connection = db_connection.get_db_connection()
        self.init_ui()
        self.load_audit_logs()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('Audit Logs - Database Operations Tracking')
        self.setGeometry(150, 150, 1200, 700)
        
        # Modern styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F8F9FA;
            }
            QLabel {
                color: #1A1D23;
            }
            QPushButton {
                background-color: #2563EB;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
            QPushButton:pressed {
                background-color: #1E40AF;
            }
            QComboBox, QDateEdit {
                padding: 8px;
                border: 1px solid #E1E4E8;
                border-radius: 6px;
                background-color: white;
                font-size: 13px;
            }
            QComboBox:focus, QDateEdit:focus {
                border: 2px solid #2563EB;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #E1E4E8;
                border-radius: 8px;
                gridline-color: #E1E4E8;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #F3F4F6;
            }
            QTableWidget::item:selected {
                background-color: #DBEAFE;
                color: #1E40AF;
            }
            QHeaderView::section {
                background-color: #F3F4F6;
                color: #1A1D23;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #E1E4E8;
                font-weight: 600;
                font-size: 13px;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)
        central_widget.setLayout(main_layout)
        
        # Header
        header = QLabel('Audit Trail')
        header.setFont(QFont('Segoe UI', 24, QFont.Bold))
        header.setStyleSheet("color: #1A1D23; padding: 8px 0;")
        main_layout.addWidget(header)
        
        subtitle = QLabel('Track all INSERT, UPDATE, and DELETE operations on student marks and attendance')
        subtitle.setFont(QFont('Segoe UI', 12))
        subtitle.setStyleSheet("color: #57606A; padding-bottom: 8px;")
        main_layout.addWidget(subtitle)
        
        # Filter section
        filter_widget = QWidget()
        filter_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #E1E4E8;
            }
        """)
        filter_layout = QHBoxLayout()
        filter_layout.setContentsMargins(16, 16, 16, 16)
        filter_layout.setSpacing(12)
        filter_widget.setLayout(filter_layout)
        
        # Table filter
        filter_layout.addWidget(QLabel('Table:'))
        self.table_filter = QComboBox()
        self.table_filter.addItems(['All Tables', 'Student Marks', 'Student Attendance'])
        self.table_filter.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.table_filter)
        
        # Operation type filter
        filter_layout.addWidget(QLabel('Operation:'))
        self.operation_filter = QComboBox()
        self.operation_filter.addItems(['All Operations', 'INSERT', 'UPDATE', 'DELETE'])
        self.operation_filter.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.operation_filter)
        
        # Date filter
        filter_layout.addWidget(QLabel('From:'))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_from.dateChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.date_from)
        
        filter_layout.addWidget(QLabel('To:'))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.dateChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.date_to)
        
        filter_layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton('🔄 Refresh')
        refresh_btn.clicked.connect(self.load_audit_logs)
        filter_layout.addWidget(refresh_btn)
        
        main_layout.addWidget(filter_widget)
        
        # Audit table
        self.audit_table = QTableWidget()
        self.audit_table.setColumnCount(7)
        self.audit_table.setHorizontalHeaderLabels([
            'Audit ID', 'Table Name', 'Operation', 'Record ID', 
            'Timestamp', 'User', 'Details'
        ])
        
        # Set column widths
        header = self.audit_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.Stretch)
        
        self.audit_table.setAlternatingRowColors(True)
        self.audit_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.audit_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        main_layout.addWidget(self.audit_table)
        
        # Statistics panel
        stats_widget = QWidget()
        stats_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #E1E4E8;
            }
        """)
        stats_layout = QHBoxLayout()
        stats_layout.setContentsMargins(16, 12, 16, 12)
        stats_widget.setLayout(stats_layout)
        
        self.stats_label = QLabel('Total Records: 0')
        self.stats_label.setFont(QFont('Segoe UI', 11))
        self.stats_label.setStyleSheet("color: #57606A;")
        stats_layout.addWidget(self.stats_label)
        
        stats_layout.addStretch()
        
        main_layout.addWidget(stats_widget)
    
    def load_audit_logs(self):
        """Load audit logs from database."""
        cursor = None
        try:
            # Rollback any pending transaction first
            try:
                self.connection.rollback()
            except:
                pass
            
            cursor = self.connection.cursor()
            
            # Query to get audit logs
            query = """
                SELECT 
                    audit_id,
                    table_name,
                    operation_type,
                    record_id,
                    operation_time,
                    COALESCE(user_name, 'System') as user_name,
                    COALESCE(details, '') as details
                FROM audit_log
                ORDER BY operation_time DESC
                LIMIT 1000
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            # Commit the transaction
            self.connection.commit()
            
            # Store all rows for filtering
            self.all_audit_data = rows
            
            # Display the data
            self.display_audit_data(rows)
            
        except Exception as e:
            # Rollback on error
            try:
                self.connection.rollback()
            except:
                pass
            
            QMessageBox.critical(self, 'Error', f'Failed to load audit logs:\n{str(e)}')
            import traceback
            traceback.print_exc()
        
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
    
    def display_audit_data(self, rows):
        """Display audit data in the table."""
        self.audit_table.setRowCount(len(rows))
        
        for i, row in enumerate(rows):
            # Audit ID
            self.audit_table.setItem(i, 0, QTableWidgetItem(str(row[0])))
            
            # Table Name
            table_item = QTableWidgetItem(row[1])
            self.audit_table.setItem(i, 1, table_item)
            
            # Operation Type with color coding
            operation_item = QTableWidgetItem(row[2])
            if row[2] == 'INSERT':
                operation_item.setForeground(Qt.darkGreen)
            elif row[2] == 'UPDATE':
                operation_item.setForeground(Qt.darkBlue)
            elif row[2] == 'DELETE':
                operation_item.setForeground(Qt.darkRed)
            self.audit_table.setItem(i, 2, operation_item)
            
            # Record ID
            self.audit_table.setItem(i, 3, QTableWidgetItem(str(row[3]) if row[3] else 'N/A'))
            
            # Timestamp
            timestamp = row[4].strftime('%Y-%m-%d %H:%M:%S') if hasattr(row[4], 'strftime') else str(row[4])
            self.audit_table.setItem(i, 4, QTableWidgetItem(timestamp))
            
            # User
            self.audit_table.setItem(i, 5, QTableWidgetItem(row[5]))
            
            # Details
            self.audit_table.setItem(i, 6, QTableWidgetItem(row[6]))
        
        # Update statistics
        self.stats_label.setText(f'Total Records: {len(rows)}')
    
    def apply_filters(self):
        """Apply filters to the audit data."""
        if not hasattr(self, 'all_audit_data'):
            return
        
        filtered_data = []
        
        table_filter = self.table_filter.currentText()
        operation_filter = self.operation_filter.currentText()
        date_from = self.date_from.date().toPyDate()
        date_to = self.date_to.date().toPyDate()
        
        for row in self.all_audit_data:
            # Filter by table
            if table_filter != 'All Tables':
                table_map = {
                    'Student Marks': 'student_mark',
                    'Student Attendance': 'student_attendance'
                }
                if row[1] != table_map.get(table_filter, row[1]):
                    continue
            
            # Filter by operation
            if operation_filter != 'All Operations' and row[2] != operation_filter:
                continue
            
            # Filter by date
            operation_date = row[4].date() if hasattr(row[4], 'date') else row[4]
            if operation_date < date_from or operation_date > date_to:
                continue
            
            filtered_data.append(row)
        
        self.display_audit_data(filtered_data)
    
    def closeEvent(self, event):
        """Handle window close event."""
        event.accept()