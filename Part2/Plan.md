## Plan for Project Part 2 : 
### Database Design and Schema Extension

The first part focuses on **ERD revision, normalization, and extending the database schema** using PostgreSQL.

| Step | Objective | Source Reference |
| :--- | :--- | :--- |
| **Phase A: ERD Revision and Normalization (Section 6.2.1)** | | |
| 1. ERD Revision | **Drop the `Department` entity**. Revise the university ERD (the ultimate ERD from section 2.4, which includes `Enrollment` and `Marks` tables,). | |
| 2. Attribute Modification | **Add new attributes** (`Department name`, `Department building`, `Department budget`) to the `Instructor` entity. | |
| 3. New ERD and Schema | Provide the new ERD and map the proposed ERD to a relational schema. | |
| 4. Normalization | Analyse the obtained relational schema to determine if it is in **2NF, 3NF, or BCNF**. If not, provide a BCNF decomposition and discuss whether the decomposition is lossless. | |
| **Phase B: Schema Extension (Section 6.2.2)** | | |
| 5. Course Activities Extension | **Extend the ERD to include courses' activities**, ensuring each course has a mandatory Lecture activity, and may have optional Tutorial activity and/or Practical activity. | |
| 6. Student/Exam Extension | Extend the ERD to include **students' marks management** and **exams running** (covering room reservation, dates, and time slots). | |
| 7. Final Schema Mapping | Map the extended ERD to a relational schema. | |
| 8. Implementation | Use **PostgreSQL (mandatory)** to update the university database schema in the used labs. (This involves applying necessary `CREATE TABLE` and alteration statements, building upon existing schema elements like `Student`, `Course`, `Enrollment`, `Marks`, etc.-). |,- |

---
The second part involves developing a Python application with a graphical interface that implements the required features.

### Map for Project :

#### Needed Skills to be Documented

To successfully build the Python application described in the sources, the following skills will be necessary:

1.  **Python Programming:** Proficiency in core Python syntax and object-oriented programming to structure the application.
2.  **Graphical User Interface (GUI) Development:** Ability to use a Python library (e.g., Tkinter, PyQt, etc.—though the specific library is not dictated by the sources) to create a **graphic interface** and input screen menus.
3.  **Database Interfacing (SQL/PostgreSQL):** Skill in connecting Python to the PostgreSQL database and executing SQL queries and database commands.
4.  **Data Manipulation (CRUD):** Understanding how to implement **CRUD operations** (Create, Read, Update, Delete) for all tables within the application.
5.  **Advanced SQL Query Writing:** Expertise in writing complex SQL queries, including those involving joins, grouping, and subqueries, specifically the ten required queries (a) through (j), which must include at least five functions. (The sources already provide examples of complex functions and queries-).
6.  **Database Auditing/Trigger Management:** Knowledge of how to manage and display information related to **statement triggers** and the **audit table**, which logs data manipulation operations on student marks and attendance.

#### Process to Build the App (Step-by-Step)

The process to build the application follows the required feature list:

| Step | Feature Development | Details |
| :--- | :--- | :--- |
| 1. Setup & Core Interface | **Initial Application Structure** | Create the basic GUI structure and establish a connection to the PostgreSQL database. |
| 2. Core CRUD Functionality | **CRUD Operations Module** | Develop a sub-menu and associated input screens to handle **CRUD operations** for all major tables (`Student`, `Instructor`, `Course`, `Department`, etc.). |
| 3. Module Assignment | **Assignment Management Sub-menu** | Implement the functionality to manage the assignment of modules to teaching staff and to manage reservations. |
| 4. Student Progress Management | **Student Attendance & Marks Sub-menu** | Implement the sub-menu to manage student marks and their attendance to the different activities of the modules. |
| 5. Grading and Results | **Grading Sub-menu** | Implement the sub-menu to manage student grading (results processing), considering the **failing mark for each module**. |
| 6. Complex Query Display | **SQL Query Display Sub-menu** | Implement the sub-menu to display the results of required SQL queries (a) to (j), ensuring **at least five functions** are included. Queries cover student lists, time tables, student performance (e.g., students who passed the semester, students eligible for a resit), and module statistics. |
| 7. Auditing Implementation | **Audit Sub-menu** | Implement an "Audit" sub-menu to allow users to audit data manipulation operations (`INSERT`, `UPDATE`, and `DELETE`) on student marks and student attendance. This requires displaying information from the audit table, including `OperationType` (e.g., 'INSERT'), `OperationTime` (current timestamp), and enumeration attributes. (The sources show that a `Student_Audit_Log` table and trigger functions are required for this,). |

***
