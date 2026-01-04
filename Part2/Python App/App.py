"""
Main Application - University Database Management System
Main window with navigation to 6 sub-menus.
"""

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from db_connection import get_db_connection
from db_connection_demo import get_demo_db_connection
import sys
import os
from crud_window import CRUDWindow
from reservation_window import ReservationWindow
from marks_attendance_window import MarksAttendanceWindow
from grading_window import GradingWindow
from reporting_window import ReportingWindow
from audit_window import AuditWindow


class MainWindow(QMainWindow):
    """Main application window with navigation menu."""
    
    def __init__(self, use_demo=False):
        super().__init__()
        self.use_demo = use_demo
        self.db_connection = None
        self.init_ui()
        self.test_connection()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('University Database Management System')
        self.setGeometry(100, 100, 900, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Title
        title = QLabel('University Database Management System')
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("padding: 20px; color: #2c3e50;")
        main_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel('Select a module from the menu below')
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("padding: 10px; color: #7f8c8d;")
        main_layout.addWidget(subtitle)
        
        # Buttons layout (2 columns, 3 rows)
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(15)
        
        # Row 1
        row1 = QHBoxLayout()
        row1.setSpacing(15)
        
        btn_crud = self.create_menu_button('CRUD Operations', 
                                           'Manage Create, Read, Update, Delete operations')
        btn_assign = self.create_menu_button('Assignment/Reservations', 
                                            'Manage course assignments and room reservations')
        
        row1.addWidget(btn_crud)
        row1.addWidget(btn_assign)
        buttons_layout.addLayout(row1)
        
        # Row 2
        row2 = QHBoxLayout()
        row2.setSpacing(15)
        
        btn_marks = self.create_menu_button('Marks & Attendance', 
                                           'Manage student marks and attendance records')
        btn_grading = self.create_menu_button('Grading/Results Processing', 
                                             'Process grades and generate results')
        
        row2.addWidget(btn_marks)
        row2.addWidget(btn_grading)
        buttons_layout.addLayout(row2)
        
        # Row 3
        row3 = QHBoxLayout()
        row3.setSpacing(15)
        
        btn_reporting = self.create_menu_button('Reporting (SQL Queries)', 
                                               'Execute complex SQL queries and generate reports')
        btn_audit = self.create_menu_button('Audit', 
                                           'View audit logs and trigger information')
        
        row3.addWidget(btn_reporting)
        row3.addWidget(btn_audit)
        buttons_layout.addLayout(row3)
        
        # Add buttons layout to main layout
        main_layout.addLayout(buttons_layout)
        
        # Add stretch to push buttons to center
        main_layout.addStretch()
        
        # Status bar
        self.statusBar().showMessage('Ready')
        
        # Connect button signals
        btn_crud.clicked.connect(self.open_crud_operations)
        btn_assign.clicked.connect(self.open_assignment_reservations)
        btn_marks.clicked.connect(self.open_marks_attendance)
        btn_grading.clicked.connect(self.open_grading_results)
        btn_reporting.clicked.connect(self.open_reporting)
        btn_audit.clicked.connect(self.open_audit)
    
    def create_menu_button(self, text, tooltip):
        """
        Create a styled menu button.
        
        Args:
            text: Button text
            tooltip: Tooltip text
            
        Returns:
            QPushButton: Configured button
        """
        button = QPushButton(text)
        button.setToolTip(tooltip)
        button.setMinimumHeight(100)
        button.setFont(QFont('Arial', 12, QFont.Bold))
        button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        return button
    
    def test_connection(self):
        """Test database connection on startup."""
        try:
            if self.use_demo:
                # Ensure other modules will return demo connections
                os.environ['USE_DEMO_DB'] = '1'
                from db_connection_demo import get_demo_db_connection
                self.db_connection = get_demo_db_connection()
                self.db_connection.connect()
                self.statusBar().showMessage('Demo database connected successfully (SQLite)')
            else:
                self.db_connection = get_db_connection()
                self.db_connection.connect()
                self.statusBar().showMessage('Database connected successfully')
        except Exception as e:
            if not self.use_demo:
                reply = QMessageBox.question(self, 'Connection Error', 
                                            f'Failed to connect to PostgreSQL database:\n{str(e)}\n\n'
                                            'Would you like to use the demo database (SQLite) instead?\n'
                                            'This requires no setup and works immediately.',
                                            QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    # Switch to demo mode
                    self.use_demo = True
                    os.environ['USE_DEMO_DB'] = '1'
                    self.test_connection()  # Retry with demo
                else:
                    self.statusBar().showMessage('Database connection failed')
            else:
                QMessageBox.warning(self, 'Connection Error', 
                                  f'Failed to connect to demo database:\n{str(e)}')
                self.statusBar().showMessage('Database connection failed')
    
    def open_crud_operations(self):
        """Open CRUD Operations sub-menu."""
        self.crud_window = CRUDWindow(self)
        self.crud_window.show()
    
    def open_assignment_reservations(self):
        """Open Assignment/Reservations sub-menu."""
        self.reservation_window = ReservationWindow(self)
        self.reservation_window.show()
    
    def open_marks_attendance(self):
        """Open Marks & Attendance sub-menu."""
        self.marks_attendance_window = MarksAttendanceWindow(self)
        self.marks_attendance_window.show()
    
    def open_grading_results(self):
        """Open Grading/Results Processing sub-menu."""
        self.grading_window = GradingWindow(self)
        self.grading_window.show()
    
    def open_reporting(self):
        """Open Reporting (SQL Queries) sub-menu."""
        self.reporting_window = ReportingWindow(self)
        self.reporting_window.show()
    
    def open_audit(self):
        """Open Audit sub-menu."""
        self.audit_window = AuditWindow(self)
        self.audit_window.show()
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.db_connection:
            self.db_connection.close()
        event.accept()


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Check for demo mode argument
    use_demo = '--demo' in sys.argv or '-d' in sys.argv
    
    if use_demo:
        # Setup demo database if needed
        try:
            # Signal demo mode to the connection factory
            os.environ['USE_DEMO_DB'] = '1'
            from setup_demo_database import create_demo_database
            create_demo_database()
        except:
            pass
    
    window = MainWindow(use_demo=use_demo)
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
