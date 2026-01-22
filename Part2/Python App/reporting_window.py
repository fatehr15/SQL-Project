from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTableWidget, QTableWidgetItem, QLabel,
                             QMessageBox, QComboBox, QHeaderView, QTextEdit,
                             QSplitter, QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import db_connection


class ReportingWindow(QMainWindow):
    """Window for SQL reporting and predefined queries."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.connection = db_connection.get_db_connection()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('SQL Reporting - Query Results')
        self.setGeometry(100, 100, 1400, 800)
        
        # Modern styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F8F9FA;
            }
            QLabel {
                color: #1A1D23;
            }
            QPushButton {
                background-color: #2563EB;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
            QPushButton:pressed {
                background-color: #1E40AF;
            }
            QPushButton#exportBtn {
                background-color: #059669;
            }
            QPushButton#exportBtn:hover {
                background-color: #047857;
            }
            QComboBox {
                padding: 8px;
                border: 1px solid #E1E4E8;
                border-radius: 6px;
                background-color: white;
                font-size: 13px;
                min-width: 300px;
            }
            QComboBox:focus {
                border: 2px solid #2563EB;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #E1E4E8;
                border-radius: 8px;
                gridline-color: #E1E4E8;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #F3F4F6;
            }
            QTableWidget::item:selected {
                background-color: #DBEAFE;
                color: #1E40AF;
            }
            QHeaderView::section {
                background-color: #F3F4F6;
                color: #1A1D23;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #E1E4E8;
                font-weight: 600;
                font-size: 13px;
            }
            QTextEdit {
                background-color: #F8F9FA;
                border: 1px solid #E1E4E8;
                border-radius: 6px;
                padding: 12px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                color: #1A1D23;
            }
            QGroupBox {
                background-color: white;
                border: 1px solid #E1E4E8;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                font-weight: 600;
            }
            QGroupBox::title {
                color: #1A1D23;
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)
        central_widget.setLayout(main_layout)
        
        # Header
        header = QLabel('SQL Reporting')
        header.setFont(QFont('Segoe UI', 24, QFont.Bold))
        header.setStyleSheet("color: #1A1D23; padding: 8px 0;")
        main_layout.addWidget(header)
        
        subtitle = QLabel('Execute predefined queries and view comprehensive reports')
        subtitle.setFont(QFont('Segoe UI', 12))
        subtitle.setStyleSheet("color: #57606A; padding-bottom: 8px;")
        main_layout.addWidget(subtitle)
        
        # Query selection section
        query_section = QGroupBox('Select Report')
        query_layout = QHBoxLayout()
        query_layout.setContentsMargins(16, 16, 16, 16)
        query_section.setLayout(query_layout)
        
        query_layout.addWidget(QLabel('Report Type:'))
        
        self.query_combo = QComboBox()
        self.query_combo.addItems([
            '(a) List of students by group',
            '(b) List of students by section',
            '(c) Instructor timetables',
            '(d) Student timetables (by section and group)',
            '(e) Students who passed the semester',
            '(f) Disqualifying marks by module',
            '(g) Average marks by course and group',
            '(h) Students with failing grades in a module',
            '(i) Students eligible for resit',
            '(j) Students excluded from module'
        ])
        query_layout.addWidget(self.query_combo)
        
        execute_btn = QPushButton('▶ Execute Query')
        execute_btn.clicked.connect(self.execute_query)
        query_layout.addWidget(execute_btn)
        
        query_layout.addStretch()
        
        main_layout.addWidget(query_section)
        
        # Splitter for SQL and Results
        splitter = QSplitter(Qt.Vertical)
        
        # SQL Display section
        sql_group = QGroupBox('SQL Query')
        sql_layout = QVBoxLayout()
        sql_layout.setContentsMargins(12, 12, 12, 12)
        sql_group.setLayout(sql_layout)
        
        self.sql_display = QTextEdit()
        self.sql_display.setReadOnly(True)
        self.sql_display.setMaximumHeight(150)
        sql_layout.addWidget(self.sql_display)
        
        splitter.addWidget(sql_group)
        
        # Results section
        results_group = QGroupBox('Query Results')
        results_layout = QVBoxLayout()
        results_layout.setContentsMargins(12, 12, 12, 12)
        results_group.setLayout(results_layout)
        
        self.results_table = QTableWidget()
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        results_layout.addWidget(self.results_table)
        
        splitter.addWidget(results_group)
        
        # Set splitter sizes
        splitter.setSizes([150, 450])
        
        main_layout.addWidget(splitter)
        
        # Bottom toolbar
        toolbar_widget = QWidget()
        toolbar_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #E1E4E8;
            }
        """)
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(16, 12, 16, 12)
        toolbar_widget.setLayout(toolbar_layout)
        
        self.record_count_label = QLabel('No results')
        self.record_count_label.setFont(QFont('Segoe UI', 11))
        self.record_count_label.setStyleSheet("color: #57606A;")
        toolbar_layout.addWidget(self.record_count_label)
        
        toolbar_layout.addStretch()
        
        export_btn = QPushButton('📊 Export to CSV')
        export_btn.setObjectName('exportBtn')
        export_btn.clicked.connect(self.export_results)
        toolbar_layout.addWidget(export_btn)
        
        main_layout.addWidget(toolbar_widget)
    
    def get_query(self, query_type):
        """Get SQL query based on selection."""
        queries = {
            '(a) List of students by group': """
                -- List of students by group using STRING_AGG and COUNT
                SELECT 
                    g.group_id,
                    g.group_name,
                    COUNT(DISTINCT s.student_id) as student_count,
                    STRING_AGG(DISTINCT CONCAT(s.first_name, ' ', s.last_name), ', ' 
                               ORDER BY CONCAT(s.first_name, ' ', s.last_name)) as students
                FROM "group" g
                LEFT JOIN student s ON g.group_id = s.group_id
                GROUP BY g.group_id, g.group_name
                ORDER BY g.group_name;
            """,
            
            '(b) List of students by section': """
                -- List of students by section using STRING_AGG, COUNT, and UPPER
                SELECT 
                    sec.section_id,
                    UPPER(sec.section_name) as section_name,
                    COUNT(DISTINCT s.student_id) as total_students,
                    STRING_AGG(DISTINCT s.email, '; ' ORDER BY s.email) as student_emails,
                    STRING_AGG(DISTINCT CONCAT(s.first_name, ' ', s.last_name), ', '
                               ORDER BY CONCAT(s.first_name, ' ', s.last_name)) as students
                FROM section sec
                LEFT JOIN "group" g ON sec.section_id = g.section_id
                LEFT JOIN student s ON g.group_id = s.group_id
                GROUP BY sec.section_id, sec.section_name
                ORDER BY sec.section_name;
            """,
            
            '(c) Instructor timetables': """
                -- Instructor timetables using STRING_AGG, COUNT, CONCAT, and TO_CHAR
                SELECT 
                    i.instructor_id,
                    CONCAT(i.first_name, ' ', i.last_name) as instructor_name,
                    COUNT(DISTINCT ts.timeslot_id) as total_slots,
                    STRING_AGG(DISTINCT 
                        CONCAT(ts.day_of_week, ' ', 
                               TO_CHAR(ts.start_time, 'HH24:MI'), '-',
                               TO_CHAR(ts.end_time, 'HH24:MI')),
                        ', ' ORDER BY 
                        CONCAT(ts.day_of_week, ' ', 
                               TO_CHAR(ts.start_time, 'HH24:MI'), '-',
                               TO_CHAR(ts.end_time, 'HH24:MI'))
                    ) as schedule
                FROM instructor i
                LEFT JOIN course_assignment ca ON i.instructor_id = ca.instructor_id
                LEFT JOIN timeslot ts ON ca.timeslot_id = ts.timeslot_id
                GROUP BY i.instructor_id, i.first_name, i.last_name
                ORDER BY instructor_name;
            """,
            
            '(d) Student timetables (by section and group)': """
                -- Student timetables by section and group using multiple functions
                SELECT 
                    sec.section_name,
                    g.group_name,
                    COUNT(DISTINCT s.student_id) as student_count,
                    STRING_AGG(DISTINCT 
                        CONCAT(c.course_name, ' - ', 
                               ts.day_of_week, ' ',
                               TO_CHAR(ts.start_time, 'HH24:MI'), '-',
                               TO_CHAR(ts.end_time, 'HH24:MI')),
                        ' | ' ORDER BY 
                        CONCAT(c.course_name, ' - ', 
                               ts.day_of_week, ' ',
                               TO_CHAR(ts.start_time, 'HH24:MI'), '-',
                               TO_CHAR(ts.end_time, 'HH24:MI'))
                    ) as timetable
                FROM section sec
                JOIN "group" g ON sec.section_id = g.section_id
                LEFT JOIN student s ON g.group_id = s.group_id
                LEFT JOIN course_assignment ca ON g.group_id = ca.group_id
                LEFT JOIN course c ON ca.course_id = c.course_id
                LEFT JOIN timeslot ts ON ca.timeslot_id = ts.timeslot_id
                GROUP BY sec.section_id, sec.section_name, g.group_id, g.group_name
                ORDER BY sec.section_name, g.group_name;
            """,
            
            '(e) Students who passed the semester': """
                -- Students who passed using AVG, COUNT, ROUND, and CONCAT
                SELECT 
                    s.student_id,
                    CONCAT(s.first_name, ' ', s.last_name) as student_name,
                    g.group_name,
                    COUNT(DISTINCT sm.course_id) as courses_taken,
                    ROUND(AVG(sm.mark)::numeric, 2) as average_mark
                FROM student s
                JOIN "group" g ON s.group_id = g.group_id
                JOIN student_mark sm ON s.student_id = sm.student_id
                GROUP BY s.student_id, s.first_name, s.last_name, g.group_name
                HAVING AVG(sm.mark) >= 10
                ORDER BY average_mark DESC;
            """,
            
            '(f) Disqualifying marks by module': """
                -- Disqualifying marks (< 10) using COUNT, AVG, ROUND, and STRING_AGG
                SELECT 
                    c.course_id,
                    c.course_name,
                    m.module_name,
                    COUNT(DISTINCT sm.student_id) as students_with_failing_marks,
                    ROUND(AVG(sm.mark)::numeric, 2) as average_failing_mark,
                    STRING_AGG(DISTINCT CONCAT(s.first_name, ' ', s.last_name, ' (', sm.mark, ')'),
                               ', ' ORDER BY CONCAT(s.first_name, ' ', s.last_name, ' (', sm.mark, ')')) 
                    as failing_students
                FROM course c
                JOIN module m ON c.module_id = m.module_id
                JOIN student_mark sm ON c.course_id = sm.course_id
                JOIN student s ON sm.student_id = s.student_id
                WHERE sm.mark < 10
                GROUP BY c.course_id, c.course_name, m.module_id, m.module_name
                ORDER BY students_with_failing_marks DESC;
            """,
            
            '(g) Average marks by course and group': """
                -- Average marks by course and group using AVG, COUNT, ROUND, MAX, and MIN
                SELECT 
                    c.course_name,
                    g.group_name,
                    COUNT(DISTINCT sm.student_id) as students_enrolled,
                    ROUND(AVG(sm.mark)::numeric, 2) as average_mark,
                    MAX(sm.mark) as highest_mark,
                    MIN(sm.mark) as lowest_mark
                FROM course c
                JOIN student_mark sm ON c.course_id = sm.course_id
                JOIN student s ON sm.student_id = s.student_id
                JOIN "group" g ON s.group_id = g.group_id
                GROUP BY c.course_id, c.course_name, g.group_id, g.group_name
                ORDER BY c.course_name, g.group_name;
            """,
            
            '(h) Students with failing grades in a module': """
                -- Students with failing grades using CONCAT, COUNT, and STRING_AGG
                SELECT 
                    m.module_name,
                    s.student_id,
                    CONCAT(s.first_name, ' ', s.last_name) as student_name,
                    COUNT(DISTINCT c.course_id) as failed_courses_in_module,
                    STRING_AGG(DISTINCT CONCAT(c.course_name, ' (', sm.mark, ')'),
                               ', ' ORDER BY CONCAT(c.course_name, ' (', sm.mark, ')')) as failed_courses
                FROM student s
                JOIN student_mark sm ON s.student_id = sm.student_id
                JOIN course c ON sm.course_id = c.course_id
                JOIN module m ON c.module_id = m.module_id
                WHERE sm.mark < 10
                GROUP BY m.module_id, m.module_name, s.student_id, s.first_name, s.last_name
                ORDER BY m.module_name, student_name;
            """,
            
            '(i) Students eligible for resit': """
                -- Students eligible for resit (mark between 8-9.99) using COUNT, ROUND, and AVG
                SELECT 
                    s.student_id,
                    CONCAT(s.first_name, ' ', s.last_name) as student_name,
                    c.course_name,
                    sm.mark as resit_mark,
                    g.group_name,
                    COUNT(*) OVER (PARTITION BY s.student_id) as total_resits_needed
                FROM student s
                JOIN student_mark sm ON s.student_id = sm.student_id
                JOIN course c ON sm.course_id = c.course_id
                JOIN "group" g ON s.group_id = g.group_id
                WHERE sm.mark >= 8 AND sm.mark < 10
                ORDER BY student_name, c.course_name;
            """,
            
            '(j) Students excluded from module': """
                -- Students excluded (mark < 8) using COUNT, STRING_AGG, and CONCAT
                SELECT 
                    m.module_name,
                    s.student_id,
                    CONCAT(s.first_name, ' ', s.last_name) as student_name,
                    s.email,
                    COUNT(DISTINCT c.course_id) as excluded_courses,
                    STRING_AGG(DISTINCT CONCAT(c.course_name, ' (', sm.mark, ')'),
                               ', ' ORDER BY CONCAT(c.course_name, ' (', sm.mark, ')')) 
                    as exclusion_details
                FROM student s
                JOIN student_mark sm ON s.student_id = sm.student_id
                JOIN course c ON sm.course_id = c.course_id
                JOIN module m ON c.module_id = m.module_id
                WHERE sm.mark < 8
                GROUP BY m.module_id, m.module_name, s.student_id, s.first_name, s.last_name, s.email
                ORDER BY m.module_name, student_name;
            """
        }
        
        return queries.get(query_type, "")
    
    def execute_query(self):
        """Execute the selected query and display results."""
        query_type = self.query_combo.currentText()
        sql = self.get_query(query_type)
        
        if not sql:
            QMessageBox.warning(self, 'Warning', 'No query defined for this selection.')
            return
        
        # Display SQL
        self.sql_display.setText(sql.strip())
        
        cursor = None
        try:
            # Rollback any pending transaction first
            try:
                self.connection.rollback()
            except:
                pass
            
            cursor = self.connection.cursor()
            cursor.execute(sql)
            
            # Get column names
            columns = [desc[0] for desc in cursor.description]
            
            # Fetch results
            rows = cursor.fetchall()
            
            # Commit the transaction (for read queries, this just clears the transaction)
            self.connection.commit()
            
            # Display results in table
            self.results_table.setColumnCount(len(columns))
            self.results_table.setHorizontalHeaderLabels(columns)
            self.results_table.setRowCount(len(rows))
            
            for i, row in enumerate(rows):
                for j, value in enumerate(row):
                    item = QTableWidgetItem(str(value) if value is not None else '')
                    self.results_table.setItem(i, j, item)
            
            # Auto-resize columns
            self.results_table.resizeColumnsToContents()
            header = self.results_table.horizontalHeader()
            for i in range(len(columns)):
                if header.sectionSize(i) > 300:
                    header.setSectionResizeMode(i, QHeaderView.Stretch)
                else:
                    header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
            
            # Update record count
            self.record_count_label.setText(f'Records found: {len(rows)}')
            
        except Exception as e:
            # Rollback the failed transaction
            try:
                self.connection.rollback()
            except:
                pass
            
            QMessageBox.critical(self, 'Query Error', f'Failed to execute query:\n{str(e)}')
            import traceback
            traceback.print_exc()
        
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
    
    def export_results(self):
        """Export results to CSV file."""
        if self.results_table.rowCount() == 0:
            QMessageBox.warning(self, 'Warning', 'No results to export. Please run a query first.')
            return
        
        try:
            from PyQt5.QtWidgets import QFileDialog
            import csv
            
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                'Export Results',
                '',
                'CSV Files (*.csv);;All Files (*)'
            )
            
            if not file_path:
                return
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write headers
                headers = []
                for col in range(self.results_table.columnCount()):
                    headers.append(self.results_table.horizontalHeaderItem(col).text())
                writer.writerow(headers)
                
                # Write data
                for row in range(self.results_table.rowCount()):
                    row_data = []
                    for col in range(self.results_table.columnCount()):
                        item = self.results_table.item(row, col)
                        row_data.append(item.text() if item else '')
                    writer.writerow(row_data)
            
            QMessageBox.information(self, 'Success', f'Results exported to:\n{file_path}')
            
        except Exception as e:
            QMessageBox.critical(self, 'Export Error', f'Failed to export results:\n{str(e)}')
    
    def closeEvent(self, event):
        """Handle window close event."""
        event.accept()