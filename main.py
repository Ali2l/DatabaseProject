#!/usr/bin/env python3
"""
Hotel Booking System - Database Migration Project
Main Orchestrator Module

This project demonstrates migration from MySQL (Relational DB) to Redis (Key-Value Store).
It showcases:
1. MySQL Operations: Connection, table creation, data insertion
2. Data Migration: Transforming SQL tables to Redis data structures
3. Redis Queries: Retrieving data without SQL JOINs
4. Sharding Concepts: Hash slot calculation for distributed data

Author: Ali Alkhowaiter
Course: Database Systems
"""

import sys
from modules.mysql_operations import MySQLOperations
from modules.redis_migration import RedisMigration
from modules.redis_queries import RedisQueries


class DatabaseMigrationProject:
    """
    Main orchestrator class that coordinates:
    - MySQL database operations
    - Data migration to Redis
    - Query execution on Redis
    
    This demonstrates the complete workflow of migrating from
    a relational database to a NoSQL Key-Value store.
    """
    
    def __init__(self):
        """Initialize the project components."""
        self.mysql_ops = None
        self.redis_migration = None
        self.redis_queries = None
    
    def setup_mysql(self):
        """
        Step 1: Setup MySQL database.
        - Connect to MySQL
        - Create tables
        - Insert sample data
        """
        print("\n" + "="*70)
        print("STEP 1: MySQL Setup (Relational Database)")
        print("="*70)
        
        # Initialize MySQL operations
        self.mysql_ops = MySQLOperations(
            host='localhost',
            port=3306,
            user='root',
            password='root',
            database='hotel_db'
        )
        
        # Connect to MySQL
        self.mysql_ops.connect(max_retries=10, retry_delay=3)
        
        # Create tables
        print("\n--- Creating Tables ---")
        self.mysql_ops.create_tables()
        
        # Note: Sample data is inserted automatically from sql/02_sample_data.sql
        # when MySQL container starts
        
        # Display MySQL records
        print("\n--- MySQL Records ---")
        self.mysql_ops.fetch_all_records('Users')
        self.mysql_ops.fetch_all_records('Hotels')
        self.mysql_ops.fetch_all_records('Bookings')
    
    
    def migrate_to_redis(self, mysql_data):
        """
        Step 2: Migrate data from MySQL to Redis.
        - Connect to Redis
        - Transform SQL data to Redis data structures
        - Display hash slots (demonstrates sharding)
        - Verify migration
        """
        print("\n" + "="*70)
        print("STEP 2: Data Migration (MySQL -> Redis)")
        print("="*70)
        
        self.redis_migration = RedisMigration(host='localhost', port=16379)
        
        self.redis_migration.connect(max_retries=10, retry_delay=3)
        
        self.redis_migration.display_cluster_info()
        
        print("\n--- Fetching MySQL Data ---")
        
        migration_stats = self.redis_migration.migrate_data(mysql_data)
        
        if migration_stats:
            self.redis_migration.verify_migration()
        
        return migration_stats
    
    def execute_redis_queries(self, mysql_data):
        """
        Step 3: Execute queries on Redis (NO MySQL).
        Demonstrates how to retrieve and join data using Redis data structures.
        Uses actual data from migration for dynamic queries.
        """
        print("\n" + "="*70)
        print("STEP 3: Redis Queries (NO MySQL - Pure Key-Value Queries)")
        print("="*70)
        
        self.redis_queries = RedisQueries(self.redis_migration.connection)
        
        if mysql_data.get('users') and len(mysql_data['users']) > 0:
            first_user_id = mysql_data['users'][0]['id']
            self.redis_queries.search_user_by_id(first_user_id)
            
            self.redis_queries.get_user_booking_history(first_user_id)
            
            if len(mysql_data['users']) > 1:
                second_user_id = mysql_data['users'][1]['id']
                self.redis_queries.get_user_booking_history(second_user_id)
        
        if mysql_data.get('hotels') and len(mysql_data['hotels']) > 0:
            first_city = mysql_data['hotels'][0]['city']
            print("\n")
            self.redis_queries.get_hotels_by_city(first_city)
        
        if mysql_data.get('users') and len(mysql_data['users']) > 0:
            first_email = mysql_data['users'][0]['email']
            print("\n")
            self.redis_queries.get_user_by_email(first_email)
    
    def print_summary(self, migration_stats=None):
        """
        Print project completion summary.
        """
        print("\n" + "="*70)
        print("PROJECT SUMMARY - ALL OPERATIONS COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("MySQL Database:")
        print("   - Created tables (Users, Hotels, Bookings)")
        if migration_stats:
            print(f"   - Migrated data: {migration_stats['users']} users, {migration_stats['hotels']} hotels, {migration_stats['bookings']} bookings")
        else:
            print("   - Inserted sample data")
        print("")
        print("Redis Migration:")
        print("   - Connected to Redis (Key-Value Store)")
        print("   - Migrated all MySQL data to Redis")
        print("   - Transformed SQL tables -> Redis Hashes")
        print("   - Mapped relationships -> Redis Lists/Sets")
        print("   - Displayed hash slots (demonstrates sharding)")
        print("")
        print("Redis Queries:")
        print("   - Executed complex queries WITHOUT MySQL")
        print("   - Traversed relationships using Lists")
        print("   - Retrieved data from distributed hash slots")
        print("")
        print("Key Concepts Demonstrated:")
        print("   - Relational -> NoSQL migration")
        print("   - SQL JOINs -> Redis Lists/Sets")
        print("   - Data sharding (hash slot distribution)")
        print("   - Key-Value store operations")
        print("="*70)
    
    def cleanup(self):
        """
        Close all database connections.
        """
        if self.mysql_ops:
            self.mysql_ops.close()
        if self.redis_migration:
            self.redis_migration.close()
    
    def run(self):
        """
        Main execution flow.
        Orchestrates the entire migration project.
        """
        try:
            self.setup_mysql()
            
            mysql_data = self.mysql_ops.get_all_data()
            
            migration_stats = self.migrate_to_redis(mysql_data)
            
            if migration_stats and mysql_data:
                self.execute_redis_queries(mysql_data)
            
            self.print_summary(migration_stats)
        
        except Exception as e:
            print(f"\nFatal error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        
        finally:
            self.cleanup()


def main():
    """
    Entry point of the application.
    """
    print("="*70)
    print("HOTEL BOOKING SYSTEM - DATABASE MIGRATION PROJECT")
    print("MySQL (Relational) -> Redis (Key-Value Store)")
    print("="*70)
    
    # Create and run the project
    project = DatabaseMigrationProject()
    project.run()


if __name__ == "__main__":
    main()
