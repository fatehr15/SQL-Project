-- Functions
-- 1) rooms_with_capacity: return rooms with capacity > min_capacity
CREATE OR REPLACE FUNCTION rooms_with_capacity(min_capacity integer)
RETURNS TABLE(building varchar, roomno varchar, capacity integer)
LANGUAGE sql AS $$
SELECT building, roomno, capacity
FROM room
WHERE capacity > $1
ORDER BY capacity DESC;
$$;


-- 2) get_department_id: return department_id for a given name
CREATE OR REPLACE FUNCTION get_department_id(dept_name text)
RETURNS integer
LANGUAGE sql AS $$
SELECT department_id
FROM department
WHERE name = $1
LIMIT 1;
$$;


-- 3) CheckReservation: check conflicts and return number of conflicts
CREATE OR REPLACE FUNCTION CheckReservation(p_building text,p_roomno text,p_date date,p_start time,p_end time)
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
SELECT array_length(conflict_ids,1) INTO conflicts_count;
RAISE NOTICE 'Conflicting reservation IDs: % (count = %)', conflict_ids, conflicts_count;
RETURN conflicts_count;
END IF;
END;
$$;


--Transactions
-- Insert a new student
BEGIN;
INSERT INTO Student (Student_ID, Last_Name, First_Name, DOB) VALUES (6, 'Saad', 'El Saad', '1999-01-01');
INSERT INTO Enrollment (Student_ID, Course_ID, Dept_ID) VALUES (6, 1, 1);
COMMIT;



-- Simple transaction (no savepoints): create a new reservation (atomic)
BEGIN;
SELECT CheckReservation('A','301','2006-12-01'::date,'09:00:00'::time,'11:00:00'::time);
INSERT INTO Reservation (Reservation_ID, Building, RoomNo, Course_ID, Department_ID, Instructor_ID,Reserv_Date, Start_Time, End_Time, Hours_Number)
VALUES (100, 'A', '301', 1, 1, 1,'2006-12-01'::date, '09:00:00'::time, '11:00:00'::time, 2);
COMMIT;



-- Transaction with savepoint: insert several reservations, drop the problematic one
BEGIN;
-- Insert two safe reservations
INSERT INTO Reservation (Reservation_ID, Building, RoomNo, Course_ID, Department_ID, Instructor_ID, Reserv_Date, Start_Time, End_Time, Hours_Number)
VALUES
(101, 'B', '020', 1, 1, 1, '2006-12-10'::date, '08:30:00'::time, '10:30:00'::time, 2),
(102, 'B', '020', 1, 1, 2, '2006-12-10'::date, '10:45:00'::time, '12:45:00'::time, 2);
-- Savepoint before risky operation
SAVEPOINT before_risky;
-- Risky: attempt to insert a reservation that overlaps an existing reservation (e.g. conflicts with 101)
INSERT INTO Reservation (Reservation_ID, Building, RoomNo, Course_ID, Department_ID, Instructor_ID, Reserv_Date, Start_Time, End_Time, Hours_Number)
VALUES
(103, 'B', '020', 1, 1, 3, '2006-12-10'::date, '09:30:00'::time, '11:00:00'::time, 2);
-- If the above insert fails or we decide it's bad, roll back to the savepoint:
ROLLBACK TO before_risky;
-- Insert a corrected non-conflicting reservation instead
INSERT INTO Reservation (Reservation_ID, Building, RoomNo, Course_ID, Department_ID, Instructor_ID, Reserv_Date, Start_Time, End_Time, Hours_Number)
VALUES
(104, 'B', '020', 1, 1, 3, '2006-12-10'::date, '12:45:00'::time, '14:45:00'::time, 2);
COMMIT;
-- Transaction with savepoints: multi-step update with partial rollback
BEGIN;
-- Step 1: bump capacities (bulk change)
UPDATE Room
SET Capacity = Capacity + 5
WHERE building = 'B';
SAVEPOINT after_capacity_bump;
-- Step 2 (risky): insert a reservation with invalid time (start >= end) to show partial rollback
-- Intentional mistake: start time 15:00, end time 14:00 (violates the CK_Reservation_StartEndTime)
INSERT INTO Reservation (Reservation_ID, Building, RoomNo, Course_ID, Department_ID, Instructor_ID, Reserv_Date, Start_Time, End_Time, Hours_Number)
VALUES (110, 'C', 'Hall 2', 4, 4, 6, '2006-12-20'::date, '15:00:00'::time, '14:00:00'::time, 1);



