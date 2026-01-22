import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QMessageBox, QScrollArea)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QCursor
import types
from pathlib import Path
import json


class DatabaseConnectionManager:
    """Centralized database connection manager with stub system."""
    
    def __init__(self):
        self._connection = None
        self._stubs_initialized = False
        self.use_demo = False
        self.in_memory = False
    
    def initialize_stubs(self):
        """Create lightweight stub modules for lazy loading."""
        if self._stubs_initialized:
            return
        
        # db_connection stub
        mod = types.ModuleType('db_connection')
        mod.get_db_connection = lambda: self.get_connection()
        
        # db_connection_demo stub
        mod_demo = types.ModuleType('db_connection_demo')
        mod_demo.get_demo_db_connection = lambda: self.get_connection()
        
        # Handle DemoDatabaseConnection class access
        def _demo_getattr(name):
            if name == 'DemoDatabaseConnection':
                import importlib
                real_module = importlib.import_module('db_connection_demo')
                return real_module.DemoDatabaseConnection
            raise AttributeError(f"module 'db_connection_demo' has no attribute '{name}'")
        
        mod_demo.__getattr__ = _demo_getattr
        
        # Insert into sys.modules
        sys.modules['db_connection'] = mod
        sys.modules['db_connection_demo'] = mod_demo
        
        self._stubs_initialized = True
    
    def get_connection(self):
        """Get the current database connection."""
        if self._connection is None:
            raise Exception("Database connection not initialized. Call connect() first.")
        return self._connection
    
    def connect(self, use_demo=False, db_path=None):
        """
        Establish database connection with fallback strategy.
        
        Args:
            use_demo: If True, use demo SQLite database
            db_path: Path to SQLite database (for demo mode)
        
        Returns:
            tuple: (success: bool, message: str, connection_type: str)
        """
        # Ensure static demo database exists
        self._ensure_static_demo()
        
        # Try requested connection type first
        if use_demo:
            return self._connect_demo(db_path)
        else:
            return self._connect_postgresql()
    
    def _connect_postgresql(self):
        """Connect to PostgreSQL database."""
        try:
            # Import the real module directly, bypassing stub temporarily
            import importlib
            
            # Remove stub to import real module
            old_stub = sys.modules.get('db_connection')
            if 'db_connection' in sys.modules:
                del sys.modules['db_connection']
            
            try:
                # Import real db_connection module
                db_module = importlib.import_module('db_connection')
                
                # Get connection from the real module
                self._connection = db_module.get_db_connection()
            finally:
                # Restore stub
                if old_stub:
                    sys.modules['db_connection'] = old_stub
            
            if not self._connection:
                return False, "Database connection object could not be created", None
            
            # Call connect() method if available
            connect_method = getattr(self._connection, "connect", None)
            if callable(connect_method):
                connect_method()
            
            # Check and initialize schema if needed
            self._check_and_init_schema()
            
            self.use_demo = False
            self.in_memory = False
            return True, "Database connected successfully", "postgresql"
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False, f"PostgreSQL connection failed: {str(e)}", None
    
    def _connect_demo(self, db_path=None):
        """Connect to demo SQLite database with fallback to in-memory."""
        import importlib
        
        # Always import the real module bypassing stub
        old_stub = sys.modules.get('db_connection_demo')
        if 'db_connection_demo' in sys.modules:
            del sys.modules['db_connection_demo']
        
        try:
            real_demo_module = importlib.import_module('db_connection_demo')
            DemoDatabaseConnection = real_demo_module.DemoDatabaseConnection
        finally:
            # Restore stub
            if old_stub:
                sys.modules['db_connection_demo'] = old_stub
        
        # Try file-based demo database first
        if db_path != ':memory:':
            try:
                # Use the default demo database path
                demo_conn = DemoDatabaseConnection()  # No db_path = use default
                demo_conn.connect()
                
                self._connection = demo_conn
                self.use_demo = True
                self.in_memory = False
                return True, "Demo database connected successfully (SQLite)", "demo_file"
            
            except Exception as file_error:
                # Continue to in-memory fallback
                print(f"File-based demo failed: {file_error}")
        
        # Fallback to in-memory database
        try:
            # Check if DemoDatabaseConnection accepts db_path parameter
            import inspect
            sig = inspect.signature(DemoDatabaseConnection.__init__)
            
            if 'db_path' in sig.parameters:
                demo_conn = DemoDatabaseConnection(db_path=':memory:')
            else:
                # Create default instance and manually set to in-memory
                demo_conn = DemoDatabaseConnection()
                # Override the db_path before connecting
                demo_conn.db_path = ':memory:'
            
            demo_conn.connect()
            
            self._connection = demo_conn
            self.use_demo = True
            self.in_memory = True
            return True, "Using in-memory demo database (SQLite)", "demo_memory"
            
        except Exception as mem_error:
            return False, f"Demo database connection failed.\nFile DB error: {str(file_error) if 'file_error' in locals() else 'Not attempted'}\nIn-memory error: {str(mem_error)}", None
    
    def _ensure_static_demo(self):
        """Ensure static demo database exists."""
        try:
            project_root = Path(__file__).resolve().parent.parent.parent
            demo_db = project_root / "demo" / "university_demo.db"
            
            if not demo_db.exists():
                try:
                    from setup_static_demo import create_static_demo_database
                    create_static_demo_database()
                except Exception as e:
                    print(f"Warning: Could not create static demo database: {e}")
        except Exception as e:
            print(f"Warning: Could not ensure static demo database: {e}")
    
    def _check_and_init_schema(self):
        """Check and initialize schema for PostgreSQL connections."""
        try:
            from connection_validator import check_schema_exists, initialize_database_schema
            
            actual_conn = getattr(self._connection, 'connection', None)
            if actual_conn:
                if not check_schema_exists(actual_conn):
                    project_root = Path(__file__).parent.parent.parent
                    initialize_database_schema(actual_conn, project_root)
        except Exception as e:
            print(f"Warning: Schema check/initialization failed: {e}")
    
    def close(self):
        """Close database connection."""
        if self._connection:
            try:
                # Commit any pending changes
                try:
                    self._connection.commit()
                except:
                    pass
                self._connection.close()
            except:
                pass
            self._connection = None


