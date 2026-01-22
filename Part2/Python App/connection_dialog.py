"""
Database Connection Dialog
Allows users to configure database connection settings.
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QPushButton, QLabel, QMessageBox,
                             QGroupBox, QCheckBox, QProgressBar, QFrame, QWidget,
                             QRadioButton, QButtonGroup, QToolButton)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QIntValidator, QIcon
import json
from pathlib import Path
from connection_validator import ConnectionValidatorThread


class InlineMessageWidget(QWidget):
    """Inline message widget for field validation feedback."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVisible(False)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(6)
        self.setLayout(layout)
        
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(16, 16)
        layout.addWidget(self.icon_label)
        
        self.text_label = QLabel()
        self.text_label.setWordWrap(True)
        self.text_label.setStyleSheet("font-size: 11px;")
        layout.addWidget(self.text_label, 1)
    
    def show_message(self, message, msg_type="error"):
        """Show inline message with icon and styling."""
        colors = {
            'error': '#DC2626',
            'success': '#059669',
            'warning': '#D97706',
            'info': '#2563EB'
        }
        
        icons = {
            'error': '✕',
            'success': '✓',
            'warning': '!',
            'info': 'i'
        }
        
        self.icon_label.setText(icons.get(msg_type, 'i'))
        self.icon_label.setStyleSheet(f"color: {colors.get(msg_type, '#6E7781')}; font-weight: bold;")
        self.text_label.setText(message)
        self.text_label.setStyleSheet(f"color: {colors.get(msg_type, '#6E7781')}; font-size: 11px;")
        self.setVisible(True)
    
    def hide_message(self):
        """Hide the inline message."""
        self.setVisible(False)


