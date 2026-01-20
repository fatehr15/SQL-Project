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
from window_base import get_connection_from_parent, is_demo_mode, show_error, show_info, show_warning


class MarksAttendanceWindow(QMainWindow):
    """Window for managing student marks and attendance."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        try:
            self.db_connection = get_connection_from_parent(parent)
            self.is_demo = is_demo_mode(self.db_connection)
        except Exception as e:
            show_error(self, "Connection Error", str(e))
            raise
        
        self.current_mark_id = None
        self.init_ui()
        self.ensure_tables()
        self.load_dropdowns()
        self.load_marks_data()
        self.load_attendance_data()
    
    def ensure_tables(self):
        """Ensure Marks and Attendance tables exist."""
        try:
            cursor = self.db_connection.get_cursor()
            
            if self.is_demo:
                # SQLite - check and create Marks table
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Marks'")
                if not cursor.fetchone():
                    cursor.execute("""
                        CREATE TABLE Marks (
                            mark_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            student_id INTEGER NOT NULL,
                            course_id INTEGER NOT NULL,
                            dept_id INTEGER NOT NULL,
                            mark REAL NOT NULL CHECK (mark >= 0 AND mark <= 20),
                            mark_date DATE NOT NULL DEFAULT (date('now')),
                            FOREIGN KEY(student_id) REFERENCES Student(Student_ID),
                            FOREIGN KEY(course_id, dept_id) REFERENCES Course(Course_ID, Department_ID)
                        )
                    """)
                
                # Check and create Attendance table
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Attendance'")
                if not cursor.fetchone():
                    cursor.execute("""
                        CREATE TABLE Attendance (
                            attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            student_id INTEGER NOT NULL,
                            course_id INTEGER NOT NULL,
                            dept_id INTEGER NOT NULL,
                            attendance_date DATE NOT NULL DEFAULT (date('now')),
                            status VARCHAR(20) NOT NULL,
                            notes TEXT,
                            FOREIGN KEY(student_id) REFERENCES Student(Student_ID),
                            FOREIGN KEY(course_id, dept_id) REFERENCES Course(Course_ID, Department_ID)
                        )
                    """)
                
                self.db_connection.commit()
            else:
                # PostgreSQL - check via information_schema
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' AND table_name = 'marks'
                    )
                """)
                if not cursor.fetchone()[0]:
                    cursor.execute("""
                        CREATE TABLE Marks (
                            mark_id SERIAL PRIMARY KEY,
                            student_id INT NOT NULL,
                            course_id INT NOT NULL,
                            dept_id INT NOT NULL,
                            mark NUMERIC(4,2) NOT NULL CHECK (mark >= 0 AND mark <= 20),
                            mark_date DATE NOT NULL DEFAULT CURRENT_DATE,
                            FOREIGN KEY(student_id) REFERENCES Student(Student_ID),
                            FOREIGN KEY(course_id, dept_id) REFERENCES Course(Course_ID, Department_ID)
                        )
                    """)
                
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' AND table_name = 'attendance'
                    )
                """)
                if not cursor.fetchone()[0]:
                    cursor.execute("""
                        CREATE TABLE Attendance (
                            attendance_id SERIAL PRIMARY KEY,
                            student_id INT NOT NULL,
                            course_id INT NOT NULL,
                            dept_id INT NOT NULL,
                            attendance_date DATE NOT NULL DEFAULT CURRENT_DATE,
                            status VARCHAR(20) NOT NULL CHECK (status IN ('Present', 'Absent', 'Late', 'Excused')),
                            notes TEXT,
                            FOREIGN KEY(student_id) REFERENCES Student(Student_ID),
                            FOREIGN KEY(course_id, dept_id) REFERENCES Course(Course_ID, Department_ID)
                        )
                    """))
                
                self.db_connection.commit()
        except Exception as e:
            print(f"Note: Table creation: {e}")
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('✍ Marks & Attendance Management')
        self.setGeometry(50, 50, 1400, 900)
        
        self.setStyleSheet("""
            QMainWindow {
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
            QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox {
                padding: 8px;
                border: 2px solid #dcdde1;
                border-radius: 5px;
                background-color: white;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QDoubleSpinBox:focus {
                border: 2px solid #3498db;
            }
            QPushButton {
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #dcdde1;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        central_widget.setLayout(main_layout)
        
        # Title
        title = QLabel('✍ Marks & Attendance Management')
        title.setFont(QFont('Segoe UI', 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; padding: 10px;")
        main_layout.addWidget(title)
        
        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #dcdde1;
                border-radius: 5px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                padding: 10px 20px;
                margin-right: 5px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid white;
            }
        """)
        main_layout.addWidget(self.tabs)
        
        # Create tabs
        self.create_marks_tab()
        self.create_attendance_tab()
    
    def create_marks_tab(self):
        """Create the marks management tab."""
        marks_tab = QWidget()
        marks_layout = QVBoxLayout()
        marks_layout.setContentsMargins(20, 20, 20, 20)
        marks_layout.setSpacing(15)
        marks_tab.setLayout(marks_layout)
        
        # Marks form
        marks_form_group = QGroupBox('📝 Marks Entry')
        marks_form_layout = QFormLayout()
        marks_form_layout.setSpacing(12)
        marks_form_group.setLayout(marks_form_layout)
        
        self.student_combo = QComboBox()
        marks_form_layout.addRow('Student *', self.student_combo)
        
        self.marks_course_combo = QComboBox()
        marks_form_layout.addRow('Course *', self.marks_course_combo)
        
        self.mark_value = QDoubleSpinBox()
        self.mark_value.setRange(0.0, 20.0)
        self.mark_value.setDecimals(2)
        self.mark_value.setSingleStep(0.5)
        marks_form_layout.addRow('Mark (0-20) *', self.mark_value)
        
        self.mark_date = QDateEdit()
        self.mark_date.setCalendarPopup(True)
        self.mark_date.setDate(QDate.currentDate())
        marks_form_layout.addRow('Mark Date *', self.mark_date)
        
        marks_layout.addWidget(marks_form_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_add_mark = QPushButton('➕ Add Mark')
        self.btn_add_mark.clicked.connect(self.add_mark)
        self.btn_add_mark.setStyleSheet("background-color: #27ae60; color: white;")
        
        self.btn_update_mark = QPushButton('✏️ Update Mark')
        self.btn_update_mark.clicked.connect(self.update_mark)
        self.btn_update_mark.setStyleSheet("background-color: #f39c12; color: white;")
        self.btn_update_mark.setEnabled(False)
        
        self.btn_clear_mark = QPushButton('🔄 Clear')
        self.btn_clear_mark.clicked.connect(self.clear_marks_form)
        self.btn_clear_mark.setStyleSheet("background-color: #95a5a6; color: white;")
        
        self.btn_refresh_marks = QPushButton('🔃 Refresh')
        self.btn_refresh_marks.clicked.connect(self.load_marks_data)
        self.btn_refresh_marks.setStyleSheet("background-color: #3498db; color: white;")
        
        btn_layout.addWidget(self.btn_add_mark)
        btn_layout.addWidget(self.btn_update_mark)
        btn_layout.addWidget(self.btn_clear_mark)
        btn_layout.addWidget(self.btn_refresh_marks)
        btn_layout.addStretch()
        
        marks_layout.addLayout(btn_layout)
        
        # Table
        self.marks_table = QTableWidget()
        self.marks_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.marks_table.setSelectionMode(QTableWidget.SingleSelection)
        self.marks_table.itemSelectionChanged.connect(self.on_mark_selected)
        self.marks_table.horizontalHeader().setStretchLastSection(True)
        marks_layout.addWidget(self.marks_table)
        
        self.tabs.addTab(marks_tab, '📝 Marks')
    
    def create_attendance_tab(self):
        """Create the attendance management tab."""
        attendance_tab = QWidget()
        attendance_layout = QVBoxLayout()
        attendance_layout.setContentsMargins(20, 20, 20, 20)
        attendance_layout.setSpacing(15)
        attendance_tab.setLayout(attendance_layout)
        
        # Form
        form_group = QGroupBox('✅ Attendance Entry')
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_group.setLayout(form_layout)
        
        self.attendance_student_combo = QComboBox()
        form_layout.addRow('Student *', self.attendance_student_combo)
        
        self.attendance_course_combo = QComboBox()
        form_layout.addRow('Course *', self.attendance_course_combo)
        
        self.attendance_date = QDateEdit()
        self.attendance_date.setCalendarPopup(True)
        self.attendance_date.setDate(QDate.currentDate())
        form_layout.addRow('Date *', self.attendance_date)
        
        self.attendance_status = QComboBox()
        self.attendance_status.addItems(['Present', 'Absent', 'Late', 'Excused'])
        form_layout.addRow('Status *', self.attendance_status)
        
        self.attendance_notes = QLineEdit()
        form_layout.addRow('Notes', self.attendance_notes)
        
        attendance_layout.addWidget(form_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_add_attendance = QPushButton('➕ Record Attendance')
        self.btn_add_attendance.clicked.connect(self.add_attendance)
        self.btn_add_attendance.setStyleSheet("background-color: #27ae60; color: white;")
        
        self.btn_refresh_attendance = QPushButton('🔃 Refresh')
        self.btn_refresh_attendance.clicked.connect(self.load_attendance_data)
        self.btn_refresh_attendance.setStyleSheet("background-color: #3498db; color: white;")
        
        self.btn_clear_attendance = QPushButton('🔄 Clear')
        self.btn_clear_attendance.clicked.connect(self.clear_attendance_form)
        self.btn_clear_attendance.setStyleSheet("background-color: #95a5a6; color: white;")
        
        btn_layout.addWidget(self.btn_add_attendance)
        btn_layout.addWidget(self.btn_refresh_attendance)
        btn_layout.addWidget(self.btn_clear_attendance)
        btn_layout.addStretch()
        
        attendance_layout.addLayout(btn_layout)
        
        # Table
        self.attendance_table = QTableWidget()
        self.attendance_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.attendance_table.horizontalHeader().setStretchLastSection(True)
        attendance_layout.addWidget(self.attendance_table)
        
        self.tabs.addTab(attendance_tab, '✅ Attendance')
    
    def load_dropdowns(self):
        """Load data for combo boxes."""
        try:
            cursor = self.db_connection.get_cursor()
            
            # Students
            cursor.execute("SELECT Student_ID, First_Name, Last_Name FROM Student ORDER BY Last_Name, First_Name")
            students = cursor.fetchall()
            
            self.student_combo.clear()
            self.attendance_student_combo.clear()
            for sid, fname, lname in students:
                text = f"{lname}, {fname} (ID: {sid})"
                self.student_combo.addItem(text, sid)
                self.attendance_student_combo.addItem(text, sid)
            
            # Courses
            cursor.execute("""
                SELECT c.Course_ID, c.Department_ID, c.name, d.name 
                FROM Course c
                JOIN Department d ON c.Department_ID = d.Department_id
                ORDER BY d.name, c.name
            """)
            courses = cursor.fetchall()
            
            self.marks_course_combo.clear()
            self.attendance_course_combo.clear()
            for cid, did, cname, dname in courses:
                text = f"{cname} ({dname}, ID: {cid}/{did})"
                self.marks_course_combo.addItem(text, (cid, did))
                self.attendance_course_combo.addItem(text, (cid, did))
        except Exception as e:
            show_warning(self, 'Load Error', f'Failed to load dropdowns:\n{str(e)}')
    
    def add_mark(self):
        """Add a new mark."""
        try:
            sid = self.student_combo.currentData()
            course_data = self.marks_course_combo.currentData()
            
            if not sid or not course_data:
                show_warning(self, 'Validation', 'Select student and course')
                return
            
            cid, did = course_data
            mark = self.mark_value.value()
            date = self.mark_date.date().toString('yyyy-MM-dd')
            
            cursor = self.db_connection.get_cursor()
            cursor.execute(
                "INSERT INTO Marks (student_id, course_id, dept_id, mark, mark_date) VALUES (%s, %s, %s, %s, %s)",
                (sid, cid, did, mark, date)
            )
            self.db_connection.commit()
            
            show_info(self, 'Success', 'Mark added successfully!')
            self.clear_marks_form()
            self.load_marks_data()
        except Exception as e:
            show_error(self, 'Error', f'Failed to add mark:\n{str(e)}')
    
    def update_mark(self):
        """Update selected mark."""
        if not self.current_mark_id:
            show_warning(self, 'Error', 'No mark selected')
            return
        
        try:
            mark = self.mark_value.value()
            date = self.mark_date.date().toString('yyyy-MM-dd')
            
            cursor = self.db_connection.get_cursor()
            cursor.execute(
                "UPDATE Marks SET mark = %s, mark_date = %s WHERE mark_id = %s",
                (mark, date, self.current_mark_id)
            )
            self.db_connection.commit()
            
            show_info(self, 'Success', 'Mark updated!')
            self.clear_marks_form()
            self.load_marks_data()
        except Exception as e:
            show_error(self, 'Error', f'Failed to update:\n{str(e)}')
    
    def on_mark_selected(self):
        """Handle mark selection."""
        items = self.marks_table.selectedItems()
        if not items:
            return
        
        row = items[0].row()
        self.current_mark_id = int(self.marks_table.item(row, 0).text())
        
        # Load into form
        sid = int(self.marks_table.item(row, 1).text())
        cid = int(self.marks_table.item(row, 2).text())
        did = int(self.marks_table.item(row, 3).text())
        mark = float(self.marks_table.item(row, 7).text())
        date_str = self.marks_table.item(row, 8).text()
        
        idx = self.student_combo.findData(sid)
        if idx >= 0:
            self.student_combo.setCurrentIndex(idx)
        
        idx = self.marks_course_combo.findData((cid, did))
        if idx >= 0:
            self.marks_course_combo.setCurrentIndex(idx)
        
        self.mark_value.setValue(mark)
        self.mark_date.setDate(QDate.fromString(date_str, 'yyyy-MM-dd'))
        
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
        """Load marks table data."""
        try:
            cursor = self.db_connection.get_cursor()
            cursor.execute("""
                SELECT m.mark_id, m.student_id, m.course_id, m.dept_id,
                       s.Last_Name || ', ' || s.First_Name,
                       c.name, d.name,
                       m.mark, m.mark_date
                FROM Marks m
                JOIN Student s ON m.student_id = s.Student_ID
                JOIN Course c ON m.course_id = c.Course_ID AND m.dept_id = c.Department_ID
                JOIN Department d ON m.dept_id = d.Department_id
                ORDER BY m.mark_date DESC
            """)
            rows = cursor.fetchall()
            
            headers = ['ID', 'SID', 'CID', 'DID', 'Student', 'Course', 'Dept', 'Mark', 'Date']
            self.marks_table.setRowCount(len(rows))
            self.marks_table.setColumnCount(len(headers))
            self.marks_table.setHorizontalHeaderLabels(headers)
            
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    item = QTableWidgetItem(str(val) if val else '')
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.marks_table.setItem(i, j, item)
            
            self.marks_table.resizeColumnsToContents()
        except Exception as e:
            show_error(self, 'Error', f'Failed to load marks:\n{str(e)}')
    
    def add_attendance(self):
        """Add attendance record."""
        try:
            sid = self.attendance_student_combo.currentData()
            course_data = self.attendance_course_combo.currentData()
            
            if not sid or not course_data:
                show_warning(self, 'Validation', 'Select student and course')
                return
            
            cid, did = course_data
            date = self.attendance_date.date().toString('yyyy-MM-dd')
            status = self.attendance_status.currentText()
            notes = self.attendance_notes.text().strip() or None
            
            cursor = self.db_connection.get_cursor()
            cursor.execute(
                "INSERT INTO Attendance (student_id, course_id, dept_id, attendance_date, status, notes) VALUES (%s, %s, %s, %s, %s, %s)",
                (sid, cid, did, date, status, notes)
            )
            self.db_connection.commit()
            
            show_info(self, 'Success', 'Attendance recorded!')
            self.clear_attendance_form()
            self.load_attendance_data()
        except Exception as e:
            show_error(self, 'Error', f'Failed to record:\n{str(e)}')
    
    def clear_attendance_form(self):
        """Clear attendance form."""
        self.attendance_student_combo.setCurrentIndex(0)
        self.attendance_course_combo.setCurrentIndex(0)
        self.attendance_date.setDate(QDate.currentDate())
        self.attendance_status.setCurrentIndex(0)
        self.attendance_notes.clear()
    
    def load_attendance_data(self):
        """Load attendance table data."""
        try:
            cursor = self.db_connection.get_cursor()
            cursor.execute("""
                SELECT a.attendance_id, a.student_id, a.course_id, a.dept_id,
                       s.Last_Name || ', ' || s.First_Name,
                       c.name, d.name,
                       a.attendance_date, a.status, a.notes
                FROM Attendance a
                JOIN Student s ON a.student_id = s.Student_ID
                JOIN Course c ON a.course_id = c.Course_ID AND a.dept_id = c.Department_ID
                JOIN Department d ON a.dept_id = d.Department_id
                ORDER BY a.attendance_date DESC
            """)
            rows = cursor.fetchall()
            
            headers = ['ID', 'SID', 'CID', 'DID', 'Student', 'Course', 'Dept', 'Date', 'Status', 'Notes']
            self.attendance_table.setRowCount(len(rows))
            self.attendance_table.setColumnCount(len(headers))
            self.attendance_table.setHorizontalHeaderLabels(headers)
            
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    item = QTableWidgetItem(str(val) if val else '')
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.attendance_table.setItem(i, j, item)
            
            self.attendance_table.resizeColumnsToContents()
        except Exception as e:
            show_error(self, 'Error', f'Failed to load attendance:\n{str(e)}')