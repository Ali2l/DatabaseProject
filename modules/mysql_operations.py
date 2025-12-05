#!/usr/bin/env python3
"""
MySQL Operations - Handles MySQL database operations
"""

import mysql.connector
import time


class MySQLOperations:
    """Handles MySQL database operations."""
    
    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
    
    def connect(self):
        """Connect to MySQL database."""
        for attempt in range(10):
            try:
                self.connection = mysql.connector.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database
                )
                if self.connection.is_connected():
                    return True
            except:
                time.sleep(3)
        raise Exception("Could not connect to MySQL")
    
    def create_tables(self):
        """Create Users, Hotels, and Bookings tables."""
        cursor = self.connection.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Hotels (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(200) NOT NULL,
                city VARCHAR(100) NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Bookings (
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT NOT NULL,
                hotel_id INT NOT NULL,
                date DATE NOT NULL,
                FOREIGN KEY (user_id) REFERENCES Users(id),
                FOREIGN KEY (hotel_id) REFERENCES Hotels(id)
            )
        """)
        
        self.connection.commit()
        cursor.close()
    
    def get_all_data(self):
        """Get all data from all tables for migration."""
        cursor = self.connection.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM Users")
        users = cursor.fetchall()
        
        cursor.execute("SELECT * FROM Hotels")
        hotels = cursor.fetchall()
        
        cursor.execute("SELECT * FROM Bookings")
        bookings = cursor.fetchall()
        
        cursor.close()
        
        return {'users': users, 'hotels': hotels, 'bookings': bookings}
    
    def close(self):
        """Close the database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
