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
from db_connection import get_db_connection
import psycopg2
import os


class GradingWindow(QMainWindow):
    """Window for grading and results processing."""
    
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
        self.passing_grade = 10.0  # Default passing grade (can be overridden per course)
        self.init_ui()
        self.load_courses()
        self.ensure_passing_grade_column()
    
    def ensure_passing_grade_column(self):
        """Ensure Course table has Passing_Grade column, add if not."""
        try:
            cursor = self.db_connection.get_cursor()
            # Check if column exists (Postgres vs SQLite)
            if os.getenv('USE_DEMO_DB', '0') == '1':
                cursor.execute("PRAGMA table_info('Course')")
                cols = [row[1] for row in cursor.fetchall()]
                if 'passing_grade' not in cols:
                    cursor.execute("ALTER TABLE Course ADD COLUMN passing_grade REAL DEFAULT 10.0")
                    cursor.execute("UPDATE Course SET passing_grade = 10.0 WHERE passing_grade IS NULL")
                    self.db_connection.commit()
            else:
                # Check if column exists
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_schema = 'public' 
                        AND table_name = 'course' 
                        AND column_name = 'passing_grade'
                    )
                """)
                if not cursor.fetchone()[0]:
                    # Add passing_grade column with default value
                    cursor.execute("""
                        ALTER TABLE Course 
                        ADD COLUMN passing_grade NUMERIC(4,2) DEFAULT 10.0 
                        CHECK (passing_grade >= 0 AND passing_grade <= 20)
                    """)
                    # Update existing records with default passing grade
                    cursor.execute("UPDATE Course SET passing_grade = 10.0 WHERE passing_grade IS NULL")
                    self.db_connection.commit()
        except Exception as e:
            print(f"Note: Passing grade column check/create: {e}")
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('Grading & Results Processing')
        self.setGeometry(50, 50, 1400, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Title
        title = QLabel('Grading & Results Processing')
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Control panel
        control_group = QGroupBox('Results Calculation')
        control_layout = QFormLayout()
        control_group.setLayout(control_layout)
        
        # Course selection
        self.course_combo = QComboBox()
        self.course_combo.setEditable(False)
        self.course_combo.currentIndexChanged.connect(self.on_course_changed)
        control_layout.addRow('Select Course', self.course_combo)
        
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
        control_layout.addRow('Passing Grade', passing_grade_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.btn_calculate = QPushButton('Calculate Results')
        self.btn_calculate.clicked.connect(self.calculate_results)
        self.btn_calculate.setStyleSheet("background-color: #27ae60; color: white; padding: 8px;")
        
        self.btn_refresh = QPushButton('Refresh')
        self.btn_refresh.clicked.connect(self.load_results)
        self.btn_refresh.setStyleSheet("background-color: #3498db; color: white; padding: 8px;")
        
        button_layout.addWidget(self.btn_calculate)
        button_layout.addWidget(self.btn_refresh)
        button_layout.addStretch()
        
        control_layout.addRow('', button_layout)
        
        main_layout.addWidget(control_group)
        
        # Results table
        results_label = QLabel('Student Results')
        results_label.setFont(QFont('Arial', 12, QFont.Bold))
        main_layout.addWidget(results_label)
        
        self.results_table = QTableWidget()
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        main_layout.addWidget(self.results_table)
        
        # Summary group
        summary_group = QGroupBox('Summary Statistics')
        summary_layout = QVBoxLayout()
        summary_group.setLayout(summary_layout)
        
        self.summary_label = QLabel('Select a course and calculate results to see statistics.')
        self.summary_label.setWordWrap(True)
        summary_layout.addWidget(self.summary_label)
        
        main_layout.addWidget(summary_group)
    
    def load_courses(self):
        """Load courses for selection."""
        try:
            cursor = self.db_connection.get_cursor()
            cursor.execute("""
                SELECT c.Course_ID, c.Department_ID, c.name, d.name as dept_name,
                       COALESCE(c.passing_grade, 10.0) as passing_grade
                FROM Course c
                JOIN Department d ON c.Department_ID = d.Department_id
                ORDER BY d.name, c.name
            """)
            courses = cursor.fetchall()
            self.course_combo.clear()
            for course_id, dept_id, course_name, dept_name, passing_grade in courses:
                display_text = f"{course_name} (Dept: {dept_name}, ID: {course_id}/{dept_id})"
                self.course_combo.addItem(display_text, (course_id, dept_id, passing_grade))
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to load courses:\n{str(e)}')
    
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
            QMessageBox.warning(self, 'Validation Error', 'Please select a course.')
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
                    ROUND(AVG(m.mark)::numeric, 2) as Average_Mark,
                    MIN(m.mark) as Min_Mark,
                    MAX(m.mark) as Max_Mark,
                    CASE 
                        WHEN ROUND(AVG(m.mark)::numeric, 2) >= %s THEN 'PASSED'
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
                        item.setBackground(Qt.red if col_idx == 6 else Qt.lightGray)
                    elif result == 'PASSED':
                        item.setBackground(Qt.green if col_idx == 6 else Qt.white)
                    
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
            
            QMessageBox.information(self, 'Success', 
                                  f'Results calculated successfully!\n\n'
                                  f'Total Students: {total_students}\n'
                                  f'Passed: {passed_count}\n'
                                  f'Failed: {failed_count}')
            
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to calculate results:\n{str(e)}')
    
    def load_results(self):
        """Load and display results (recalculate)."""
        self.calculate_results()

