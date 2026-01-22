"""
Assignments & Reservations Window
Interface for managing room reservations with conflict validation.
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QComboBox, QDateEdit,
                             QTimeEdit, QTableWidget, QTableWidgetItem, QMessageBox,
                             QGroupBox, QFormLayout, QSpinBox, QHeaderView)
from PyQt5.QtCore import Qt, QDate, QTime
from PyQt5.QtGui import QFont
from db_connection import get_db_connection


class ReservationWindow(QMainWindow):
    """Window for managing room reservations with conflict checking."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Try to get connection from parent (MainWindow) if available
        if parent and hasattr(parent, 'db_connection') and parent.db_connection is not None:
            self.db_connection = parent.db_connection
        else:
            self.db_connection = get_db_connection()
            if self.db_connection is None:
                raise Exception("No database connection available. Please check your database setup.")
        self.db_connection.connect()
        self.init_ui()
        self.load_data()
        self.load_dropdowns()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('Assignments & Reservations')
        self.setGeometry(50, 50, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Title
        title = QLabel('Room Reservations Management')
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Form group
        form_group = QGroupBox('New Reservation')
        form_layout = QFormLayout()
        form_group.setLayout(form_layout)
        
        # Reservation ID
        self.reservation_id = QLineEdit()
        form_layout.addRow('Reservation ID *', self.reservation_id)
        
        # Building and Room
        room_layout = QHBoxLayout()
        self.building = QComboBox()
        self.building.setEditable(True)
        self.room_no = QComboBox()
        self.room_no.setEditable(True)
        room_layout.addWidget(QLabel('Building:'))
        room_layout.addWidget(self.building)
        room_layout.addWidget(QLabel('Room No:'))
        room_layout.addWidget(self.room_no)
        form_layout.addRow('Room *', room_layout)
        
        # Course selection
        self.course_combo = QComboBox()
        self.course_combo.setEditable(False)
        form_layout.addRow('Course *', self.course_combo)
        
        # Instructor selection
        self.instructor_combo = QComboBox()
        self.instructor_combo.setEditable(False)
        form_layout.addRow('Instructor *', self.instructor_combo)
        
        # Date
        self.reserv_date = QDateEdit()
        self.reserv_date.setCalendarPopup(True)
        self.reserv_date.setDate(QDate.currentDate())
        self.reserv_date.setDisplayFormat('yyyy-MM-dd')
        form_layout.addRow('Reservation Date *', self.reserv_date)
        
        # Time
        time_layout = QHBoxLayout()
        self.start_time = QTimeEdit()
        self.start_time.setTime(QTime(8, 0))
        self.start_time.setDisplayFormat('HH:mm:ss')
        self.end_time = QTimeEdit()
        self.end_time.setTime(QTime(11, 0))
        self.end_time.setDisplayFormat('HH:mm:ss')
        time_layout.addWidget(QLabel('Start:'))
        time_layout.addWidget(self.start_time)
        time_layout.addWidget(QLabel('End:'))
        time_layout.addWidget(self.end_time)
        form_layout.addRow('Time *', time_layout)
        
        # Hours Number
        self.hours_number = QSpinBox()
        self.hours_number.setMinimum(1)
        self.hours_number.setMaximum(24)
        self.hours_number.setValue(3)
        form_layout.addRow('Hours Number *', self.hours_number)
        
        main_layout.addWidget(form_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.btn_check = QPushButton('Check Availability')
        self.btn_check.clicked.connect(self.check_availability)
        self.btn_check.setStyleSheet("background-color: #3498db; color: white; padding: 8px;")
        
        self.btn_create = QPushButton('Create Reservation')
        self.btn_create.clicked.connect(self.create_reservation)
        self.btn_create.setStyleSheet("background-color: #27ae60; color: white; padding: 8px;")
        
        self.btn_refresh = QPushButton('Refresh')
        self.btn_refresh.clicked.connect(self.load_data)
        self.btn_refresh.setStyleSheet("background-color: #95a5a6; color: white; padding: 8px;")
        
        self.btn_clear = QPushButton('Clear Form')
        self.btn_clear.clicked.connect(self.clear_form)
        self.btn_clear.setStyleSheet("background-color: #95a5a6; color: white; padding: 8px;")
        
        button_layout.addWidget(self.btn_check)
        button_layout.addWidget(self.btn_create)
        button_layout.addWidget(self.btn_refresh)
        button_layout.addWidget(self.btn_clear)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
        # Data table
        table_label = QLabel('Existing Reservations')
        table_label.setFont(QFont('Arial', 12, QFont.Bold))
        main_layout.addWidget(table_label)
        
        self.data_table = QTableWidget()
        self.data_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.data_table.horizontalHeader().setStretchLastSection(True)
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        main_layout.addWidget(self.data_table)
    
    def load_dropdowns(self):
        """Load data for combo boxes."""
        try:
            cursor = self.db_connection.get_cursor()
            
            # Load rooms
            cursor.execute("SELECT DISTINCT Building FROM Room ORDER BY Building")
            buildings = [row[0] for row in cursor.fetchall()]
            self.building.clear()
            self.building.addItems(buildings)
            
            # Load courses
            cursor.execute("""
                SELECT c.Course_ID, c.Department_ID, c.name as Course_Name, d.name as Department_Name
                FROM Course c
                JOIN Department d ON c.Department_ID = d.Department_id
                ORDER BY d.name, c.name
            """)
            courses = cursor.fetchall()
            self.course_combo.clear()
            for course_id, dept_id, course_name, dept_name in courses:
                display_text = f"{course_name} (Dept: {dept_name}, ID: {course_id}/{dept_id})"
                self.course_combo.addItem(display_text, (course_id, dept_id))
            
            # Load instructors
            cursor.execute("""
                SELECT i.Instructor_ID, i.Last_Name, i.First_Name, d.name as Department_Name
                FROM Instructor i
                JOIN Department d ON i.Department_ID = d.Department_id
                ORDER BY i.Last_Name, i.First_Name
            """)
            instructors = cursor.fetchall()
            self.instructor_combo.clear()
            for inst_id, last_name, first_name, dept_name in instructors:
                display_text = f"{first_name} {last_name} (Dept: {dept_name}, ID: {inst_id})"
                self.instructor_combo.addItem(display_text, inst_id)
            
            # Update room numbers when building changes
            self.building.currentTextChanged.connect(self.update_room_numbers)
            self.update_room_numbers()
            
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to load dropdown data:\n{str(e)}')
    
    def update_room_numbers(self):
        """Update room numbers based on selected building."""
        try:
            building = self.building.currentText()
            if not building:
                return
            
            cursor = self.db_connection.get_cursor()
            cursor.execute("SELECT RoomNo FROM Room WHERE Building = %s ORDER BY RoomNo", (building,))
            rooms = [str(row[0]) for row in cursor.fetchall()]
            self.room_no.clear()
            self.room_no.addItems(rooms)
        except Exception as e:
            pass  # Silently fail if building is not selected yet
    
    def check_availability(self):
        """Check room availability using CheckReservation function."""
        try:
            building = self.building.currentText().strip()
            room_no = self.room_no.currentText().strip()
            reserv_date = self.reserv_date.date().toString('yyyy-MM-dd')
            start_time = self.start_time.time().toString('HH:mm:ss')
            end_time = self.end_time.time().toString('HH:mm:ss')
            
            if not building or not room_no:
                QMessageBox.warning(self, 'Validation Error', 'Please select a building and room.')
                return
            
            # Call CheckReservation function
            cursor = self.db_connection.get_cursor()
            query = """
                SELECT CheckReservation(%s, %s, %s::date, %s::time, %s::time)
            """
            cursor.execute(query, (building, room_no, reserv_date, start_time, end_time))
            result = cursor.fetchone()[0]
            
            if result == 0:
                QMessageBox.information(self, 'Availability Check', 
                                      f'Room {building}-{room_no} is AVAILABLE on {reserv_date}\n'
                                      f'from {start_time} to {end_time}.\n\n'
                                      f'No conflicts found.')
            else:
                QMessageBox.warning(self, 'Availability Check', 
                                   f'Room {building}-{room_no} is NOT AVAILABLE on {reserv_date}\n'
                                   f'from {start_time} to {end_time}.\n\n'
                                   f'Found {result} conflicting reservation(s).\n'
                                   f'Please choose a different time slot.')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to check availability:\n{str(e)}')
    
    def validate_form(self):
        """Validate form inputs."""
        if not self.reservation_id.text().strip():
            QMessageBox.warning(self, 'Validation Error', 'Reservation ID is required.')
            return False
        
        if not self.building.currentText().strip() or not self.room_no.currentText().strip():
            QMessageBox.warning(self, 'Validation Error', 'Building and Room are required.')
            return False
        
        if self.course_combo.currentData() is None:
            QMessageBox.warning(self, 'Validation Error', 'Please select a course.')
            return False
        
        if self.instructor_combo.currentData() is None:
            QMessageBox.warning(self, 'Validation Error', 'Please select an instructor.')
            return False
        
        if self.start_time.time() >= self.end_time.time():
            QMessageBox.warning(self, 'Validation Error', 'Start time must be before end time.')
            return False
        
        return True
    
    def create_reservation(self):
        """Create a new reservation with conflict checking."""
        if not self.validate_form():
            return
        
        try:
            building = self.building.currentText().strip()
            room_no = self.room_no.currentText().strip()
            reserv_date = self.reserv_date.date().toString('yyyy-MM-dd')
            start_time = self.start_time.time().toString('HH:mm:ss')
            end_time = self.end_time.time().toString('HH:mm:ss')
            course_data = self.course_combo.currentData()
            instructor_id = self.instructor_combo.currentData()
            
            if course_data is None or instructor_id is None:
                QMessageBox.warning(self, 'Validation Error', 'Please select both course and instructor.')
                return
            
            course_id, dept_id = course_data
            
            # Check availability first
            cursor = self.db_connection.get_cursor()
            check_query = """
                SELECT CheckReservation(%s, %s, %s::date, %s::time, %s::time)
            """
            cursor.execute(check_query, (building, room_no, reserv_date, start_time, end_time))
            conflicts = cursor.fetchone()[0]
            
            if conflicts > 0:
                reply = QMessageBox.question(self, 'Conflict Detected', 
                                           f'Found {conflicts} conflicting reservation(s).\n'
                                           f'Do you still want to create this reservation?',
                                           QMessageBox.Yes | QMessageBox.No)
                if reply != QMessageBox.Yes:
                    return
            
            # Insert reservation (using autocommit mode)
            insert_query = """
                INSERT INTO Reservation 
                (Reservation_ID, Building, RoomNo, Course_ID, Department_ID, 
                 Instructor_ID, Reserv_Date, Start_Time, End_Time, Hours_Number)
                VALUES (%s, %s, %s, %s, %s, %s, %s::date, %s::time, %s::time, %s)
            """
            cursor.execute(insert_query, (
                int(self.reservation_id.text().strip()),
                building,
                room_no,
                course_id,
                dept_id,
                instructor_id,
                reserv_date,
                start_time,
                end_time,
                self.hours_number.value()
            ))
            
            self.db_connection.commit()
            
            QMessageBox.information(self, 'Success', 'Reservation created successfully!')
            self.clear_form()
            self.load_data()
                
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to create reservation:\n{str(e)}')
    
    def clear_form(self):
        """Clear all form fields."""
        self.reservation_id.clear()
        self.building.setCurrentIndex(0)
        self.room_no.setCurrentIndex(0)
        self.course_combo.setCurrentIndex(0)
        self.instructor_combo.setCurrentIndex(0)
        self.reserv_date.setDate(QDate.currentDate())
        self.start_time.setTime(QTime(8, 0))
        self.end_time.setTime(QTime(11, 0))
        self.hours_number.setValue(3)
    
    def load_data(self):
        """Load and display reservations."""
        try:
            query = """
                SELECT r.Reservation_ID, r.Building, r.RoomNo, 
                       c.name as Course_Name, d.name as Department_Name,
                       i.Last_Name || ', ' || i.First_Name as Instructor_Name,
                       r.Reserv_Date, r.Start_Time, r.End_Time, r.Hours_Number
                FROM Reservation r
                JOIN Course c ON r.Course_ID = c.Course_ID AND r.Department_ID = c.Department_ID
                JOIN Department d ON r.Department_ID = d.Department_id
                JOIN Instructor i ON r.Instructor_ID = i.Instructor_ID
                ORDER BY r.Reserv_Date DESC, r.Start_Time
            """
            cursor = self.db_connection.get_cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            column_names = ['Reservation ID', 'Building', 'Room No', 'Course', 'Department', 
                          'Instructor', 'Date', 'Start Time', 'End Time', 'Hours']
            
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
            import traceback
            error_msg = f'Failed to load reservations:\n{str(e)}'
            # Add helpful hints based on error type
            if 'does not exist' in str(e) or 'no such table' in str(e).lower():
                error_msg += '\n\nPossible causes:\n- Tables may not be initialized\n- Database schema may be missing'
            elif 'column' in str(e).lower() and 'does not exist' in str(e).lower():
                error_msg += '\n\nPossible causes:\n- Column name mismatch\n- Database schema may need updating'
            QMessageBox.warning(self, 'Error', error_msg)

