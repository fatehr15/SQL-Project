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
        self.dashboard_widget = None
        
        self.init_ui()
        self.load_dashboard()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('University Database Management System')
        self.setGeometry(100, 100, 1200, 800)
        
        # Set modern color scheme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
            }
            QMenuBar {
                background-color: #2c3e50;
                color: white;
                padding: 5px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 5px 15px;
            }
            QMenuBar::item:selected {
                background-color: #34495e;
            }
            QMenu {
                background-color: white;
                border: 1px solid #dcdde1;
            }
            QMenu::item:selected {
                background-color: #3498db;
                color: white;
            }
            QStatusBar {
                background-color: #ecf0f1;
                color: #2c3e50;
                font-size: 11px;
            }
        """)
        
        # Add menu bar
        menubar = self.menuBar()
        
        # Settings menu
        settings_menu = menubar.addMenu('⚙ Settings')
        connection_action = settings_menu.addAction('Database Connection...')
        connection_action.triggered.connect(self.show_connection_dialog)
        
        # Help menu
        help_menu = menubar.addMenu('❓ Help')
        about_action = help_menu.addAction('About')
        about_action.triggered.connect(self.show_about)
        
        # Central widget with scrolling
        from PyQt5.QtWidgets import QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        self.setCentralWidget(scroll_area)
        
        central_widget = QWidget()
        scroll_area.setWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(20)
        central_widget.setLayout(main_layout)
        
        # Header section with icon
        header_widget = QWidget()
        header_layout = QVBoxLayout()
        header_layout.setSpacing(10)
        header_widget.setLayout(header_layout)
        
        # Title with icon
        title = QLabel('🎓 University Database Management System')
        title_font = QFont('Segoe UI', 24, QFont.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            color: #2c3e50;
            padding: 20px;
            background-color: white;
            border-radius: 10px;
            border: 2px solid #3498db;
        """)
        header_layout.addWidget(title)
        
        subtitle = QLabel('Select a module to get started')
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle_font = QFont('Segoe UI', 12)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet("padding: 5px; color: #7f8c8d;")
        header_layout.addWidget(subtitle)
        
        main_layout.addWidget(header_widget)
        
        # Info panel (placeholder for dashboard)
        self.dashboard_container = QWidget()
        dashboard_layout = QVBoxLayout()
        dashboard_layout.setContentsMargins(0, 0, 0, 0)
        self.dashboard_container.setLayout(dashboard_layout)
        main_layout.addWidget(self.dashboard_container)
        
        # Modules section
        modules_label = QLabel('📚 Available Modules')
        modules_label.setFont(QFont('Segoe UI', 14, QFont.Bold))
        modules_label.setStyleSheet("color: #2c3e50; padding: 10px 0;")
        main_layout.addWidget(modules_label)
        
        # Grid-like layout for buttons
        buttons_widget = QWidget()
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(15)
        buttons_widget.setLayout(buttons_layout)
        
        # Define button rows with icons
        row_data = [
            [
                ('📝 CRUD Operations', 'Manage Create, Read, Update, Delete operations', self.open_crud_operations, '#3498db'),
                ('📅 Assignment/Reservations', 'Manage course assignments and room reservations', self.open_assignment_reservations, '#9b59b6')
            ],
            [
                ('✍ Marks & Attendance', 'Manage student marks and attendance records', self.open_marks_attendance, '#e67e22'),
                ('📊 Grading/Results', 'Process grades and generate results', self.open_grading_results, '#27ae60')
            ],
            [
                ('🔍 Reporting (SQL)', 'Execute complex SQL queries and generate reports', self.open_reporting, '#16a085'),
                ('🔐 Audit Logs', 'View audit logs and trigger information', self.open_audit, '#c0392b')
            ]
        ]
        
        for row in row_data:
            h_layout = QHBoxLayout()
            h_layout.setSpacing(15)
            for text, tooltip, callback, color in row:
                btn = self.create_menu_button(text, tooltip, color)
                btn.clicked.connect(callback)
                h_layout.addWidget(btn)
            buttons_layout.addLayout(h_layout)
        
        main_layout.addWidget(buttons_widget)
        main_layout.addStretch()
        
        # Footer
        footer = QLabel('💡 Tip: Use Settings → Database Connection to switch between PostgreSQL and Demo mode')
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("""
            color: #95a5a6;
            font-size: 10px;
            padding: 10px;
            background-color: #ecf0f1;
            border-radius: 5px;
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
        )
    
    def _update_status_bar(self):
        """Update status bar with connection info."""
        if self.conn_manager.in_memory:
            status = 'Using in-memory demo database (SQLite)'
        elif self.conn_manager.use_demo:
            status = 'Demo database connected (SQLite)'
        else:
            status = 'Database connected (PostgreSQL)'
        
        self.statusBar().showMessage(status)
    
    def create_menu_button(self, text, tooltip, color='#3498db'):
        """Create a styled menu button with modern design."""
        button = QPushButton(text)
        button.setToolTip(tooltip)
        button.setMinimumHeight(120)
        button.setFont(QFont('Segoe UI', 11, QFont.Bold))
        button.setCursor(Qt.PointingHandCursor)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 12px;
                padding: 20px;
                text-align: left;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(color)};
                transform: translateY(-2px);
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(color, 0.3)};
                transform: translateY(0px);
            }}
        """)
        return button
    
    def _darken_color(self, hex_color, factor=0.15):
        """Darken a hex color by a given factor."""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = int(r * (1 - factor))
        g = int(g * (1 - factor))
        b = int(b * (1 - factor))
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
                self.load_dashboard()
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
                self.load_dashboard()
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
            
            # Create and add dashboard
            from dashboard_widget import DashboardWidget
            self.dashboard_widget = DashboardWidget(connection, self)
            layout.addWidget(self.dashboard_widget)
            
        except Exception as e:
            print(f"Warning: Could not load dashboard: {e}")
            import traceback
            traceback.print_exc()
            # Show a placeholder message instead
            placeholder = QLabel("📊 Dashboard currently unavailable")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet("""
                padding: 20px;
                background-color: #fff3cd;
                color: #856404;
                border-radius: 8px;
                border: 1px solid #ffeaa7;
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