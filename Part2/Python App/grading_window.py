"""
Grading & Results Processing Window
Interface for calculating student averages and processing results.
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QComboBox, QTableWidget, 
                             QTableWidgetItem, QMessageBox, QGroupBox, QFormLayout,
                             QHeaderView, QDoubleSpinBox, QCheckBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from window_base import get_connection_from_parent, show_error, show_info, show_warning


class GradingWindow(QMainWindow):
    """Window for grading and results processing."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Get connection from parent
        try:
            self.db_connection = get_connection_from_parent(parent)
        except Exception as e:
            show_error(self, "Connection Error", 
                      f"Could not access database connection:\n{str(e)}")
            raise
        
        self.passing_grade = 10.0  # Default passing grade
        self.init_ui()
        
        # Ensure column exists BEFORE loading courses
        self.ensure_passing_grade_column()
        self.load_courses()
    
    def _is_demo_mode(self):
        """Check if using demo database (SQLite)."""
        try:
            from db_connection_demo import DemoDatabaseConnection
            return isinstance(self.db_connection, DemoDatabaseConnection)
        except:
            return False
    
    def ensure_passing_grade_column(self):
        """Ensure Course table has Passing_Grade column, add if not."""
        try:
            cursor = self.db_connection.get_cursor()
            is_demo = self._is_demo_mode()
            
            if is_demo:
                # SQLite - check using PRAGMA
                cursor.execute("PRAGMA table_info(Course)")
                cols = [row[1].lower() for row in cursor.fetchall()]
                if 'passing_grade' not in cols:
                    cursor.execute("ALTER TABLE Course ADD COLUMN passing_grade REAL DEFAULT 10.0")
                    cursor.execute("UPDATE Course SET passing_grade = 10.0 WHERE passing_grade IS NULL")
                    self.db_connection.commit()
                    print("Added passing_grade column to Course table (SQLite)")
            else:
                # PostgreSQL - check using information_schema
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'course' 
                    AND column_name = 'passing_grade'
                """)
                
                if cursor.fetchone() is None:
                    # Column doesn't exist, add it
                    cursor.execute("""
                        ALTER TABLE Course 
                        ADD COLUMN passing_grade NUMERIC(4,2) DEFAULT 10.0 
                        CHECK (passing_grade >= 0 AND passing_grade <= 20)
                    """)
                    cursor.execute("UPDATE Course SET passing_grade = 10.0 WHERE passing_grade IS NULL")
                    self.db_connection.commit()
                    print("Added passing_grade column to Course table (PostgreSQL)")
                    
        except Exception as e:
            # If error occurs, column might already exist or there's another issue
            print(f"Note: Passing grade column check: {e}")
            # Try to rollback in case of error
            try:
                self.db_connection.rollback()
            except:
                pass
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('Grading & Results Processing - University Database')
        self.setGeometry(50, 50, 1400, 900)
        
        # Apply modern styling
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
            QComboBox {
                padding: 8px;
                border: 2px solid #dcdde1;
                border-radius: 5px;
                background-color: white;
            }
            QPushButton {
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11px;
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
        
        # Title
        title = QLabel('📊 Grading & Results Processing')
        title.setFont(QFont('Segoe UI', 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; background-color: white; padding: 20px; border-radius: 10px;")
        main_layout.addWidget(title)
        
        # Control panel
        control_group = QGroupBox('Results Calculation')
        control_layout = QFormLayout()
        control_layout.setSpacing(15)
        control_group.setLayout(control_layout)
        
        # Course selection
        self.course_combo = QComboBox()
        self.course_combo.setEditable(False)
        self.course_combo.currentIndexChanged.connect(self.on_course_changed)
        control_layout.addRow('Select Course:', self.course_combo)
        
        # Passing grade override
        passing_grade_layout = QHBoxLayout()
        self.passing_grade_override = QDoubleSpinBox()
        self.passing_grade_override.setMinimum(0.0)
        self.passing_grade_override.setMaximum(20.0)
        self.passing_grade_override.setDecimals(2)
        self.passing_grade_override.setValue(10.0)
        self.passing_grade_override.setSingleStep(0.5)
        self.use_override = QCheckBox('Use custom passing grade')
        passing_grade_layout.addWidget(self.use_override)
        passing_grade_layout.addWidget(self.passing_grade_override)
        passing_grade_layout.addWidget(QLabel('(Default: 10.0/20)'))
        passing_grade_layout.addStretch()
        control_layout.addRow('Passing Grade:', passing_grade_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.btn_calculate = QPushButton('📈 Calculate Results')
        self.btn_calculate.clicked.connect(self.calculate_results)
        self.btn_calculate.setStyleSheet("background-color: #27ae60; color: white;")
        
        self.btn_refresh = QPushButton('🔃 Refresh')
        self.btn_refresh.clicked.connect(self.load_results)
        self.btn_refresh.setStyleSheet("background-color: #3498db; color: white;")
        
        button_layout.addWidget(self.btn_calculate)
        button_layout.addWidget(self.btn_refresh)
        button_layout.addStretch()
        
        control_layout.addRow('', button_layout)
        
        main_layout.addWidget(control_group)
        
        # Results table
        results_label = QLabel('📋 Student Results')
        results_label.setFont(QFont('Segoe UI', 14, QFont.Bold))
        results_label.setStyleSheet("color: #2c3e50; padding: 10px;")
        main_layout.addWidget(results_label)
        
        self.results_table = QTableWidget()
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.results_table.setStyleSheet("""
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
        main_layout.addWidget(self.results_table)
        
        # Summary group
        summary_group = QGroupBox('Summary Statistics')
        summary_layout = QVBoxLayout()
        summary_group.setLayout(summary_layout)
        
        self.summary_label = QLabel('💡 Select a course and calculate results to see statistics.')
        self.summary_label.setWordWrap(True)
        self.summary_label.setStyleSheet("padding: 10px; font-size: 11px;")
        summary_layout.addWidget(self.summary_label)
        
        main_layout.addWidget(summary_group)
    
    def load_courses(self):
        """Load courses for selection."""
        try:
            cursor = self.db_connection.get_cursor()
            
            # First check if passing_grade column exists
            cursor.execute("""
                SELECT c.Course_ID, c.Department_ID, c.name as Course_Name, d.name as Department_Name
                FROM Course c
                JOIN Department d ON c.Department_ID = d.Department_id
                ORDER BY d.name, c.name
            """)
            courses_basic = cursor.fetchall()
            
            # Try to get passing_grade if column exists
            try:
                cursor.execute("""
                    SELECT c.Course_ID, c.Department_ID, c.name as Course_Name, d.name as Department_Name,
                           COALESCE(c.passing_grade, 10.0) as passing_grade
                    FROM Course c
                    JOIN Department d ON c.Department_ID = d.Department_id
                    ORDER BY d.name, c.name
                """)
                courses = cursor.fetchall()
            except:
                # If passing_grade column doesn't exist, use default
                courses = [(c[0], c[1], c[2], c[3], 10.0) for c in courses_basic]
            
            self.course_combo.clear()
            for course_id, dept_id, course_name, dept_name, *passing_grade_tuple in courses:
                passing_grade = passing_grade_tuple[0] if passing_grade_tuple else 10.0
                display_text = f"{course_name} (Dept: {dept_name}, ID: {course_id}/{dept_id})"
                self.course_combo.addItem(display_text, (course_id, dept_id, passing_grade))
                
        except Exception as e:
            show_warning(self, 'Error', f'Failed to load courses:\n{str(e)}')
    
    def on_course_changed(self):
        """Handle course selection change."""
        course_data = self.course_combo.currentData()
        if course_data:
            _, _, passing_grade = course_data
            if not self.use_override.isChecked():
                self.passing_grade_override.setValue(float(passing_grade))
    
    def get_passing_grade(self):
        """Get the passing grade to use."""
        if self.use_override.isChecked():
            return self.passing_grade_override.value()
        else:
            course_data = self.course_combo.currentData()
            if course_data:
                _, _, passing_grade = course_data
                return float(passing_grade)
            return 10.0
    
    def calculate_results(self):
        """Calculate student results for selected course."""
        course_data = self.course_combo.currentData()
        if course_data is None:
            show_warning(self, 'Validation Error', 'Please select a course.')
            return
        
        course_id, dept_id, _ = course_data
        passing_grade = self.get_passing_grade()
        
        try:
            cursor = self.db_connection.get_cursor()
            
            # Calculate averages for each student in the course
            query = """
                SELECT 
                    m.student_id,
                    s.Last_Name || ', ' || s.First_Name as Student_Name,
                    COUNT(m.mark_id) as Mark_Count,
                    ROUND(CAST(AVG(m.mark) AS NUMERIC), 2) as Average_Mark,
                    MIN(m.mark) as Min_Mark,
                    MAX(m.mark) as Max_Mark,
                    CASE 
                        WHEN ROUND(CAST(AVG(m.mark) AS NUMERIC), 2) >= %s THEN 'PASSED'
                        ELSE 'FAILED'
                    END as Result
                FROM Marks m
                JOIN Student s ON m.student_id = s.Student_ID
                WHERE m.course_id = %s AND m.dept_id = %s
                GROUP BY m.student_id, s.Last_Name, s.First_Name
                ORDER BY Average_Mark DESC, s.Last_Name
            """
            
            cursor.execute(query, (passing_grade, course_id, dept_id))
            results = cursor.fetchall()
            
            if not results:
                show_info(self, 'No Results', 'No marks found for this course.')
                return
            
            # Display results
            column_names = ['Student ID', 'Student Name', 'Number of Marks', 
                          'Average Mark', 'Min Mark', 'Max Mark', 'Result']
            
            self.results_table.setRowCount(len(results))
            self.results_table.setColumnCount(len(column_names))
            self.results_table.setHorizontalHeaderLabels(column_names)
            
            passed_count = 0
            failed_count = 0
            
            for row_idx, row in enumerate(results):
                student_id, student_name, mark_count, avg_mark, min_mark, max_mark, result = row
                
                # Color code based on result
                for col_idx, value in enumerate(row):
                    item = QTableWidgetItem(str(value) if value is not None else '')
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    
                    # Highlight failed students
                    if result == 'FAILED':
                        from PyQt5.QtGui import QColor
                        item.setBackground(QColor(255, 200, 200) if col_idx != 6 else QColor(231, 76, 60))
                        if col_idx == 6:
                            item.setForeground(QColor(255, 255, 255))
                    elif result == 'PASSED':
                        from PyQt5.QtGui import QColor
                        item.setBackground(QColor(200, 255, 200) if col_idx != 6 else QColor(39, 174, 96))
                        if col_idx == 6:
                            item.setForeground(QColor(255, 255, 255))
                    
                    self.results_table.setItem(row_idx, col_idx, item)
                
                if result == 'PASSED':
                    passed_count += 1
                else:
                    failed_count += 1
            
            self.results_table.resizeColumnsToContents()
            
            # Update summary
            total_students = len(results)
            pass_rate = (passed_count / total_students * 100) if total_students > 0 else 0
            
            summary_text = f"""
            <b>Course Results Summary</b><br><br>
            <b>Total Students:</b> {total_students}<br>
            <b>Passed:</b> {passed_count} ({pass_rate:.1f}%)<br>
            <b>Failed:</b> {failed_count} ({100 - pass_rate:.1f}%)<br>
            <b>Passing Grade:</b> {passing_grade}/20<br><br>
            <i>Note: Students with average mark below {passing_grade}/20 are marked as FAILED.</i>
            """
            self.summary_label.setText(summary_text)
            
            show_info(self, 'Success', 
                     f'Results calculated successfully!\n\n'
                     f'Total Students: {total_students}\n'
                     f'Passed: {passed_count}\n'
                     f'Failed: {failed_count}')
            
        except Exception as e:
            show_error(self, 'Error', f'Failed to calculate results:\n{str(e)}')
    
    def load_results(self):
        """Load and display results (recalculate)."""
        self.calculate_results()