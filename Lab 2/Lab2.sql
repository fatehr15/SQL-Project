--1
SELECT 
    Last_Name,
    First_Name
FROM Student;
--2
SELECT
Last_Name,
First_Name
FROM Student
WHERE  City = 'Algiers';
---3
SELECT Last_Name, First_Name
FROM Student
WHERE Last_Name LIKE 'A%';
--4
SELECT Last_Name, First_Name
FROM Instructor
WHERE Last_Name LIKE '%E_';
 --5
 SELECT Last_Name, First_Name
FROM Instructor
ORDER BY Department_ID, Last_Name, First_Name;
--6
SELECT COUNT(*) AS Substitute_Count
FROM Instructor
WHERE Rank = 'Substitute';
--7
SELECT Last_Name, First_Name
FROM Student
WHERE Fax IS NULL;
--8
SELECT Name
FROM Course
WHERE Description LIKE '%Licence%';
--9
SELECT 
    C.Name,
    SUM(R.Hours_Number * 3000) AS Cost_DA
FROM Course C
JOIN Reservation R
  ON C.Course_ID = R.Course_ID
 AND C.Department_ID = R.Department_ID
GROUP BY C.Name;
--10
SELECT Name
FROM (
    SELECT 
        C.Name,
        SUM(R.Hours_Number * 3000) AS Cost_DA
    FROM Course C
    JOIN Reservation R
      ON C.Course_ID = R.Course_ID
     AND C.Department_ID = R.Department_ID
    GROUP BY C.Name
) AS Course_Cost
WHERE Cost_DA BETWEEN 3000 AND 5000;

--11
SELECT 
    AVG(Capacity) AS Average_Capacity,
    MAX(Capacity) AS Max_Capacity
FROM Room;
--12
SELECT Building, RoomNo, Capacity
FROM Room
WHERE Capacity < (
    SELECT AVG(Capacity)
    FROM Room
);
--13
SELECT Last_Name, First_Name
FROM Instructor
WHERE Department_ID IN (
    SELECT Department_ID
    FROM Department
    WHERE Name IN ('SADS', 'CCS')
);
--14
SELECT Last_Name, First_Name
FROM Instructor
WHERE Department_ID NOT IN (
    SELECT Department_ID
    FROM Department
    WHERE Name IN ('SADS', 'CCS')
);
--15
SELECT Last_Name, First_Name, City
FROM Student
ORDER BY City;
--16
SELECT Department_ID, COUNT(*) AS Course_Count
FROM Course
GROUP BY Department;
--17
SELECT Department.Name
FROM Department, Course
WHERE Department.Department_ID = Course.Department_ID
GROUP BY Department.Name
HAVING COUNT(*) >= 3;
--18
SELECT Last_Name, First_Name
FROM Instructor 
WHERE EXISTS (
    SELECT 1
    FROM Reservation 
    WHERE Reservation.Instructor_ID = Instructor.Instructor_ID
    GROUP BY Reservation.Instructor_ID
    HAVING COUNT(*) >= 2
);
--19
SELECT I.Last_Name, I.First_Name
FROM Instructor I
JOIN Reservation R ON I.Instructor_ID = R.Instructor_ID
GROUP BY I.Instructor_ID, I.Last_Name, I.First_Name
HAVING COUNT(*) >= ALL (
    SELECT COUNT(*)
    FROM Reservation
    GROUP BY Instructor_ID
);
---20
SELECT Last_Name, First_Name
FROM Instructor
WHERE Instructor_ID NOT IN (
    SELECT DISTINCT Instructor_ID
    FROM Reservation
);
--- 21
SELECT Building, RoomNo
FROM Reservation
GROUP BY Building, RoomNo
HAVING COUNT(DISTINCT Reserv_Date) = (
    SELECT COUNT(DISTINCT Reserv_Date)
    FROM Reservation
);
