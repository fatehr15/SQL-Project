# Lab 3: SQL User-Defined Functions and Transactions

## Introduction

This lab demonstrates the implementation of **SQL User-Defined Functions (UDFs)** and **Transaction Management** in PostgreSQL. The objectives include creating reusable functions for database operations and implementing both simple and complex transactions using savepoints to ensure data integrity.

---

## 4.1 SQL User-Defined Functions

### 4.1.1 Function 1: Rooms with Capacity

This function returns all rooms that meet or exceed a specific capacity requirement.

**Function Definition:**

```sql
CREATE OR REPLACE FUNCTION rooms_with_capacity(min_capacity integer)
RETURNS TABLE(building varchar, roomno varchar, capacity integer)
LANGUAGE sql AS $$
    SELECT building, roomno, capacity
    FROM room
    WHERE capacity > $1
    ORDER BY capacity DESC;
$$;

```

**Use Case:**

```sql
-- Find all rooms with capacity greater than 30
SELECT * FROM rooms_with_capacity(30);

```

**Explanation:**

* Accepts a single integer parameter `min_capacity`.
* Returns a virtual table containing the building, room number, and capacity.
* Uses **positional notation ($1)** to reference the input.
* Results are sorted in descending order for better readability.

---

### 4.1.2 Function 2: Get Department ID

A utility function to quickly retrieve a primary key based on a department's name.

**Function Definition:**

```sql
CREATE OR REPLACE FUNCTION get_department_id(dept_name text)
RETURNS integer
LANGUAGE sql AS $$
    SELECT department_id
    FROM department
    WHERE name = $1
    LIMIT 1;
$$;

```

**Use Case:**

```sql
-- Get the ID of the Computer Science department
SELECT get_department_id('Computer Science');

```

**Explanation:**

* Streamlines lookups by converting a text name into an integer ID.
* Uses `LIMIT 1` to prevent errors if duplicate names exist.

---

### 4.1.3 Function 3: Check Reservation Conflicts

This advanced function identifies if a room is already booked during a requested time slot.

**Function Definition:**

```sql
CREATE OR REPLACE FUNCTION CheckReservation(
    p_building text,
    p_roomno text,
    p_date date,
    p_start time,
    p_end time
)
RETURNS integer
LANGUAGE plpgsql AS $$
DECLARE
    conflict_ids int[];
    conflicts_count int;
BEGIN
    SELECT array_agg(reservation_id) INTO conflict_ids
    FROM reservation
    WHERE building = p_building
      AND roomno = p_roomno
      AND reserv_date = p_date
      AND NOT (end_time <= p_start OR start_time >= p_end);
        
    IF conflict_ids IS NULL THEN
        RAISE NOTICE 'No conflicts. Reservation possible for % % on % from % to %',
            p_building, p_roomno, p_date, p_start, p_end;
        RETURN 0;
    ELSE
        SELECT array_length(conflict_ids, 1) INTO conflicts_count;
        RAISE NOTICE 'Conflicting reservation IDs: % (count = %)', 
            conflict_ids, conflicts_count;
        RETURN conflicts_count;
    END IF;
END;
$$;

```

**Use Case:**

```sql
-- Check if room A-301 is available on 2006-12-01 from 09:00 to 11:00
SELECT CheckReservation('A', '301', '2006-12-01'::date, '09:00:00'::time, '11:00:00'::time);

```

**Explanation:**

* Written in **PL/pgSQL** to allow for variables and conditional logic.
* **Conflict Logic:** Detects overlaps using the condition `NOT (end_time <= p_start OR start_time >= p_end)`.
* Provides feedback via `RAISE NOTICE` and returns the number of conflicts found.

---

## 4.2 Transactions

### 4.2.1 Simple Transaction 1: Atomic Insert

Ensures that a student record and their enrollment record are created simultaneously.

```sql
BEGIN;

INSERT INTO Student (Student_ID, Last_Name, First_Name, DOB) 
VALUES (6, 'Saad', 'El Saad', '1999-01-01');

INSERT INTO Enrollment (Student_ID, Course_ID, Dept_ID) 
VALUES (6, 1, 1);

COMMIT;

```

---

### 4.2.2 Simple Transaction 2: Reservation with Validation

Combines the conflict check function and the insertion into one atomic unit.

```sql
BEGIN;

SELECT CheckReservation('A', '301', '2006-12-01'::date, '09:00:00'::time, '11:00:00'::time);

INSERT INTO Reservation (Reservation_ID, Building, RoomNo, Course_ID, Department_ID, Instructor_ID, Reserv_Date, Start_Time, End_Time, Hours_Number)
VALUES (100, 'A', '301', 1, 1, 1, '2006-12-01'::date, '09:00:00'::time, '11:00:00'::time, 2);

COMMIT;

```

---

### 4.2.3 Transaction with Savepoint 1: Error Recovery

Demonstrates how to recover from a failed insertion without losing previous work.

```sql
BEGIN;

-- Insert two safe reservations
INSERT INTO Reservation (Reservation_ID, Building, RoomNo, Course_ID, Department_ID, Instructor_ID, Reserv_Date, Start_Time, End_Time, Hours_Number)
VALUES 
(101, 'B', '020', 1, 1, 1, '2006-12-10'::date, '08:30:00'::time, '10:30:00'::time, 2),
(102, 'B', '020', 1, 1, 2, '2006-12-10'::date, '10:45:00'::time, '12:45:00'::time, 2);

SAVEPOINT before_risky;

-- Risky: attempt to insert a conflicting reservation
INSERT INTO Reservation (Reservation_ID, Building, RoomNo, Course_ID, Department_ID, Instructor_ID, Reserv_Date, Start_Time, End_Time, Hours_Number)
VALUES (103, 'B', '020', 1, 1, 3, '2006-12-10'::date, '09:30:00'::time, '11:00:00'::time, 2);

-- Conflict detected: Roll back only the risky operation
ROLLBACK TO before_risky;

-- Insert a corrected non-conflicting reservation instead
INSERT INTO Reservation (Reservation_ID, Building, RoomNo, Course_ID, Department_ID, Instructor_ID, Reserv_Date, Start_Time, End_Time, Hours_Number)
VALUES (104, 'B', '020', 1, 1, 3, '2006-12-10'::date, '12:45:00'::time, '14:45:00'::time, 2);

COMMIT;

```

---

## Key Summary

### Concepts Demonstrated

| Concept | Description |
| --- | --- |
| **SQL Functions** | Simplifies repetitive queries into one-line calls. |
| **PL/pgSQL** | Enables procedural logic (IF/ELSE, Loops) inside the database. |
| **Atomicity** | Ensures a group of SQL statements either all succeed or all fail. |
| **Savepoints** | Allows "partial rollbacks" to specific points within a transaction. |

### Benefits

* **Data Integrity:** Prevents "orphaned" data (e.g., a student with no enrollment).
* **Performance:** Logic executed on the server reduces the amount of data sent over the network.
* **Maintainability:** Centralizing logic in functions makes updates easier.

---
