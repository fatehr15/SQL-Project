"""
Database Connection Dialog
Allows users to configure database connection settings.
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QPushButton, QLabel, QMessageBox,
                             QGroupBox, QCheckBox, QSpinBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import os
import json
from pathlib import Path


class ConnectionDialog(QDialog):
    """Dialog for configuring database connection settings."""
    
    CONFIG_FILE = Path(__file__).parent / "db_config.json"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Database Connection Settings')
        self.setGeometry(200, 200, 500, 400)
        self.setModal(True)
        
        self.connection_settings = {}
        self.load_saved_settings()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title
        title = QLabel('Database Connection Configuration')
        title_font = QFont('Arial', 14, QFont.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # PostgreSQL Connection Group
        pg_group = QGroupBox('PostgreSQL Connection')
        pg_layout = QFormLayout()
        pg_group.setLayout(pg_layout)
        
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText('localhost')
        self.host_input.setText(self.connection_settings.get('host', 'localhost'))
        pg_layout.addRow('Host:', self.host_input)
        
        self.port_input = QSpinBox()
        self.port_input.setMinimum(1)
        self.port_input.setMaximum(65535)
        self.port_input.setValue(self.connection_settings.get('port', 5432))
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
        # Don't show saved password for security, but allow user to enter it
        pg_layout.addRow('Password:', self.password_input)
        
        layout.addWidget(pg_group)
        
        # Demo Database Option
        demo_group = QGroupBox('Demo Mode')
        demo_layout = QVBoxLayout()
        demo_group.setLayout(demo_layout)
        
        self.use_demo_checkbox = QCheckBox('Use Demo Database (SQLite - Always Available)')
        self.use_demo_checkbox.setChecked(self.connection_settings.get('use_demo', False))
        self.use_demo_checkbox.setToolTip('Use a local SQLite database with sample data. No PostgreSQL required.')
        demo_layout.addWidget(self.use_demo_checkbox)
        
        demo_info = QLabel('The demo database includes sample data and works without PostgreSQL setup.')
        demo_info.setWordWrap(True)
        demo_info.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        demo_layout.addWidget(demo_info)
        
        layout.addWidget(demo_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.btn_test = QPushButton('Test Connection')
        self.btn_test.clicked.connect(self.test_connection)
        self.btn_test.setStyleSheet("background-color: #3498db; color: white; padding: 8px;")
        button_layout.addWidget(self.btn_test)
        
        button_layout.addStretch()
        
        self.btn_cancel = QPushButton('Cancel')
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_cancel.setStyleSheet("padding: 8px;")
        button_layout.addWidget(self.btn_cancel)
        
        self.btn_ok = QPushButton('Connect')
        self.btn_ok.clicked.connect(self.accept)
        self.btn_ok.setStyleSheet("background-color: #27ae60; color: white; padding: 8px; font-weight: bold;")
        button_layout.addWidget(self.btn_ok)
        
        layout.addLayout(button_layout)
    
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
        settings = {
            'host': self.host_input.text() or 'localhost',
            'port': self.port_input.value(),
            'database': self.database_input.text() or 'university_db',
            'user': self.user_input.text() or 'postgres',
            'use_demo': self.use_demo_checkbox.isChecked()
        }
        # Only save password if it was entered (not empty)
        password = self.password_input.text()
        if password:
            settings['password'] = password
        
        try:
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(settings, f, indent=2)
            self.connection_settings = settings
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Could not save settings: {e}")
    
    def get_connection_settings(self):
        """Get the connection settings from the dialog."""
        return {
            'host': self.host_input.text() or 'localhost',
            'port': self.port_input.value(),
            'database': self.database_input.text() or 'university_db',
            'user': self.user_input.text() or 'postgres',
            'password': self.password_input.text(),
            'use_demo': self.use_demo_checkbox.isChecked()
        }
    
    def test_connection(self):
        """Test the database connection with current settings."""
        settings = self.get_connection_settings()
        
        if settings['use_demo']:
            QMessageBox.information(
                self, 
                "Connection Test", 
                "Demo database will be used. No connection test needed.\n"
                "The demo database is always available."
            )
            return
        
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=settings['host'],
                port=settings['port'],
                database=settings['database'],
                user=settings['user'],
                password=settings['password'] if settings['password'] else None
            )
            conn.close()
            QMessageBox.information(
                self, 
                "Connection Successful", 
                f"Successfully connected to:\n"
                f"Host: {settings['host']}\n"
                f"Port: {settings['port']}\n"
                f"Database: {settings['database']}\n"
                f"User: {settings['user']}"
            )
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Connection Failed", 
                f"Could not connect to database:\n\n{str(e)}\n\n"
                f"Please check:\n"
                f"1. PostgreSQL is running\n"
                f"2. Database '{settings['database']}' exists\n"
                f"3. Credentials are correct\n\n"
                f"You can use the Demo Database option to try the app without PostgreSQL."
            )
    
    def accept(self):
        """Handle OK button click."""
        self.save_settings()
        super().accept()

