import mysql.connector

class DB:
    def __init__(self, host, user, password, database):
        #temporary connection to create DB
        temp_conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        temp_cursor = temp_conn.cursor()
        
        temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
        
        temp_cursor.close()
        temp_conn.close()

        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.connection.cursor(dictionary=True)

    def createTables(self) -> None:
        #Creating tables if they don't exist yet
        create_rooms = """
        CREATE TABLE IF NOT EXISTS Rooms (
            id INT PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        );
        """
        create_students = """
        CREATE TABLE IF NOT EXISTS Students (
            id INT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            birthday DATE NOT NULL,
            sex CHAR(1) NOT NULL,
            room INT,
            FOREIGN KEY (room) REFERENCES Rooms(id),
            INDEX idx_students_room (room),
            INDEX idx_students_birthday (birthday)
        );
        """
        self.cursor.execute(create_rooms)
        self.cursor.execute(create_students)
        self.connection.commit()

    def insertRooms(self, rooms: list) -> None:
        #inserting into Rooms table, checking for duplicate keys to avoid errors at running program again
        query = """
        INSERT INTO Rooms (id, name) 
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE name = VALUES(name);
        """
        for room in rooms:
            self.cursor.execute(query, (room['id'], room['name']))
        self.connection.commit()

    def insertStudents(self, student_list: list) -> None:
        #inserting into Students table
        query = """
        INSERT INTO Students (id, name, birthday, sex, room) 
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            name = VALUES(name),
            sex = VALUES(sex),
            birthday = VALUES(birthday),
            room = VALUES(room);
        """
        for student in student_list:
            data = (student['id'], student['name'], student['birthday'], student['sex'], student['room'])
            self.cursor.execute(query, data)
        self.connection.commit()

    def roomsStudentCount(self) -> list:
        #query returning student count in every room
        query = """
        SELECT Rooms.id, Rooms.name, COUNT(Students.id) AS student_count
        FROM Rooms
        LEFT JOIN Students ON Rooms.id = Students.room
        GROUP BY Rooms.id, Rooms.name;
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def smallestAvgAge(self) -> list:
        #query returning 5 rooms with smallest average age
        query = """
        SELECT r.name
        FROM Rooms r 
        JOIN Students s ON r.id = s.room 
        GROUP BY r.id, r.name 
        ORDER BY AVG(TIMESTAMPDIFF(YEAR, s.birthday, NOW())) ASC 
        LIMIT 5;
        """

        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def maxAgeDiff(self) -> list:
        #query returning 5 rooms where age gap is the biggest
        query = """
        SELECT r.name
        FROM Rooms r 
        JOIN Students s ON r.id = s.room 
        GROUP BY r.id, r.name 
        ORDER BY TIMESTAMPDIFF(YEAR, MIN(s.birthday), MAX(s.birthday)) DESC 
        LIMIT 5;
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def differentSex(self) -> list:
        #query returning rooms that have students with different sex 
        query = """SELECT r.id 
        FROM Rooms r 
        JOIN Students s ON r.id = s.room 
        GROUP BY r.id 
        HAVING COUNT(DISTINCT s.sex) = 2;
        """

        self.cursor.execute(query)
        return self.cursor.fetchall()