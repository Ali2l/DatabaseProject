#!/usr/bin/env python3
"""
Hotel Booking System
MySQL (Relational) -> Redis Cluster (Key-Value)
"""

from modules.mysql_operations import MySQLOperations
from modules.redis_migration import RedisMigration
from modules.redis_queries import RedisQueries


def main():
    print("\n=== Hotel Booking System ===")
    print("Demonstrating: MySQL (Relational) -> Redis Cluster (Key-Value)\n")
    
    # Step 1: Connect to MySQL (Relational Database)
    print("STEP 1: Connect to MySQL (Relational Database)")
    print("  Tables: Users, Hotels, Bookings (with foreign keys)")
    mysql = MySQLOperations(
        host='localhost', port=3306,
        database='hotel_db', user='root', password='root'
    )
    mysql.connect()
    # Step 1.1: Create tables 
    mysql.create_tables()
    # Step 1.2: Get all data
    mysql_data = mysql.get_all_data()
    print(f"  Data: {len(mysql_data['users'])} users, {len(mysql_data['hotels'])} hotels, {len(mysql_data['bookings'])} bookings")
    
    # Step 2: Connect to Redis Cluster
    print("\nSTEP 2: Connect to Redis Cluster")
    print("  Cluster: 3 masters + 3 replicas on ports 7001-7006")
    redis_migration = RedisMigration()
    redis_migration.connect()
    print("  Connected!")
    
    # Step 3: Migrate data (Relational -> Key-Value)
    print("\nSTEP 3: Migrate Data (Relational -> Key-Value)")
    print("  Mapping: SQL Row -> Redis Hash")
    print("  Mapping: Foreign Key -> Redis List")
    # Step 3.1: Migrate all data
    stats = redis_migration.migrate_data(mysql_data)
    print(f"  Migrated: {stats['users']} users, {stats['hotels']} hotels, {stats['bookings']} bookings")
    
    # Step 4: Query Redis (No SQL needed!)
    print("\nSTEP 4: Query Redis (No SQL needed!)")
    print("  Data is sharded across 3 masters using hash slots")
    queries = RedisQueries(redis_migration.connection)
    queries.run_interactive()
    
    # Done
    mysql.close()
    redis_migration.close()
    print("\nDone. Run 'python3 stop_cluster.py' to stop the cluster.")


if __name__ == "__main__":
    main()
