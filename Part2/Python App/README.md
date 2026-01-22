# Python Application - University Database Management System

This directory contains the complete Python GUI application for managing the University Database System. The application provides a comprehensive interface for CRUD operations, reservations, marks management, grading, reporting, and audit logging.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [File Structure](#file-structure)
- [Core Files](#core-files)
- [Window Modules](#window-modules)
- [Database Connection](#database-connection)
- [Configuration](#configuration)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)

---

## Overview

The University Database Management System is a PyQt5-based desktop application that provides a user-friendly interface for managing a university database. It supports both PostgreSQL (production) and SQLite (demo/testing) databases.

**Key Features:**
- ✅ CRUD Operations (Create, Read, Update, Delete)
- ✅ Room Reservations with Conflict Checking
- ✅ Marks & Attendance Management
- ✅ Grading & Results Processing
- ✅ SQL Query Reporting
- ✅ Audit Logging
- ✅ Connection Configuration Dialog
- ✅ Demo Database (SQLite) Support

---


## Quick Start

### 1. Install Dependencies

```bash
cd "Part2/Python App"
pip install -r Requirements.txt
```

### 2. Configure Database Connection

**Option A: Use Connection Dialog (Recommended)**
- Run the application: `python App.py`
- The connection dialog will appear on first run
- Enter your PostgreSQL credentials or select "Use Demo Database"

**Option B: Use Demo Database**
- Simply select "Use Demo Database" in the connection dialog
- No PostgreSQL setup required!

### 3. Run the Application

```bash
python App.py
```

Or on Linux/macOS:
```bash
python3 App.py
```

---

## File Structure

```
Part2/Python App/
│
├── README.md                     # This file - comprehensive documentation
├── Requirements.txt              # Python package dependencies
│
├── App.py                        # Main application entry point
├── connection_dialog.py          # Database connection configuration dialog
│
├── db_connection.py              # PostgreSQL database connection handler
├── db_connection_demo.py         # SQLite demo database connection handler
├── db_config.json                # Database configuration (auto-generated)
│
├── crud_window.py                # CRUD operations main window
├── crud_forms.py                 # Generic CRUD forms implementation
│
├── reservation_window.py         # Room reservations management window
├── marks_attendance_window.py    # Marks & attendance management window
├── grading_window.py             # Grading & results processing window
├── reporting_window.py           # SQL query reporting window
├── audit_window.py               # Audit logging window
│
├── setup_static_demo.py          # Static demo database setup script
├── create_database.py            # PostgreSQL database creation script
├── test_connection.py            # Database connection testing script
│
├── setup_database.ps1            # PowerShell script for Part 1 lab setup
├── run_labs_manual.ps1           # Manual lab runner script
├── reporting_functions.sql       # SQL reporting functions definitions
│
└── __pycache__/                  # Python bytecode cache (auto-generated)
```

---

## Core Files

### `App.py`
**Purpose:** Main application entry point and window manager

**Key Components:**
- `MainWindow` class - Main application window with navigation menu
- `_ensure_db_stubs()` - Creates stub modules to prevent premature database connections
- Database connection management with automatic fallback to demo database
- Window navigation and lifecycle management

**Features:**
- Shows connection dialog on first run or connection failure
- Automatic demo database creation if missing
- Menu bar with "Settings → Database Connection..." option
- Graceful error handling and user notifications

**Usage:**
```bash
python App.py              # Run with default settings
python App.py --demo       # Force demo mode
python App.py -d           # Force demo mode (short form)
```

**Dependencies:**
- PyQt5 (QtWidgets, QtCore, QtGui)
- db_connection, db_connection_demo
- All window modules (loaded dynamically)

---

### `connection_dialog.py`
**Purpose:** GUI dialog for configuring database connection settings

**Key Features:**
- User-friendly form for entering database credentials
- Connection testing functionality
- Demo database option (always available)
- Settings persistence (saves to `db_config.json`)

**Form Fields:**
- Host (default: localhost)
- Port (default: 5432)
- Database name (default: university_db)
- Username (default: postgres)
- Password (masked input)
- Use Demo Database checkbox

**Configuration Storage:**
- Settings are saved to `db_config.json` in the same directory
- Format: JSON with connection parameters
- Password is saved (consider security implications)

**Methods:**
- `load_saved_settings()` - Loads configuration from file
- `save_settings()` - Saves configuration to file
- `test_connection()` - Tests PostgreSQL connection
- `get_connection_settings()` - Returns settings dictionary

---

### `db_connection.py`
**Purpose:** PostgreSQL database connection handler

**Class: `DatabaseConnection`**

**Methods:**
- `__init__(host, port, database, user, password)` - Initialize connection parameters
- `connect()` - Establish PostgreSQL connection
- `get_cursor()` - Get database cursor for query execution
- `execute_query(query, params)` - Execute SQL query with optional parameters
- `commit()` - Commit current transaction
- `rollback()` - Rollback current transaction
- `close()` - Close connection and cursor

**Function: `get_db_connection()`**
- Loads settings from `db_config.json` if available
- Falls back to environment variables
- Falls back to default values
- Returns configured `DatabaseConnection` instance

**Configuration Priority:**
1. `db_config.json` file
2. Environment variables (`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`)
3. Default values

**Dependencies:**
- psycopg2 (PostgreSQL adapter)

---

### `db_connection_demo.py`
**Purpose:** SQLite demo database connection handler

**Class: `DemoDatabaseConnection`**

**Features:**
- SQLite database wrapper for compatibility with PostgreSQL code
- Automatic PostgreSQL-to-SQLite syntax adaptation
- Parameter placeholder conversion (`%s` → `?`)
- Function registration (e.g., `CheckReservation`)
- Auto-creates static demo database if missing

**Methods:**
- `__init__(db_path)` - Initialize with database path (default: `demo/university_demo.db`)
- `connect()` - Establish SQLite connection
- `get_cursor()` - Get wrapped cursor with SQL adaptation
- `execute_query(query, params)` - Execute adapted SQL query
- `_adapt_query(query)` - Convert PostgreSQL syntax to SQLite
- `commit()` - Commit transaction
- `rollback()` - Rollback transaction
- `close()` - Close connection

**SQL Adaptation:**
- Removes PostgreSQL type casts (`::date`, `::time`, `::numeric`)
- Converts `SERIAL` to `INTEGER`
- Replaces `CURRENT_TIMESTAMP` with `datetime('now')`
- Handles function calls and syntax differences

**Function: `get_demo_db_connection()`**
- Returns configured `DemoDatabaseConnection` instance
- Uses default demo database path

**Dependencies:**
- sqlite3 (standard library)

---

## Window Modules

### `crud_window.py`
**Purpose:** Main window for CRUD operations

**Features:**
- Table selector (Department, Student, Instructor, Course)
- Stacked widget for different forms
- Seamless switching between tables

**Methods:**
- `init_ui()` - Initialize user interface
- `on_table_changed(index)` - Handle table selection change

**Dependencies:**
- crud_forms (for form widgets)

---

### `crud_forms.py`
**Purpose:** Generic CRUD form implementation

**Class: `GenericCRUDForm`**

**Features:**
- Generic form that works with any table configuration
- Dynamic form generation based on column configuration
- Support for different input types (text, date, combo, integer, real)
- Data validation
- Create, Read, Update, Delete operations
- Primary key handling

**Table Configurations:**
- Department form
- Student form
- Instructor form
- Course form

**Factory Functions:**
- `get_department_form()` - Returns Department CRUD form
- `get_student_form()` - Returns Student CRUD form
- `get_instructor_form()` - Returns Instructor CRUD form
- `get_course_form()` - Returns Course CRUD form

**Key Methods:**
- `load_data()` - Load and display table data
- `create_record()` - Create new record
- `update_record()` - Update selected record
- `delete_record()` - Delete selected record
- `validate_form()` - Validate form inputs
- `clear_form()` - Clear form fields

---

### `reservation_window.py`
**Purpose:** Room reservation management with conflict checking

**Class: `ReservationWindow`**

**Features:**
- Room availability checking
- Conflict detection using `CheckReservation()` function
- Building and room selection
- Date and time selection
- Course and instructor association
- Reservation creation with validation
- Display existing reservations

**Key Methods:**
- `check_availability()` - Check if room is available
- `create_reservation()` - Create new reservation with conflict check
- `load_data()` - Load and display reservations
- `load_dropdowns()` - Load building, room, course, instructor options
- `validate_form()` - Validate reservation inputs

**Database Functions Used:**
- `CheckReservation(building, room, date, start_time, end_time)` - Checks for conflicts

**Table: Reservation**
- Columns: Reservation_ID, Building, RoomNo, Course_ID, Department_ID, Instructor_ID, Reserv_Date, Start_Time, End_Time, Hours_Number

---

### `marks_attendance_window.py`
**Purpose:** Student marks and attendance management

**Class: `MarksAttendanceWindow`**

**Features:**
- Two-tab interface (Marks / Attendance)
- Add, update, delete marks
- Add, update, delete attendance records
- Student and course selection
- Date selection for records
- Data validation

**Marks Tab:**
- Mark value input
- Mark date selection
- Student-course association
- Display marks table

**Attendance Tab:**
- Attendance date selection
- Status selection (Present/Absent)
- Student-course association
- Display attendance table

**Key Methods:**
- `add_mark()` - Add new mark record
- `update_mark()` - Update existing mark
- `add_attendance()` - Add attendance record
- `load_marks_data()` - Load marks table
- `load_attendance_data()` - Load attendance table
- `load_dropdowns()` - Load student and course options

**Tables:**
- Marks (Mark_ID, Student_ID, Course_ID, Mark_Value, Mark_Date)
- Attendance (Attendance_ID, Student_ID, Course_ID, Attendance_Date, Status)

---

### `grading_window.py`
**Purpose:** Student grading and results processing

**Class: `GradingWindow`**

**Features:**
- Course selection
- Automatic grade calculation
- Average mark computation
- Pass/Fail determination
- Summary statistics
- Passing grade configuration (default: 10.0)

**Key Methods:**
- `load_courses()` - Load available courses
- `calculate_results()` - Calculate student averages and results
- `load_results()` - Display calculated results
- `ensure_passing_grade_column()` - Ensure Course table has Passing_Grade column

**Calculations:**
- Average mark per student per course
- Pass/Fail status based on passing grade
- Summary statistics (total students, passed, failed)

**Table: Course**
- Passing_Grade column (auto-created if missing)

---

### `reporting_window.py`
**Purpose:** SQL query execution and reporting

**Class: `ReportingWindow`**

**Features:**
- Pre-defined SQL queries (a) through (j)
- Query parameter input
- Results table display
- SQL code display
- Function creation and management
- Query refresh functionality

**Pre-defined Queries:**
- (a) List of students by group
- (b) Students with marks above average
- (c) Course enrollment statistics
- (d) Department statistics
- (e) Student performance summary
- And more...

**Key Methods:**
- `load_dropdowns()` - Load query options
- `on_query_changed()` - Handle query selection
- `setup_parameters()` - Setup parameter inputs for queries
- `execute_query()` - Execute selected query
- `refresh_query()` - Re-execute current query
- `ensure_functions()` - Ensure SQL functions exist
- `create_functions_directly()` - Create reporting functions in database

**SQL Functions:**
- Functions are defined in `reporting_functions.sql`
- Automatically created if missing

---

### `audit_window.py`
**Purpose:** Audit logging and monitoring

**Class: `AuditWindow`**

**Features:**
- Three-tab interface:
  - Marks Audit Log
  - Attendance Audit Log
  - Summary Statistics
- Operation filtering (INSERT, UPDATE, DELETE)
- Date filtering
- Audit table creation (automatic)
- Trigger setup (automatic)

**Key Methods:**
- `setup_audit_tables()` - Create audit tables if missing
- `setup_triggers()` - Create audit triggers if missing
- `load_marks_audit()` - Load marks audit log
- `load_attendance_audit()` - Load attendance audit log
- `load_summary()` - Display summary statistics

**Audit Tables:**
- Marks_Audit_Log (LogID, Mark_ID, Operation, Old_Value, New_Value, Change_Date, Changed_By)
- Attendance_Audit_Log (LogID, Attendance_ID, Operation, Old_Value, New_Value, Change_Date, Changed_By)

**Triggers:**
- Automatically created on Marks and Attendance tables
- Logs all INSERT, UPDATE, DELETE operations

---

## Database Connection

### Configuration File: `db_config.json`

**Location:** `Part2/Python App/db_config.json`

**Format:**
```json
{
  "host": "localhost",
  "port": 5432,
  "database": "university_db",
  "user": "postgres",
  "password": "your_password",
  "use_demo": false
}
```

**Notes:**
- Auto-generated by connection dialog
- Password is stored in plain text (consider security)
- `use_demo: true` forces demo database mode

### Connection Flow

1. **First Run:**
   - No `db_config.json` exists
   - Connection dialog appears
   - User enters credentials or selects demo mode
   - Settings saved to `db_config.json`

2. **Subsequent Runs:**
   - Settings loaded from `db_config.json`
   - Connection attempted
   - If fails, dialog appears again
   - Fallback to demo database if all else fails

3. **Connection Priority:**
   1. PostgreSQL connection (if configured)
   2. Demo database (SQLite)
   3. In-memory SQLite (last resort)

---

## Utility Scripts

### `setup_static_demo.py`
**Purpose:** Create static demo database with sample data

**Function: `create_static_demo_database()`**

**Features:**
- Creates SQLite database at `demo/university_demo.db`
- Creates all required tables
- Inserts sample data (departments, students, instructors, courses, rooms, etc.)
- Registers `CheckReservation()` function
- Always available, no PostgreSQL required

**Sample Data Includes:**
- 4 Departments (CS, MATH, PHYS, ENG)
- 5 Students
- 4 Instructors
- 5 Courses
- 6 Rooms
- Sample reservations, enrollments, marks, attendance

**Usage:**
```bash
python setup_static_demo.py
```

**Auto-Execution:**
- Automatically called if demo database is missing
- Called when demo mode is selected

---

### `create_database.py`
**Purpose:** Create PostgreSQL database programmatically

**Function: `create_database()`**

**Features:**
- Connects to PostgreSQL server
- Checks if database exists
- Creates `university_db` database if missing
- Provides clear error messages
- Reads settings from environment or config

**Usage:**
```bash
python create_database.py
```

**Configuration:**
- Uses environment variables or config file
- Prompts for credentials if needed

**Note:**
- Only creates the database
- Tables must be created using Part 1 lab scripts
- Use `setup_database.ps1` for complete setup

---

### `test_connection.py`
**Purpose:** Test database connection and setup

**Function: `test_connection()`**

**Features:**
- Tests database connectivity
- Displays PostgreSQL version
- Checks for required tables
- Shows data counts
- Verifies sample data

**Usage:**
```bash
python test_connection.py
```

**Output:**
- Connection status
- Database version
- Table existence check
- Row counts for key tables

**Exit Codes:**
- 0: Success
- 1: Failure

---

### `setup_database.ps1`
**Purpose:** PowerShell script for complete database setup

**Features:**
- Finds PostgreSQL installation
- Creates database if needed
- Runs Part 1 lab scripts (Lab 1, Lab 3, Lab 4)
- Verifies setup
- Interactive password input

**Usage:**
```powershell
.\setup_database.ps1
```

**Requirements:**
- PowerShell
- PostgreSQL installed
- Part 1 lab SQL files in correct location

**Script Flow:**
1. Find PostgreSQL installation
2. Prompt for credentials
3. Create database (if needed)
4. Run Lab 1 (tables and data)
5. Run Lab 3 (functions)
6. Run Lab 4 (triggers)
7. Verify setup

---

### `run_labs_manual.ps1`
**Purpose:** Manual lab script runner

**Features:**
- Runs Part 1 lab scripts manually
- Useful for testing individual labs
- Interactive credential input

**Usage:**
```powershell
.\run_labs_manual.ps1
```

---

### `reporting_functions.sql`
**Purpose:** SQL function definitions for reporting queries

**Content:**
- SQL function definitions used by reporting window
- Functions are created automatically if missing
- Can be run manually if needed

**Usage:**
- Automatically loaded by `reporting_window.py`
- Can be executed manually in PostgreSQL

---

## Configuration

### Environment Variables

The application supports the following environment variables:

```bash
# PostgreSQL Connection
DB_HOST=localhost          # Database host
DB_PORT=5432              # Database port
DB_NAME=university_db     # Database name
DB_USER=postgres          # Database username
DB_PASSWORD=your_password # Database password

# Demo Mode (deprecated - use connection dialog)
USE_DEMO_DB=1             # Force demo database mode
```

**Priority:**
1. `db_config.json` file
2. Environment variables
3. Default values

---

## Usage

### Starting the Application

**Basic Usage:**
```bash
python App.py
```

**Demo Mode:**
```bash
python App.py --demo
# or
python App.py -d
```

### Changing Database Connection

1. Click "Settings" menu
2. Select "Database Connection..."
3. Enter new credentials or select demo mode
4. Click "Test Connection" to verify
5. Click "Connect" to save and use

### Module Workflows

#### CRUD Operations
1. Click "CRUD Operations"
2. Select table from dropdown
3. Use form to create, update, or delete records
4. Click "Refresh" to reload data

#### Reservations
1. Click "Assignment/Reservations"
2. Select building and room
3. Choose date and time
4. Click "Check Availability"
5. If available, fill in details and create reservation

#### Marks & Attendance
1. Click "Marks & Attendance"
2. Select tab (Marks or Attendance)
3. Choose student and course
4. Enter mark/attendance data
5. Click "Add" or "Update"

#### Grading
1. Click "Grading/Results Processing"
2. Select course from dropdown
3. Click "Calculate Results"
4. View student averages and pass/fail status

#### Reporting
1. Click "Reporting (SQL Queries)"
2. Select query from dropdown
3. Enter parameters if needed
4. Click "Execute Query"
5. View results in table

#### Audit
1. Click "Audit"
2. Select tab (Marks, Attendance, or Summary)
3. Use filters to narrow results
4. Click "Refresh" to reload

---

## Troubleshooting

### Common Issues

#### "Database does not exist"
**Solution:**
1. Run `python create_database.py` to create the database
2. Or use pgAdmin to create `university_db` manually
3. Or use demo database mode

#### "Connection refused"
**Solutions:**
1. Verify PostgreSQL is running
2. Check host and port settings
3. Verify firewall settings
4. Use demo database as fallback

#### "Table does not exist"
**Solution:**
1. Run Part 1 lab scripts:
   ```powershell
   .\setup_database.ps1
   ```
2. Or use demo database (has all tables pre-configured)

#### "Function does not exist"
**Solution:**
- Functions are created automatically
- If issues persist, run `Part1/Lab 3/lab3.sql` manually

#### "No module named 'PyQt5'"
**Solution:**
```bash
pip install -r Requirements.txt
```

#### Demo Database Not Working
**Solution:**
1. Run `python setup_static_demo.py` manually
2. Check file permissions
3. Verify `demo/` directory exists

---

## Dependencies

### Python Packages (Requirements.txt)

```
psycopg2-binary>=2.9.0    # PostgreSQL adapter
PyQt5>=5.15.0             # GUI framework
```


### Installation

```bash
pip install -r Requirements.txt
```

---

## File Relationships

```
App.py
  ├── connection_dialog.py (shown on startup/failure)
  ├── db_connection.py (PostgreSQL handler)
  ├── db_connection_demo.py (SQLite handler)
  │
  ├── crud_window.py
  │     └── crud_forms.py
  │
  ├── reservation_window.py
  ├── marks_attendance_window.py
  ├── grading_window.py
  ├── reporting_window.py
  │     └── reporting_functions.sql
  │
  └── audit_window.py

setup_static_demo.py
  └── Creates demo/university_demo.db
      (used by db_connection_demo.py)
```

---

## Development Notes

### Code Structure

- **Separation of Concerns:** Each window is a separate module
- **Database Abstraction:** Connection handlers abstract PostgreSQL/SQLite differences
- **Error Handling:** Graceful fallbacks and user-friendly error messages
- **Configuration Management:** Centralized in `db_config.json`

### Adding New Features

1. **New Window:**
   - Create new window module (e.g., `new_window.py`)
   - Add to `App.py` navigation
   - Follow existing window patterns

2. **New Table:**
   - Add to CRUD forms configuration
   - Update demo database setup script
   - Add to relevant windows

3. **New Database Function:**
   - Add to `reporting_functions.sql`
   - Create in database via window or script
   - Register in SQLite (if needed for demo)

---

## License

This project is part of "Introduction to database" course at NSCS .

---

## Support

For issues or questions:
1. Check this README.md
2. Review Part2/README.md for database setup
3. Check error messages in the application
4. Verify database connection settings

---

**Last Updated:** Jan 2026

**Python Version:** 3.8+

**PostgreSQL Version:** 12+ (optional)

**GUI Framework:** PyQt5