class MainWindow(QMainWindow):
    """Main application window with navigation menu."""
    
    def __init__(self, connection_manager):
        super().__init__()
        self.conn_manager = connection_manager
        self.active_window = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('University Database Management System')
        self.setGeometry(100, 100, 1280, 840)
        
        # Modern, refined color scheme with better contrast
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F8F9FA;
            }
            QMenuBar {
                background-color: #1A1D23;
                color: #FFFFFF;
                padding: 8px;
                font-size: 14px;
                border-bottom: 1px solid #2D3139;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 16px;
                border-radius: 6px;
            }
            QMenuBar::item:selected {
                background-color: #2D3139;
            }
            QMenu {
                background-color: #FFFFFF;
                border: 1px solid #E1E4E8;
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 24px 8px 16px;
                border-radius: 4px;
                color: #24292E;
            }
            QMenu::item:selected {
                background-color: #2563EB;
                color: #FFFFFF;
            }
            QStatusBar {
                background-color: #FFFFFF;
                color: #57606A;
                font-size: 13px;
                border-top: 1px solid #E1E4E8;
                padding: 4px 8px;
            }
        """)
        
        # Add menu bar
        menubar = self.menuBar()
        
        # Settings menu
        settings_menu = menubar.addMenu('Settings')
        connection_action = settings_menu.addAction('Database Connection...')
        connection_action.triggered.connect(self.show_connection_dialog)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        about_action = help_menu.addAction('About')
        about_action.triggered.connect(self.show_about)
        
        # Central widget with scrolling
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        scroll_area.setStyleSheet("background-color: #F8F9FA;")
        self.setCentralWidget(scroll_area)
        
        central_widget = QWidget()
        scroll_area.setWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(48, 32, 48, 32)
        main_layout.setSpacing(24)
        central_widget.setLayout(main_layout)
        
        # Header section - refined and modern
        header_widget = QWidget()
        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)
        header_widget.setLayout(header_layout)
        
        # Title with clean design
        title = QLabel('University Database Management')
        title_font = QFont('Segoe UI', 28, QFont.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            color: #1A1D23;
            padding: 24px;
            background-color: #FFFFFF;
            border-radius: 12px;
            border: 1px solid #E1E4E8;
        """)
        header_layout.addWidget(title)
        
        subtitle = QLabel('Choose a module to begin managing your institution')
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle_font = QFont('Segoe UI', 14)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet("padding: 8px; color: #57606A;")
        header_layout.addWidget(subtitle)
        
        main_layout.addWidget(header_widget)
        
        # Modules section header
        modules_label = QLabel('Available Modules')
        modules_label.setFont(QFont('Segoe UI', 18, QFont.Bold))
        modules_label.setStyleSheet("color: #1A1D23; padding: 16px 0 8px 0;")
        main_layout.addWidget(modules_label)
        
        # Grid layout for module buttons - grouped by function
        buttons_widget = QWidget()
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(16)
        buttons_widget.setLayout(buttons_layout)
        
        # Group 1: Core Operations
        core_label = QLabel('Core Operations')
        core_label.setFont(QFont('Segoe UI', 13, QFont.Medium))
        core_label.setStyleSheet("color: #57606A; padding: 8px 0 4px 0;")
        buttons_layout.addWidget(core_label)
        
        core_row = QHBoxLayout()
        core_row.setSpacing(16)
        
        crud_btn = self.create_menu_button(
            'CRUD Operations',
            'Create, read, update, and delete database records',
            '#2563EB'
        )
        crud_btn.clicked.connect(self.open_crud_operations)
        core_row.addWidget(crud_btn)
        
        assign_btn = self.create_menu_button(
            'Assignments & Reservations',
            'Manage course assignments and room bookings',
            '#7C3AED'
        )
        assign_btn.clicked.connect(self.open_assignment_reservations)
        core_row.addWidget(assign_btn)
        
        buttons_layout.addLayout(core_row)
        
        # Group 2: Academic Management
        academic_label = QLabel('Academic Management')
        academic_label.setFont(QFont('Segoe UI', 13, QFont.Medium))
        academic_label.setStyleSheet("color: #57606A; padding: 16px 0 4px 0;")
        buttons_layout.addWidget(academic_label)
        
        academic_row = QHBoxLayout()
        academic_row.setSpacing(16)
        
        marks_btn = self.create_menu_button(
            'Marks & Attendance',
            'Record and track student marks and attendance',
            '#DC2626'
        )
        marks_btn.clicked.connect(self.open_marks_attendance)
        academic_row.addWidget(marks_btn)
        
        grading_btn = self.create_menu_button(
            'Grading & Results',
            'Process grades and generate student results',
            '#059669'
        )
        grading_btn.clicked.connect(self.open_grading_results)
        academic_row.addWidget(grading_btn)
        
        buttons_layout.addLayout(academic_row)
        
        # Group 3: Analytics & Audit
        analytics_label = QLabel('Analytics & Audit')
        analytics_label.setFont(QFont('Segoe UI', 13, QFont.Medium))
        analytics_label.setStyleSheet("color: #57606A; padding: 16px 0 4px 0;")
        buttons_layout.addWidget(analytics_label)
        
        analytics_row = QHBoxLayout()
        analytics_row.setSpacing(16)
        
        reporting_btn = self.create_menu_button(
            'SQL Reporting',
            'Execute queries and generate custom reports',
            '#0891B2'
        )
        reporting_btn.clicked.connect(self.open_reporting)
        analytics_row.addWidget(reporting_btn)
        
        audit_btn = self.create_menu_button(
            'Audit Logs',
            'Review system audit trails and trigger logs',
            '#64748B'
        )
        audit_btn.clicked.connect(self.open_audit)
        analytics_row.addWidget(audit_btn)
        
        buttons_layout.addLayout(analytics_row)
        
        main_layout.addWidget(buttons_widget)
        main_layout.addStretch()
        
        # Footer - refined info panel
        footer = QLabel('Tip: Switch between PostgreSQL and Demo mode in Settings → Database Connection')
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("""
            color: #57606A;
            font-size: 14px;
            padding: 16px;
            background-color: #FFFFFF;
            border-radius: 8px;
            border: 1px solid #E1E4E8;
        """)
        main_layout.addWidget(footer)
        
        # Update status bar
        self._update_status_bar()
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About University Database Management System",
            "<h3>University Database Management System</h3>"
            "<p>Version 1.0</p>"
            "<p>A comprehensive database management application for educational institutions.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>CRUD Operations for all entities</li>"
            "<li>Course assignments and room reservations</li>"
            "<li>Student marks and attendance tracking</li>"
            "<li>Automated grading and results processing</li>"
            "<li>Advanced SQL reporting</li>"
            "<li>Complete audit trail</li>"
            "</ul>"
            "<p><b>Database Support:</b> PostgreSQL and SQLite</p>"
            "<p>Developed by Hassani Fateh and Raid Kahlrass</p>"
        )
    
    def _update_status_bar(self):
        """Update status bar with connection info."""
        if self.conn_manager.in_memory:
            status = '● In-memory demo database (SQLite) • Data will not persist'
        elif self.conn_manager.use_demo:
            status = '● Demo database connected (SQLite)'
        else:
            status = '● Connected to PostgreSQL'
        
        self.statusBar().showMessage(status)
    
    def create_menu_button(self, text, tooltip, color='#2563EB'):
        """Create a modern, accessible menu button with proper contrast."""
        button = QPushButton(text)
        button.setToolTip(tooltip)
        button.setMinimumHeight(96)
        button.setFont(QFont('Segoe UI', 13, QFont.DemiBold))
        button.setCursor(Qt.PointingHandCursor)
        
        # Hover color calculation
        hover_color = self._adjust_color(color, -15)
        pressed_color = self._adjust_color(color, -25)
        
        button.setStyleSheet(f"""
            QPushButton {{
                background: {color};
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                padding: 20px 24px;
                text-align: left;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: {hover_color};
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            }}
            QPushButton:pressed {{
                background: {pressed_color};
                transform: translateY(1px);
            }}
        """)
        return button
    
    def _adjust_color(self, hex_color, amount):
        """Adjust hex color brightness by amount."""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        r = max(0, min(255, r + amount))
        g = max(0, min(255, g + amount))
        b = max(0, min(255, b + amount))
        
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def show_connection_dialog(self):
        """Show connection dialog to user."""
        from connection_dialog import ConnectionDialog
        
        dialog = ConnectionDialog(self)
        if dialog.exec_() == dialog.Accepted:
            settings = dialog.get_connection_settings()
            use_demo = settings.get('use_demo', False)
            
            # Attempt connection
            success, message, conn_type = self.conn_manager.connect(use_demo=use_demo)
            
            if success:
                self._update_status_bar()
            else:
                # Show error and options
                self._show_connection_error(message)
    
    def _show_connection_error(self, error_message):
        """Show connection error dialog with options."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Connection Failed")
        msg_box.setText("Could not establish database connection")
        msg_box.setInformativeText(f"{error_message}\n\nWhat would you like to do?")
        
        retry_btn = msg_box.addButton("Try Again", QMessageBox.ActionRole)
        demo_btn = msg_box.addButton("Use Demo Mode", QMessageBox.ActionRole)
        cancel_btn = msg_box.addButton("Cancel", QMessageBox.RejectRole)
        
        msg_box.setDefaultButton(retry_btn)
        msg_box.exec_()
        
        if msg_box.clickedButton() == retry_btn:
            self.show_connection_dialog()
        elif msg_box.clickedButton() == demo_btn:
            success, message, conn_type = self.conn_manager.connect(use_demo=True)
            if success:
                QMessageBox.information(
                    self,
                    "Using Demo Mode",
                    "Switched to demo database mode.\n\n"
                    "You can change connection settings later from the menu."
                )
                self._update_status_bar()
            else:
                QMessageBox.critical(self, "Demo Connection Failed", message)
    
    def load_dashboard(self):
        """Load and display dashboard widget."""
        try:
            connection = self.conn_manager.get_connection()
            if not connection:
                return
            
            # Get dashboard container layout
            layout = self.dashboard_container.layout()
            
            # Remove existing dashboard if any
            if self.dashboard_widget:
                layout.removeWidget(self.dashboard_widget)
                self.dashboard_widget.setParent(None)
                self.dashboard_widget = None
            
            
        except Exception as e:
            print(f"Warning: Could not load dashboard: {e}")
            import traceback
            traceback.print_exc()
            # Show a placeholder message instead
            placeholder = QLabel("Dashboard currently unavailable")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet("""
                padding: 24px;
                background-color: #FEF3C7;
                color: #92400E;
                border-radius: 8px;
                border: 1px solid #FCD34D;
                font-size: 14px;
            """)
            self.dashboard_container.layout().addWidget(placeholder)
    
    def _safe_open(self, import_path, class_name, attr_name):
        """Safely open a module window with error handling."""
        try:
            connection = self.conn_manager.get_connection()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Database Connection Error",
                f"Cannot open module: {str(e)}\n\n"
                "Please check your database connection in Settings."
            )
            return
        
        try:
            module = __import__(import_path, fromlist=[class_name])
            window_class = getattr(module, class_name)
            self.active_window = window_class(self)
            setattr(self, attr_name, self.active_window)
            self.active_window.show()
        except ImportError as ie:
            QMessageBox.critical(self, "Module Load Error",
                               f"Cannot load module {import_path}: {ie}")
        except Exception as e:
            QMessageBox.critical(self, "Error",
                               f"Could not open module: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Navigation methods
    def open_crud_operations(self):
        self._safe_open('crud_window', 'CRUDWindow', 'crud_window')
    
    def open_assignment_reservations(self):
        self._safe_open('reservation_window', 'ReservationWindow', 'reservation_window')
    
    def open_marks_attendance(self):
        self._safe_open('marks_attendance_window', 'MarksAttendanceWindow', 'marks_attendance_window')
    
    def open_grading_results(self):
        self._safe_open('grading_window', 'GradingWindow', 'grading_window')
    
    def open_reporting(self):
        self._safe_open('reporting_window', 'ReportingWindow', 'reporting_window')
    
    def open_audit(self):
        self._safe_open('audit_window', 'AuditWindow', 'audit_window')
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.conn_manager.close()
        event.accept()


def load_saved_config():
    """Load saved configuration from file."""
    config_file = Path(__file__).parent / "db_config.json"
    
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                print(f"Loaded configuration from {config_file}:")
                for key, value in config.items():
                    if key == 'password':
                        print(f"  {key}: {'***' if value else '(empty)'}")
                    else:
                        print(f"  {key}: {value}")
                return config
        except Exception as e:
            print(f"Error loading config: {e}")
    else:
        print(f"No config file found at {config_file}")
    
    return {}


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Initialize connection manager with stubs
    conn_manager = DatabaseConnectionManager()
    conn_manager.initialize_stubs()
    
    # Check for demo mode flag
    use_demo = '--demo' in sys.argv or '-d' in sys.argv
    
    # Show connection dialog unless demo mode is forced
    if not use_demo:
        from connection_dialog import ConnectionDialog
        
        print("Opening connection dialog...")
        dialog = ConnectionDialog()
        result = dialog.exec_()
        
        if result != dialog.Accepted:
            print("User cancelled connection dialog")
            sys.exit(0)
        
        # Get settings from dialog
        settings = dialog.get_connection_settings()
        use_demo = settings.get('use_demo', False)
        
        print(f"\nConnection dialog accepted with settings:")
        print(f"  Use Demo: {use_demo}")
        print(f"  Host: {settings.get('host')}")
        print(f"  Port: {settings.get('port')}")
        print(f"  Database: {settings.get('database')}")
        print(f"  User: {settings.get('user')}")
    else:
        print("Demo mode forced via command line argument")
    
    # Attempt initial connection
    print(f"\nAttempting connection (use_demo={use_demo})...")
    success, message, conn_type = conn_manager.connect(use_demo=use_demo)
    
    if not success:
        print(f"Connection failed: {message}")
        QMessageBox.critical(
            None,
            "Connection Failed",
            f"Could not establish database connection:\n\n{message}\n\n"
            "The application will now exit."
        )
        sys.exit(1)
    
    print(f"Connection successful! Type: {conn_type}")
    
    # Create and show main window
    window = MainWindow(conn_manager)
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()