-- 1. Creating the audit table
CREATE TABLE Student_Audit_Log (
    LogID SERIAL PRIMARY KEY,
    OperationType VARCHAR(50) NOT NULL,
    OperationTime TIMESTAMP NOT NULL,
    Description TEXT
);

-- 2.trigger function
CREATE OR REPLACE FUNCTION simple_student_trigger()
RETURNS TRIGGER 
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO Student_Audit_Log (OperationType, OperationTime, Description)
    VALUES (TG_OP, CURRENT_TIMESTAMP, 'Student table changed');
    
    RETURN NULL; 
END;
$$;

-- 3. The trigger (This syntax was correct, but failed because the function above it was invalid)
CREATE TRIGGER trg_audit_students_statement 
AFTER INSERT OR UPDATE OR DELETE ON Student
FOR EACH STATEMENT EXECUTE FUNCTION simple_student_trigger();

--- 4. Test the trigger 
UPDATE Student SET City = 'TestCity' WHERE City IS NULL;
SELECT * FROM Student_Audit_Log;
