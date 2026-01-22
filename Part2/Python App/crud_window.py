"""
CRUD Operations Window
Main window for managing CRUD operations on database tables.
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QStackedWidget, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from window_base import get_connection_from_parent, show_error


class CRUDWindow(QMainWindow):
    """Main CRUD operations window with table selector."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        try:
            self.db_connection = get_connection_from_parent(parent)
        except Exception as e:
            show_error(self, "Connection Error", 
                      f"Could not access database connection:\n{str(e)}")
            raise
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('CRUD Operations - University Database')
        self.setGeometry(50, 50, 1400, 900)
        
        # Apply modern styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
            }
            QComboBox {
                padding: 8px;
                border: 2px solid #dcdde1;
                border-radius: 5px;
                background-color: white;
                min-width: 200px;
            }
            QComboBox:focus {
                border: 2px solid #3498db;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        central_widget.setLayout(main_layout)
        
        # Header
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        header_layout = QHBoxLayout()
        header_widget.setLayout(header_layout)
        
        # Title with icon
        title = QLabel('📝 CRUD Operations')
        title.setFont(QFont('Segoe UI', 20, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Table selector
        selector_container = QHBoxLayout()
        selector_container.setSpacing(10)
        
        table_label = QLabel('Select Table:')
        table_label.setFont(QFont('Segoe UI', 11))
        table_label.setStyleSheet("color: #2c3e50;")
        selector_container.addWidget(table_label)
        
        self.table_selector = QComboBox()
        self.table_selector.addItems([
            '🏛️ Department',
            '👨‍🎓 Student', 
            '👨‍🏫 Instructor',
            '📚 Course'
        ])
        self.table_selector.setFont(QFont('Segoe UI', 10))
        self.table_selector.currentIndexChanged.connect(self.on_table_changed)
        selector_container.addWidget(self.table_selector)
        
        header_layout.addLayout(selector_container)
        
        main_layout.addWidget(header_widget)
        
        # Info label
        info_label = QLabel('💡 Select a table above to perform Create, Read, Update, and Delete operations.')
        info_label.setWordWrap(True)
        info_label.setStyleSheet("""
            padding: 12px;
            background-color: #e8f4f8;
            border-left: 4px solid #3498db;
            border-radius: 5px;
            color: #2c3e50;
            font-size: 11px;
        """)
        main_layout.addWidget(info_label)
        
        # Stacked widget for forms
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Create forms for each table
        try:
            from crud_forms import (get_department_form, get_student_form, 
                                   get_instructor_form, get_course_form)
            
            # Pass parent (self) to forms, not db_connection
            # Forms will get connection from parent via window_base
            self.forms = {
                'Department': get_department_form(parent=self),
                'Student': get_student_form(parent=self),
                'Instructor': get_instructor_form(parent=self),
                'Course': get_course_form(parent=self)
            }
            
            # Add forms to stacked widget
            for form in self.forms.values():
                self.stacked_widget.addWidget(form)
            
            # Set initial form
            self.stacked_widget.setCurrentIndex(0)
            
        except ImportError as e:
            error_widget = QWidget()
            error_layout = QVBoxLayout()
            error_widget.setLayout(error_layout)
            
            error_label = QLabel(
                f"⚠️ CRUD Forms Module Not Found\n\n"
                f"The crud_forms.py module is required for CRUD operations.\n"
                f"Error: {str(e)}"
            )
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("""
                padding: 40px;
                background-color: #fadbd8;
                color: #e74c3c;
                border-radius: 10px;
                font-size: 12px;
            """)
            error_layout.addWidget(error_label)
            
            self.stacked_widget.addWidget(error_widget)
    
    def on_table_changed(self, index):
        """Handle table selection change."""
        # Remove emoji from table name
        table_text = self.table_selector.currentText()
        table_name = table_text.split(' ', 1)[1] if ' ' in table_text else table_text
        
        if hasattr(self, 'forms') and table_name in self.forms:
            # Find the index of the form in stacked widget
            for i in range(self.stacked_widget.count()):
                if self.stacked_widget.widget(i) == self.forms[table_name]:
                    self.stacked_widget.setCurrentIndex(i)
                    break