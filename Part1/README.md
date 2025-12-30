# NSCS Database Project Report

**Students:** Raid Kahlerras (A3), Hassani Fateh (A3)

---
# Database Management Labs - PostgreSQL

A comprehensive series of 4 laboratory exercises covering fundamental to advanced database concepts using PostgreSQL.

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Database Schema](#database-schema)
- [Installation & Setup](#installation--setup)
- [Lab Contents](#lab-contents)
- [Usage](#usage)
- [Lab Descriptions](#lab-descriptions)
- [Key Learning Outcomes](#key-learning-outcomes)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🎯 Overview

This repository contains four progressive SQL laboratory exercises that cover the complete spectrum of database management operations. The labs use a university course reservation system as the domain model, demonstrating real-world database design and implementation.

**Domain Model:** University Course Reservation System
- Track departments, students, instructors, and courses
- Manage room reservations for classes
- Record student enrollments and grades
- Audit database changes

## 📚 Prerequisites

### Required Software
- PostgreSQL 12.x or higher
- psql command-line tool
- Text editor or SQL IDE (pgAdmin, DBeaver, or VSCode with SQL extensions)

### Required Knowledge
- Basic SQL syntax
- Understanding of relational database concepts
- Familiarity with command-line interfaces

## 🗄️ Database Schema

The database consists of 8 main tables:

### Core Tables
1. **Department** - Academic departments
2. **Student** - Student information and contact details
3. **Instructor** - Faculty members with ranks
4. **Course** - Academic courses with descriptions
5. **Room** - Physical classroom spaces with capacity
6. **Reservation** - Room bookings for courses

### Extended Tables (Lab 1)
7. **Enrollment** - Student course enrollments
8. **Marks** - Student grades for courses

### Audit Tables (Lab 4)
9. **Student_Audit_Log** - Tracks changes to Student table

## 🚀 Installation & Setup

### 1. Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Windows:**
Download and install from [postgresql.org](https://www.postgresql.org/download/windows/)

### 2. Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE university_db;

# Connect to the database
\c university_db
```

### 3. Run Lab Scripts in Order

```bash
# Lab 1: DDL - Create tables and insert data
psql -U postgres -d university_db -f lab1.sql

# Lab 2: DML - Query exercises
psql -U postgres -d university_db -f Lab2.sql

# Lab 3: Functions and Transactions
psql -U postgres -d university_db -f lab3.sql

# Lab 4: Triggers
psql -U postgres -d university_db -f "lab 4.sql"
```

## 📁 Lab Contents

```
.
├── images
├── Lab 1
│   ├── ERD.png
│   ├── images
│   ├── lab1REPORT.md
│   └── Lab1.sql
├── Lab 2
│   ├── images
│   ├── lab2REPORT.md
│   └── Lab2.sql
├── Lab 3
│   ├── lab3REPORT.md
│   └── lab3.sql
├── Lab 4
│   ├── images
│   ├── lab4REPORT.md
│   └── Lab4.sql
├── PostgerLabs.pdf
└── README.md
```

## 💻 Usage

### Running Individual Labs

**Lab 1 - Setup:**
```bash
psql -U postgres -d university_db -f lab1.sql
```

**Lab 2 - Queries:**
```bash
# Run all queries
psql -U postgres -d university_db -f Lab2.sql

# Or run specific queries interactively
psql -U postgres -d university_db
university_db=# SELECT * FROM Student WHERE City = 'Algiers';
```

**Lab 3 - Functions:**
```bash
# Create functions
psql -U postgres -d university_db -f lab3.sql

# Test functions
psql -U postgres -d university_db
university_db=# SELECT * FROM rooms_with_capacity(20);
university_db=# SELECT CheckReservation('A','301','2006-12-01','09:00','11:00');
```

**Lab 4 - Triggers:**
```bash
# Create trigger and audit table
psql -U postgres -d university_db -f "lab 4.sql"

# Test trigger
university_db=# UPDATE Student SET City = 'TestCity' WHERE City IS NULL;
university_db=# SELECT * FROM Student_Audit_Log;
```

## 📖 Lab Descriptions

### Lab 1: Data Definition Language (DDL)
**Focus:** Database schema creation and data population

**Key Topics:**
- Creating tables with constraints (PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK)
- Defining relationships between tables
- Inserting sample data
- Schema evolution (adding Enrollment and Marks tables)
- Creating views for data aggregation

**Main Files:** `Lab 1/lab1.sql`

**Key Queries:**
```sql
-- Create Department table
CREATE TABLE Department(...);

-- Add enrollment tracking
CREATE TABLE Enrollment(...);

-- Create view for instructor reservations
CREATE VIEW View_Res AS ...;
```

---

### Lab 2: Data Manipulation Language (DML)
**Focus:** Querying and data retrieval

**Key Topics:**
- Basic SELECT statements
- WHERE clauses and filtering
- Pattern matching with LIKE
- Aggregate functions (COUNT, SUM, AVG, MAX)
- JOIN operations
- Subqueries and nested queries
- GROUP BY and HAVING clauses
- ORDER BY sorting

**Main Files:** `Lab2.sql`

**Sample Queries:**
- Query 1-5: Basic selection and filtering
- Query 6: Counting records
- Query 7: NULL value handling
- Query 8: Pattern matching
- Query 9-10: Aggregation with JOINs
- Query 11-12: Statistical functions
- Query 13-14: IN/NOT IN operators
- Query 15-17: Grouping and sorting
- Query 18-19: EXISTS and complex aggregations
- Query 20-21: Advanced subqueries

---

### Lab 3: Functions and Transactions
**Focus:** User-defined functions and transaction management

**Key Topics:**

#### Part A: SQL Functions
1. **rooms_with_capacity(min_capacity)** - Returns rooms exceeding a capacity threshold
2. **get_department_id(dept_name)** - Retrieves department ID by name
3. **CheckReservation(...)** - Validates room availability and detects conflicts

**Function Examples:**
```sql
-- Find large rooms
SELECT * FROM rooms_with_capacity(30);

-- Check for reservation conflicts
SELECT CheckReservation('A','301','2006-12-01','09:00','11:00');
```

#### Part B: Transactions
- Simple transactions with BEGIN/COMMIT
- Transaction rollback with ROLLBACK
- Savepoints for partial transaction rollback
- ACID properties demonstration

**Transaction Examples:**
```sql
-- Simple transaction
BEGIN;
INSERT INTO Student VALUES (...);
INSERT INTO Enrollment VALUES (...);
COMMIT;

-- Transaction with savepoint
BEGIN;
INSERT INTO Reservation VALUES (101, ...);
SAVEPOINT before_risky;
INSERT INTO Reservation VALUES (103, ...); -- May conflict
ROLLBACK TO before_risky;
INSERT INTO Reservation VALUES (104, ...); -- Corrected
COMMIT;
```

**Main Files:** `lab3.sql`

---

### Lab 4: Triggers and Audit Logging
**Focus:** Automated database behaviors and change tracking

**Key Topics:**
- Trigger functions in PL/pgSQL
- Statement-level triggers
- Row-level triggers
- Audit logging
- Special trigger variables (TG_OP, NEW, OLD)

**Components:**

1. **Audit Table:**
```sql
CREATE TABLE Student_Audit_Log (
    LogID SERIAL PRIMARY KEY,
    OperationType VARCHAR(50),
    OperationTime TIMESTAMP,
    Description TEXT
);
```

2. **Trigger Function:**
```sql
CREATE OR REPLACE FUNCTION simple_student_trigger()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO Student_Audit_Log (...)
    VALUES (TG_OP, CURRENT_TIMESTAMP, 'Student table changed');
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;
```

3. **Trigger:**
```sql
CREATE TRIGGER trg_audit_students_statement 
AFTER INSERT OR UPDATE OR DELETE ON Student
FOR EACH STATEMENT 
EXECUTE FUNCTION simple_student_trigger();
```

**Testing:**
```sql
-- Trigger will automatically log this change
UPDATE Student SET City = 'TestCity' WHERE City IS NULL;

-- View audit log
SELECT * FROM Student_Audit_Log;
```

**Main Files:** `lab 4.sql`

## 🎓 Key Learning Outcomes

After completing these labs, you will be able to:

### Technical Skills
- ✅ Design and implement normalized database schemas
- ✅ Write complex SQL queries with joins, subqueries, and aggregations
- ✅ Create user-defined functions in SQL and PL/pgSQL
- ✅ Manage transactions with proper ACID compliance
- ✅ Implement triggers for automated data management
- ✅ Handle NULL values and data validation
- ✅ Optimize queries using views and indexes

### Conceptual Understanding
- ✅ Understand referential integrity and foreign key constraints
- ✅ Apply normalization principles
- ✅ Implement business logic at the database level
- ✅ Design audit systems for compliance
- ✅ Handle concurrent data access with transactions

## 🔧 Troubleshooting

### Common Issues

**Issue 1: Connection refused**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL
sudo systemctl start postgresql
```

**Issue 2: Permission denied**
```bash
# Grant proper permissions
sudo -u postgres psql
GRANT ALL PRIVILEGES ON DATABASE university_db TO your_username;
```

**Issue 3: Trigger function error "RETURN NULL not allowed"**
```sql
-- For statement-level triggers, use RETURN NULL
-- For row-level AFTER triggers, use RETURN NULL
-- For row-level BEFORE triggers, use RETURN NEW or RETURN OLD
```

**Issue 4: Foreign key constraint violations**
```bash
# Check insertion order - parent tables must be populated first
# Correct order:
1. Department
2. Room
3. Course
4. Instructor & Student
5. Reservation
6. Enrollment & Marks
```

**Issue 5: Function already exists**
```sql
-- Use OR REPLACE to update functions
CREATE OR REPLACE FUNCTION function_name() ...

-- Or drop the function first
DROP FUNCTION IF EXISTS function_name;
```

### Viewing Database Objects

```sql
-- List all tables
\dt

-- Describe a table structure
\d table_name

-- List all functions
\df

-- List all triggers
SELECT * FROM pg_trigger;

-- View function definition
\sf function_name
```

## 📊 Sample Data Overview

The database includes:
- **4 Departments:** SADS, CCS, GRC, INS
- **5 Students:** From various cities in Algeria
- **6 Instructors:** With ranks from Substitute to PROF
- **5 Rooms:** Capacity ranging from 15 to 500
- **4 Courses:** Including Databases, C++, Advanced DBs, English
- **21 Reservations:** Spanning multiple dates and time slots

## 🔐 Best Practices Demonstrated

1. **Data Integrity:**
   - Primary and foreign key constraints
   - CHECK constraints for data validation
   - NOT NULL constraints for mandatory fields

2. **Code Organization:**
   - Meaningful table and column names
   - Consistent naming conventions
   - Comprehensive comments

3. **Security:**
   - Input validation through constraints
   - Audit logging for accountability

4. **Performance:**
   - Proper indexing through primary keys
   - Views for frequently used queries
   - Efficient query design

## 📝 Additional Resources

- [PostgreSQL Official Documentation](https://www.postgresql.org/docs/)
- [PostgreSQL Tutorial](https://www.postgresqltutorial.com/)
- [SQL Style Guide](https://www.sqlstyle.guide/)
- [Database Normalization](https://en.wikipedia.org/wiki/Database_normalization)

## 🤝 Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Create a Pull Request


## 📞 Support

For questions or issues:
- Review PostgreSQL documentation
- Create an issue in the repository

---
