#!/usr/bin/env python3
"""
MySQL Operations - Handles MySQL database operations
"""

import mysql.connector
import time
import os


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
    
    def _execute_sql_file(self, filename):
        """Execute SQL statements from a file."""
        cursor = self.connection.cursor()
        
        sql_file = os.path.join(os.path.dirname(__file__), '..', 'sql', filename)
        with open(sql_file, 'r') as f:
            sql_content = f.read()
        
        for statement in sql_content.split(';'):
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                cursor.execute(statement)
        
        self.connection.commit()
        cursor.close()
    
    def create_tables(self):
        """Create tables from SQL schema file."""
        cursor = self.connection.cursor()
        
        # Check if tables already exist
        cursor.execute("SHOW TABLES LIKE 'Users'")
        if cursor.fetchone():
            cursor.close()
            return  # Tables already exist
        cursor.close()
        
        self._execute_sql_file('01_schema.sql')
    
    def insert_sample_data(self):
        """Insert sample data from SQL file."""
        cursor = self.connection.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM Users")
        if cursor.fetchone()[0] > 0:
            cursor.close()
            return  # Data already exists
        cursor.close()
        
        self._execute_sql_file('02_sample_data.sql')
    
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
