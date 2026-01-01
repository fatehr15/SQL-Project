"""
Marks & Attendance Window
Interface for managing student marks and attendance records.
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QComboBox, QDateEdit, QTableWidget, 
                             QTableWidgetItem, QMessageBox, QGroupBox, QFormLayout, 
                             QDoubleSpinBox, QTabWidget, QHeaderView, QLineEdit)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from db_connection import get_db_connection
import psycopg2


class MarksAttendanceWindow(QMainWindow):
    """Window for managing student marks and attendance."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_connection = get_db_connection()
        self.db_connection.connect()
        self.current_mark_id = None
        self.init_ui()
        self.load_dropdowns()
        self.load_marks_data()
        self.load_attendance_data()
        self.ensure_attendance_table()
    
    def ensure_attendance_table(self):
        """Ensure Attendance table exists, create if not."""
        try:
            cursor = self.db_connection.get_cursor()
            # Check if table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'attendance'
                )
            """)
            if not cursor.fetchone()[0]:
                # Create attendance table
                cursor.execute("""
                    CREATE TABLE Attendance (
                        attendance_id SERIAL PRIMARY KEY,
                        student_id INT NOT NULL,
                        course_id INT NOT NULL,
                        dept_id INT NOT NULL,
                        attendance_date DATE NOT NULL DEFAULT CURRENT_DATE,
                        status VARCHAR(20) NOT NULL CHECK (status IN ('Present', 'Absent', 'Late', 'Excused')),
                        notes TEXT,
                        FOREIGN KEY(student_id) REFERENCES Student(student_id),
                        FOREIGN KEY(course_id, dept_id) REFERENCES Course(course_id, department_id)
                    )
                """)
                self.db_connection.connection.commit()
        except Exception as e:
            print(f"Note: Attendance table check/create: {e}")
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('Marks & Attendance Management')
        self.setGeometry(50, 50, 1400, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Title
        title = QLabel('Marks & Attendance Management')
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Tab widget for Marks and Attendance
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Marks Tab
        marks_tab = QWidget()
        marks_layout = QVBoxLayout()
        marks_tab.setLayout(marks_layout)
        
        # Marks form
        marks_form_group = QGroupBox('Marks Entry')
        marks_form_layout = QFormLayout()
        marks_form_group.setLayout(marks_form_layout)
        
        # Student selection
        self.student_combo = QComboBox()
        self.student_combo.setEditable(False)
        marks_form_layout.addRow('Student *', self.student_combo)
        
        # Course selection
        self.marks_course_combo = QComboBox()
        self.marks_course_combo.setEditable(False)
        marks_form_layout.addRow('Course *', self.marks_course_combo)
        
        # Mark value
        self.mark_value = QDoubleSpinBox()
        self.mark_value.setMinimum(0.0)
        self.mark_value.setMaximum(20.0)
        self.mark_value.setDecimals(2)
        self.mark_value.setSingleStep(0.5)
        marks_form_layout.addRow('Mark (0-20) *', self.mark_value)
        
        # Mark date
        self.mark_date = QDateEdit()
        self.mark_date.setCalendarPopup(True)
        self.mark_date.setDate(QDate.currentDate())
        self.mark_date.setDisplayFormat('yyyy-MM-dd')
        marks_form_layout.addRow('Mark Date *', self.mark_date)
        
        marks_layout.addWidget(marks_form_group)
        
        # Marks buttons
        marks_button_layout = QHBoxLayout()
        
        self.btn_add_mark = QPushButton('Add Mark')
        self.btn_add_mark.clicked.connect(self.add_mark)
        self.btn_add_mark.setStyleSheet("background-color: #27ae60; color: white; padding: 8px;")
        
        self.btn_update_mark = QPushButton('Update Mark')
        self.btn_update_mark.clicked.connect(self.update_mark)
        self.btn_update_mark.setStyleSheet("background-color: #f39c12; color: white; padding: 8px;")
        self.btn_update_mark.setEnabled(False)
        
        self.btn_clear_mark = QPushButton('Clear')
        self.btn_clear_mark.clicked.connect(self.clear_marks_form)
        self.btn_clear_mark.setStyleSheet("background-color: #95a5a6; color: white; padding: 8px;")
        
        self.btn_refresh_marks = QPushButton('Refresh')
        self.btn_refresh_marks.clicked.connect(self.load_marks_data)
        self.btn_refresh_marks.setStyleSheet("background-color: #3498db; color: white; padding: 8px;")
        
        marks_button_layout.addWidget(self.btn_add_mark)
        marks_button_layout.addWidget(self.btn_update_mark)
        marks_button_layout.addWidget(self.btn_clear_mark)
        marks_button_layout.addWidget(self.btn_refresh_marks)
        marks_button_layout.addStretch()
        
        marks_layout.addLayout(marks_button_layout)
        
        # Marks table
        marks_table_label = QLabel('Student Marks')
        marks_table_label.setFont(QFont('Arial', 12, QFont.Bold))
        marks_layout.addWidget(marks_table_label)
        
        self.marks_table = QTableWidget()
        self.marks_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.marks_table.setSelectionMode(QTableWidget.SingleSelection)
        self.marks_table.itemSelectionChanged.connect(self.on_mark_selected)
        self.marks_table.horizontalHeader().setStretchLastSection(True)
        self.marks_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        marks_layout.addWidget(self.marks_table)
        
        self.tabs.addTab(marks_tab, 'Marks')
        
        # Attendance Tab
        attendance_tab = QWidget()
        attendance_layout = QVBoxLayout()
        attendance_tab.setLayout(attendance_layout)
        
        # Attendance form
        attendance_form_group = QGroupBox('Attendance Entry')
        attendance_form_layout = QFormLayout()
        attendance_form_group.setLayout(attendance_form_layout)
        
        # Student selection for attendance
        self.attendance_student_combo = QComboBox()
        self.attendance_student_combo.setEditable(False)
        attendance_form_layout.addRow('Student *', self.attendance_student_combo)
        
        # Course selection for attendance
        self.attendance_course_combo = QComboBox()
        self.attendance_course_combo.setEditable(False)
        attendance_form_layout.addRow('Course *', self.attendance_course_combo)
        
        # Attendance date
        self.attendance_date = QDateEdit()
        self.attendance_date.setCalendarPopup(True)
        self.attendance_date.setDate(QDate.currentDate())
        self.attendance_date.setDisplayFormat('yyyy-MM-dd')
        attendance_form_layout.addRow('Date *', self.attendance_date)
        
        # Status
        self.attendance_status = QComboBox()
        self.attendance_status.addItems(['Present', 'Absent', 'Late', 'Excused'])
        attendance_form_layout.addRow('Status *', self.attendance_status)
        
        # Notes
        self.attendance_notes = QLineEdit()
        attendance_form_layout.addRow('Notes', self.attendance_notes)
        
        attendance_layout.addWidget(attendance_form_group)
        
        # Attendance buttons
        attendance_button_layout = QHBoxLayout()
        
        self.btn_add_attendance = QPushButton('Record Attendance')
        self.btn_add_attendance.clicked.connect(self.add_attendance)
        self.btn_add_attendance.setStyleSheet("background-color: #27ae60; color: white; padding: 8px;")
        
        self.btn_refresh_attendance = QPushButton('Refresh')
        self.btn_refresh_attendance.clicked.connect(self.load_attendance_data)
        self.btn_refresh_attendance.setStyleSheet("background-color: #3498db; color: white; padding: 8px;")
        
        self.btn_clear_attendance = QPushButton('Clear')
        self.btn_clear_attendance.clicked.connect(self.clear_attendance_form)
        self.btn_clear_attendance.setStyleSheet("background-color: #95a5a6; color: white; padding: 8px;")
        
        attendance_button_layout.addWidget(self.btn_add_attendance)
        attendance_button_layout.addWidget(self.btn_refresh_attendance)
        attendance_button_layout.addWidget(self.btn_clear_attendance)
        attendance_button_layout.addStretch()
        
        attendance_layout.addLayout(attendance_button_layout)
        
        # Attendance table
        attendance_table_label = QLabel('Attendance Records')
        attendance_table_label.setFont(QFont('Arial', 12, QFont.Bold))
        attendance_layout.addWidget(attendance_table_label)
        
        self.attendance_table = QTableWidget()
        self.attendance_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.attendance_table.horizontalHeader().setStretchLastSection(True)
        self.attendance_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        attendance_layout.addWidget(self.attendance_table)
        
        self.tabs.addTab(attendance_tab, 'Attendance')
    
    def load_dropdowns(self):
        """Load data for combo boxes."""
        try:
            cursor = self.db_connection.get_cursor()
            
            # Load students
            cursor.execute("""
                SELECT Student_ID, First_Name, Last_Name 
                FROM Student 
                ORDER BY Last_Name, First_Name
            """)
            students = cursor.fetchall()
            self.student_combo.clear()
            self.attendance_student_combo.clear()
            for student_id, first_name, last_name in students:
                display_text = f"{last_name}, {first_name} (ID: {student_id})"
                self.student_combo.addItem(display_text, student_id)
                self.attendance_student_combo.addItem(display_text, student_id)
            
            # Load courses
            cursor.execute("""
                SELECT c.Course_ID, c.Department_ID, c.name, d.name as dept_name
                FROM Course c
                JOIN Department d ON c.Department_ID = d.Department_id
                ORDER BY d.name, c.name
            """)
            courses = cursor.fetchall()
            self.marks_course_combo.clear()
            self.attendance_course_combo.clear()
            for course_id, dept_id, course_name, dept_name in courses:
                display_text = f"{course_name} (Dept: {dept_name}, ID: {course_id}/{dept_id})"
                self.marks_course_combo.addItem(display_text, (course_id, dept_id))
                self.attendance_course_combo.addItem(display_text, (course_id, dept_id))
                
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to load dropdown data:\n{str(e)}')
    
    def add_mark(self):
        """Add a new mark."""
        try:
            student_id = self.student_combo.currentData()
            course_data = self.marks_course_combo.currentData()
            
            if student_id is None or course_data is None:
                QMessageBox.warning(self, 'Validation Error', 'Please select both student and course.')
                return
            
            course_id, dept_id = course_data
            mark_value = self.mark_value.value()
            mark_date = self.mark_date.date().toString('yyyy-MM-dd')
            
            cursor = self.db_connection.get_cursor()
            query = """
                INSERT INTO Marks (student_id, course_id, dept_id, mark, mark_date)
                VALUES (%s, %s, %s, %s, %s::date)
            """
            cursor.execute(query, (student_id, course_id, dept_id, mark_value, mark_date))
            self.db_connection.connection.commit()
            
            QMessageBox.information(self, 'Success', 'Mark added successfully!')
            self.clear_marks_form()
            self.load_marks_data()
            
        except psycopg2.IntegrityError as e:
            QMessageBox.warning(self, 'Database Error', 
                              f'Failed to add mark:\n{str(e)}\n\n'
                              'This may be due to:\n'
                              '- Foreign key constraint violation\n'
                              '- Invalid mark value')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to add mark:\n{str(e)}')
    
    def update_mark(self):
        """Update selected mark."""
        if not self.current_mark_id:
            QMessageBox.warning(self, 'Error', 'No mark selected for update.')
            return
        
        try:
            mark_value = self.mark_value.value()
            mark_date = self.mark_date.date().toString('yyyy-MM-dd')
            
            cursor = self.db_connection.get_cursor()
            query = """
                UPDATE Marks 
                SET mark = %s, mark_date = %s::date
                WHERE mark_id = %s
            """
            cursor.execute(query, (mark_value, mark_date, self.current_mark_id))
            self.db_connection.connection.commit()
            
            if cursor.rowcount > 0:
                QMessageBox.information(self, 'Success', 'Mark updated successfully!')
                self.clear_marks_form()
                self.load_marks_data()
            else:
                QMessageBox.warning(self, 'Error', 'No mark was updated.')
                
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to update mark:\n{str(e)}')
    
    def on_mark_selected(self):
        """Handle mark selection in table."""
        selected_rows = self.marks_table.selectedItems()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        
        # Get mark_id from first column
        mark_id_item = self.marks_table.item(row, 0)
        if mark_id_item:
            self.current_mark_id = int(mark_id_item.text())
        
        # Load data into form
        student_id_item = self.marks_table.item(row, 1)
        course_id_item = self.marks_table.item(row, 2)
        dept_id_item = self.marks_table.item(row, 3)
        mark_item = self.marks_table.item(row, 4)
        date_item = self.marks_table.item(row, 5)
        
        if student_id_item:
            student_id = int(student_id_item.text())
            index = self.student_combo.findData(student_id)
            if index >= 0:
                self.student_combo.setCurrentIndex(index)
        
        if course_id_item and dept_id_item:
            course_id = int(course_id_item.text())
            dept_id = int(dept_id_item.text())
            index = self.marks_course_combo.findData((course_id, dept_id))
            if index >= 0:
                self.marks_course_combo.setCurrentIndex(index)
        
        if mark_item:
            self.mark_value.setValue(float(mark_item.text()))
        
        if date_item:
            date = QDate.fromString(date_item.text(), 'yyyy-MM-dd')
            if date.isValid():
                self.mark_date.setDate(date)
        
        self.btn_update_mark.setEnabled(True)
        self.btn_add_mark.setEnabled(False)
    
    def clear_marks_form(self):
        """Clear marks form."""
        self.student_combo.setCurrentIndex(0)
        self.marks_course_combo.setCurrentIndex(0)
        self.mark_value.setValue(0.0)
        self.mark_date.setDate(QDate.currentDate())
        self.current_mark_id = None
        self.btn_update_mark.setEnabled(False)
        self.btn_add_mark.setEnabled(True)
    
    def load_marks_data(self):
        """Load and display marks."""
        try:
            query = """
                SELECT m.mark_id, m.student_id, m.course_id, m.dept_id,
                       s.Last_Name || ', ' || s.First_Name as Student_Name,
                       c.name as Course_Name, d.name as Department_Name,
                       m.mark, m.mark_date
                FROM Marks m
                JOIN Student s ON m.student_id = s.Student_ID
                JOIN Course c ON m.course_id = c.Course_ID AND m.dept_id = c.Department_ID
                JOIN Department d ON m.dept_id = d.Department_id
                ORDER BY m.mark_date DESC, s.Last_Name
            """
            cursor = self.db_connection.get_cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            column_names = ['Mark ID', 'Student ID', 'Course ID', 'Dept ID', 
                          'Student Name', 'Course', 'Department', 'Mark', 'Date']
            
            self.marks_table.setRowCount(len(results))
            self.marks_table.setColumnCount(len(column_names))
            self.marks_table.setHorizontalHeaderLabels(column_names)
            
            for row_idx, row in enumerate(results):
                for col_idx, value in enumerate(row):
                    item = QTableWidgetItem(str(value) if value is not None else '')
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.marks_table.setItem(row_idx, col_idx, item)
            
            self.marks_table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to load marks:\n{str(e)}')
    
    def add_attendance(self):
        """Add attendance record."""
        try:
            student_id = self.attendance_student_combo.currentData()
            course_data = self.attendance_course_combo.currentData()
            
            if student_id is None or course_data is None:
                QMessageBox.warning(self, 'Validation Error', 'Please select both student and course.')
                return
            
            course_id, dept_id = course_data
            attendance_date = self.attendance_date.date().toString('yyyy-MM-dd')
            status = self.attendance_status.currentText()
            notes = self.attendance_notes.text().strip() or None
            
            cursor = self.db_connection.get_cursor()
            query = """
                INSERT INTO Attendance (student_id, course_id, dept_id, attendance_date, status, notes)
                VALUES (%s, %s, %s, %s::date, %s, %s)
            """
            cursor.execute(query, (student_id, course_id, dept_id, attendance_date, status, notes))
            self.db_connection.connection.commit()
            
            QMessageBox.information(self, 'Success', 'Attendance recorded successfully!')
            self.clear_attendance_form()
            self.load_attendance_data()
            
        except psycopg2.IntegrityError as e:
            QMessageBox.warning(self, 'Database Error', 
                              f'Failed to record attendance:\n{str(e)}\n\n'
                              'This may be due to:\n'
                              '- Foreign key constraint violation')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to record attendance:\n{str(e)}')
    
    def clear_attendance_form(self):
        """Clear attendance form."""
        self.attendance_student_combo.setCurrentIndex(0)
        self.attendance_course_combo.setCurrentIndex(0)
        self.attendance_date.setDate(QDate.currentDate())
        self.attendance_status.setCurrentIndex(0)
        self.attendance_notes.clear()
    
    def load_attendance_data(self):
        """Load and display attendance records."""
        try:
            query = """
                SELECT a.attendance_id, a.student_id, a.course_id, a.dept_id,
                       s.Last_Name || ', ' || s.First_Name as Student_Name,
                       c.name as Course_Name, d.name as Department_Name,
                       a.attendance_date, a.status, a.notes
                FROM Attendance a
                JOIN Student s ON a.student_id = s.Student_ID
                JOIN Course c ON a.course_id = c.Course_ID AND a.dept_id = c.Department_ID
                JOIN Department d ON a.dept_id = d.Department_id
                ORDER BY a.attendance_date DESC, s.Last_Name
            """
            cursor = self.db_connection.get_cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            column_names = ['Attendance ID', 'Student ID', 'Course ID', 'Dept ID',
                          'Student Name', 'Course', 'Department', 'Date', 'Status', 'Notes']
            
            self.attendance_table.setRowCount(len(results))
            self.attendance_table.setColumnCount(len(column_names))
            self.attendance_table.setHorizontalHeaderLabels(column_names)
            
            for row_idx, row in enumerate(results):
                for col_idx, value in enumerate(row):
                    item = QTableWidgetItem(str(value) if value is not None else '')
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.attendance_table.setItem(row_idx, col_idx, item)
            
            self.attendance_table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to load attendance:\n{str(e)}')

