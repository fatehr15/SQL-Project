"""
Dashboard Widget with KPI Cards
Displays key performance indicators on the main window.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, 
                             QLabel, QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class KPICard(QFrame):
    """A single KPI card widget displaying a metric."""
    
    def __init__(self, title, value, subtitle="", icon="📊", color="#3498db"):
        super().__init__()
        self.color = color
        self.init_ui(title, value, subtitle, icon)
    
    def init_ui(self, title, value, subtitle, icon):
        """Initialize the KPI card UI."""
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.color}, stop:1 {self._darken_color(self.color)});
                border-radius: 12px;
                padding: 20px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        self.setLayout(layout)
        
        # Icon and title row
        header_layout = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("color: rgba(255, 255, 255, 0.9); font-size: 24px;")
        header_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: white; font-size: 12px; font-weight: bold;")
        title_label.setWordWrap(True)
        header_layout.addWidget(title_label, 1)
        
        layout.addLayout(header_layout)
        
        # Value label (big number)
        value_label = QLabel(str(value))
        value_label.setStyleSheet("color: white; font-size: 36px; font-weight: bold;")
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)
        
        # Subtitle label (optional)
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet("color: rgba(255, 255, 255, 0.85); font-size: 10px;")
            subtitle_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(subtitle_label)
    
    def _darken_color(self, hex_color, factor=0.2):
        """Darken a hex color."""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = int(r * (1 - factor))
        g = int(g * (1 - factor))
        b = int(b * (1 - factor))
        return f'#{r:02x}{g:02x}{b:02x}'


class DashboardWidget(QWidget):
    """Dashboard widget displaying KPI cards."""
    
    def __init__(self, db_connection, parent=None):
        super().__init__(parent)
        self.db_connection = db_connection
        self.setStyleSheet("background-color: transparent;")
        self.init_ui()
        self.load_kpis()
    
    def init_ui(self):
        """Initialize the dashboard UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 10, 0, 10)
        layout.setSpacing(15)
        self.setLayout(layout)
        
        # Title
        title = QLabel("📊 Dashboard Overview")
        title.setFont(QFont('Segoe UI', 14, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; padding: 5px 0;")
        layout.addWidget(title)
        
        # Grid layout for KPI cards
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(15)
        layout.addLayout(self.grid_layout)
    
    def load_kpis(self):
        """Load KPI values from database."""
        try:
            if not self.db_connection:
                self.show_error_message("No database connection")
                return
            
            cursor = self.db_connection.get_cursor()
            if cursor is None:
                self.show_error_message("Cannot get database cursor")
                return
            
            # Clear existing cards
            self._clear_grid()
            
            # KPI 1: Total Students
            total_students = self._safe_query(cursor, "SELECT COUNT(*) FROM Student", 0)
            
            # KPI 2: Total Instructors
            total_instructors = self._safe_query(cursor, "SELECT COUNT(*) FROM Instructor", 0)
            
            # KPI 3: Total Courses
            total_courses = self._safe_query(cursor, "SELECT COUNT(*) FROM Course", 0)
            
            # KPI 4: Total Departments
            total_depts = self._safe_query(cursor, "SELECT COUNT(*) FROM Department", 0)
            
            # KPI 5: Active Enrollments (if table exists)
            total_enrollments = self._safe_query(cursor, "SELECT COUNT(*) FROM Enrollment", 0)
            
            # KPI 6: Recent Marks (if table exists)
            recent_marks = self._safe_query(cursor, 
                "SELECT COUNT(*) FROM Marks WHERE mark_date >= CURRENT_DATE - INTERVAL '30 days'", 0)
            
            # Create and add KPI cards with icons
            cards = [
                ("Students", total_students, "Total enrolled", "👨‍🎓", "#3498db"),
                ("Instructors", total_instructors, "Teaching staff", "👨‍🏫", "#2ecc71"),
                ("Courses", total_courses, "Available courses", "📚", "#9b59b6"),
                ("Departments", total_depts, "Academic units", "🏛️", "#e67e22"),
                ("Enrollments", total_enrollments, "Active students", "✅", "#1abc9c"),
                ("Recent Marks", recent_marks, "Last 30 days", "📝", "#f39c12"),
            ]
            
            # Add cards to grid (3 columns)
            for i, (title, value, subtitle, icon, color) in enumerate(cards):
                card = KPICard(title, value, subtitle, icon, color)
                card.setMinimumHeight(140)
                row = i // 3
                col = i % 3
                self.grid_layout.addWidget(card, row, col)
        
        except Exception as e:
            print(f"Dashboard error: {e}")
            import traceback
            traceback.print_exc()
            self.show_error_message(f"Error loading dashboard: {str(e)}")
    
    def _safe_query(self, cursor, query, default=0):
        """Execute query safely and return result or default."""
        try:
            cursor.execute(query)
            result = cursor.fetchone()
            return result[0] if result and result[0] is not None else default
        except Exception as e:
            print(f"Query failed: {query} - {e}")
            return default
    
    def _clear_grid(self):
        """Clear all widgets from grid layout."""
        for i in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)
    
    def show_error_message(self, message):
        """Show error message in dashboard."""
        self._clear_grid()
        error_label = QLabel(f"⚠️ {message}")
        error_label.setStyleSheet("""
            color: #e74c3c;
            padding: 20px;
            background-color: #fadbd8;
            border-radius: 8px;
            font-size: 12px;
        """)
        error_label.setAlignment(Qt.AlignCenter)
        self.grid_layout.addWidget(error_label, 0, 0, 1, 3)
    
    def refresh(self):
        """Refresh KPI data."""
        self.load_kpis()