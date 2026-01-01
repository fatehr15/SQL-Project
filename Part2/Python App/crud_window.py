"""
CRUD Operations Window
Main window for managing CRUD operations on database tables.
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QStackedWidget, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from crud_forms import get_department_form, get_student_form, get_instructor_form, get_course_form


class CRUDWindow(QMainWindow):
    """Main CRUD operations window with table selector."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('CRUD Operations - University Database')
        self.setGeometry(50, 50, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel('CRUD Operations')
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Table selector
        table_label = QLabel('Select Table:')
        table_label.setFont(QFont('Arial', 10))
        header_layout.addWidget(table_label)
        
        self.table_selector = QComboBox()
        self.table_selector.addItems(['Department', 'Student', 'Instructor', 'Course'])
        self.table_selector.setMinimumWidth(150)
        self.table_selector.currentIndexChanged.connect(self.on_table_changed)
        header_layout.addWidget(self.table_selector)
        
        main_layout.addLayout(header_layout)
        
        # Stacked widget for forms
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Create forms for each table
        self.forms = {
            'Department': get_department_form(),
            'Student': get_student_form(),
            'Instructor': get_instructor_form(),
            'Course': get_course_form()
        }
        
        # Add forms to stacked widget
        for form in self.forms.values():
            self.stacked_widget.addWidget(form)
        
        # Set initial form
        self.stacked_widget.setCurrentIndex(0)
    
    def on_table_changed(self, index):
        """Handle table selection change."""
        table_name = self.table_selector.currentText()
        if table_name in self.forms:
            # Find the index of the form in stacked widget
            for i in range(self.stacked_widget.count()):
                if self.stacked_widget.widget(i) == self.forms[table_name]:
                    self.stacked_widget.setCurrentIndex(i)
                    break

