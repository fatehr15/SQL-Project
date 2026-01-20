"""
Database Connection Dialog
Allows users to configure database connection settings.
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QPushButton, QLabel, QMessageBox,
                             QGroupBox, QCheckBox, QProgressBar, QFrame, QWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIntValidator
import json
from pathlib import Path
from connection_validator import ConnectionValidatorThread


class ConnectionDialog(QDialog):
    """Dialog for configuring database connection settings."""
    
    CONFIG_FILE = Path(__file__).parent / "db_config.json"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Database Connection Settings')
        self.setFixedSize(600, 650)
        self.setModal(True)
        
        self.connection_settings = {}
        self.load_saved_settings()
        self.validator_thread = None
        self.last_connection_test_successful = False
        
        # Apply modern styling
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f6fa;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dcdde1;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
                color: #2c3e50;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #dcdde1;
                border-radius: 5px;
                background-color: white;
                font-size: 11px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
            QCheckBox {
                spacing: 8px;
                font-weight: normal;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 2px solid #dcdde1;
            }
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border: 2px solid #3498db;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEzLjMzMzMgNEw2IDExLjMzMzNMMi42NjY2NyA4IiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
            }
            QPushButton {
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
            QPushButton:pressed {
                padding-top: 12px;
                padding-bottom: 8px;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
                color: #ecf0f1;
            }
            QProgressBar {
                border: 2px solid #dcdde1;
                border-radius: 5px;
                text-align: center;
                background-color: white;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        self.setLayout(layout)
        
        # Header with icon
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        
        # Icon (emoji as placeholder)
        icon_label = QLabel('🔌')
        icon_label.setFont(QFont('Segoe UI', 36))
        icon_label.setFixedSize(60, 60)
        icon_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(icon_label)
        
        # Title and subtitle
        title_container = QVBoxLayout()
        title_container.setSpacing(5)
        
        title = QLabel('Database Connection')
        title_font = QFont('Segoe UI', 16, QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #2c3e50;")
        title_container.addWidget(title)
        
        subtitle = QLabel('Configure your database connection settings')
        subtitle.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        title_container.addWidget(subtitle)
        
        header_layout.addLayout(title_container)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #dcdde1; max-height: 2px;")
        layout.addWidget(separator)
        
        # PostgreSQL Connection Group
        pg_group = QGroupBox('🐘 PostgreSQL Connection')
        pg_layout = QFormLayout()
        pg_layout.setSpacing(12)
        pg_layout.setContentsMargins(15, 20, 15, 15)
        pg_group.setLayout(pg_layout)
        
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText('localhost')
        self.host_input.setText(self.connection_settings.get('host', 'localhost'))
        pg_layout.addRow('Host:', self.host_input)
        
        self.port_input = QLineEdit()
        self.port_input.setValidator(QIntValidator(1, 65535))
        self.port_input.setText(str(self.connection_settings.get('port', 5432)))
        pg_layout.addRow('Port:', self.port_input)
        
        self.database_input = QLineEdit()
        self.database_input.setPlaceholderText('university_db')
        self.database_input.setText(self.connection_settings.get('database', 'university_db'))
        pg_layout.addRow('Database:', self.database_input)
        
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText('postgres')
        self.user_input.setText(self.connection_settings.get('user', 'postgres'))
        pg_layout.addRow('Username:', self.user_input)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText('Enter password')
        saved_password = self.connection_settings.get('password', '')
        if saved_password:
            self.password_input.setText(saved_password)
        pg_layout.addRow('Password:', self.password_input)
        
        layout.addWidget(pg_group)
        
        # Demo Database Option
        demo_group = QGroupBox('💾 Demo Mode (SQLite)')
        demo_layout = QVBoxLayout()
        demo_layout.setSpacing(10)
        demo_layout.setContentsMargins(15, 20, 15, 15)
        demo_group.setLayout(demo_layout)
        
        self.use_demo_checkbox = QCheckBox('Use Demo Database (No PostgreSQL Required)')
        self.use_demo_checkbox.setChecked(self.connection_settings.get('use_demo', False))
        self.use_demo_checkbox.setToolTip('Use a local SQLite database with sample data')
        self.use_demo_checkbox.toggled.connect(self.on_demo_mode_toggled)
        demo_layout.addWidget(self.use_demo_checkbox)
        
        demo_info = QLabel('✓ Includes sample data for testing\n✓ Works offline without setup\n✓ Perfect for development and demos')
        demo_info.setWordWrap(True)
        demo_info.setStyleSheet("color: #27ae60; font-size: 10px; padding-left: 26px; line-height: 1.6;")
        demo_layout.addWidget(demo_info)
        
        layout.addWidget(demo_group)
        
        # Status section
        status_container = QWidget()
        status_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
                border: 2px solid #dcdde1;
            }
        """)
        status_layout = QVBoxLayout()
        status_layout.setContentsMargins(15, 10, 15, 10)
        status_layout.setSpacing(8)
        status_container.setLayout(status_layout)
        
        # Status icon and text
        status_header_layout = QHBoxLayout()
        self.status_icon = QLabel('⚡')
        self.status_icon.setFont(QFont('Segoe UI', 14))
        status_header_layout.addWidget(self.status_icon)
        
        self.status_label = QLabel('Ready to connect')
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        status_header_layout.addWidget(self.status_label, 1)
        status_layout.addLayout(status_header_layout)
        
        # Progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        layout.addWidget(status_container)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.btn_test = QPushButton('🔍 Test Connection')
        self.btn_test.clicked.connect(self.test_connection)
        self.btn_test.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        button_layout.addWidget(self.btn_test)
        
        button_layout.addStretch()
        
        self.btn_cancel = QPushButton('Cancel')
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        button_layout.addWidget(self.btn_cancel)
        
        self.btn_ok = QPushButton('✓ Connect')
        self.btn_ok.clicked.connect(self.accept)
        self.btn_ok.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        button_layout.addWidget(self.btn_ok)
        
        layout.addLayout(button_layout)
        
        # Update UI based on initial demo mode state
        self.on_demo_mode_toggled(self.use_demo_checkbox.isChecked())
    
    def on_demo_mode_toggled(self, checked):
        """Handle demo mode checkbox toggle."""
        # Enable/disable PostgreSQL fields
        self.host_input.setEnabled(not checked)
        self.port_input.setEnabled(not checked)
        self.database_input.setEnabled(not checked)
        self.user_input.setEnabled(not checked)
        self.password_input.setEnabled(not checked)
        
        # Update test button text and state
        if checked:
            self.btn_test.setText('💾 Demo Mode Active')
            self.btn_test.setEnabled(False)
            self._update_status('success', 'Demo mode enabled - no connection needed')
            self.last_connection_test_successful = True  # Demo mode is always "successful"
        else:
            self.btn_test.setText('🔍 Test Connection')
            self.btn_test.setEnabled(True)
            self._update_status('ready', 'Ready to connect')
            self.last_connection_test_successful = False  # Reset test status when switching to PostgreSQL
    
    def load_saved_settings(self):
        """Load saved connection settings from config file."""
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    self.connection_settings = json.load(f)
            except Exception:
                self.connection_settings = {}
        else:
            self.connection_settings = {}
    
    def save_settings(self):
        """Save connection settings to config file."""
        try:
            # Parse port value
            port_text = self.port_input.text().strip()
            try:
                port_value = int(port_text) if port_text else 5432
            except ValueError:
                port_value = 5432
            
            # Build settings dictionary from form inputs
            settings = {
                'host': self.host_input.text().strip() or 'localhost',
                'port': port_value,
                'database': self.database_input.text().strip() or 'university_db',
                'user': self.user_input.text().strip() or 'postgres',
                'password': self.password_input.text(),  # Keep empty string if no password
                'use_demo': self.use_demo_checkbox.isChecked()
            }
            
            # Debug: Print what we're about to save
            print(f"Saving settings to {self.CONFIG_FILE}:")
            for key, value in settings.items():
                if key == 'password':
                    print(f"  {key}: {'***' if value else '(empty)'}")
                else:
                    print(f"  {key}: {value}")
            
            # Ensure directory exists
            self.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            
            # Write to file
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(settings, f, indent=2)
            
            # Update internal settings cache
            self.connection_settings = settings
            
            print(f"Settings saved successfully to {self.CONFIG_FILE}")
            return True
            
        except Exception as e:
            print(f"Error saving settings: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "Save Error", f"Could not save settings: {e}")
            return False
    
    def get_connection_settings(self):
        """Get the connection settings from the dialog inputs."""
        # Parse port value
        port_text = self.port_input.text().strip()
        try:
            port_value = int(port_text) if port_text else 5432
        except ValueError:
            port_value = 5432
        
        # Build settings from current form values
        settings = {
            'host': self.host_input.text().strip() or 'localhost',
            'port': port_value,
            'database': self.database_input.text().strip() or 'university_db',
            'user': self.user_input.text().strip() or 'postgres',
            'password': self.password_input.text(),  # Keep as-is, including empty string
            'use_demo': self.use_demo_checkbox.isChecked()
        }
        
        return settings
    
    def validate_inputs(self):
        """Validate that required inputs are filled."""
        if self.use_demo_checkbox.isChecked():
            return True  # Demo mode doesn't need validation
        
        # Validate PostgreSQL connection fields
        host = self.host_input.text().strip()
        database = self.database_input.text().strip()
        user = self.user_input.text().strip()
        
        if not host:
            self._show_validation_error("Host cannot be empty.", self.host_input)
            return False
        
        if not database:
            self._show_validation_error("Database name cannot be empty.", self.database_input)
            return False
        
        if not user:
            self._show_validation_error("Username cannot be empty.", self.user_input)
            return False
        
        return True
    
    def _show_validation_error(self, message, field):
        """Show validation error with styling."""
        field.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e74c3c;
                background-color: #fadbd8;
            }
        """)
        QMessageBox.warning(self, "⚠️ Validation Error", message)
        field.setFocus()
        # Reset style after focus
        field.textChanged.connect(lambda: field.setStyleSheet(""))
    
    def test_connection(self):
        """Test the database connection with current settings (threaded)."""
        settings = self.get_connection_settings()
        
        if settings['use_demo']:
            self._update_status('success', 'Demo database will be used (always available)')
            self.last_connection_test_successful = True
            QMessageBox.information(
                self,
                "💾 Demo Mode",
                "Demo database will be used.\n\n"
                "✓ No connection test needed\n"
                "✓ Always available offline\n"
                "✓ Includes sample data"
            )
            return
        
        # Validate inputs first
        if not self.validate_inputs():
            return
        
        # Stop any existing validator thread
        if self.validator_thread and self.validator_thread.isRunning():
            self.validator_thread.terminate()
            self.validator_thread.wait()
        
        # Disable buttons during validation
        self.btn_test.setEnabled(False)
        self.btn_ok.setEnabled(False)
        self.btn_cancel.setEnabled(False)
        self.progress_bar.setVisible(True)
        self._update_status('testing', 'Testing connection...')
        
        # Create and start validation thread
        self.validator_thread = ConnectionValidatorThread(
            settings['host'],
            settings['port'],
            settings['database'],
            settings['user'],
            settings['password']
        )
        self.validator_thread.connection_success.connect(self.on_connection_success)
        self.validator_thread.connection_error.connect(self.on_connection_error)
        self.validator_thread.finished.connect(self.on_validation_finished)
        self.validator_thread.start()
    
    def _update_status(self, status_type, message):
        """Update status display with icon and message."""
        icons = {
            'success': '✅',
            'error': '❌',
            'testing': '🔄',
            'warning': '⚠️',
            'ready': '⚡'
        }
        colors = {
            'success': '#27ae60',
            'error': '#e74c3c',
            'testing': '#3498db',
            'warning': '#f39c12',
            'ready': '#7f8c8d'
        }
        
        self.status_icon.setText(icons.get(status_type, '⚡'))
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {colors.get(status_type, '#7f8c8d')}; font-size: 11px;")
    
    def on_connection_success(self, info):
        """Handle successful connection."""
        self._update_status('success', 'Connection successful!')
        self.last_connection_test_successful = True
        version = info.get('version', 'Unknown')
        has_schema = info.get('has_schema', False)
        
        message = "Successfully connected to database!\n\n"
        message += f"📊 PostgreSQL Version: {version.split(',')[0]}\n\n"
        if has_schema:
            message += "✓ Schema: All required tables found"
        else:
            message += "⚠️ Schema: Tables missing (will be created automatically)"
        
        QMessageBox.information(self, "✅ Connection Successful", message)
    
    def on_connection_error(self, error_msg):
        """Handle connection error with options."""
        self._update_status('error', f'Connection failed: {error_msg[:50]}...')
        self.last_connection_test_successful = False
        
        # Show styled error dialog
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("❌ Connection Failed")
        msg_box.setText("Could not connect to database")
        msg_box.setInformativeText(
            f"<b>Error:</b> {error_msg}<br><br>"
            f"<b>Please check:</b><br>"
            f"• PostgreSQL is running<br>"
            f"• Database exists (run create_database.py)<br>"
            f"• Credentials are correct<br>"
            f"• Firewall allows connection"
        )
        
        # Add buttons
        retry_btn = msg_box.addButton("🔄 Try Again", QMessageBox.ActionRole)
        demo_btn = msg_box.addButton("💾 Use Demo Mode", QMessageBox.ActionRole)
        cancel_btn = msg_box.addButton("Cancel", QMessageBox.RejectRole)
        
        msg_box.setDefaultButton(retry_btn)
        msg_box.exec_()
        
        if msg_box.clickedButton() == demo_btn:
            self.use_demo_checkbox.setChecked(True)
            self._update_status('success', 'Switched to demo mode')
            self.last_connection_test_successful = True
        elif msg_box.clickedButton() == retry_btn:
            self._update_status('ready', 'Ready to connect')
    
    def on_validation_finished(self):
        """Called when validation thread finishes."""
        self.btn_test.setEnabled(True)
        self.btn_ok.setEnabled(True)
        self.btn_cancel.setEnabled(True)
        self.progress_bar.setVisible(False)
    
    def accept(self):
        """Handle Connect button click."""
        # First, validate inputs
        if not self.validate_inputs():
            return
        
        # Get current settings from form
        settings = self.get_connection_settings()
        
        # Debug: Print settings to verify they're captured
        print(f"Connection settings captured:")
        print(f"  Use Demo: {settings['use_demo']}")
        print(f"  Host: {settings['host']}")
        print(f"  Port: {settings['port']}")
        print(f"  Database: {settings['database']}")
        print(f"  User: {settings['user']}")
        print(f"  Password: {'***' if settings['password'] else '(empty)'}")
        
        # Demo mode always works
        if settings['use_demo']:
            print("Demo mode selected - saving and accepting...")
            if not self.save_settings():
                QMessageBox.warning(self, "Error", "Could not save settings.")
                return
            print("Settings saved successfully")
            super().accept()
            return
        
        # For PostgreSQL, require successful test
        if not self.last_connection_test_successful:
            reply = QMessageBox.question(
                self,
                "⚠️ Connection Not Tested",
                "Connection has not been tested yet.\n\n"
                "Would you like to test it now?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                self.test_connection()
                return
            else:
                QMessageBox.warning(
                    self,
                    "Test Required",
                    "Please test your connection before proceeding.\n\n"
                    "Click 'Test Connection' to verify settings."
                )
                return
        
        # Connection was tested successfully, save and accept
        print("PostgreSQL connection tested successfully - saving and accepting...")
        if not self.save_settings():
            QMessageBox.warning(self, "Error", "Could not save settings.")
            return
        
        print("Settings saved successfully")
        super().accept()