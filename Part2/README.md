# Part 2: Python Application - University Database Management System

This document explains how to set up the database from Part 1 and configure the Python application to connect to it.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Step 1: Database Setup (Using Part 1 Labs)](#step-1-database-setup-using-part-1-labs)
- [Step 2: Configure Database Connection](#step-2-configure-database-connection)
- [Step 3: Install Python Dependencies](#step-3-install-python-dependencies)
- [Step 4: Test the Application](#step-4-test-the-application)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, ensure you have:

1. **PostgreSQL** installed and running (version 12.x or higher)
2. **Python** 3.8 or higher installed
3. **pip** (Python package manager)
4. Access to the Part 1 lab SQL files

---

## Step 1: Database Setup (Using Part 1 Labs)

The Python application uses the database created in Part 1. Follow these steps to set up the database:

### 1.1 Create the Database

#### Windows Setup

**Option A: Using pgAdmin (Recommended for Windows)**

1. Open **pgAdmin** (installed with PostgreSQL)
2. Connect to your PostgreSQL server
3. Right-click on "Databases" → "Create" → "Database"
4. Name: `university_db`
5. Click "Save"

**Option B: Using Command Line (Windows)**

First, add PostgreSQL to your PATH:

1. Find PostgreSQL installation directory (usually `C:\Program Files\PostgreSQL\<version>\bin`)
2. Add to PATH:
   - Open "Environment Variables" (Windows key → type "environment")
   - Edit "Path" variable
   - Add: `C:\Program Files\PostgreSQL\<version>\bin`
   - Restart PowerShell/Command Prompt

Then run:

```powershell
# Connect to PostgreSQL
psql -U postgres
```

**Option C: Using Full Path (Windows - No PATH setup needed)**

```powershell
# Use full path to psql (adjust version number)
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres
```

Or for different versions:
```powershell
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres
& "C:\Program Files\PostgreSQL\14\bin\psql.exe" -U postgres
```

Once connected, create the database:

```sql
-- Create the university database
CREATE DATABASE university_db;

-- Connect to the new database
\c university_db
```

#### Linux/macOS Setup

Open a terminal and connect to PostgreSQL:

```bash
# Connect to PostgreSQL as superuser
psql -U postgres
```

Once connected, create the database:

```sql
-- Create the university database
CREATE DATABASE university_db;

-- Connect to the new database
\c university_db
```

### 1.2 Run Lab Scripts in Order

The database schema is built progressively through the lab exercises. Run the SQL scripts in the following order:

**Quick Setup for Windows Users:**

We've provided a PowerShell script to automate the setup:

```powershell
# Navigate to Python App directory
cd "Part2\Python App"

# Run the setup script
.\setup_database.ps1
```

This script will:
- Find your PostgreSQL installation
- Create the database if needed
- Run all required lab scripts
- Verify the setup

**Manual Setup (Alternative):**

#### Windows - Using PowerShell or Command Prompt

**Option A: Using pgAdmin (Easiest for Windows)**

1. Open **pgAdmin**
2. Right-click on `university_db` → "Query Tool"
3. Open each SQL file and execute:
   - `Part1\Lab 1\Lab1.sql`
   - `Part1\Lab 3\lab3.sql`
   - `Part1\Lab 4\Lab4.sql`

**Option B: Using Command Line with Full Path**

```powershell
# Navigate to project root
cd "C:\Users\ram com\Downloads\SQL-Project"

# Lab 1: DDL - Create Tables and Insert Data
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -d university_db -f "Part1\Lab 1\Lab1.sql"

# Lab 3: Functions and Transactions
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -d university_db -f "Part1\Lab 3\lab3.sql"

# Lab 4: Triggers
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -d university_db -f "Part1\Lab 4\Lab4.sql"
```

**Note:** Replace `16` with your PostgreSQL version (15, 14, etc.)

**Option C: If psql is in PATH**

```powershell
# From the project root directory
psql -U postgres -d university_db -f "Part1\Lab 1\Lab1.sql"
psql -U postgres -d university_db -f "Part1\Lab 3\lab3.sql"
psql -U postgres -d university_db -f "Part1\Lab 4\Lab4.sql"
```

#### Linux/macOS

```bash
# From the project root directory
# Lab 1: DDL - Create Tables and Insert Data
psql -U postgres -d university_db -f "Part1/Lab 1/Lab1.sql"

# Lab 2: DML - Query Exercises (Optional for Part 2)
psql -U postgres -d university_db -f "Part1/Lab 2/Lab2.sql"

# Lab 3: Functions and Transactions
psql -U postgres -d university_db -f "Part1/Lab 3/lab3.sql"

# Lab 4: Triggers
psql -U postgres -d university_db -f "Part1/Lab 4/Lab4.sql"
```

#### What Each Lab Creates

**Lab 1: DDL - Create Tables and Insert Data**
- Core tables: `Department`, `Student`, `Instructor`, `Course`, `Room`, `Reservation`
- Extended tables: `Enrollment`, `Marks`
- Inserts sample data

**Lab 2: DML - Query Exercises (Optional)**
- Query exercises (not required for Part 2 setup, but safe to run)

**Lab 3: Functions and Transactions**
- `CheckReservation()` - Used by the Reservations module
- `rooms_with_capacity()`
- `get_department_id()`

**Lab 4: Triggers**
- `Student_Audit_Log` table
- `simple_student_trigger()` function
- `trg_audit_students_statement` trigger

### 1.3 Verify Database Setup

#### Using pgAdmin (Windows - Recommended)

1. Open **pgAdmin**
2. Expand `university_db` → "Schemas" → "public" → "Tables"
3. You should see tables listed

Or use Query Tool:
```sql
-- Check if key tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

#### Using Command Line

```sql
-- Connect to the database
\c university_db

-- List all tables
\dt

-- Check if key tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

You should see tables like:
- `Department`
- `Student`
- `Instructor`
- `Course`
- `Room`
- `Reservation`
- `Enrollment`
- `Marks`
- `Student_Audit_Log`

### 1.4 Verify Sample Data

Check that sample data was inserted:

```sql
-- Check students
SELECT COUNT(*) FROM Student;

-- Check departments
SELECT * FROM Department;

-- Check courses
SELECT * FROM Course;
```

---

## Step 2: Configure Database Connection

The Python application uses the `db_connection.py` module to connect to the database. Configure it as follows:

### 2.1 Default Configuration

The default configuration in `db_connection.py` is:

```python
host='localhost'
port=5432
database='university_db'  # Matches Part 1 database name
user='postgres'
password='postgres'
```

### 2.2 Custom Configuration Options

You can configure the connection in three ways:

#### Option A: Edit `db_connection.py` directly

Modify the `get_db_connection()` function:

```python
def get_db_connection():
    return DatabaseConnection(
        host='localhost',           # Your PostgreSQL host
        port=5432,                  # Your PostgreSQL port
        database='university_db',   # Database name from Part 1
        user='postgres',            # Your PostgreSQL username
        password='your_password'    # Your PostgreSQL password
    )
```

#### Option B: Use Environment Variables (Recommended)

Set environment variables before running the application:

**Windows (PowerShell):**
```powershell
$env:DB_HOST="localhost"
$env:DB_PORT="5432"
$env:DB_NAME="university_db"
$env:DB_USER="postgres"
$env:DB_PASSWORD="your_password"
```

**Windows (Command Prompt):**
```cmd
set DB_HOST=localhost
set DB_PORT=5432
set DB_NAME=university_db
set DB_USER=postgres
set DB_PASSWORD=your_password
```

**Linux/macOS:**
```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=university_db
export DB_USER=postgres
export DB_PASSWORD=your_password
```

#### Option C: Create a `.env` file (if using python-dotenv)

Create a `.env` file in the `Part2/Python App/` directory:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=university_db
DB_USER=postgres
DB_PASSWORD=your_password
```

**Note:** You would need to install `python-dotenv` and modify `db_connection.py` to load it.

### 2.3 Verify Connection Settings

The connection settings are used by all modules:
- CRUD Operations
- Assignments & Reservations
- Marks & Attendance
- Grading & Results
- Reporting (SQL Queries)
- Audit

---

## Step 3: Install Python Dependencies

Navigate to the Python App directory and install required packages:

```bash
cd "Part2/Python App"
pip install -r Requirements.txt
```

This installs:
- `psycopg2-binary` - PostgreSQL adapter for Python
- `PyQt5` - GUI framework

**Note:** If you encounter issues installing PyQt5 on some systems, you may need additional system dependencies. See [Troubleshooting](#troubleshooting).

---

## Step 4: Test the Application

After setting up the database and installing dependencies, test the application:

### 4.1 Test Database Connection (Recommended First Step)

Before running the main application, test the database connection:

```bash
# From the Part2/Python App directory
python test_connection.py
```

Or:

```bash
python3 test_connection.py
```

**Expected Output:**
- ✓ Connected to database
- ✓ PostgreSQL version displayed
- ✓ All required tables exist
- ✓ Sample data counts displayed
- ✓ Connection test completed successfully

**If errors occur:**
- Check database credentials in `db_connection.py`
- Verify PostgreSQL is running
- Ensure Part 1 lab scripts were run successfully

### 4.2 Start the Application

After successful connection test, start the main application:

```bash
# From the Part2/Python App directory
python App.py
```

Or:

```bash
python3 App.py
```

When the application starts, it will:
1. Attempt to connect to the database
2. Display connection status in the status bar
3. Show a warning if connection fails

**Expected Behavior:**
- Main window opens with 6 menu buttons
- Status bar shows: "Database connected successfully"
- No error messages

### 4.3 Test Each Module

Test each module to ensure proper database connectivity:

#### Test 1: CRUD Operations
1. Click "CRUD Operations"
2. Select "Department" from the dropdown
3. Click "Refresh" - should display existing departments
4. Try creating a new department

#### Test 2: Assignments & Reservations
1. Click "Assignment/Reservations"
2. Click "Refresh" - should display existing reservations
3. Try checking room availability

#### Test 3: Marks & Attendance
1. Click "Marks & Attendance"
2. Switch to "Marks" tab
3. Click "Refresh" - should display existing marks
4. Switch to "Attendance" tab
5. Click "Refresh" - should display attendance records (may be empty initially)

#### Test 4: Grading & Results
1. Click "Grading/Results Processing"
2. Select a course from dropdown
3. Click "Calculate Results" - should calculate student averages

#### Test 5: Reporting (SQL Queries)
1. Click "Reporting (SQL Queries)"
2. Select query "(a) List of students by group"
3. Click "Execute Query" - should display students

#### Test 6: Audit
1. Click "Audit"
2. Check "Marks Audit Log" tab - should display audit records
3. Check "Attendance Audit Log" tab - should display audit records
4. Check "Summary" tab - should show statistics

### 4.4 Verify Automatic Setup

The application automatically:
- Creates missing columns (`group_id`, `section_id` in Student table)
- Creates missing tables (`Attendance`, audit tables)
- Creates missing functions (reporting functions)
- Creates missing triggers (audit triggers)

Check the database to verify:

```sql
-- Check if Attendance table exists
SELECT * FROM Attendance LIMIT 1;

-- Check if audit tables exist
SELECT * FROM Marks_Audit_Log LIMIT 1;
SELECT * FROM Attendance_Audit_Log LIMIT 1;

-- Check if reporting functions exist
SELECT routine_name 
FROM information_schema.routines 
WHERE routine_schema = 'public' 
AND routine_type = 'FUNCTION';
```

---

## Troubleshooting

### Connection Issues

**Problem:** "Failed to connect to database"

**Solutions:**
1. Verify PostgreSQL is running:
   - **Windows:** 
     - Open "Services" (Windows key → type "services")
     - Look for "postgresql-x64-XX" service
     - Ensure it's "Running"
     - Or check pgAdmin connection
   - **Linux:**
     ```bash
     sudo systemctl status postgresql
     ```
   - **macOS:**
     ```bash
     brew services list
     ```

2. Verify database exists:
   - **Windows (pgAdmin):** Check databases list
   - **Windows (Command Line):**
     ```powershell
     & "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -l
     ```
   - **Linux/macOS:**
     ```bash
     psql -U postgres -l
     ```

3. Check credentials in `db_connection.py`

4. Verify firewall/network settings

5. Check PostgreSQL logs for errors

### psql Command Not Found (Windows)

**Problem:** `psql : Le terme «psql» n'est pas reconnu` (psql not recognized)

**Solutions:**

**Option 1: Use Full Path (Quick Fix)**
```powershell
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres
```

**Option 2: Add to PATH (Permanent Fix)**
1. Find PostgreSQL bin directory: `C:\Program Files\PostgreSQL\<version>\bin`
2. Open "Environment Variables":
   - Windows key → type "environment variables"
   - Click "Edit the system environment variables"
   - Click "Environment Variables" button
3. Under "System variables", find "Path" and click "Edit"
4. Click "New" and add: `C:\Program Files\PostgreSQL\16\bin`
   (Replace `16` with your version)
5. Click "OK" on all dialogs
6. **Restart PowerShell/Command Prompt**

**Option 3: Use pgAdmin (No Command Line Needed)**
- Use pgAdmin's Query Tool instead of command line
- All SQL scripts can be run through pgAdmin

### Missing Tables/Data

**Problem:** "Table does not exist" or "No data found"

**Solutions:**
1. Re-run Lab 1 SQL script:
   ```bash
   psql -U postgres -d university_db -f "Part1/Lab 1/Lab1.sql"
   ```

2. Verify tables exist:
   ```sql
   \dt
   ```

3. Check if data was inserted:
   ```sql
   SELECT COUNT(*) FROM Student;
   ```

### PyQt5 Installation Issues

**Problem:** Error installing PyQt5

**Solutions:**

**Windows:**
```bash
pip install --upgrade pip
pip install PyQt5
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install python3-pyqt5
pip install PyQt5
```

**macOS:**
```bash
brew install pyqt5
pip install PyQt5
```

### Function/Trigger Errors

**Problem:** "Function does not exist" or "Trigger error"

**Solutions:**
1. The application automatically creates missing functions/triggers
2. If errors persist, manually run:
   ```sql
   -- Re-run Lab 3 for functions
   psql -U postgres -d university_db -f "Part1/Lab 3/lab3.sql"
   
   -- Re-run Lab 4 for triggers
   psql -U postgres -d university_db -f "Part1/Lab 4/Lab4.sql"
   ```

### Permission Issues

**Problem:** "Permission denied" errors

**Solutions:**
1. Grant necessary permissions:
   ```sql
   GRANT ALL PRIVILEGES ON DATABASE university_db TO postgres;
   GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
   ```

2. Ensure you're using a user with sufficient privileges

---

## Database Schema Overview

The application works with the following main tables:

- **Department** - Academic departments
- **Student** - Student information
- **Instructor** - Faculty members
- **Course** - Course offerings
- **Room** - Classroom facilities
- **Reservation** - Room reservations
- **Enrollment** - Student course enrollments
- **Marks** - Student grades
- **Attendance** - Attendance records (created automatically)
- **Marks_Audit_Log** - Audit log for Marks table
- **Attendance_Audit_Log** - Audit log for Attendance table

---

## Next Steps

After successful setup and testing:

1. **Explore CRUD Operations** - Manage basic tables
2. **Create Reservations** - Use the CheckReservation function
3. **Record Marks & Attendance** - Add student data
4. **Process Grades** - Calculate student results
5. **Run Reports** - Execute complex SQL queries
6. **View Audit Logs** - Monitor database changes

---

## Support

For issues related to:
- **Database setup**: Refer to Part 1 README.md
- **Application issues**: Check error messages and logs
- **SQL errors**: Verify Part 1 lab scripts ran successfully

---

**Last Updated:** 2024
**Database Version:** PostgreSQL 12+
**Python Version:** 3.8+

