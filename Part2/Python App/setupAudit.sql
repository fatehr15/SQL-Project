-- ============================================================================
-- AUDIT SYSTEM SETUP FOR UNIVERSITY DATABASE
-- ============================================================================
-- This script creates the audit_log table and triggers to track
-- INSERT, UPDATE, and DELETE operations on student marks and attendance
-- ============================================================================

-- Drop existing audit objects if they exist
DROP TRIGGER IF EXISTS audit_student_mark_trigger ON student_mark;
DROP TRIGGER IF EXISTS audit_student_attendance_trigger ON student_attendance;
DROP FUNCTION IF EXISTS audit_student_mark_changes();
DROP FUNCTION IF EXISTS audit_student_attendance_changes();
DROP TABLE IF EXISTS audit_log;

-- Create audit_log table
CREATE TABLE audit_log (
    audit_id SERIAL PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    operation_type VARCHAR(10) NOT NULL CHECK (operation_type IN ('INSERT', 'UPDATE', 'DELETE')),
    record_id INTEGER,
    operation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_name VARCHAR(100) DEFAULT CURRENT_USER,
    details TEXT
);

-- Create index for faster queries
CREATE INDEX idx_audit_log_table ON audit_log(table_name);
CREATE INDEX idx_audit_log_operation ON audit_log(operation_type);
CREATE INDEX idx_audit_log_time ON audit_log(operation_time DESC);

-- ============================================================================
-- TRIGGER FUNCTION FOR student_mark TABLE
-- ============================================================================
CREATE OR REPLACE FUNCTION audit_student_mark_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log (table_name, operation_type, record_id, details)
        VALUES (
            'student_mark',
            'INSERT',
            NEW.mark_id,
            FORMAT('Student: %s, Course: %s, Mark: %s', 
                   NEW.student_id, NEW.course_id, NEW.mark)
        );
        RETURN NEW;
        
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (table_name, operation_type, record_id, details)
        VALUES (
            'student_mark',
            'UPDATE',
            NEW.mark_id,
            FORMAT('Student: %s, Course: %s, Old Mark: %s → New Mark: %s',
                   NEW.student_id, NEW.course_id, OLD.mark, NEW.mark)
        );
        RETURN NEW;
        
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (table_name, operation_type, record_id, details)
        VALUES (
            'student_mark',
            'DELETE',
            OLD.mark_id,
            FORMAT('Student: %s, Course: %s, Mark: %s',
                   OLD.student_id, OLD.course_id, OLD.mark)
        );
        RETURN OLD;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TRIGGER FUNCTION FOR student_attendance TABLE
-- ============================================================================
CREATE OR REPLACE FUNCTION audit_student_attendance_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log (table_name, operation_type, record_id, details)
        VALUES (
            'student_attendance',
            'INSERT',
            NEW.attendance_id,
            FORMAT('Student: %s, Course: %s, Date: %s, Status: %s',
                   NEW.student_id, NEW.course_id, NEW.attendance_date, NEW.status)
        );
        RETURN NEW;
        
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (table_name, operation_type, record_id, details)
        VALUES (
            'student_attendance',
            'UPDATE',
            NEW.attendance_id,
            FORMAT('Student: %s, Course: %s, Date: %s, Old Status: %s → New Status: %s',
                   NEW.student_id, NEW.course_id, NEW.attendance_date, OLD.status, NEW.status)
        );
        RETURN NEW;
        
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (table_name, operation_type, record_id, details)
        VALUES (
            'student_attendance',
            'DELETE',
            OLD.attendance_id,
            FORMAT('Student: %s, Course: %s, Date: %s, Status: %s',
                   OLD.student_id, OLD.course_id, OLD.attendance_date, OLD.status)
        );
        RETURN OLD;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- CREATE TRIGGERS
-- ============================================================================

-- Trigger for student_mark table
CREATE TRIGGER audit_student_mark_trigger
AFTER INSERT OR UPDATE OR DELETE ON student_mark
FOR EACH ROW
EXECUTE FUNCTION audit_student_mark_changes();

-- Trigger for student_attendance table
CREATE TRIGGER audit_student_attendance_trigger
AFTER INSERT OR UPDATE OR DELETE ON student_attendance
FOR EACH ROW
EXECUTE FUNCTION audit_student_attendance_changes();

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify audit_log table exists
SELECT 'audit_log table created successfully' AS status;

-- Verify triggers exist
SELECT 
    trigger_name,
    event_object_table,
    action_timing,
    string_agg(event_manipulation, ', ' ORDER BY event_manipulation) AS events
FROM information_schema.triggers
WHERE trigger_name LIKE 'audit_%'
GROUP BY trigger_name, event_object_table, action_timing;

COMMENT ON TABLE audit_log IS 'Audit trail for tracking all INSERT, UPDATE, and DELETE operations on student marks and attendance';
COMMENT ON COLUMN audit_log.operation_type IS 'Type of SQL operation: INSERT, UPDATE, or DELETE';
COMMENT ON COLUMN audit_log.operation_time IS 'Timestamp when the operation occurred';
COMMENT ON COLUMN audit_log.user_name IS 'Database user who performed the operation';
COMMENT ON COLUMN audit_log.details IS 'Additional details about the change';