"""
Reporting & SQL Queries Window
Interface for executing complex SQL queries (a) through (j) with at least 5 functions.
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QComboBox, QTableWidget, 
                             QTableWidgetItem, QMessageBox, QGroupBox, QFormLayout,
                             QHeaderView, QLineEdit, QSpinBox, QDoubleSpinBox, QTextEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from db_connection import get_db_connection


class ReportingWindow(QMainWindow):
    """Window for executing reporting queries and SQL functions."""
    
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
        self.load_dropdowns()
        self.ensure_functions()
        self.ensure_student_columns()
    
    def ensure_student_columns(self):
        """Ensure Student table has group_id and section_id columns."""
        try:
            cursor = self.db_connection.get_cursor()
            # Check and add group_id
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND table_name = 'student' 
                    AND column_name = 'group_id'
                )
            """)
            if not cursor.fetchone()[0]:
                cursor.execute("ALTER TABLE Student ADD COLUMN group_id INTEGER DEFAULT 1")
            
            # Check and add section_id
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND table_name = 'student' 
                    AND column_name = 'section_id'
                )
            """)
            if not cursor.fetchone()[0]:
                cursor.execute("ALTER TABLE Student ADD COLUMN section_id INTEGER DEFAULT 1")
            
            self.db_connection.commit()
        except Exception as e:
            print(f"Note: Student columns check/create: {e}")
    
    def ensure_functions(self):
        """Ensure all SQL functions exist in the database."""
        import os
        try:
            # Try multiple possible paths
            sql_file_paths = [
                'Part2/Python App/reporting_functions.sql',
                'reporting_functions.sql',
                os.path.join(os.path.dirname(__file__), 'reporting_functions.sql')
            ]
            
            sql_script = None
            for path in sql_file_paths:
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        sql_script = f.read()
                    break
                except FileNotFoundError:
                    continue
            
            if sql_script:
                cursor = self.db_connection.get_cursor()
                # Execute the entire script
                cursor.execute(sql_script)
                self.db_connection.commit()
            else:
                # If file not found, create functions directly
                self.create_functions_directly()
        except Exception as e:
            print(f"Note: Functions may already exist: {e}")
            # Try to create functions directly anyway
            try:
                self.create_functions_directly()
            except Exception as e2:
                print(f"Note: Could not create functions: {e2}")
                # Functions might already exist, which is fine
    
    def create_functions_directly(self):
        """Create functions directly in the database."""
        cursor = self.db_connection.get_cursor()
        
        # Function 1: get_instructor_schedule
        cursor.execute("""
            CREATE OR REPLACE FUNCTION get_instructor_schedule(p_instructor_id INTEGER)
            RETURNS TABLE (
                reservation_id INTEGER, building VARCHAR, roomno VARCHAR,
                course_name VARCHAR, department_name VARCHAR, reserv_date DATE,
                start_time TIME, end_time TIME, hours_number INTEGER
            )
            LANGUAGE plpgsql AS $$
            BEGIN
                RETURN QUERY
                SELECT r.Reservation_ID, r.Building, r.RoomNo, c.name, d.name,
                       r.Reserv_Date, r.Start_Time, r.End_Time, r.Hours_Number
                FROM Reservation r
                JOIN Course c ON r.Course_ID = c.Course_ID AND r.Department_ID = c.Department_ID
                JOIN Department d ON r.Department_ID = d.Department_id
                WHERE r.Instructor_ID = p_instructor_id
                ORDER BY r.Reserv_Date, r.Start_Time;
            END;
            $$;
        """)
        
        # Function 2: get_passing_students
        cursor.execute("""
            CREATE OR REPLACE FUNCTION get_passing_students(
                p_course_id INTEGER DEFAULT NULL,
                p_dept_id INTEGER DEFAULT NULL,
                p_passing_grade NUMERIC DEFAULT 10.0
            )
            RETURNS TABLE (
                student_id INTEGER, student_name VARCHAR, course_id INTEGER,
                course_name VARCHAR, average_mark NUMERIC, mark_count INTEGER
            )
            LANGUAGE plpgsql AS $$
            BEGIN
                RETURN QUERY
                SELECT m.student_id, s.Last_Name || ', ' || s.First_Name,
                       m.course_id, c.name, ROUND(AVG(m.mark)::NUMERIC, 2),
                       COUNT(m.mark_id)::INTEGER
                FROM Marks m
                JOIN Student s ON m.student_id = s.Student_ID
                JOIN Course c ON m.course_id = c.Course_ID AND m.dept_id = c.Department_ID
                WHERE (p_course_id IS NULL OR m.course_id = p_course_id)
                  AND (p_dept_id IS NULL OR m.dept_id = p_dept_id)
                GROUP BY m.student_id, s.Last_Name, s.First_Name, m.course_id, c.name
                HAVING AVG(m.mark) >= p_passing_grade
                ORDER BY ROUND(AVG(m.mark)::NUMERIC, 2) DESC, s.Last_Name;
            END;
            $$;
        """)
        
        # Function 3: get_failed_modules
        cursor.execute("""
            CREATE OR REPLACE FUNCTION get_failed_modules(p_student_id INTEGER)
            RETURNS TABLE (
                course_id INTEGER, dept_id INTEGER, course_name VARCHAR,
                department_name VARCHAR, average_mark NUMERIC,
                passing_grade NUMERIC, mark_count INTEGER
            )
            LANGUAGE plpgsql AS $$
            BEGIN
                RETURN QUERY
                SELECT m.course_id, m.dept_id, c.name, d.name,
                       ROUND(AVG(m.mark)::NUMERIC, 2),
                       COALESCE(c.passing_grade, 10.0), COUNT(m.mark_id)::INTEGER
                FROM Marks m
                JOIN Course c ON m.course_id = c.Course_ID AND m.dept_id = c.Department_ID
                JOIN Department d ON m.dept_id = d.Department_id
                WHERE m.student_id = p_student_id
                GROUP BY m.course_id, m.dept_id, c.name, d.name, c.passing_grade
                HAVING AVG(m.mark) < COALESCE(c.passing_grade, 10.0)
                ORDER BY c.name;
            END;
            $$;
        """)
        
        # Function 4: check_resit_eligibility
        cursor.execute("""
            CREATE OR REPLACE FUNCTION check_resit_eligibility(p_student_id INTEGER)
            RETURNS TABLE (
                course_id INTEGER, dept_id INTEGER, course_name VARCHAR,
                department_name VARCHAR, average_mark NUMERIC,
                passing_grade NUMERIC, eligible BOOLEAN, reason TEXT
            )
            LANGUAGE plpgsql AS $$
            BEGIN
                RETURN QUERY
                SELECT m.course_id, m.dept_id, c.name, d.name,
                       ROUND(AVG(m.mark)::NUMERIC, 2), COALESCE(c.passing_grade, 10.0),
                       CASE WHEN AVG(m.mark) < COALESCE(c.passing_grade, 10.0) 
                            AND AVG(m.mark) >= (COALESCE(c.passing_grade, 10.0) - 2.0)
                       THEN TRUE ELSE FALSE END,
                       CASE WHEN AVG(m.mark) >= COALESCE(c.passing_grade, 10.0) 
                            THEN 'Passed - No resit needed'
                            WHEN AVG(m.mark) < (COALESCE(c.passing_grade, 10.0) - 2.0) 
                            THEN 'Grade too low for resit'
                            ELSE 'Eligible for resit examination' END
                FROM Marks m
                JOIN Course c ON m.course_id = c.Course_ID AND m.dept_id = c.Department_ID
                JOIN Department d ON m.dept_id = d.Department_id
                WHERE m.student_id = p_student_id
                GROUP BY m.course_id, m.dept_id, c.name, d.name, c.passing_grade
                HAVING AVG(m.mark) < COALESCE(c.passing_grade, 10.0)
                ORDER BY c.name;
            END;
            $$;
        """)
        
        # Function 5: check_attendance_exclusion
        cursor.execute("""
            CREATE OR REPLACE FUNCTION check_attendance_exclusion(
                p_student_id INTEGER, p_min_attendance_rate NUMERIC DEFAULT 0.75
            )
            RETURNS TABLE (
                course_id INTEGER, dept_id INTEGER, course_name VARCHAR,
                department_name VARCHAR, total_sessions INTEGER,
                attended_sessions INTEGER, attendance_rate NUMERIC,
                excluded BOOLEAN, reason TEXT
            )
            LANGUAGE plpgsql AS $$
            BEGIN
                RETURN QUERY
                SELECT a.course_id, a.dept_id, c.name, d.name,
                       COUNT(DISTINCT a.attendance_date)::INTEGER,
                       COUNT(CASE WHEN a.status IN ('Present', 'Late') THEN 1 END)::INTEGER,
                       ROUND((COUNT(CASE WHEN a.status IN ('Present', 'Late') THEN 1 END)::NUMERIC / 
                             NULLIF(COUNT(DISTINCT a.attendance_date), 0)) * 100, 2),
                       CASE WHEN (COUNT(CASE WHEN a.status IN ('Present', 'Late') THEN 1 END)::NUMERIC / 
                                 NULLIF(COUNT(DISTINCT a.attendance_date), 0)) < p_min_attendance_rate
                       THEN TRUE ELSE FALSE END,
                       CASE WHEN (COUNT(CASE WHEN a.status IN ('Present', 'Late') THEN 1 END)::NUMERIC / 
                                 NULLIF(COUNT(DISTINCT a.attendance_date), 0)) < p_min_attendance_rate
                       THEN 'Attendance below ' || (p_min_attendance_rate * 100)::TEXT || '% threshold'
                       ELSE 'Attendance acceptable' END
                FROM Attendance a
                JOIN Course c ON a.course_id = c.Course_ID AND a.dept_id = c.Department_ID
                JOIN Department d ON a.dept_id = d.Department_id
                WHERE a.student_id = p_student_id
                GROUP BY a.course_id, a.dept_id, c.name, d.name
                ORDER BY ROUND((COUNT(CASE WHEN a.status IN ('Present', 'Late') THEN 1 END)::NUMERIC / 
                               NULLIF(COUNT(DISTINCT a.attendance_date), 0)) * 100, 2) ASC, c.name;
            END;
            $$;
        """)
        
        self.db_connection.connection.commit()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('Reporting & SQL Queries')
        self.setGeometry(50, 50, 1400, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Title
        title = QLabel('Reporting & SQL Queries (a) through (j)')
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Query selection
        query_group = QGroupBox('Select Query')
        query_layout = QHBoxLayout()
        query_group.setLayout(query_layout)
        
        self.query_combo = QComboBox()
        self.query_combo.addItems([
            '(a) List of students by group',
            '(b) List of students by section',
            '(c) Time table of instructor [FUNCTION]',
            '(d) Time table by section',
            '(e) Students who passed [FUNCTION]',
            '(f) Disqualifying marks',
            '(g) Average marks by course/group',
            '(h) Students with failing grade [FUNCTION]',
            '(i) Eligible for resit [FUNCTION]',
            '(j) Excluded students [FUNCTION]'
        ])
        self.query_combo.currentIndexChanged.connect(self.on_query_changed)
        query_layout.addWidget(QLabel('Query:'))
        query_layout.addWidget(self.query_combo)
        query_layout.addStretch()
        
        main_layout.addWidget(query_group)
        
        # Parameters group
        self.params_group = QGroupBox('Query Parameters')
        self.params_layout = QFormLayout()
        self.params_group.setLayout(self.params_layout)
        main_layout.addWidget(self.params_group)
        
        # Initialize parameter widgets
        self.param_widgets = {}
        self.setup_parameters()
        
        # Execute button
        button_layout = QHBoxLayout()
        
        self.btn_execute = QPushButton('Execute Query')
        self.btn_execute.clicked.connect(self.execute_query)
        self.btn_execute.setStyleSheet("background-color: #27ae60; color: white; padding: 8px; font-weight: bold;")
        
        self.btn_refresh = QPushButton('Refresh')
        self.btn_refresh.clicked.connect(self.refresh_query)
        self.btn_refresh.setStyleSheet("background-color: #3498db; color: white; padding: 8px;")
        
        button_layout.addWidget(self.btn_execute)
        button_layout.addWidget(self.btn_refresh)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
        # Results table
        results_label = QLabel('Query Results')
        results_label.setFont(QFont('Arial', 12, QFont.Bold))
        main_layout.addWidget(results_label)
        
        self.results_table = QTableWidget()
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        main_layout.addWidget(self.results_table)
        
        # SQL display
        sql_group = QGroupBox('Generated SQL')
        sql_layout = QVBoxLayout()
        sql_group.setLayout(sql_layout)
        
        self.sql_display = QTextEdit()
        self.sql_display.setReadOnly(True)
        self.sql_display.setMaximumHeight(100)
        sql_layout.addWidget(self.sql_display)
        
        main_layout.addWidget(sql_group)
    
    def setup_parameters(self):
        """Setup parameter widgets for queries."""
        # Clear existing widgets
        while self.params_layout.count():
            child = self.params_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        self.param_widgets.clear()
        
        query_index = self.query_combo.currentIndex()
        
        if query_index == 0:  # (a) Students by group
            group_id = QSpinBox()
            group_id.setMinimum(1)
            group_id.setMaximum(100)
            group_id.setValue(1)
            self.params_layout.addRow('Group ID:', group_id)
            self.param_widgets['group_id'] = group_id
            
        elif query_index == 1:  # (b) Students by section
            section_id = QSpinBox()
            section_id.setMinimum(1)
            section_id.setMaximum(100)
            section_id.setValue(1)
            self.params_layout.addRow('Section ID:', section_id)
            self.param_widgets['section_id'] = section_id
            
        elif query_index == 2:  # (c) Instructor schedule
            instructor_combo = QComboBox()
            self.params_layout.addRow('Instructor:', instructor_combo)
            self.param_widgets['instructor_id'] = instructor_combo
            self.load_instructors()
            
        elif query_index == 3:  # (d) Time table by section
            section_id = QSpinBox()
            section_id.setMinimum(1)
            section_id.setMaximum(100)
            section_id.setValue(1)
            self.params_layout.addRow('Section ID:', section_id)
            self.param_widgets['section_id'] = section_id
            
        elif query_index == 4:  # (e) Passing students
            course_combo = QComboBox()
            course_combo.addItem('All Courses', None)
            self.params_layout.addRow('Course (optional):', course_combo)
            self.param_widgets['course_id'] = course_combo
            passing_grade = QDoubleSpinBox()
            passing_grade.setMinimum(0.0)
            passing_grade.setMaximum(20.0)
            passing_grade.setValue(10.0)
            passing_grade.setDecimals(2)
            self.params_layout.addRow('Passing Grade:', passing_grade)
            self.param_widgets['passing_grade'] = passing_grade
            self.load_courses()
            
        elif query_index == 5:  # (f) Disqualifying marks
            threshold = QDoubleSpinBox()
            threshold.setMinimum(0.0)
            threshold.setMaximum(20.0)
            threshold.setValue(5.0)
            threshold.setDecimals(2)
            self.params_layout.addRow('Threshold (<):', threshold)
            self.param_widgets['threshold'] = threshold
            
        elif query_index == 6:  # (g) Avg marks by course/group
            group_id = QSpinBox()
            group_id.setMinimum(1)
            group_id.setMaximum(100)
            group_id.setValue(1)
            self.params_layout.addRow('Group ID (optional, 0 for all):', group_id)
            self.param_widgets['group_id'] = group_id
            
        elif query_index == 7:  # (h) Failed modules
            student_combo = QComboBox()
            self.params_layout.addRow('Student:', student_combo)
            self.param_widgets['student_id'] = student_combo
            self.load_students()
            
        elif query_index == 8:  # (i) Resit eligibility
            student_combo = QComboBox()
            self.params_layout.addRow('Student:', student_combo)
            self.param_widgets['student_id'] = student_combo
            self.load_students()
            
        elif query_index == 9:  # (j) Excluded students
            student_combo = QComboBox()
            self.params_layout.addRow('Student:', student_combo)
            self.param_widgets['student_id'] = student_combo
            min_rate = QDoubleSpinBox()
            min_rate.setMinimum(0.0)
            min_rate.setMaximum(100.0)
            min_rate.setValue(75.0)
            min_rate.setDecimals(2)
            self.params_layout.addRow('Min Attendance Rate (%):', min_rate)
            self.param_widgets['min_rate'] = min_rate
            self.load_students()
    
    def on_query_changed(self):
        """Handle query selection change."""
        self.setup_parameters()
    
    def load_dropdowns(self):
        """Load data for dropdowns."""
        self.load_instructors()
        self.load_courses()
        self.load_students()
    
    def load_instructors(self):
        """Load instructors for dropdown."""
        try:
            cursor = self.db_connection.get_cursor()
            cursor.execute("""
                SELECT Instructor_ID, Last_Name, First_Name 
                FROM Instructor 
                ORDER BY Last_Name, First_Name
            """)
            instructors = cursor.fetchall()
            
            if 'instructor_id' in self.param_widgets:
                combo = self.param_widgets['instructor_id']
                combo.clear()
                for inst_id, last_name, first_name in instructors:
                    combo.addItem(f"{last_name}, {first_name} (ID: {inst_id})", inst_id)
        except Exception as e:
            pass
    
    def load_courses(self):
        """Load courses for dropdown."""
        try:
            cursor = self.db_connection.get_cursor()
            cursor.execute("""
                SELECT c.Course_ID, c.Department_ID, c.name, d.name as dept_name
                FROM Course c
                JOIN Department d ON c.Department_ID = d.Department_id
                ORDER BY d.name, c.name
            """)
            courses = cursor.fetchall()
            
            if 'course_id' in self.param_widgets:
                combo = self.param_widgets['course_id']
                if combo.count() == 0 or combo.itemData(0) is None:
                    combo.addItem('All Courses', None)
                for course_id, dept_id, course_name, dept_name in courses:
                    display_text = f"{course_name} (Dept: {dept_name}, ID: {course_id}/{dept_id})"
                    combo.addItem(display_text, (course_id, dept_id))
        except Exception as e:
            pass
    
    def load_students(self):
        """Load students for dropdown."""
        try:
            cursor = self.db_connection.get_cursor()
            cursor.execute("""
                SELECT Student_ID, Last_Name, First_Name 
                FROM Student 
                ORDER BY Last_Name, First_Name
            """)
            students = cursor.fetchall()
            
            if 'student_id' in self.param_widgets:
                combo = self.param_widgets['student_id']
                combo.clear()
                for student_id, last_name, first_name in students:
                    combo.addItem(f"{last_name}, {first_name} (ID: {student_id})", student_id)
        except Exception as e:
            pass
    
    def execute_query(self):
        """Execute the selected query."""
        query_index = self.query_combo.currentIndex()
        
        try:
            if query_index == 0:
                self.query_a_students_by_group()
            elif query_index == 1:
                self.query_b_students_by_section()
            elif query_index == 2:
                self.query_c_instructor_schedule()
            elif query_index == 3:
                self.query_d_timetable_by_section()
            elif query_index == 4:
                self.query_e_passing_students()
            elif query_index == 5:
                self.query_f_disqualifying_marks()
            elif query_index == 6:
                self.query_g_avg_marks_by_course_group()
            elif query_index == 7:
                self.query_h_failed_modules()
            elif query_index == 8:
                self.query_i_resit_eligibility()
            elif query_index == 9:
                self.query_j_excluded_students()
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to execute query:\n{str(e)}')
    
    def refresh_query(self):
        """Refresh current query."""
        self.execute_query()
    
    def display_results(self, results, column_names, sql_text=""):
        """Display query results in table."""
        self.results_table.setRowCount(len(results))
        self.results_table.setColumnCount(len(column_names))
        self.results_table.setHorizontalHeaderLabels(column_names)
        
        for row_idx, row in enumerate(results):
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value) if value is not None else '')
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.results_table.setItem(row_idx, col_idx, item)
        
        self.results_table.resizeColumnsToContents()
        self.sql_display.setText(sql_text)
    
    # Query implementations
    def query_a_students_by_group(self):
        """(a) List of students by group"""
        group_id = self.param_widgets['group_id'].value()
        
        query = "SELECT * FROM Student WHERE group_id = %s ORDER BY Last_Name, First_Name"
        sql_text = f"SELECT * FROM Student WHERE group_id = {group_id} ORDER BY Last_Name, First_Name"
        
        cursor = self.db_connection.get_cursor()
        cursor.execute(query, (group_id,))
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        
        self.display_results(results, column_names, sql_text)
    
    def query_b_students_by_section(self):
        """(b) List of students by section"""
        section_id = self.param_widgets['section_id'].value()
        
        query = "SELECT * FROM Student WHERE section_id = %s ORDER BY Last_Name, First_Name"
        sql_text = f"SELECT * FROM Student WHERE section_id = {section_id} ORDER BY Last_Name, First_Name"
        
        cursor = self.db_connection.get_cursor()
        cursor.execute(query, (section_id,))
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        
        self.display_results(results, column_names, sql_text)
    
    def query_c_instructor_schedule(self):
        """(c) Time table of instructor [FUNCTION]"""
        instructor_id = self.param_widgets['instructor_id'].currentData()
        if instructor_id is None:
            QMessageBox.warning(self, 'Validation Error', 'Please select an instructor.')
            return
        
        query = "SELECT * FROM get_instructor_schedule(%s)"
        sql_text = f"SELECT * FROM get_instructor_schedule({instructor_id})"
        
        cursor = self.db_connection.get_cursor()
        cursor.execute(query, (instructor_id,))
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        
        self.display_results(results, column_names, sql_text)
    
    def query_d_timetable_by_section(self):
        """(d) Time table by section"""
        section_id = self.param_widgets['section_id'].value()
        
        query = """
            SELECT DISTINCT r.Reserv_Date, r.Start_Time, r.End_Time,
                   r.Building || '-' || r.RoomNo as Room,
                   c.name as Course_Name, d.name as Department_Name,
                   i.Last_Name || ', ' || i.First_Name as Instructor_Name
            FROM Reservation r
            JOIN Course c ON r.Course_ID = c.Course_ID AND r.Department_ID = c.Department_ID
            JOIN Department d ON r.Department_ID = d.Department_id
            JOIN Instructor i ON r.Instructor_ID = i.Instructor_ID
            JOIN Enrollment e ON e.Course_ID = r.Course_ID AND e.Dept_ID = r.Department_ID
            JOIN Student s ON e.Student_ID = s.Student_ID
            WHERE s.section_id = %s
            ORDER BY r.Reserv_Date, r.Start_Time
        """
        sql_text = f"""SELECT DISTINCT r.Reserv_Date, r.Start_Time, r.End_Time,
                   r.Building || '-' || r.RoomNo as Room,
                   c.name as Course_Name, d.name as Department_Name,
                   i.Last_Name || ', ' || i.First_Name as Instructor_Name
            FROM Reservation r
            JOIN Course c ON r.Course_ID = c.Course_ID AND r.Department_ID = c.Department_ID
            JOIN Department d ON r.Department_ID = d.Department_id
            JOIN Instructor i ON r.Instructor_ID = i.Instructor_ID
            JOIN Enrollment e ON e.Course_ID = r.Course_ID AND e.Dept_ID = r.Department_ID
            JOIN Student s ON e.Student_ID = s.Student_ID
            WHERE s.section_id = {section_id}
            ORDER BY r.Reserv_Date, r.Start_Time"""
        
        cursor = self.db_connection.get_cursor()
        cursor.execute(query, (section_id,))
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        
        self.display_results(results, column_names, sql_text)
    
    def query_e_passing_students(self):
        """(e) Students who passed [FUNCTION]"""
        course_data = self.param_widgets['course_id'].currentData()
        passing_grade = self.param_widgets['passing_grade'].value()
        
        course_id = None
        dept_id = None
        if course_data:
            course_id, dept_id = course_data
        
        query = "SELECT * FROM get_passing_students(%s, %s, %s)"
        sql_text = f"SELECT * FROM get_passing_students({course_id if course_id else 'NULL'}, {dept_id if dept_id else 'NULL'}, {passing_grade})"
        
        cursor = self.db_connection.get_cursor()
        cursor.execute(query, (course_id, dept_id, passing_grade))
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        
        self.display_results(results, column_names, sql_text)
    
    def query_f_disqualifying_marks(self):
        """(f) Disqualifying marks"""
        threshold = self.param_widgets['threshold'].value()
        
        query = """
            SELECT m.mark_id, m.student_id, s.Last_Name || ', ' || s.First_Name as Student_Name,
                   m.course_id, c.name as Course_Name, m.mark, m.mark_date
            FROM Marks m
            JOIN Student s ON m.student_id = s.Student_ID
            JOIN Course c ON m.course_id = c.Course_ID AND m.dept_id = c.Department_ID
            WHERE m.mark < %s
            ORDER BY m.mark ASC, s.Last_Name
        """
        sql_text = f"""SELECT m.mark_id, m.student_id, s.Last_Name || ', ' || s.First_Name as Student_Name,
                   m.course_id, c.name as Course_Name, m.mark, m.mark_date
            FROM Marks m
            JOIN Student s ON m.student_id = s.Student_ID
            JOIN Course c ON m.course_id = c.Course_ID AND m.dept_id = c.Department_ID
            WHERE m.mark < {threshold}
            ORDER BY m.mark ASC, s.Last_Name"""
        
        cursor = self.db_connection.get_cursor()
        cursor.execute(query, (threshold,))
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        
        self.display_results(results, column_names, sql_text)
    
    def query_g_avg_marks_by_course_group(self):
        """(g) Average marks by course/group"""
        group_id = self.param_widgets['group_id'].value()
        
        if group_id == 0:
            query = """
                SELECT c.Course_ID, c.name as Course_Name, d.name as Department_Name,
                       ROUND(AVG(m.mark)::NUMERIC, 2) as Average_Mark,
                       COUNT(m.mark_id) as Mark_Count
                FROM Marks m
                JOIN Course c ON m.course_id = c.Course_ID AND m.dept_id = c.Department_ID
                JOIN Department d ON m.dept_id = d.Department_id
                GROUP BY c.Course_ID, c.name, d.name
                ORDER BY Average_Mark DESC
            """
            sql_text = query
        else:
            query = """
                SELECT c.Course_ID, c.name as Course_Name, d.name as Department_Name,
                       ROUND(AVG(m.mark)::NUMERIC, 2) as Average_Mark,
                       COUNT(m.mark_id) as Mark_Count
                FROM Marks m
                JOIN Course c ON m.course_id = c.Course_ID AND m.dept_id = c.Department_ID
                JOIN Department d ON m.dept_id = d.Department_id
                JOIN Student s ON m.student_id = s.Student_ID
                WHERE s.group_id = %s
                GROUP BY c.Course_ID, c.name, d.name
                ORDER BY Average_Mark DESC
            """
            sql_text = f"""SELECT c.Course_ID, c.name as Course_Name, d.name as Department_Name,
                       ROUND(AVG(m.mark)::NUMERIC, 2) as Average_Mark,
                       COUNT(m.mark_id) as Mark_Count
                FROM Marks m
                JOIN Course c ON m.course_id = c.Course_ID AND m.dept_id = c.Department_ID
                JOIN Department d ON m.dept_id = d.Department_id
                JOIN Student s ON m.student_id = s.Student_ID
                WHERE s.group_id = {group_id}
                GROUP BY c.Course_ID, c.name, d.name
                ORDER BY Average_Mark DESC"""
        
        cursor = self.db_connection.get_cursor()
        if group_id == 0:
            cursor.execute(query)
        else:
            cursor.execute(query, (group_id,))
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        
        self.display_results(results, column_names, sql_text)
    
    def query_h_failed_modules(self):
        """(h) Students with failing grade [FUNCTION]"""
        student_id = self.param_widgets['student_id'].currentData()
        if student_id is None:
            QMessageBox.warning(self, 'Validation Error', 'Please select a student.')
            return
        
        query = "SELECT * FROM get_failed_modules(%s)"
        sql_text = f"SELECT * FROM get_failed_modules({student_id})"
        
        cursor = self.db_connection.get_cursor()
        cursor.execute(query, (student_id,))
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        
        self.display_results(results, column_names, sql_text)
    
    def query_i_resit_eligibility(self):
        """(i) Eligible for resit [FUNCTION]"""
        student_id = self.param_widgets['student_id'].currentData()
        if student_id is None:
            QMessageBox.warning(self, 'Validation Error', 'Please select a student.')
            return
        
        query = "SELECT * FROM check_resit_eligibility(%s)"
        sql_text = f"SELECT * FROM check_resit_eligibility({student_id})"
        
        cursor = self.db_connection.get_cursor()
        cursor.execute(query, (student_id,))
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        
        self.display_results(results, column_names, sql_text)
    
    def query_j_excluded_students(self):
        """(j) Excluded students [FUNCTION]"""
        student_id = self.param_widgets['student_id'].currentData()
        if student_id is None:
            QMessageBox.warning(self, 'Validation Error', 'Please select a student.')
            return
        
        min_rate = self.param_widgets['min_rate'].value() / 100.0  # Convert to decimal
        
        query = "SELECT * FROM check_attendance_exclusion(%s, %s)"
        sql_text = f"SELECT * FROM check_attendance_exclusion({student_id}, {min_rate})"
        
        cursor = self.db_connection.get_cursor()
        cursor.execute(query, (student_id, min_rate))
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        
        self.display_results(results, column_names, sql_text)

