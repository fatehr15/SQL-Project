# Lab 1: Database Schema Creation and Management
---

## 1. Introduction

### 1.1 Objective
This lab focuses on mastering the Data Definition Language (DDL) in PostgreSQL to create, modify, and manage database schemas. The specific goals include:

- Understanding and implementing DDL commands
- Creating a complete database schema for a university management system
- Performing schema evolution by adding new tables
- Inserting and manipulating data
- Creating views for data abstraction

### 1.2 PostgreSQL Overview
PostgreSQL is an enterprise-grade, open-source object-relational database management system with over 30 years of active development. Key characteristics relevant to this lab include:

- **ACID Compliance**: Ensures data integrity for transactional operations
- **Advanced SQL Support**: Provides comprehensive DDL and DML capabilities including foreign keys, constraints, and triggers
- **Extensibility**: Supports custom data types and user-defined functions
- **MVCC Architecture**: Enables high concurrency without locking issues

---

## 2. Database Design and Implementation

### 2.1 Database Creation

The lab began with creating a university database using the `psql` command-line tool:

```sql
CREATE DATABASE university;
\c university
```

This establishes the database context for all subsequent operations.

### 2.2 Schema Design

The university management system consists of six core tables with the following relationships:

#### 2.2.1 Entity Tables

**Department Table**
- Stores academic departments
- Primary Key: `Department_id`
- Unique constraint on department name to prevent duplicates

**Student Table**
- Contains student personal information
- Primary Key: `Student_ID`
- Includes comprehensive contact details (address, phone, fax, email)
- All contact fields are optional (DEFAULT NULL)

**Instructor Table**
- Manages faculty information
- Primary Key: `Instructor_ID`
- Foreign Key: `Department_ID` (links to Department)
- Includes rank constraint: only 'Substitute', 'MCB', 'MCA', or 'PROF' allowed
- Enforces referential integrity with Department table

**Room Table**
- Tracks classroom facilities
- Composite Primary Key: `(Building, RoomNo)`
- Check constraint: Capacity must be greater than 1

**Course Table**
- Stores course offerings
- Composite Primary Key: `(Course_ID, Department_ID)`
- Foreign Key: `Department_ID` (links to Department)
- Includes course description field for detailed information

**Reservation Table**
- Central table managing room bookings for courses
- Primary Key: `Reservation_ID`
- Multiple foreign keys establishing relationships with:
  - Room (Building, RoomNo)
  - Course (Course_ID, Department_ID)
  - Instructor (Instructor_ID)
- Business rules enforced through constraints:
  - `Hours_Number >= 1`
  - `Start_Time < End_Time`
  - Default values for date and time fields

### 2.3 Referential Integrity

The schema implements comprehensive referential integrity through foreign key constraints with `RESTRICT` options on both UPDATE and DELETE operations. This prevents:

- Deletion of departments that have associated instructors or courses
- Deletion of rooms, courses, or instructors that have reservations
- Updates to primary keys that would orphan dependent records

---

## 3. Data Population

### 3.1 Sample Data Insertion

The database was populated with sample data across all tables:

**Departments (4 records)**
- SADS, CCS, GRC, INS

**Students (5 records)**
- Diverse student population from different Algerian cities (Algiers, Batna, Oran, Annaba, Constantine)

**Instructors (6 records)**
- Faculty with various ranks distributed across departments
- Mix of complete and incomplete contact information

**Rooms (5 records)**
- Buildings A, B, and C with varying capacities (15 to 500)
- Includes both regular classrooms and halls

**Courses (4 records)**
- Database-related courses and English course
- Detailed descriptions for academic programs

**Reservations (21 records)**
- Extensive booking history from 2003 and 2006
- Multiple instructors teaching the same courses
- Various time slots (morning and afternoon sessions)

---

## 4. Schema Evolution

### 4.1 Enrollment Table

A new table was created to manage student enrollments in courses:

```sql
CREATE TABLE Enrollment (
    Student_ID int,
    Course_ID int,
    Dept_ID int,
    Enroll_Date date DEFAULT CURRENT_DATE,
    PRIMARY KEY (Student_ID, Course_ID, Dept_ID),
    FOREIGN KEY (Student_ID) REFERENCES Student(Student_ID),
    FOREIGN KEY (Course_ID, Dept_ID) REFERENCES Course(Course_ID, Department_ID)
);
```

**Design Features:**
- Composite primary key prevents duplicate enrollments
- Automatic date stamping with `DEFAULT CURRENT_DATE`
- Maintains referential integrity with both Student and Course tables
- Supports many-to-many relationship between students and courses

### 4.2 Marks Table

A grading system was implemented through the Marks table:

```sql
CREATE TABLE Marks (
    mark_id SERIAL PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    dept_id INT NOT NULL, 
    mark NUMERIC NOT NULL CHECK (mark BETWEEN 0 AND 20),
    mark_date DATE NOT NULL DEFAULT CURRENT_DATE,
    
    FOREIGN KEY(student_id) REFERENCES Student(student_id),
    FOREIGN KEY(course_id, dept_id) REFERENCES Course(course_id, department_id)
);
```

