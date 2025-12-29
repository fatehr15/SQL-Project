
-- creating tables 

CREATE TABLE Department(
    Department_id integer,
    name varchar(25) NOT NULL,
    CONSTRAINT UN_Department_Name UNIQUE (name),
    CONSTRAINT PK_Department PRIMARY KEY(Department_Id)
);

CREATE TABLE Student(
    Student_ID integer,
    Last_Name varchar(25) NOT NULL,
    First_Name varchar(25) NOT NULL,
    DOB date NOT NULL,
    Address varchar(50) DEFAULT NULL,
    City varchar(25) DEFAULT NULL,
    Zip_Code varchar(9) DEFAULT NULL,
    Phone varchar(10) DEFAULT NULL,
    Fax varchar(10) DEFAULT NULL,
    Email varchar(100) DEFAULT NULL,
    CONSTRAINT PK_Student PRIMARY KEY (Student_ID)
);
CREATE TABLE Room(
    Building varchar(1),
    RoomNo varchar(10),
    Capacity integer CHECK (Capacity > 1),
    CONSTRAINT PK_Room PRIMARY KEY (Building, RoomNo)
);
CREATE TABLE Course(
    Course_ID int4 NOT NULL,
    Department_ID int4 NOT NULL,
    name varchar(60) NOT NULL,
    Description varchar(1000),
    CONSTRAINT PK_Course PRIMARY KEY (Course_ID, Department_ID),
    CONSTRAINT FK_Course_Department FOREIGN KEY (Department_ID) 
        REFERENCES Department (Department_ID)
        ON UPDATE RESTRICT ON DELETE RESTRICT
);
CREATE TABLE Instructor(
    Instructor_ID integer,
    Department_ID integer NOT NULL,
    Last_Name varchar(25) NOT NULL,
    First_Name varchar(25) NOT NULL,
    Rank varchar(25),
    Phone varchar(10) DEFAULT NULL,
    Fax varchar(10) DEFAULT NULL,
    Email varchar(100) DEFAULT NULL,
    CONSTRAINT PK_Instructor PRIMARY KEY (Instructor_ID),
    CONSTRAINT CK_Instructor_Rank CHECK (Rank IN ('Substitute','MCB', 'MCA', 'PROF')),
    CONSTRAINT FK_Instructor_Department_ID FOREIGN KEY (Department_ID) 
        REFERENCES Department (Department_ID)
        ON UPDATE RESTRICT ON DELETE RESTRICT
);
CREATE TABLE Reservation(
    Reservation_ID integer, 
    Building varchar(1) NOT NULL,
    RoomNo varchar(10) NOT NULL,
    Course_ID integer NOT NULL,
    Department_ID integer NOT NULL,
    Instructor_ID integer NOT NULL,
    Reserv_Date date NOT NULL DEFAULT CURRENT_DATE,
    Start_Time time NOT NULL DEFAULT CURRENT_TIME,
    End_Time time NOT NULL DEFAULT '23:00:00',
    Hours_Number integer NOT NULL,
    CONSTRAINT PK_Reservation PRIMARY KEY (Reservation_ID),
    CONSTRAINT FK_Reservation_Room FOREIGN KEY (Building, RoomNo) 
        REFERENCES Room (Building, RoomNo)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT FK_Reservation_Course FOREIGN KEY (Course_ID, Department_ID) 
        REFERENCES Course (Course_ID, Department_ID)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT FK_Reservation_Instructor FOREIGN KEY (Instructor_ID) 
        REFERENCES Instructor (Instructor_ID)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT CK_Reservation_Hours_Number CHECK (Hours_Number >= 1),
    CONSTRAINT CK_Reservation_StartEndTime CHECK (Start_Time < End_Time)
);
--INSERTING
--INSERTING INTO DEPARTEMENTS
INSERT INTO Department VALUES ('1','SADS');
INSERT INTO Department VALUES ('2','CCS');
INSERT INTO Department VALUES ('3','GRC');
INSERT INTO Department VALUES ('4','INS');
--INSERTING INTO students
INSERT INTO Student VALUES ('1','Ali', 'Ben Ali','1979-02-18','50, 1st street','Algiers','16000','0143567890',NULL,'A1@yahoo.fr');
INSERT INTO Student VALUES ('2','Amar', 'Ben Ammar','1980-08-23','10, Avenue b','BATNA','05000','0678567801',NULL,'pt@yahoo.fr');
INSERT INTO Student VALUES ('3','Ameur', 'Ben Ameur','1978-05-12','25, 2nd street','Oran','31000','0145678956','0145678956','o@yahoo.fr');
INSERT INTO Student VALUES ('4','Aissa', 'Ben Aissa','1979-07-15','56, Road','Annaba','23000','0678905645',NULL,'d@hotmail.com');
INSERT INTO Student VALUES ('5','Fatima', 'Ben Abdedallah','1979-08-15','45, Faubourg','Constantine','25000',NULL,NULL,NULL);
--INSURTING INTO INSTRUCTORS
INSERT INTO Instructor VALUES ('1','1','Abbas','BenAbbes','MCA','4185','4091','Ab@yahoo.fr');
INSERT INTO Instructor VALUES ('2','1','Mokhtar','BenMokhtar','Substitute', NULL, NULL, NULL);
INSERT INTO Instructor VALUES ('3','1','Djemaa','Ben Mohamed','MCB', NULL, NULL, NULL);
INSERT INTO Instructor VALUES ('4','1','Lahlou','Mohamed','PROF', NULL, NULL, NULL);
INSERT INTO Instructor VALUES ('5','1','Abla','Chad','MCA',NULL,NULL,'ab@lgmail.com');
INSERT INTO Instructor VALUES ('6','4','Mariam','BALI','Substitute',NULL,NULL,NULL);
--INSURTING INTO ROOMS
INSERT INTO Room VALUES ('B', '020', 15);
INSERT INTO Room VALUES ('B', '022', 15);
INSERT INTO Room VALUES ('A', '301', 45);
INSERT INTO Room VALUES ('C', 'Hall 1', 500);
INSERT INTO Room VALUES ('C', 'Hall 2', 200);
--INSURTING INTO ROOMS
INSERT INTO Course VALUES ('1','1','Databases','Licence(L3) : Modeling E/A and UML, Relational Model, Relational Algebra, Relational calculs, SQL, NFs and FDs');
INSERT INTO Course VALUES ('2','1','C++ progr.','Level Master 1');
INSERT INTO Course VALUES ('3','1','Advanced DBs','Level Master 2 - Program Licence and Master 1');
INSERT INTO Course VALUES ('4','4','English','');
--INSURTING INTO Reservation
INSERT INTO Reservation VALUES ('1','B','022','1','1','1','2006-10-15','08:30:00','11:45:00','3');
INSERT INTO Reservation VALUES ('2','B','022','1','1','4','2006-11-04','08:30:00','11:45:00','3');
INSERT INTO Reservation VALUES ('3','B','022','1','1','4','2006-11-07','08:30:00','11:45:00','3');
INSERT INTO Reservation VALUES ('4','B','020','1','1','5','2006-10-20','13:45:00','17:00:00','3');
INSERT INTO Reservation VALUES ('5','B','020','1','1','4','2006-12-09','13:45:00','17:00:00','3');
INSERT INTO Reservation VALUES ('6','A','301','2','1','1','2006-09-02','08:30:00','11:45:00','3');
INSERT INTO Reservation VALUES ('7','A','301','2','1','1','2006-09-03','08:30:00','11:45:00','3');
INSERT INTO Reservation VALUES ('8','A','301','2','1','1','2006-09-10','08:30:00','11:45:00','3');
INSERT INTO Reservation VALUES ('9','A','301','3','1','1','2006-09-24','13:45:00','17:00:00','3');
INSERT INTO Reservation VALUES ('10','B','022','3','1','1','2006-10-15','13:45:00','17:00:00','3');
INSERT INTO Reservation VALUES ('11','A','301','3','1','1','2006-10-01','13:45:00','17:00:00','3');
INSERT INTO Reservation VALUES ('12','A','301','3','1','1','2006-10-08','13:45:00','17:00:00','3');
INSERT INTO Reservation VALUES ('13','B','022','1','1','4','2006-11-03','13:45:00','17:00:00','3');
INSERT INTO Reservation VALUES ('14','B','022','1','1','5','2006-10-20','13:45:00','17:00:00','3');
INSERT INTO Reservation VALUES ('15','B','022','1','1','4','2006-12-09','13:45:00','17:00:00','3');
INSERT INTO Reservation VALUES ('16','B','022','1','1','4','2006-09-03','08:30:00','11:45:00','3');
INSERT INTO Reservation VALUES ('17','B','022','1','1','5','2006-09-10','08:30:00','11:45:00','3');
INSERT INTO Reservation VALUES ('18','B','022','1','1','4','2006-09-24','13:45:00','17:00:00','3');
INSERT INTO Reservation VALUES ('19','B','022','1','1','5','2006-10-01','13:45:00','17:00:00','3');
INSERT INTO Reservation VALUES ('20','B','022','1','1','1','2006-10-08','13:45:00','17:00:00','3');
INSERT INTO Reservation VALUES ('21','B','022','1','1','4','2003-09-02','08:30:00','11:45:00','3');
-- SHOW THE ROWS AND THE TUPLES OF THE TABLES
SELECT * FROM Department;
SELECT * FROM Student;
SELECT * FROM Instructor;
SELECT * FROM Course;
SELECT * FROM Room;
SELECT * FROM Reservation;
--------------------------------
-- SECTION 2.4: DATABASE EVOLUTION
----creating a new enrolment relation
CREATE TABLE Enrollment (
    Student_ID int,
    Course_ID int,
    Dept_ID int,
    Enroll_Date date DEFAULT CURRENT_DATE,
    PRIMARY KEY (Student_ID, Course_ID, Dept_ID),
    FOREIGN KEY (Student_ID) REFERENCES Student(Student_ID),
    FOREIGN KEY (Course_ID, Dept_ID) REFERENCES Course(Course_ID, Department_ID)
);
- creating the mark relation
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
----------------
- THE VIEWS

CREATE VIEW View_Res AS
SELECT instructor_id, COUNT(*) AS total
FROM Reservation
GROUP BY instructor_id;
