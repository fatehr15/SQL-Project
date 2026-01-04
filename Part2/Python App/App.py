import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import types

# add lightweight stub modules so import-time get_db_connection / get_demo_db_connection
# from other modules won't try to connect to PostgreSQL. MainWindow will register a getter
# that returns the active connection object once available.
def _ensure_db_stubs():
	# db_connection stub
	mod = types.ModuleType('db_connection')
	def _set_getter(fn):
		mod._getter = fn
	def _get_db_connection():
		getter = getattr(mod, '_getter', None)
		if callable(getter):
			return getter()
		raise Exception("db_connection getter not set yet")
	mod.set_connection_getter = _set_getter
	mod.get_db_connection = _get_db_connection

	# db_connection_demo stub
	mod_demo = types.ModuleType('db_connection_demo')
	def _set_demo_getter(fn):
		mod_demo._getter = fn
	def _get_demo_db_connection():
		getter = getattr(mod_demo, '_getter', None)
		if callable(getter):
			return getter()
		# If getter not set, import the real module and use it
		try:
			import importlib
			# Remove stub temporarily to import real module
			real_module = importlib.import_module('db_connection_demo')
			return real_module.get_demo_db_connection()
		except Exception:
			raise Exception("db_connection_demo getter not set yet")
	mod_demo.set_connection_getter = _set_demo_getter
	mod_demo.get_demo_db_connection = _get_demo_db_connection
	
	# Add __getattr__ to stub to handle missing attributes (like DemoDatabaseConnection)
	def _demo_getattr(name):
		if name == 'DemoDatabaseConnection':
			# Import the real module to get the class
			import importlib
			real_module = importlib.import_module('db_connection_demo')
			return real_module.DemoDatabaseConnection
		raise AttributeError(f"module 'db_connection_demo' has no attribute '{name}'")
	mod_demo.__getattr__ = _demo_getattr

	# Insert/override into sys.modules to intercept imports
	sys.modules['db_connection'] = mod
	sys.modules['db_connection_demo'] = mod_demo

# ensure stubs exist immediately
_ensure_db_stubs()

