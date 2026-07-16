import mysql.connector
import re
from mysql.connector import Error

class DB:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def connect(self) -> None:
        if not re.match(r'^[a-zA-Z0-9_]+$', self.database):
            raise ValueError("Dangerous database name detected!")

        try:
            temp_conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            temp_cursor = temp_conn.cursor()
            temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            temp_cursor.close()
            temp_conn.close()
        except Error as e:
            raise e

        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.connection.cursor(dictionary=True)
        except Error as e:
            raise e

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
            query = """
            INSERT INTO Rooms (id, name) 
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE name = VALUES(name);
            """
            rooms_data = [(room['id'], room['name']) for room in rooms]
            
            self.cursor.executemany(query, rooms_data)
            self.connection.commit()

    def insertStudents(self, student_list: list) -> None:
        #inserting into Students table
        query = """
        INSERT INTO Students (id, name, birthday, sex, room) 
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            name = VALUES(name), 
            birthday = VALUES(birthday), 
            sex = VALUES(sex), 
            room = VALUES(room);
        """

        data = [(student['id'], student['name'], student['birthday'], student['sex'], student['room']) for student in student_list]
        self.cursor.executemany(query, data)
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
        ORDER BY AVG(DATEDIFF(NOW(), s.birthday)) ASC 
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
        ORDER BY DATEDIFF(MAX(s.birthday), MIN(s.birthday)) DESC 
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