class ConnectionDialog(QDialog):
    """Professional dialog for configuring database connection settings."""
    
    CONFIG_FILE = Path(__file__).parent / "db_config.json"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Database Connection Settings')
        self.setMinimumWidth(560)
        self.setMaximumWidth(680)
        self.setModal(True)
        
        self.connection_settings = {}
        self.load_saved_settings()
        self.validator_thread = None
        self.last_connection_test_successful = False
        self.password_visible = False
        
        # Modern, professional styling
        self.setStyleSheet("""
            QDialog {
                background-color: #F8F9FA;
            }
            QGroupBox {
                font-weight: 600;
                font-size: 13px;
                border: 1px solid #E1E4E8;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 16px;
                background-color: #FFFFFF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
                color: #1A1D23;
            }
            QLabel {
                color: #24292E;
            }
            QLineEdit {
                padding: 10px 12px;
                border: 1px solid #D0D7DE;
                border-radius: 6px;
                background-color: #FFFFFF;
                font-size: 13px;
                color: #24292E;
            }
            QLineEdit:focus {
                border: 2px solid #2563EB;
                padding: 9px 11px;
            }
            QLineEdit:disabled {
                background-color: #F6F8FA;
                color: #57606A;
            }
            QRadioButton {
                spacing: 8px;
                font-size: 13px;
                color: #24292E;
                padding: 8px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid #D0D7DE;
                background-color: #FFFFFF;
            }
            QRadioButton::indicator:checked {
                background-color: #2563EB;
                border: 2px solid #2563EB;
            }
            QRadioButton::indicator:checked::after {
                content: '';
                width: 8px;
                height: 8px;
                border-radius: 4px;
                background-color: #FFFFFF;
                position: absolute;
                left: 5px;
                top: 5px;
            }
            QPushButton {
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                font-size: 13px;
                min-height: 36px;
            }
            QPushButton:hover {
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                transform: translateY(0px);
            }
            QPushButton:disabled {
                background-color: #E1E4E8;
                color: #89929B;
            }
            QProgressBar {
                border: 1px solid #E1E4E8;
                border-radius: 4px;
                text-align: center;
                background-color: #F6F8FA;
                height: 6px;
            }
            QProgressBar::chunk {
                background-color: #2563EB;
                border-radius: 3px;
            }
        """)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the professional user interface."""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(32, 32, 32, 32)
        self.setLayout(layout)
        
        # Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(6)
        
        title = QLabel('Database Connection')
        title.setFont(QFont('Segoe UI', 20, QFont.Bold))
        title.setStyleSheet("color: #1A1D23;")
        header_layout.addWidget(title)
        
        subtitle = QLabel('Choose your connection type and configure settings')
        subtitle.setFont(QFont('Segoe UI', 13))
        subtitle.setStyleSheet("color: #57606A;")
        header_layout.addWidget(subtitle)
        
        layout.addLayout(header_layout)
        
        # Connection Type Selection (Radio buttons)
        type_group = QGroupBox('Connection Type')
        type_layout = QVBoxLayout()
        type_layout.setSpacing(8)
        type_layout.setContentsMargins(16, 20, 16, 16)
        type_group.setLayout(type_layout)
        
        self.connection_type_group = QButtonGroup()
        
        # PostgreSQL option
        self.radio_postgresql = QRadioButton('PostgreSQL Database')
        self.radio_postgresql.setToolTip('Connect to a PostgreSQL server')
        postgres_desc = QLabel('Production-ready database with full features')
        postgres_desc.setStyleSheet("color: #57606A; font-size: 12px; margin-left: 26px;")
        type_layout.addWidget(self.radio_postgresql)
        type_layout.addWidget(postgres_desc)
        
        type_layout.addSpacing(8)
        
        # Demo/SQLite option
        self.radio_demo = QRadioButton('Demo Mode (SQLite)')
        self.radio_demo.setToolTip('Use local SQLite database with sample data')
        demo_desc = QLabel('Offline mode with sample data • Perfect for testing')
        demo_desc.setStyleSheet("color: #57606A; font-size: 12px; margin-left: 26px;")
        type_layout.addWidget(self.radio_demo)
        type_layout.addWidget(demo_desc)
        
        self.connection_type_group.addButton(self.radio_postgresql, 0)
        self.connection_type_group.addButton(self.radio_demo, 1)
        
        # Set initial selection based on saved settings
        if self.connection_settings.get('use_demo', False):
            self.radio_demo.setChecked(True)
        else:
            self.radio_postgresql.setChecked(True)
        
        self.connection_type_group.buttonClicked.connect(self.on_connection_type_changed)
        
        layout.addWidget(type_group)
        
        # PostgreSQL Connection Settings
        self.pg_group = QGroupBox('PostgreSQL Settings')
        pg_layout = QFormLayout()
        pg_layout.setSpacing(12)
        pg_layout.setContentsMargins(16, 20, 16, 16)
        pg_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        self.pg_group.setLayout(pg_layout)
        
        # Host field with inline validation
        host_container = QWidget()
        host_container_layout = QVBoxLayout()
        host_container_layout.setContentsMargins(0, 0, 0, 0)
        host_container_layout.setSpacing(0)
        host_container.setLayout(host_container_layout)
        
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText('localhost or IP address')
        self.host_input.setText(self.connection_settings.get('host', 'localhost'))
        self.host_input.textChanged.connect(lambda: self.host_message.hide_message())
        host_container_layout.addWidget(self.host_input)
        
        self.host_message = InlineMessageWidget()
        host_container_layout.addWidget(self.host_message)
        
        pg_layout.addRow('Host:', host_container)
        
        # Port field
        port_container = QWidget()
        port_container_layout = QVBoxLayout()
        port_container_layout.setContentsMargins(0, 0, 0, 0)
        port_container_layout.setSpacing(0)
        port_container.setLayout(port_container_layout)
        
        self.port_input = QLineEdit()
        self.port_input.setValidator(QIntValidator(1, 65535))
        self.port_input.setText(str(self.connection_settings.get('port', 5432)))
        self.port_input.setPlaceholderText('5432')
        self.port_input.textChanged.connect(lambda: self.port_message.hide_message())
        port_container_layout.addWidget(self.port_input)
        
        self.port_message = InlineMessageWidget()
        port_container_layout.addWidget(self.port_message)
        
        pg_layout.addRow('Port:', port_container)
        
        # Database field
        db_container = QWidget()
        db_container_layout = QVBoxLayout()
        db_container_layout.setContentsMargins(0, 0, 0, 0)
        db_container_layout.setSpacing(0)
        db_container.setLayout(db_container_layout)
        
        self.database_input = QLineEdit()
        self.database_input.setPlaceholderText('university_db')
        self.database_input.setText(self.connection_settings.get('database', 'university_db'))
        self.database_input.textChanged.connect(lambda: self.db_message.hide_message())
        db_container_layout.addWidget(self.database_input)
        
        self.db_message = InlineMessageWidget()
        db_container_layout.addWidget(self.db_message)
        
        pg_layout.addRow('Database:', db_container)
        
        # Username field
        user_container = QWidget()
        user_container_layout = QVBoxLayout()
        user_container_layout.setContentsMargins(0, 0, 0, 0)
        user_container_layout.setSpacing(0)
        user_container.setLayout(user_container_layout)
        
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText('postgres')
        self.user_input.setText(self.connection_settings.get('user', 'postgres'))
        self.user_input.textChanged.connect(lambda: self.user_message.hide_message())
        user_container_layout.addWidget(self.user_input)
        
        self.user_message = InlineMessageWidget()
        user_container_layout.addWidget(self.user_message)
        
        pg_layout.addRow('Username:', user_container)
        
        # Password field with toggle visibility
        password_container = QWidget()
        password_container_layout = QVBoxLayout()
        password_container_layout.setContentsMargins(0, 0, 0, 0)
        password_container_layout.setSpacing(0)
        password_container.setLayout(password_container_layout)
        
        password_input_row = QWidget()
        password_input_layout = QHBoxLayout()
        password_input_layout.setContentsMargins(0, 0, 0, 0)
        password_input_layout.setSpacing(4)
        password_input_row.setLayout(password_input_layout)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText('Enter password')
        saved_password = self.connection_settings.get('password', '')
        if saved_password:
            self.password_input.setText(saved_password)
        password_input_layout.addWidget(self.password_input)
        
        # Toggle password visibility button
        self.toggle_password_btn = QToolButton()
        self.toggle_password_btn.setText('👁')
        self.toggle_password_btn.setFixedSize(36, 36)
        self.toggle_password_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_password_btn.setStyleSheet("""
            QToolButton {
                background-color: #F6F8FA;
                border: 1px solid #D0D7DE;
                border-radius: 6px;
                font-size: 16px;
            }
            QToolButton:hover {
                background-color: #EAEEF2;
            }
            QToolButton:pressed {
                background-color: #DDE2E8;
            }
        """)
        self.toggle_password_btn.clicked.connect(self.toggle_password_visibility)
        password_input_layout.addWidget(self.toggle_password_btn)
        
        password_container_layout.addWidget(password_input_row)
        
        self.password_message = InlineMessageWidget()
        password_container_layout.addWidget(self.password_message)
        
        pg_layout.addRow('Password:', password_container)
        
        layout.addWidget(self.pg_group)
        
        # Connection Status Panel
        self.status_panel = QFrame()
        self.status_panel.setStyleSheet("""
            QFrame {
                background-color: #F6F8FA;
                border: 1px solid #D0D7DE;
                border-radius: 8px;
            }
        """)
        status_layout = QVBoxLayout()
        status_layout.setContentsMargins(16, 12, 16, 12)
        status_layout.setSpacing(8)
        self.status_panel.setLayout(status_layout)
        
        # Status message
        status_row = QHBoxLayout()
        status_row.setSpacing(8)
        
        self.status_icon = QLabel('○')
        self.status_icon.setFont(QFont('Segoe UI', 16))
        self.status_icon.setStyleSheet("color: #57606A;")
        status_row.addWidget(self.status_icon)
        
        self.status_label = QLabel('Ready to connect')
        self.status_label.setFont(QFont('Segoe UI', 12))
        self.status_label.setStyleSheet("color: #24292E;")
        status_row.addWidget(self.status_label, 1)
        
        status_layout.addLayout(status_row)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumHeight(6)
        status_layout.addWidget(self.progress_bar)
        
        layout.addWidget(self.status_panel)
        
        # Action Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        # Test Connection button
        self.btn_test = QPushButton('Test Connection')
        self.btn_test.setCursor(Qt.PointingHandCursor)
        self.btn_test.clicked.connect(self.test_connection)
        self.btn_test.setStyleSheet("""
            QPushButton {
                background-color: #F6F8FA;
                color: #24292E;
                border: 1px solid #D0D7DE;
            }
            QPushButton:hover {
                background-color: #EAEEF2;
                border-color: #1F2328;
            }
            QPushButton:pressed {
                background-color: #DDE2E8;
            }
        """)
        button_layout.addWidget(self.btn_test)
        
        button_layout.addStretch()
        
        # Cancel button
        self.btn_cancel = QPushButton('Cancel')
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #F6F8FA;
                color: #24292E;
                border: 1px solid #D0D7DE;
            }
            QPushButton:hover {
                background-color: #EAEEF2;
                border-color: #1F2328;
            }
        """)
        button_layout.addWidget(self.btn_cancel)
        
        # Connect button (primary action)
        self.btn_ok = QPushButton('Connect')
        self.btn_ok.setCursor(Qt.PointingHandCursor)
        self.btn_ok.clicked.connect(self.accept)
        self.btn_ok.setDefault(True)
        self.btn_ok.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: #FFFFFF;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
            QPushButton:pressed {
                background-color: #1E40AF;
            }
        """)
        button_layout.addWidget(self.btn_ok)
        
        layout.addLayout(button_layout)
        
        # Initialize UI state
        self.on_connection_type_changed()
    
    def toggle_password_visibility(self):
        """Toggle password field visibility."""
        if self.password_visible:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_password_btn.setText('👁')
            self.password_visible = False
        else:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_password_btn.setText('👁‍🗨')
            self.password_visible = True
    
    def on_connection_type_changed(self):
        """Handle connection type selection change."""
        is_demo = self.radio_demo.isChecked()
        
        # Enable/disable PostgreSQL fields
        self.pg_group.setEnabled(not is_demo)
        self.host_input.setEnabled(not is_demo)
        self.port_input.setEnabled(not is_demo)
        self.database_input.setEnabled(not is_demo)
        self.user_input.setEnabled(not is_demo)
        self.password_input.setEnabled(not is_demo)
        self.toggle_password_btn.setEnabled(not is_demo)
        
        # Update test button and status
        if is_demo:
            self.btn_test.setEnabled(False)
            self.btn_test.setText('Test Connection')
            self._update_status('success', 'Demo mode - no connection required')
            self.last_connection_test_successful = True
        else:
            self.btn_test.setEnabled(True)
            self.btn_test.setText('Test Connection')
            self._update_status('ready', 'Ready to connect')
            self.last_connection_test_successful = False
    
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
            port_text = self.port_input.text().strip()
            try:
                port_value = int(port_text) if port_text else 5432
            except ValueError:
                port_value = 5432
            
            settings = {
                'host': self.host_input.text().strip() or 'localhost',
                'port': port_value,
                'database': self.database_input.text().strip() or 'university_db',
                'user': self.user_input.text().strip() or 'postgres',
                'password': self.password_input.text(),
                'use_demo': self.radio_demo.isChecked()
            }
            
            self.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(settings, f, indent=2)
            
            self.connection_settings = settings
            return True
            
        except Exception as e:
            print(f"Error saving settings: {e}")
            QMessageBox.warning(self, "Save Error", f"Could not save settings: {e}")
            return False
    
    def get_connection_settings(self):
        """Get the connection settings from the dialog inputs."""
        port_text = self.port_input.text().strip()
        try:
            port_value = int(port_text) if port_text else 5432
        except ValueError:
            port_value = 5432
        
        settings = {
            'host': self.host_input.text().strip() or 'localhost',
            'port': port_value,
            'database': self.database_input.text().strip() or 'university_db',
            'user': self.user_input.text().strip() or 'postgres',
            'password': self.password_input.text(),
            'use_demo': self.radio_demo.isChecked()
        }
        
        return settings
    
    def validate_inputs(self):
        """Validate inputs with inline feedback."""
        if self.radio_demo.isChecked():
            return True
        
        is_valid = True
        
        # Validate host
        host = self.host_input.text().strip()
        if not host:
            self.host_message.show_message("Host is required", "error")
            is_valid = False
        
        # Validate port
        port_text = self.port_input.text().strip()
        if not port_text:
            self.port_message.show_message("Port is required", "error")
            is_valid = False
        else:
            try:
                port = int(port_text)
                if port < 1 or port > 65535:
                    self.port_message.show_message("Port must be between 1 and 65535", "error")
                    is_valid = False
            except ValueError:
                self.port_message.show_message("Port must be a number", "error")
                is_valid = False
        
        # Validate database
        database = self.database_input.text().strip()
        if not database:
            self.db_message.show_message("Database name is required", "error")
            is_valid = False
        
        # Validate username
        user = self.user_input.text().strip()
        if not user:
            self.user_message.show_message("Username is required", "error")
            is_valid = False
        
        return is_valid
    
    def test_connection(self):
        """Test the database connection with visual feedback."""
        settings = self.get_connection_settings()
        
        if settings['use_demo']:
            self._update_status('success', 'Demo database - always available')
            self.last_connection_test_successful = True
            self._show_success_toast('Demo Mode', 'Demo database is ready to use')
            return
        
        if not self.validate_inputs():
            return
        
        # Stop existing thread
        if self.validator_thread and self.validator_thread.isRunning():
            self.validator_thread.terminate()
            self.validator_thread.wait()
        
        # Disable UI during test
        self.btn_test.setEnabled(False)
        self.btn_ok.setEnabled(False)
        self.btn_cancel.setEnabled(False)
        self.progress_bar.setVisible(True)
        self._update_status('testing', 'Testing connection...')
        
        # Start validation
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
        """Update status display with modern styling."""
        icons = {
            'success': '✓',
            'error': '✕',
            'testing': '○',
            'ready': '○'
        }
        colors = {
            'success': '#059669',
            'error': '#DC2626',
            'testing': '#2563EB',
            'ready': '#57606A'
        }
        
        self.status_icon.setText(icons.get(status_type, '○'))
        self.status_icon.setStyleSheet(f"color: {colors.get(status_type, '#57606A')};")
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {colors.get(status_type, '#24292E')};")
    
    def _show_success_toast(self, title, message):
        """Show success message."""
        QMessageBox.information(self, title, message)
    
    def on_connection_success(self, info):
        """Handle successful connection."""
        self._update_status('success', 'Connection successful!')
        self.last_connection_test_successful = True
        
        version = info.get('version', 'Unknown')
        has_schema = info.get('has_schema', False)
        
        message = f"Successfully connected to database\n\n"
        message += f"PostgreSQL Version: {version.split(',')[0]}\n"
        message += f"Schema Status: {'Ready' if has_schema else 'Will be created'}"
        
        QMessageBox.information(self, "Connection Successful", message)
    
    def on_connection_error(self, error_msg):
        """Handle connection error with helpful feedback."""
        self._update_status('error', 'Connection failed')
        self.last_connection_test_successful = False
        
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Connection Failed")
        msg_box.setText("Could not connect to the database")
        msg_box.setInformativeText(
            f"Error: {error_msg}\n\n"
            f"Common solutions:\n"
            f"• Verify PostgreSQL is running\n"
            f"• Check host and port are correct\n"
            f"• Ensure database exists\n"
            f"• Verify credentials\n"
            f"• Check firewall settings"
        )
        
        demo_btn = msg_box.addButton("Use Demo Mode", QMessageBox.ActionRole)
        retry_btn = msg_box.addButton("Retry", QMessageBox.ActionRole)
        cancel_btn = msg_box.addButton("Cancel", QMessageBox.RejectRole)
        
        msg_box.exec_()
        
        if msg_box.clickedButton() == demo_btn:
            self.radio_demo.setChecked(True)
            self.on_connection_type_changed()
    
    def on_validation_finished(self):
        """Re-enable UI after validation."""
        self.btn_test.setEnabled(not self.radio_demo.isChecked())
        self.btn_ok.setEnabled(True)
        self.btn_cancel.setEnabled(True)
        self.progress_bar.setVisible(False)
    
    def accept(self):
        """Handle Connect button with validation."""
        if not self.validate_inputs():
            return
        
        settings = self.get_connection_settings()
        
        # Demo mode is always ready
        if settings['use_demo']:
            if not self.save_settings():
                QMessageBox.warning(self, "Error", "Could not save settings.")
                return
            super().accept()
            return
        
        # PostgreSQL requires successful test
        if not self.last_connection_test_successful:
            reply = QMessageBox.question(
                self,
                "Connection Not Tested",
                "The connection has not been tested yet.\n\n"
                "Would you like to test it now?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                self.test_connection()
                return
            else:
                return
        
        # Save and accept
        if not self.save_settings():
            QMessageBox.warning(self, "Error", "Could not save settings.")
            return
        
        super().accept()
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts."""
        # Escape key closes dialog
        if event.key() == Qt.Key_Escape:
            self.reject()
        # Enter/Return on focused button triggers it
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if self.btn_ok.hasFocus():
                self.accept()
            elif self.btn_test.hasFocus():
                self.test_connection()
            elif self.btn_cancel.hasFocus():
                self.reject()
        else:
            super().keyPressEvent(event)