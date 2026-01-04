-- PostgreSQL Functions for Reporting Module
-- These functions will be called from Python for complex queries

-- Function 1: Get Instructor Schedule (Time table of instructor)
CREATE OR REPLACE FUNCTION get_instructor_schedule(p_instructor_id INTEGER)
RETURNS TABLE (
    reservation_id INTEGER,
    building VARCHAR,
    roomno VARCHAR,
    course_name VARCHAR,
    department_name VARCHAR,
    reserv_date DATE,
    start_time TIME,
    end_time TIME,
    hours_number INTEGER
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT 
        r.Reservation_ID,
        r.Building,
        r.RoomNo,
        c.name AS course_name,
        d.name AS department_name,
        r.Reserv_Date,
        r.Start_Time,
        r.End_Time,
        r.Hours_Number
    FROM Reservation r
    JOIN Course c ON r.Course_ID = c.Course_ID AND r.Department_ID = c.Department_ID
    JOIN Department d ON r.Department_ID = d.Department_id
    WHERE r.Instructor_ID = p_instructor_id
    ORDER BY r.Reserv_Date, r.Start_Time;
END;
$$;

-- Function 2: Get Passing Students (Students who passed in a semester/course)
CREATE OR REPLACE FUNCTION get_passing_students(
    p_course_id INTEGER DEFAULT NULL,
    p_dept_id INTEGER DEFAULT NULL,
    p_passing_grade NUMERIC DEFAULT 10.0
)
RETURNS TABLE (
    student_id INTEGER,
    student_name VARCHAR,
    course_id INTEGER,
    course_name VARCHAR,
    average_mark NUMERIC,
    mark_count INTEGER
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT 
        m.student_id,
        s.Last_Name || ', ' || s.First_Name AS student_name,
        m.course_id,
        c.name AS course_name,
        ROUND(AVG(m.mark)::NUMERIC, 2) AS average_mark,
        COUNT(m.mark_id)::INTEGER AS mark_count
    FROM Marks m
    JOIN Student s ON m.student_id = s.Student_ID
    JOIN Course c ON m.course_id = c.Course_ID AND m.dept_id = c.Department_ID
    WHERE (p_course_id IS NULL OR m.course_id = p_course_id)
      AND (p_dept_id IS NULL OR m.dept_id = p_dept_id)
    GROUP BY m.student_id, s.Last_Name, s.First_Name, m.course_id, c.name
    HAVING AVG(m.mark) >= p_passing_grade
    ORDER BY average_mark DESC, s.Last_Name;
END;
$$;

-- Function 3: Get Failed Modules (Students with failing grade)
CREATE OR REPLACE FUNCTION get_failed_modules(p_student_id INTEGER)
RETURNS TABLE (
    course_id INTEGER,
    dept_id INTEGER,
    course_name VARCHAR,
    department_name VARCHAR,
    average_mark NUMERIC,
    passing_grade NUMERIC,
    mark_count INTEGER
)
LANGUAGE plpgsql AS $$
DECLARE
    v_passing_grade NUMERIC;
BEGIN
    RETURN QUERY
    SELECT 
        m.course_id,
        m.dept_id,
        c.name AS course_name,
        d.name AS department_name,
        ROUND(AVG(m.mark)::NUMERIC, 2) AS average_mark,
        COALESCE(c.passing_grade, 10.0) AS passing_grade,
        COUNT(m.mark_id)::INTEGER AS mark_count
    FROM Marks m
    JOIN Course c ON m.course_id = c.Course_ID AND m.dept_id = c.Department_ID
    JOIN Department d ON m.dept_id = d.Department_id
    WHERE m.student_id = p_student_id
    GROUP BY m.course_id, m.dept_id, c.name, d.name, c.passing_grade
    HAVING AVG(m.mark) < COALESCE(c.passing_grade, 10.0)
    ORDER BY c.name;
END;
$$;

-- Function 4: Check Resit Eligibility
CREATE OR REPLACE FUNCTION check_resit_eligibility(p_student_id INTEGER)
RETURNS TABLE (
    course_id INTEGER,
    dept_id INTEGER,
    course_name VARCHAR,
    department_name VARCHAR,
    average_mark NUMERIC,
    passing_grade NUMERIC,
    eligible BOOLEAN,
    reason TEXT
)
LANGUAGE plpgsql AS $$
DECLARE
    v_passing_grade NUMERIC;
    v_avg_mark NUMERIC;
BEGIN
    RETURN QUERY
    SELECT 
        m.course_id,
        m.dept_id,
        c.name AS course_name,
        d.name AS department_name,
        ROUND(AVG(m.mark)::NUMERIC, 2) AS average_mark,
        COALESCE(c.passing_grade, 10.0) AS passing_grade,
        CASE 
            WHEN AVG(m.mark) < COALESCE(c.passing_grade, 10.0) 
                 AND AVG(m.mark) >= (COALESCE(c.passing_grade, 10.0) - 2.0)
            THEN TRUE
            ELSE FALSE
        END AS eligible,
        CASE 
            WHEN AVG(m.mark) >= COALESCE(c.passing_grade, 10.0) THEN 'Passed - No resit needed'
            WHEN AVG(m.mark) < (COALESCE(c.passing_grade, 10.0) - 2.0) THEN 'Grade too low for resit'
            ELSE 'Eligible for resit examination'
        END AS reason
    FROM Marks m
    JOIN Course c ON m.course_id = c.Course_ID AND m.dept_id = c.Department_ID
    JOIN Department d ON m.dept_id = d.Department_id
    WHERE m.student_id = p_student_id
    GROUP BY m.course_id, m.dept_id, c.name, d.name, c.passing_grade
    HAVING AVG(m.mark) < COALESCE(c.passing_grade, 10.0)
    ORDER BY c.name;
END;
$$;

-- Function 5: Check Attendance Exclusion
CREATE OR REPLACE FUNCTION check_attendance_exclusion(p_student_id INTEGER, p_min_attendance_rate NUMERIC DEFAULT 0.75)
RETURNS TABLE (
    course_id INTEGER,
    dept_id INTEGER,
    course_name VARCHAR,
    department_name VARCHAR,
    total_sessions INTEGER,
    attended_sessions INTEGER,
    attendance_rate NUMERIC,
    excluded BOOLEAN,
    reason TEXT
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT 
        a.course_id,
        a.dept_id,
        c.name AS course_name,
        d.name AS department_name,
        COUNT(DISTINCT a.attendance_date)::INTEGER AS total_sessions,
        COUNT(CASE WHEN a.status IN ('Present', 'Late') THEN 1 END)::INTEGER AS attended_sessions,
        ROUND(
            (COUNT(CASE WHEN a.status IN ('Present', 'Late') THEN 1 END)::NUMERIC / 
             NULLIF(COUNT(DISTINCT a.attendance_date), 0)) * 100, 2
        ) AS attendance_rate,
        CASE 
            WHEN (COUNT(CASE WHEN a.status IN ('Present', 'Late') THEN 1 END)::NUMERIC / 
                  NULLIF(COUNT(DISTINCT a.attendance_date), 0)) < p_min_attendance_rate
            THEN TRUE
            ELSE FALSE
        END AS excluded,
        CASE 
            WHEN (COUNT(CASE WHEN a.status IN ('Present', 'Late') THEN 1 END)::NUMERIC / 
                  NULLIF(COUNT(DISTINCT a.attendance_date), 0)) < p_min_attendance_rate
            THEN 'Attendance below ' || (p_min_attendance_rate * 100)::TEXT || '% threshold'
            ELSE 'Attendance acceptable'
        END AS reason
    FROM Attendance a
    JOIN Course c ON a.course_id = c.Course_ID AND a.dept_id = c.Department_ID
    JOIN Department d ON a.dept_id = d.Department_id
    WHERE a.student_id = p_student_id
    GROUP BY a.course_id, a.dept_id, c.name, d.name
    ORDER BY attendance_rate ASC, c.name;
END;
$$;