class MainWindow(QMainWindow):
    """Main application window with navigation menu."""
    
    def __init__(self, use_demo=False):
        super().__init__()
        self.use_demo = use_demo
        self.db_connection = None
        self.active_window = None                 # keep reference so windows aren't GC'd
        self.in_memory_demo = False
        self.init_ui()
        # Show connection dialog if no saved settings or connection fails
        self.setup_connection()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('University Database Management System')
        self.setGeometry(100, 100, 900, 600)
        
        # Add menu bar
        menubar = self.menuBar()
        settings_menu = menubar.addMenu('Settings')
        connection_action = settings_menu.addAction('Database Connection...')
        connection_action.triggered.connect(self.show_connection_dialog)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Title section
        title = QLabel('University Database Management System')
        title_font = QFont('Arial', 20, QFont.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("padding: 20px; color: #2c3e50;")
        main_layout.addWidget(title)
        
        subtitle = QLabel('Select a module from the menu below')
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("padding: 10px; color: #7f8c8d;")
        main_layout.addWidget(subtitle)
        
        # Grid-like layout for buttons
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(15)
        
        # Define button rows
        row_data = [
            [('CRUD Operations', 'Manage Create, Read, Update, Delete operations', self.open_crud_operations),
             ('Assignment/Reservations', 'Manage course assignments and room reservations', self.open_assignment_reservations)],
            [('Marks & Attendance', 'Manage student marks and attendance records', self.open_marks_attendance),
             ('Grading/Results Processing', 'Process grades and generate results', self.open_grading_results)],
            [('Reporting (SQL Queries)', 'Execute complex SQL queries and generate reports', self.open_reporting),
             ('Audit', 'View audit logs and trigger information', self.open_audit)]
        ]

        for row in row_data:
            h_layout = QHBoxLayout()
            h_layout.setSpacing(15)
            for text, tooltip, callback in row:
                btn = self.create_menu_button(text, tooltip)
                btn.clicked.connect(callback)
                h_layout.addWidget(btn)
            buttons_layout.addLayout(h_layout)
        
        main_layout.addLayout(buttons_layout)
        main_layout.addStretch()
        
        self.statusBar().showMessage('Ready')
    
    def create_menu_button(self, text, tooltip):
        """Create a styled menu button."""
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
    
    def setup_connection(self):
        """Setup database connection, showing dialog if needed."""
        # First, try to ensure static demo database exists
        self.ensure_static_demo()
        
        # Check if config file exists
        from pathlib import Path
        config_file = Path(__file__).parent / "db_config.json"
        
        # If no config file exists, show dialog first
        if not config_file.exists():
            self.show_connection_dialog()
        else:
            # Try to connect with saved settings
            if not self.test_connection():
                # If connection failed, show connection dialog
                self.show_connection_dialog()
    
    def show_connection_dialog(self):
        """Show connection dialog to user."""
        from connection_dialog import ConnectionDialog
        dialog = ConnectionDialog(self)
        if dialog.exec_() == dialog.Accepted:
            # User clicked Connect, try connecting again
            settings = dialog.get_connection_settings()
            self.use_demo = settings.get('use_demo', False)
            if not self.test_connection():
                # Still failed, show error
                QMessageBox.critical(
                    self,
                    "Connection Failed",
                    "Could not establish database connection.\n\n"
                    "The app will use the demo database instead."
                )
                # Force demo mode
                self.use_demo = True
                self.test_connection()
    
    def ensure_static_demo(self):
        """Ensure static demo database exists."""
        try:
            from pathlib import Path
            project_root = Path(__file__).parent.parent.parent
            demo_db = project_root / "demo" / "university_demo.db"
            
            if not demo_db.exists():
                # Create static demo database
                try:
                    from setup_static_demo import create_static_demo_database
                    create_static_demo_database()
                except Exception as e:
                    print(f"Warning: Could not create static demo database: {e}")
        except Exception as e:
            print(f"Warning: Could not ensure static demo database: {e}")
    
    def test_connection(self):
        """Test database connection on startup. Use lazy imports and auto-fallback to demo.
        If both primary and packaged demo fail, create an in-memory SQLite connection so the UI can operate."""
        try:
            if self.use_demo:
                # lazy import demo connector
                from db_connection_demo import get_demo_db_connection
                self.db_connection = get_demo_db_connection()
                status_msg = 'Demo database connected successfully (SQLite)'
            else:
                # lazy import primary connector
                from db_connection import get_db_connection
                self.db_connection = get_db_connection()
                status_msg = 'Database connected successfully'

            if not self.db_connection:
                raise Exception("Database connection object could not be created.")

            # If the returned object exposes a connect() method (e.g. a wrapper), call it.
            connect_method = getattr(self.db_connection, "connect", None)
            if callable(connect_method):
                connect_method()

            # register connection getter with stubs so later imports get the same connection
            try:
                sys.modules['db_connection'].set_connection_getter(lambda: self.db_connection)
            except Exception:
                pass
            try:
                sys.modules['db_connection_demo'].set_connection_getter(lambda: self.db_connection)
            except Exception:
                pass

            self.statusBar().showMessage(status_msg)
            return True

        except Exception as e:
            # Try packaged demo connector next (unless we're already in demo mode)
            if not self.use_demo:
                try:
                    # Import directly, bypassing stub
                    import importlib
                    # Temporarily remove stub to import real module
                    old_stub = sys.modules.get('db_connection_demo')
                    if 'db_connection_demo' in sys.modules:
                        del sys.modules['db_connection_demo']
                    try:
                        real_module = importlib.import_module('db_connection_demo')
                        self.db_connection = real_module.get_demo_db_connection()
                    finally:
                        # Restore stub
                        if old_stub:
                            sys.modules['db_connection_demo'] = old_stub
                    connect_method = getattr(self.db_connection, "connect", None)
                    if callable(connect_method):
                        connect_method()
                    # register with stubs
                    try:
                        sys.modules['db_connection_demo'].set_connection_getter(lambda: self.db_connection)
                        sys.modules['db_connection'].set_connection_getter(lambda: self.db_connection)
                    except Exception:
                        pass
                    self.use_demo = True
                    self.statusBar().showMessage('Connected to demo database (SQLite)')
                    return True
                except Exception:
                    # continue to fall back to in-memory SQLite
                    pass

            # As a last-resort fallback, create an in-memory SQLite DB so the app can run.
            try:
                # Import the actual module directly, bypassing the stub
                import importlib
                # Temporarily remove stub from sys.modules to import real module
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
                # Create a DemoDatabaseConnection wrapper for in-memory database
                # Pass ':memory:' as the db_path to use in-memory database
                demo_conn = DemoDatabaseConnection(db_path=':memory:')
                # Connect to create the in-memory database
                demo_conn.connect()
                self.db_connection = demo_conn
                self.in_memory_demo = True
                self.use_demo = True
                # register with stubs so imports get this connection
                try:
                    sys.modules['db_connection'].set_connection_getter(lambda: self.db_connection)
                    sys.modules['db_connection_demo'].set_connection_getter(lambda: self.db_connection)
                except Exception:
                    pass
                self.statusBar().showMessage('Using in-memory demo database (SQLite)')
                return True
            except Exception as mem_e:
                # If even in-memory creation fails, show final error.
                QMessageBox.critical(self, 'Connection Error',
                                     f'All connection attempts failed.\nPrimary error:\n{str(e)}\n\n'
                                     f'Demo/in-memory error:\n{str(mem_e)}')
                self.statusBar().showMessage('Database connection failed')
                return False
    
    # Navigation Methods with safety wrappers
    def _safe_open(self, import_path, class_name, attr_name):
        """Lazily import window module, instantiate and keep a reference."""
        # Check if database connection is available
        if self.db_connection is None:
            QMessageBox.critical(
                self, 
                "Database Connection Error",
                "Cannot open module: No database connection available.\n\n"
                "Please ensure:\n"
                "1. PostgreSQL is running\n"
                "2. The database 'university_db' exists\n"
                "3. Connection credentials are correct\n\n"
                "You can create the database by running:\n"
                "python create_database.py"
            )
            return
        
        try:
            # ensure stub getters point to current connection before the import in case the module
            # calls get_db_connection() at import time.
            try:
                sys.modules['db_connection'].set_connection_getter(lambda: self.db_connection)
                sys.modules['db_connection_demo'].set_connection_getter(lambda: self.db_connection)
            except Exception:
                pass

            module = __import__(import_path, fromlist=[class_name])
            window_class = getattr(module, class_name)
            self.active_window = window_class(self)   # pass self so window can access use_demo / db_connection
            setattr(self, attr_name, self.active_window)
            self.active_window.show()
        except ImportError as ie:
            QMessageBox.critical(self, "Module Load Error", f"Cannot load module {import_path}: {ie}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open module: {str(e)}")

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
        if self.db_connection:
            try:
                # commit any pending changes for sqlite3.Connection
                try:
                    self.db_connection.commit()
                except Exception:
                    pass
                self.db_connection.close()
            except:
                pass
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    use_demo = '--demo' in sys.argv or '-d' in sys.argv
    
    window = MainWindow(use_demo=use_demo)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()