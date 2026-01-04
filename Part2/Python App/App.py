"""
Main Application - University Database Management System
Main window with navigation to 6 sub-menus.
"""

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QMessageBox,
                             QListWidget, QStackedWidget, QToolButton)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import QSize
from db_connection import get_db_connection
from db_connection_demo import get_demo_db_connection
import sys
import os
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

        # Overall layout: left navigation + main content
        outer_layout = QHBoxLayout()
        central_widget.setLayout(outer_layout)

        # LEFT: navigation (persistent)
        self.nav_list = QListWidget()
        self.nav_list.setFixedWidth(200)
        self.nav_list.setIconSize(QSize(24, 24))
        # Compact mode toggle
        self.compact_toggle = QToolButton()
        self.compact_toggle.setText('◀')
        self.compact_toggle.setCheckable(True)
        self.compact_toggle.setToolTip('Toggle compact sidebar (icons only)')
        self.compact_toggle.clicked.connect(self.toggle_compact_mode)

        # Nav items
        nav_items = [
            ('Dashboard', 'Overview and quick actions'),
            ('Students', 'Manage students'),
            ('Instructors', 'Manage instructors'),
            ('Courses', 'Manage courses'),
            ('Rooms', 'Manage rooms'),
            ('Reservations', 'Room reservations and assignments'),
            ('Reports', 'Reporting (SQL queries)'),
            ('Admin', 'Audit and administrative tools')
        ]

        for label, tip in nav_items:
            self.nav_list.addItem(label)
        self.nav_list.currentRowChanged.connect(self.on_nav_changed)

        left_col = QVBoxLayout()
        left_col.addWidget(self.compact_toggle)
        left_col.addWidget(self.nav_list)
        left_col.addStretch()

        left_widget = QWidget()
        left_widget.setLayout(left_col)
        outer_layout.addWidget(left_widget)

        # RIGHT: stacked content with breadcrumb/title
        right_col = QVBoxLayout()

        # Breadcrumb / title bar
        self.breadcrumb = QLabel('Dashboard')
        bc_font = QFont()
        bc_font.setPointSize(14)
        bc_font.setBold(True)
        self.breadcrumb.setFont(bc_font)
        self.breadcrumb.setStyleSheet('padding: 8px;')
        right_col.addWidget(self.breadcrumb)

        # Stacked widget for content areas
        self.stack = QStackedWidget()
        right_col.addWidget(self.stack)

        right_widget = QWidget()
        right_widget.setLayout(right_col)
        outer_layout.addWidget(right_widget, 1)

        # Create simple pages for each nav item (these can open full windows)
        pages = {}
        for label, tip in nav_items:
            page = QWidget()
            p_layout = QVBoxLayout()
            title = QLabel(label)
            title.setFont(QFont('Arial', 16, QFont.Bold))
            p_layout.addWidget(title)
            desc = QLabel(tip)
            desc.setStyleSheet('color: #555;')
            p_layout.addWidget(desc)
            # Button to open full module window (preserve existing windows)
            open_btn = QPushButton(f'Open {label} window')
            open_btn.setMaximumWidth(240)
            open_btn.clicked.connect(lambda _, name=label: self.open_module_window(name))
            p_layout.addWidget(open_btn)
            p_layout.addStretch()
            page.setLayout(p_layout)
            self.stack.addWidget(page)
            pages[label] = page

        # Default selection
        self.nav_list.setCurrentRow(0)
        
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

    def toggle_compact_mode(self):
        """Toggle sidebar compact mode (icons-only)."""
        compact = self.compact_toggle.isChecked()
        if compact:
            # icons-only: hide text by reducing width and showing only icons
            self.nav_list.setFixedWidth(64)
            for i in range(self.nav_list.count()):
                item = self.nav_list.item(i)
                item.setText('')
        else:
            self.nav_list.setFixedWidth(200)
            # restore labels
            labels = ['Dashboard','Students','Instructors','Courses','Rooms','Reservations','Reports','Admin']
            for i in range(self.nav_list.count()):
                item = self.nav_list.item(i)
                item.setText(labels[i])

    def on_nav_changed(self, index):
        """Update stacked widget and breadcrumb when navigation changes."""
        if index < 0:
            return
        self.stack.setCurrentIndex(index)
        label = self.nav_list.item(index).text() or ['Dashboard','Students','Instructors','Courses','Rooms','Reservations','Reports','Admin'][index]
        self.breadcrumb.setText(label)

    def open_module_window(self, name):
        """Open the full module window for the given module name."""
        try:
            if name == 'CRUD Operations' or name == 'Students' or name == 'Courses' or name == 'Instructors':
                self.crud_window = CRUDWindow(self)
                self.crud_window.show()
            elif name == 'Reservations' or name == 'Rooms':
                self.reservation_window = ReservationWindow(self)
                self.reservation_window.show()
            elif name == 'Marks' or name == 'Marks & Attendance' or name == 'Attendance':
                self.marks_attendance_window = MarksAttendanceWindow(self)
                self.marks_attendance_window.show()
            elif name == 'Grading' or name == 'Grading/Results Processing':
                self.grading_window = GradingWindow(self)
                self.grading_window.show()
            elif name == 'Reports' or name == 'Reporting':
                self.reporting_window = ReportingWindow(self)
                self.reporting_window.show()
            elif name == 'Admin' or name == 'Audit':
                self.audit_window = AuditWindow(self)
                self.audit_window.show()
            else:
                # fallback: attempt generic mapping by name
                mapping = {
                    'Dashboard': None,
                    'Students': CRUDWindow,
                    'Instructors': CRUDWindow,
                    'Courses': CRUDWindow,
                    'Rooms': ReservationWindow,
                    'Reservations': ReservationWindow,
                    'Reports': ReportingWindow,
                    'Admin': AuditWindow
                }
                cls = mapping.get(name)
                if cls:
                    win = cls(self)
                    win.show()
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to open {name}:\n{e}')
    
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
