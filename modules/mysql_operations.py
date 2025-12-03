#!/usr/bin/env python3
"""
MySQL Operations Module
Handles all MySQL database connectivity and operations.
"""

import mysql.connector
from mysql.connector import Error
import time


class MySQLOperations:
    """
    Class to handle MySQL database operations including:
    - Connection management with retry mechanism
    - Table creation
    - Dynamic data insertion
    - Data retrieval
    """
    
    def __init__(self, host='localhost', port=3306, user='root', 
                 password='root', database='hotel_db'):
        """
        Initialize MySQL connection parameters.
        
        Args:
            host: MySQL host address
            port: MySQL port number
            user: Database user
            password: Database password
            database: Database name
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
    
    def connect(self, max_retries=10, retry_delay=3):
        """
        Connect to MySQL database with retry mechanism.
        
        Args:
            max_retries: Maximum number of connection attempts
            retry_delay: Delay in seconds between retries
        
        Returns:
            bool: True if connection successful, False otherwise
        
        Raises:
            Exception: If connection fails after max_retries attempts
        """
        print(f"Attempting to connect to MySQL at {self.host}:{self.port}...")
        
        for attempt in range(1, max_retries + 1):
            try:
                self.connection = mysql.connector.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database
                )
                
                if self.connection.is_connected():
                    db_info = self.connection.get_server_info()
                    print(f"Successfully connected to MySQL Server version {db_info}")
                    cursor = self.connection.cursor()
                    cursor.execute("SELECT DATABASE();")
                    record = cursor.fetchone()
                    print(f"Connected to database: {record[0]}")
                    cursor.close()
                    return True
            
            except Error as e:
                print(f"Attempt {attempt}/{max_retries} failed: {e}")
                if attempt < max_retries:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    raise Exception(f"Failed to connect to MySQL after {max_retries} attempts")
        
        return False
    
    def create_tables(self):
        """
        Create Users, Hotels, and Bookings tables if they don't exist.
        
        Returns:
            bool: True if tables created successfully, False otherwise
        """
        if not self.connection or not self.connection.is_connected():
            print("Error: No active database connection")
            return False
        
        table_definitions = {
            'Users': """
                CREATE TABLE IF NOT EXISTS Users (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_email (email)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,
            
            'Hotels': """
                CREATE TABLE IF NOT EXISTS Hotels (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    name VARCHAR(200) NOT NULL,
                    city VARCHAR(100) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_city (city)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """,
            
            'Bookings': """
                CREATE TABLE IF NOT EXISTS Bookings (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id INT NOT NULL,
                    hotel_id INT NOT NULL,
                    date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
                    FOREIGN KEY (hotel_id) REFERENCES Hotels(id) ON DELETE CASCADE,
                    INDEX idx_user_id (user_id),
                    INDEX idx_hotel_id (hotel_id),
                    INDEX idx_date (date)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        }
        
        cursor = self.connection.cursor()
        
        try:
            for table_name, create_statement in table_definitions.items():
                print(f"Creating table: {table_name}...")
                cursor.execute(create_statement)
                print(f"Table '{table_name}' created successfully (or already exists)")
            
            self.connection.commit()
            print("All tables created successfully")
            return True
        
        except Error as e:
            print(f"Error creating tables: {e}")
            self.connection.rollback()
            return False
        
        finally:
            cursor.close()
    
    def insert_data(self, table_name, data_dict):
        """
        Generic function to insert data into any table dynamically.
        
        Args:
            table_name: Name of the table to insert into
            data_dict: Dictionary with column names as keys and values to insert
        
        Returns:
            int: ID of the inserted record, or None if insertion failed
        
        Example:
            insert_data('Users', {'name': 'Alice', 'email': 'alice@example.com'})
        """
        if not self.connection or not self.connection.is_connected():
            print("Error: No active database connection")
            return None
        
        if not data_dict:
            print("Error: No data provided for insertion")
            return None
        
        # Extract column names and values from dictionary
        columns = list(data_dict.keys())
        values = list(data_dict.values())
        
        # Create placeholders for parameterized query
        placeholders = ', '.join(['%s'] * len(values))
        columns_str = ', '.join(columns)
        
        # Construct dynamic INSERT query
        query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        
        cursor = self.connection.cursor()
        
        try:
            cursor.execute(query, values)
            self.connection.commit()
            inserted_id = cursor.lastrowid
            print(f"Successfully inserted into {table_name} (ID: {inserted_id}): {data_dict}")
            return inserted_id
        
        except Error as e:
            print(f"Error inserting data into {table_name}: {e}")
            self.connection.rollback()
            return None
        
        finally:
            cursor.close()
    
    def fetch_all_records(self, table_name):
        """
        Fetch all records from a specified table.
        
        Args:
            table_name: Name of the table to query
        
        Returns:
            list: List of tuples containing all records
        """
        if not self.connection or not self.connection.is_connected():
            print("Error: No active database connection")
            return []
        
        cursor = self.connection.cursor()
        
        try:
            query = f"SELECT * FROM {table_name}"
            cursor.execute(query)
            records = cursor.fetchall()
            
            # Get column names
            column_names = [desc[0] for desc in cursor.description]
            
            print(f"\n--- Records from {table_name} ---")
            print(f"Columns: {', '.join(column_names)}")
            for record in records:
                print(record)
            
            return records
        
        except Error as e:
            print(f"Error fetching data from {table_name}: {e}")
            return []
        
        finally:
            cursor.close()
    
    def get_all_data(self):
        """
        Fetch all data from all tables for migration.
        
        Returns:
            dict: Dictionary containing data from all tables
        """
        if not self.connection or not self.connection.is_connected():
            print("Error: No active database connection")
            return {}
        
        cursor = self.connection.cursor(dictionary=True)
        data = {
            'users': [],
            'hotels': [],
            'bookings': []
        }
        
        try:
            # Fetch Users
            cursor.execute("SELECT * FROM Users")
            data['users'] = cursor.fetchall()
            
            # Fetch Hotels
            cursor.execute("SELECT * FROM Hotels")
            data['hotels'] = cursor.fetchall()
            
            # Fetch Bookings
            cursor.execute("SELECT * FROM Bookings")
            data['bookings'] = cursor.fetchall()
            
            return data
        
        except Error as e:
            print(f"Error fetching data: {e}")
            return {}
        
        finally:
            cursor.close()
    
    def close(self):
        """
        Safely close database connection.
        """
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")
