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
from db_connection import get_db_connection
import psycopg2


class GenericCRUDForm(QWidget):
    """Generic CRUD form widget that can be configured for different tables."""
    
    def __init__(self, table_name, columns_config, parent=None):
        """
        Initialize generic CRUD form.
        
        Args:
            table_name: Name of the database table
            columns_config: List of dicts with column configuration
                Each dict should have: 'name', 'label', 'type', 'required', 'pk'
            parent: Parent widget
        """
        super().__init__(parent)
        self.table_name = table_name
        self.columns_config = columns_config
        self.db_connection = get_db_connection()
        self.db_connection.connect()
        self.current_edit_id = None
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title
        title = QLabel(f'{self.table_name} Management')
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Form group
        form_group = QGroupBox('Data Entry')
        form_layout = QFormLayout()
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
                # Populate combo from foreign key table or static values
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
        
        self.btn_create = QPushButton('Create')
        self.btn_create.clicked.connect(self.create_record)
        self.btn_create.setStyleSheet("background-color: #27ae60; color: white; padding: 8px;")
        
        self.btn_update = QPushButton('Update')
        self.btn_update.clicked.connect(self.update_record)
        self.btn_update.setStyleSheet("background-color: #f39c12; color: white; padding: 8px;")
        self.btn_update.setEnabled(False)
        
        self.btn_delete = QPushButton('Delete')
        self.btn_delete.clicked.connect(self.delete_record)
        self.btn_delete.setStyleSheet("background-color: #e74c3c; color: white; padding: 8px;")
        self.btn_delete.setEnabled(False)
        
        self.btn_clear = QPushButton('Clear')
        self.btn_clear.clicked.connect(self.clear_form)
        self.btn_clear.setStyleSheet("background-color: #95a5a6; color: white; padding: 8px;")
        
        self.btn_refresh = QPushButton('Refresh')
        self.btn_refresh.clicked.connect(self.load_data)
        self.btn_refresh.setStyleSheet("background-color: #3498db; color: white; padding: 8px;")
        
        button_layout.addWidget(self.btn_create)
        button_layout.addWidget(self.btn_update)
        button_layout.addWidget(self.btn_delete)
        button_layout.addWidget(self.btn_clear)
        button_layout.addWidget(self.btn_refresh)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Data table
        table_label = QLabel('Records')
        table_label.setFont(QFont('Arial', 12, QFont.Bold))
        layout.addWidget(table_label)
        
        self.data_table = QTableWidget()
        self.data_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.data_table.setSelectionMode(QTableWidget.SingleSelection)
        self.data_table.itemSelectionChanged.connect(self.on_row_selected)
        self.data_table.horizontalHeader().setStretchLastSection(True)
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        layout.addWidget(self.data_table)
    
    def populate_combo(self, combo, table, display_col, value_col):
        """Populate combo box from foreign key table."""
        try:
            query = f"SELECT {value_col}, {display_col} FROM {table} ORDER BY {display_col}"
            cursor = self.db_connection.get_cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            combo.clear()
            combo.addItem('-- Select --', None)
            for row in results:
                combo.addItem(str(row[1]), row[0])
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to load {table}:\n{str(e)}')
    
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
            # Try to find by data value first
            if value is not None and value != '':
                # Try as integer if it's a numeric string
                try:
                    int_value = int(value)
                    index = widget.findData(int_value)
                    if index >= 0:
                        widget.setCurrentIndex(index)
                        return
                except (ValueError, TypeError):
                    pass
                
                # Try as string
                index = widget.findData(str(value))
                if index >= 0:
                    widget.setCurrentIndex(index)
                    return
                
                # Try to find by text
                for i in range(widget.count()):
                    if widget.itemText(i) == str(value):
                        widget.setCurrentIndex(i)
                        return
            # If not found, set to first item (-- Select --)
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
            if field['required'] and not field['pk']:  # Don't require PK for updates
                value = self.get_field_value(field_name)
                if not value or (isinstance(value, int) and value is None):
                    QMessageBox.warning(self, 'Validation Error', 
                                      f'{field["config"]["label"]} is required.')
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
        self.current_edit_id = None
        self.btn_update.setEnabled(False)
        self.btn_delete.setEnabled(False)
        self.btn_create.setEnabled(True)
    
    def get_primary_key_columns(self):
        """Get primary key column names."""
        return [col['name'] for col in self.columns_config if col.get('pk', False)]
    
    def create_record(self):
        """Create a new record."""
        if not self.validate_form():
            return
        
        try:
            # Get column names and values
            columns = []
            values = []
            placeholders = []
            
            for col in self.columns_config:
                if not col.get('pk', False) or self.get_field_value(col['name']):  # Include PK if provided
                    columns.append(col['name'])
                    value = self.get_field_value(col['name'])
                    # Convert empty strings to None for NULL values
                    if value == '' or (isinstance(value, str) and value.strip() == ''):
                        value = None
                    # Convert combo box None to NULL
                    if value is None and col.get('type') == 'combo':
                        # Check if it's a required field
                        if col.get('required', False):
                            QMessageBox.warning(self, 'Validation Error', 
                                              f'{col["label"]} is required.')
                            return
                    values.append(value)
                    placeholders.append('%s')
            
            query = f"INSERT INTO {self.table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
            
            cursor = self.db_connection.get_cursor()
            cursor.execute(query, values)
            self.db_connection.connection.commit()
            
            QMessageBox.information(self, 'Success', 'Record created successfully!')
            self.clear_form()
            self.load_data()
        except psycopg2.IntegrityError as e:
            QMessageBox.warning(self, 'Database Error', 
                              f'Failed to create record:\n{str(e)}\n\n'
                              'This may be due to:\n'
                              '- Duplicate primary key\n'
                              '- Foreign key constraint violation\n'
                              '- Unique constraint violation')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to create record:\n{str(e)}')
    
    def update_record(self):
        """Update selected record."""
        if not self.current_edit_id:
            QMessageBox.warning(self, 'Error', 'No record selected for update.')
            return
        
        if not self.validate_form():
            return
        
        try:
            # Build SET clause
            pk_columns = self.get_primary_key_columns()
            set_clauses = []
            values = []
            
            for col in self.columns_config:
                if not col.get('pk', False):  # Don't update PK
                    set_clauses.append(f"{col['name']} = %s")
                    value = self.get_field_value(col['name'])
                    # Convert empty strings to None for NULL values
                    if value == '' or (isinstance(value, str) and value.strip() == ''):
                        value = None
                    values.append(value)
            
            # Build WHERE clause for composite or single PK
            where_clauses = []
            for pk_col in pk_columns:
                where_clauses.append(f"{pk_col} = %s")
                values.append(self.get_field_value(pk_col))
            
            query = f"UPDATE {self.table_name} SET {', '.join(set_clauses)} WHERE {' AND '.join(where_clauses)}"
            
            cursor = self.db_connection.get_cursor()
            cursor.execute(query, values)
            self.db_connection.connection.commit()
            
            if cursor.rowcount > 0:
                QMessageBox.information(self, 'Success', 'Record updated successfully!')
                self.clear_form()
                self.load_data()
            else:
                QMessageBox.warning(self, 'Error', 'No record was updated.')
        except psycopg2.IntegrityError as e:
            QMessageBox.warning(self, 'Database Error', 
                              f'Failed to update record:\n{str(e)}\n\n'
                              'This may be due to:\n'
                              '- Foreign key constraint violation\n'
                              '- Unique constraint violation')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to update record:\n{str(e)}')
    
    def delete_record(self):
        """Delete selected record."""
        if not self.current_edit_id:
            QMessageBox.warning(self, 'Error', 'No record selected for deletion.')
            return
        
        reply = QMessageBox.question(self, 'Confirm Delete', 
                                    'Are you sure you want to delete this record?',
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply != QMessageBox.Yes:
            return
        
        try:
            pk_columns = self.get_primary_key_columns()
            where_clauses = []
            values = []
            
            for pk_col in pk_columns:
                where_clauses.append(f"{pk_col} = %s")
                values.append(self.get_field_value(pk_col))
            
            query = f"DELETE FROM {self.table_name} WHERE {' AND '.join(where_clauses)}"
            
            cursor = self.db_connection.get_cursor()
            cursor.execute(query, values)
            self.db_connection.connection.commit()
            
            if cursor.rowcount > 0:
                QMessageBox.information(self, 'Success', 'Record deleted successfully!')
                self.clear_form()
                self.load_data()
            else:
                QMessageBox.warning(self, 'Error', 'No record was deleted.')
        except psycopg2.IntegrityError as e:
            error_msg = str(e)
            if 'foreign key' in error_msg.lower() or 'still referenced' in error_msg.lower():
                QMessageBox.warning(self, 'Delete Error', 
                                  f'Cannot delete this record:\n\n'
                                  f'This record is referenced by other tables.\n'
                                  f'Please delete related records first.\n\n'
                                  f'Database error: {error_msg}')
            else:
                QMessageBox.warning(self, 'Database Error', 
                                  f'Failed to delete record:\n{error_msg}')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to delete record:\n{str(e)}')
    
    def load_data(self):
        """Load and display data in table."""
        try:
            query = f"SELECT * FROM {self.table_name} ORDER BY {self.get_primary_key_columns()[0]}"
            cursor = self.db_connection.get_cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            
            self.data_table.setRowCount(len(results))
            self.data_table.setColumnCount(len(column_names))
            self.data_table.setHorizontalHeaderLabels(column_names)
            
            for row_idx, row in enumerate(results):
                for col_idx, value in enumerate(row):
                    item = QTableWidgetItem(str(value) if value is not None else '')
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.data_table.setItem(row_idx, col_idx, item)
            
            self.data_table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to load data:\n{str(e)}')
    
    def on_row_selected(self):
        """Handle row selection in data table."""
        selected_rows = self.data_table.selectedItems()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        pk_columns = self.get_primary_key_columns()
        
        # Get PK values from selected row
        pk_values = {}
        for pk_col in pk_columns:
            col_idx = None
            for i in range(self.data_table.columnCount()):
                if self.data_table.horizontalHeaderItem(i).text() == pk_col:
                    col_idx = i
                    break
            if col_idx is not None:
                item = self.data_table.item(row, col_idx)
                pk_values[pk_col] = item.text() if item else None
        
        # Load data into form
        for col in self.columns_config:
            col_name = col['name']
            col_idx = None
            for i in range(self.data_table.columnCount()):
                if self.data_table.horizontalHeaderItem(i).text() == col_name:
                    col_idx = i
                    break
            if col_idx is not None:
                item = self.data_table.item(row, col_idx)
                value = item.text() if item else None
                
                # For combo boxes with foreign keys, we need to find the ID
                # The table shows the display value, but we need the key value
                if col.get('type') == 'combo' and 'fk_table' in col:
                    # Try to find the matching item in combo by display text
                    combo_widget = self.input_fields[col_name]['widget']
                    # The value from table is the display text, find matching item
                    for i in range(combo_widget.count()):
                        if combo_widget.itemText(i) == value:
                            combo_widget.setCurrentIndex(i)
                            break
                else:
                    self.set_field_value(col_name, value)
        
        # Store PK for update/delete
        if len(pk_columns) == 1:
            self.current_edit_id = pk_values.get(pk_columns[0])
        else:
            self.current_edit_id = tuple(pk_values.get(pk, None) for pk in pk_columns)
        
        self.btn_update.setEnabled(True)
        self.btn_delete.setEnabled(True)
        self.btn_create.setEnabled(False)


def get_department_form():
    """Get Department table form configuration."""
    return GenericCRUDForm('Department', [
        {'name': 'Department_id', 'label': 'Department ID', 'type': 'text', 'required': True, 'pk': True},
        {'name': 'name', 'label': 'Department Name', 'type': 'text', 'required': True, 'pk': False}
    ])


def get_student_form():
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
    ])


def get_instructor_form():
    """Get Instructor table form configuration."""
    form = GenericCRUDForm('Instructor', [
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
    ])
    # Populate Rank combo with allowed values
    rank_field = form.input_fields['Rank']
    rank_combo = rank_field['widget']
    rank_combo.clear()
    rank_combo.addItem('-- Select --', None)
    for rank_value in ['Substitute', 'MCB', 'MCA', 'PROF']:
        rank_combo.addItem(rank_value, rank_value)
    return form


def get_course_form():
    """Get Course table form configuration."""
    form = GenericCRUDForm('Course', [
        {'name': 'Course_ID', 'label': 'Course ID', 'type': 'text', 'required': True, 'pk': True},
        {'name': 'Department_ID', 'label': 'Department', 'type': 'combo', 'required': True, 'pk': True,
         'fk_table': 'Department', 'fk_display': 'name', 'fk_value': 'Department_id'},
        {'name': 'name', 'label': 'Course Name', 'type': 'text', 'required': True, 'pk': False},
        {'name': 'Description', 'label': 'Description', 'type': 'text_area', 'required': False, 'pk': False}
    ])
    return form

