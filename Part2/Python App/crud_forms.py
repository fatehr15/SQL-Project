"""
CRUD Forms Module
Generic and specific forms for database table operations.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                             QComboBox, QDateEdit, QMessageBox, QGroupBox, QFormLayout,
                             QTextEdit, QHeaderView)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from window_base import get_connection_from_parent, show_error, show_info, show_warning, show_question


class GenericCRUDForm(QWidget):
    """Generic CRUD form widget that can be configured for different tables."""
    
    def __init__(self, table_name=None, columns_config=None, parent=None):
        """
        Initialize generic CRUD form.
        
        Args:
            table_name: Name of the database table
            columns_config: List of dicts with column configuration
            parent: Parent widget (MainWindow or CRUDWindow)
        """
        super().__init__(parent)
        self.table_name = table_name or 'Generic'
        self.columns_config = columns_config or []
        
        # Get connection from parent
        try:
            self.db_connection = get_connection_from_parent(parent)
        except Exception as e:
            show_error(self, "Connection Error", str(e))
            raise
        
        # Store current record's primary key values
        self.current_pk_values = {}
        self.init_ui()
        
        # Only load data if we have a primary key defined
        try:
            if self.columns_config and self.get_primary_key_columns():
                self.load_data()
        except Exception as e:
            print(f"Note: Could not load data: {e}")
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        self.setLayout(layout)
        
        # Title
        title = QLabel(f'📋 {self.table_name} Management')
        title.setFont(QFont('Segoe UI', 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; padding: 10px;")
        layout.addWidget(title)
        
        # Form group
        form_group = QGroupBox('Data Entry')
        form_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dcdde1;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
        """)
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_group.setLayout(form_layout)
        
        self.input_fields = {}
        for col in self.columns_config:
            label = col['label']
            field_name = col['name']
            field_type = col.get('type', 'text')
            required = col.get('required', False)
            
            if field_type == 'combo':
                widget = QComboBox()
                widget.setEditable(False)
                if 'fk_table' in col and 'fk_display' in col:
                    self.populate_combo(widget, col['fk_table'], col['fk_display'], col.get('fk_value', 'id'))
                elif 'combo_values' in col:
                    widget.addItem('-- Select --', None)
                    for value in col['combo_values']:
                        widget.addItem(str(value), value)
            elif field_type == 'date':
                widget = QDateEdit()
                widget.setCalendarPopup(True)
                widget.setDate(QDate.currentDate())
                widget.setDisplayFormat('yyyy-MM-dd')
            elif field_type == 'text_area':
                widget = QTextEdit()
                widget.setMaximumHeight(80)
            else:
                widget = QLineEdit()
                widget.setStyleSheet("padding: 8px; border: 2px solid #dcdde1; border-radius: 5px;")
            
            if required:
                label += ' *'
            
            form_layout.addRow(label, widget)
            self.input_fields[field_name] = {
                'widget': widget,
                'type': field_type,
                'required': required,
                'pk': col.get('pk', False),
                'config': col
            }
        
        layout.addWidget(form_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.btn_create = QPushButton('➕ Create')
        self.btn_create.clicked.connect(self.create_record)
        self.btn_create.setStyleSheet("background-color: #27ae60; color: white; padding: 10px 20px; border-radius: 6px; font-weight: bold;")
        
        self.btn_update = QPushButton('✏️ Update')
        self.btn_update.clicked.connect(self.update_record)
        self.btn_update.setStyleSheet("background-color: #f39c12; color: white; padding: 10px 20px; border-radius: 6px; font-weight: bold;")
        self.btn_update.setEnabled(False)
        
        self.btn_delete = QPushButton('🗑️ Delete')
        self.btn_delete.clicked.connect(self.delete_record)
        self.btn_delete.setStyleSheet("background-color: #e74c3c; color: white; padding: 10px 20px; border-radius: 6px; font-weight: bold;")
        self.btn_delete.setEnabled(False)
        
        self.btn_clear = QPushButton('🔄 Clear')
        self.btn_clear.clicked.connect(self.clear_form)
        self.btn_clear.setStyleSheet("background-color: #95a5a6; color: white; padding: 10px 20px; border-radius: 6px; font-weight: bold;")
        
        self.btn_refresh = QPushButton('🔃 Refresh')
        self.btn_refresh.clicked.connect(self.load_data)
        self.btn_refresh.setStyleSheet("background-color: #3498db; color: white; padding: 10px 20px; border-radius: 6px; font-weight: bold;")
        
        button_layout.addWidget(self.btn_create)
        button_layout.addWidget(self.btn_update)
        button_layout.addWidget(self.btn_delete)
        button_layout.addWidget(self.btn_clear)
        button_layout.addWidget(self.btn_refresh)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Data table
        table_label = QLabel(f'📊 {self.table_name} Records')
        table_label.setFont(QFont('Segoe UI', 12, QFont.Bold))
        table_label.setStyleSheet("color: #2c3e50; padding: 5px;")
        layout.addWidget(table_label)
        
        self.data_table = QTableWidget()
        self.data_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.data_table.setSelectionMode(QTableWidget.SingleSelection)
        self.data_table.itemSelectionChanged.connect(self.on_row_selected)
        self.data_table.horizontalHeader().setStretchLastSection(True)
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.data_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #dcdde1;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.data_table)
    
    def populate_combo(self, combo, table, display_col, value_col):
        """Populate combo box from foreign key table."""
        try:
            query = f'SELECT {value_col}, {display_col} FROM {table} ORDER BY {display_col}'
            cursor = self.db_connection.get_cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            combo.clear()
            combo.addItem('-- Select --', None)
            for row in results:
                combo.addItem(str(row[1]), row[0])
        except Exception as e:
            show_warning(self, 'Error', f'Failed to load {table}:\n{str(e)}')
    
    def get_field_value(self, field_name):
        """Get value from input field."""
        field = self.input_fields[field_name]
        widget = field['widget']
        field_type = field['type']
        
        if field_type == 'combo':
            return widget.currentData()
        elif field_type == 'date':
            return widget.date().toString('yyyy-MM-dd')
        elif field_type == 'text_area':
            return widget.toPlainText().strip()
        else:
            return widget.text().strip()
    
    def set_field_value(self, field_name, value):
        """Set value in input field."""
        field = self.input_fields[field_name]
        widget = field['widget']
        field_type = field['type']
        
        if field_type == 'combo':
            if value is not None and value != '':
                # Try to find by data value
                for i in range(widget.count()):
                    item_data = widget.itemData(i)
                    if item_data is not None:
                        # Compare as strings to handle type mismatches
                        if str(item_data) == str(value):
                            widget.setCurrentIndex(i)
                            return
            widget.setCurrentIndex(0)
        elif field_type == 'date':
            if value and str(value) != 'None' and str(value) != '':
                date = QDate.fromString(str(value), 'yyyy-MM-dd')
                if date.isValid():
                    widget.setDate(date)
        elif field_type == 'text_area':
            widget.setPlainText(str(value) if value is not None else '')
        else:
            widget.setText(str(value) if value is not None else '')
    
    def validate_form(self):
        """Validate form inputs."""
        for field_name, field in self.input_fields.items():
            if field['required']:
                value = self.get_field_value(field_name)
                # Check for None, empty string, or empty after strip
                if value is None or value == '' or (isinstance(value, str) and not value.strip()):
                    show_warning(self, 'Validation', f'{field["config"]["label"]} is required')
                    return False
        return True
    
    def clear_form(self):
        """Clear all input fields."""
        for field_name, field in self.input_fields.items():
            if field['type'] == 'combo':
                field['widget'].setCurrentIndex(0)
            elif field['type'] == 'date':
                field['widget'].setDate(QDate.currentDate())
            elif field['type'] == 'text_area':
                field['widget'].clear()
            else:
                field['widget'].clear()
        
        self.current_pk_values = {}
        self.btn_update.setEnabled(False)
        self.btn_delete.setEnabled(False)
        self.btn_create.setEnabled(True)
        
        # Clear table selection
        self.data_table.clearSelection()
    
    def get_primary_key_columns(self):
        """Get primary key column names."""
        return [col['name'] for col in self.columns_config if col.get('pk', False)]
    
    def create_record(self):
        """Create a new record."""
        if not self.validate_form():
            return
        
        try:
            columns = []
            values = []
            placeholders = []
            
            for col in self.columns_config:
                value = self.get_field_value(col['name'])
                
                # Skip auto-increment PKs that are empty
                if col.get('pk', False) and (value is None or value == ''):
                    continue
                
                # Skip empty optional fields
                if not col.get('required', False) and (value is None or value == ''):
                    continue
                
                columns.append(col['name'])
                values.append(value)
                placeholders.append('%s')
            
            query = f"INSERT INTO {self.table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
            
            cursor = self.db_connection.get_cursor()
            cursor.execute(query, values)
            self.db_connection.commit()
            
            show_info(self, 'Success', 'Record created successfully!')
            self.clear_form()
            self.load_data()
        except Exception as e:
            self.db_connection.rollback()
            show_error(self, 'Error', f'Failed to create record:\n{str(e)}')
    
    def update_record(self):
        """Update selected record."""
        # Debug: Print current PK values
        print(f"DEBUG - Update called. PK values: {self.current_pk_values}")
        
        if not self.current_pk_values:
            show_warning(self, 'Error', 'No record selected. Please select a record from the table first.')
            return
        
        if not self.validate_form():
            return
        
        try:
            pk_columns = self.get_primary_key_columns()
            
            # Verify we have all PK values
            missing_pks = [pk for pk in pk_columns if pk not in self.current_pk_values]
            if missing_pks:
                show_warning(self, 'Error', f'Missing primary key values: {", ".join(missing_pks)}')
                return
            
            set_clauses = []
            values = []
            
            # Build SET clause for non-PK columns
            for col in self.columns_config:
                if not col.get('pk', False):
                    set_clauses.append(f"{col['name']} = %s")
                    value = self.get_field_value(col['name'])
                    if value == '' and not col.get('required', False):
                        value = None
                    values.append(value)
            
            # Build WHERE clause using stored PK values
            where_clauses = []
            for pk_col in pk_columns:
                where_clauses.append(f"{pk_col} = %s")
                values.append(self.current_pk_values[pk_col])
            
            query = f"UPDATE {self.table_name} SET {', '.join(set_clauses)} WHERE {' AND '.join(where_clauses)}"
            print(f"DEBUG - Update query: {query}")
            print(f"DEBUG - Update values: {values}")
            
            cursor = self.db_connection.get_cursor()
            cursor.execute(query, values)
            self.db_connection.commit()
            
            show_info(self, 'Success', 'Record updated successfully!')
            self.clear_form()
            self.load_data()
        except Exception as e:
            self.db_connection.rollback()
            show_error(self, 'Error', f'Failed to update:\n{str(e)}')
    
    def delete_record(self):
        """Delete selected record."""
        # Debug: Print current PK values
        print(f"DEBUG - Delete called. PK values: {self.current_pk_values}")
        
        if not self.current_pk_values:
            show_warning(self, 'Error', 'No record selected. Please select a record from the table first.')
            return
        
        if not show_question(self, 'Confirm', 'Are you sure you want to delete this record?'):
            return
        
        try:
            pk_columns = self.get_primary_key_columns()
            
            # Verify we have all PK values
            missing_pks = [pk for pk in pk_columns if pk not in self.current_pk_values]
            if missing_pks:
                show_warning(self, 'Error', f'Missing primary key values: {", ".join(missing_pks)}')
                return
            
            where_clauses = []
            values = []
            
            # Build WHERE clause using stored PK values
            for pk_col in pk_columns:
                where_clauses.append(f"{pk_col} = %s")
                values.append(self.current_pk_values[pk_col])
            
            query = f"DELETE FROM {self.table_name} WHERE {' AND '.join(where_clauses)}"
            print(f"DEBUG - Delete query: {query}")
            print(f"DEBUG - Delete values: {values}")
            
            cursor = self.db_connection.get_cursor()
            cursor.execute(query, values)
            self.db_connection.commit()
            
            show_info(self, 'Success', 'Record deleted successfully!')
            self.clear_form()
            self.load_data()
        except Exception as e:
            self.db_connection.rollback()
            show_error(self, 'Error', f'Failed to delete:\n{str(e)}\n\nThis record may be referenced by other tables.')
    
    def load_data(self):
        """Load and display data in table."""
        try:
            pk_columns = self.get_primary_key_columns()
            if not pk_columns:
                show_warning(self, 'Error', 'No primary key defined')
                return
            
            query = f"SELECT * FROM {self.table_name} ORDER BY {', '.join(pk_columns)}"
            cursor = self.db_connection.get_cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            
            # Get column names from cursor description
            if cursor.description:
                column_names = [desc[0] for desc in cursor.description]
                print(f"DEBUG - Table columns from DB: {column_names}")
            else:
                column_names = [col['name'] for col in self.columns_config]
                print(f"DEBUG - Table columns from config: {column_names}")
            
            self.data_table.setRowCount(len(results))
            self.data_table.setColumnCount(len(column_names))
            self.data_table.setHorizontalHeaderLabels(column_names)
            
            for row_idx, row in enumerate(results):
                for col_idx, value in enumerate(row):
                    item = QTableWidgetItem(str(value) if value is not None else '')
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.data_table.setItem(row_idx, col_idx, item)
            
            self.data_table.resizeColumnsToContents()
            
            print(f"DEBUG - Loaded {len(results)} rows")
        except Exception as e:
            show_error(self, 'Error', f'Failed to load data:\n{str(e)}')
    
    def on_row_selected(self):
        """Handle row selection in data table."""
        selected_rows = self.data_table.selectedItems()
        if not selected_rows:
            # Clear form if no selection
            self.current_pk_values = {}
            self.btn_update.setEnabled(False)
            self.btn_delete.setEnabled(False)
            self.btn_create.setEnabled(True)
            return
        
        row = selected_rows[0].row()
        
        # Store primary key values
        self.current_pk_values = {}
        pk_columns = self.get_primary_key_columns()
        
        print(f"DEBUG - PK columns needed: {pk_columns}")
        
        # Get column index mapping (case-insensitive)
        column_indices = {}
        column_name_map = {}  # Maps lowercase to actual column name
        for i in range(self.data_table.columnCount()):
            header_item = self.data_table.horizontalHeaderItem(i)
            if header_item:
                actual_name = header_item.text()
                column_indices[actual_name] = i
                column_name_map[actual_name.lower()] = actual_name
        
        print(f"DEBUG - Available columns in table: {list(column_indices.keys())}")
        
        # FIRST: Extract and store ALL primary key values from the table
        for pk_col in pk_columns:
            # Try exact match first
            matched_col = None
            if pk_col in column_indices:
                matched_col = pk_col
            else:
                # Try case-insensitive match
                pk_col_lower = pk_col.lower()
                if pk_col_lower in column_name_map:
                    matched_col = column_name_map[pk_col_lower]
                    print(f"DEBUG - Matched '{pk_col}' to '{matched_col}' (case-insensitive)")
            
            if matched_col:
                col_idx = column_indices[matched_col]
                item = self.data_table.item(row, col_idx)
                value = item.text() if item else None
                if value and value.strip():
                    self.current_pk_values[pk_col] = value.strip()
                    print(f"DEBUG - Stored PK {pk_col} = {value.strip()}")
                else:
                    print(f"DEBUG - WARNING: Empty value for PK {pk_col}")
            else:
                print(f"DEBUG - ERROR: Could not find column '{pk_col}' in table")
        
        # SECOND: Load ALL data into form fields
        for col in self.columns_config:
            col_name = col['name']
            
            # Try exact match first
            matched_col = None
            if col_name in column_indices:
                matched_col = col_name
            else:
                # Try case-insensitive match
                col_name_lower = col_name.lower()
                if col_name_lower in column_name_map:
                    matched_col = column_name_map[col_name_lower]
            
            if matched_col:
                col_idx = column_indices[matched_col]
                item = self.data_table.item(row, col_idx)
                value = item.text() if item else None
                self.set_field_value(col_name, value)
        
        print(f"DEBUG - Final PK values stored: {self.current_pk_values}")
        print(f"DEBUG - Expected {len(pk_columns)} PKs, got {len(self.current_pk_values)}")
        
        # Verify we have all PK values before enabling buttons
        if len(self.current_pk_values) == len(pk_columns) and self.current_pk_values:
            self.btn_update.setEnabled(True)
            self.btn_delete.setEnabled(True)
            self.btn_create.setEnabled(False)
            print("DEBUG - Buttons enabled successfully")
        else:
            # If we don't have all PK values, something went wrong
            missing = [pk for pk in pk_columns if pk not in self.current_pk_values]
            show_warning(self, 'Error', 
                        f'Could not identify primary key values for this record.\n\n'
                        f'Expected PK columns: {pk_columns}\n'
                        f'Missing: {missing}\n'
                        f'Found: {list(self.current_pk_values.keys())}\n\n'
                        f'Available table columns: {list(column_indices.keys())}\n\n'
                        f'This usually means the column names in your configuration '
                        f'do not match the actual database column names.')
            self.current_pk_values = {}
            self.btn_update.setEnabled(False)
            self.btn_delete.setEnabled(False)


# Factory functions - Accept parent parameter
def get_department_form(parent=None):
    """Get Department table form configuration."""
    return GenericCRUDForm('Department', [
        {'name': 'Department_id', 'label': 'Department ID', 'type': 'text', 'required': True, 'pk': True},
        {'name': 'name', 'label': 'Department Name', 'type': 'text', 'required': True, 'pk': False}
    ], parent)


def get_student_form(parent=None):
    """Get Student table form configuration."""
    return GenericCRUDForm('Student', [
        {'name': 'Student_ID', 'label': 'Student ID', 'type': 'text', 'required': True, 'pk': True},
        {'name': 'Last_Name', 'label': 'Last Name', 'type': 'text', 'required': True, 'pk': False},
        {'name': 'First_Name', 'label': 'First Name', 'type': 'text', 'required': True, 'pk': False},
        {'name': 'DOB', 'label': 'Date of Birth', 'type': 'date', 'required': True, 'pk': False},
        {'name': 'Address', 'label': 'Address', 'type': 'text', 'required': False, 'pk': False},
        {'name': 'City', 'label': 'City', 'type': 'text', 'required': False, 'pk': False},
        {'name': 'Zip_Code', 'label': 'Zip Code', 'type': 'text', 'required': False, 'pk': False},
        {'name': 'Phone', 'label': 'Phone', 'type': 'text', 'required': False, 'pk': False},
        {'name': 'Fax', 'label': 'Fax', 'type': 'text', 'required': False, 'pk': False},
        {'name': 'Email', 'label': 'Email', 'type': 'text', 'required': False, 'pk': False}
    ], parent)


def get_instructor_form(parent=None):
    """Get Instructor table form configuration."""
    return GenericCRUDForm('Instructor', [
        {'name': 'Instructor_ID', 'label': 'Instructor ID', 'type': 'text', 'required': True, 'pk': True},
        {'name': 'Department_ID', 'label': 'Department', 'type': 'combo', 'required': True, 'pk': False,
         'fk_table': 'Department', 'fk_display': 'name', 'fk_value': 'Department_id'},
        {'name': 'Last_Name', 'label': 'Last Name', 'type': 'text', 'required': True, 'pk': False},
        {'name': 'First_Name', 'label': 'First Name', 'type': 'text', 'required': True, 'pk': False},
        {'name': 'Rank', 'label': 'Rank', 'type': 'combo', 'required': False, 'pk': False,
         'combo_values': ['Substitute', 'MCB', 'MCA', 'PROF']},
        {'name': 'Phone', 'label': 'Phone', 'type': 'text', 'required': False, 'pk': False},
        {'name': 'Fax', 'label': 'Fax', 'type': 'text', 'required': False, 'pk': False},
        {'name': 'Email', 'label': 'Email', 'type': 'text', 'required': False, 'pk': False}
    ], parent)


def get_course_form(parent=None):
    """Get Course table form configuration."""
    return GenericCRUDForm('Course', [
        {'name': 'Course_ID', 'label': 'Course ID', 'type': 'text', 'required': True, 'pk': True},
        {'name': 'Department_ID', 'label': 'Department', 'type': 'combo', 'required': True, 'pk': True,
         'fk_table': 'Department', 'fk_display': 'name', 'fk_value': 'Department_id'},
        {'name': 'name', 'label': 'Course Name', 'type': 'text', 'required': True, 'pk': False},
        {'name': 'Description', 'label': 'Description', 'type': 'text_area', 'required': False, 'pk': False}
    ], parent)