**Design Features:**
- Auto-incrementing `mark_id` using SERIAL data type
- Business rule validation: marks must be between 0 and 20
- Allows multiple marks per student per course (supporting retakes and multiple assessments)
- Timestamp tracking with `mark_date`
- Complete referential integrity with Student and Course tables

---

## 5. Views Implementation

### 5.1 Regular View

A regular view was created to monitor instructor workload:

```sql
CREATE VIEW View_Res AS
SELECT instructor_id, COUNT(*) AS total
FROM Reservation
GROUP BY instructor_id;
```

**Characteristics:**
- **Dynamic**: Query executes each time the view is accessed
- **Real-time data**: Always reflects current state of Reservation table
- **Purpose**: Provides quick summary of reservation counts per instructor
- **Use case**: Workload analysis and resource allocation

### 5.2 Materialized View (Required Implementation)

For performance-critical scenarios, a materialized view should be created:

```sql
CREATE MATERIALIZED VIEW Mat_View_Res AS
SELECT instructor_id, COUNT(*) AS total
FROM Reservation
GROUP BY instructor_id;
```

**Advantages over Regular View:**
- Pre-computed results stored physically
- Faster query performance for complex aggregations
- Reduces server load for frequently accessed summaries
- Requires periodic refresh: `REFRESH MATERIALIZED VIEW Mat_View_Res;`

**Trade-offs:**
- Data may become stale between refreshes
- Requires additional storage space
- Best for reports and analytics where slight delays are acceptable

---

## 6. Database Operations

### 6.1 Table Listing
The `\dt` command in psql was used to verify all created tables:
- Department
- Student
- Instructor
- Room
- Course
- Reservation
- Enrollment
- Marks

### 6.2 Data Verification
The `\t` command was utilized to toggle tuple-only mode, displaying raw data without column headers for easier data export and verification.

### 6.3 Table Dropping Sequence

When dropping tables, the order must respect foreign key dependencies:

```sql
DROP TABLE Reservation;  -- First: depends on Room, Course, Instructor
DROP TABLE Enrollment;   -- Depends on Student and Course
DROP TABLE Marks;        -- Depends on Student and Course
DROP TABLE Course;       -- Depends on Department
DROP TABLE Instructor;   -- Depends on Department
DROP TABLE Student;      -- Independent
DROP TABLE Room;         -- Independent
DROP TABLE Department;   -- Last: referenced by Course and Instructor
```

**Important Note:** The provided drop sequence in the lab document would fail because it attempts to drop Department before Course and Instructor, violating referential integrity constraints.

---

## 7. Entity-Relationship Diagram

The database schema can be represented with the following relationships:

**One-to-Many Relationships:**
- Department → Instructor (1:N)
- Department → Course (1:N)

**Many-to-Many Relationships:**
- Student ↔ Course (through Enrollment table)
- Student ↔ Course (through Marks table)

**Complex Relationships:**
- Reservation links Room, Course, and Instructor (junction table with additional attributes)

---

## 8. Lessons Learned

### 8.1 DDL Best Practices
1. **Constraint naming**: Using descriptive names (e.g., `PK_Student`, `FK_Instructor_Department_ID`) improves maintainability
2. **Default values**: Reduce application logic and ensure data consistency
3. **Check constraints**: Enforce business rules at the database level
4. **Composite keys**: Useful when natural business keys span multiple columns

### 8.2 Schema Evolution
- Adding tables to existing schemas requires careful consideration of referential integrity
- New relationships must maintain consistency with existing data model
- SERIAL data type simplifies surrogate key management

### 8.3 View Strategy
- Regular views for current, dynamic data requirements
- Materialized views for performance optimization of complex aggregations
- Views provide security through selective column exposure

---

## 9. Potential Improvements

1. **Add indexes**: Create indexes on foreign keys and frequently queried columns to improve performance
2. **Implement triggers**: Add audit triggers to track changes to critical tables
3. **Add cascading options**: Consider CASCADE on some foreign keys where appropriate (e.g., deleting a course could cascade to enrollments)
4. **Normalization review**: The Reservation table's composite foreign key on (Course_ID, Department_ID) could be simplified
5. **Data validation**: Add more check constraints (e.g., email format validation, phone number format)

---

## 10. Conclusion

This lab successfully demonstrated the complete lifecycle of database schema creation using PostgreSQL's DDL capabilities. The university management system provides a realistic example of relational database design with proper normalization, referential integrity, and business rule enforcement. The addition of Enrollment and Marks tables showcased schema evolution techniques, while the view implementations illustrated different approaches to data abstraction and query optimization.

The hands-on experience with psql tool reinforced understanding of SQL syntax and PostgreSQL-specific features, providing a solid foundation for more advanced database operations and administration tasks.
