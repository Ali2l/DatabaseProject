#!/usr/bin/env python3
"""
Redis Migration Module
Handles data migration from MySQL to Redis with sharding demonstration.
"""

import redis
import time


class RedisMigration:
    """
    Class to handle Redis connectivity and data migration.
    Demonstrates:
    - Connection to Redis (Key-Value store)
    - Data transformation from SQL to Redis data structures
    - Hash slot calculation (demonstrates sharding concept)
    - Relationship mapping without JOINs
    """
    
    def __init__(self, host='localhost', port=16379):
        """
        Initialize Redis connection parameters.
        
        Args:
            host: Redis host address
            port: Redis port number
        """
        self.host = host
        self.port = port
        self.connection = None
    
    def connect(self, max_retries=10, retry_delay=3):
        """
        Connect to Redis with retry mechanism.
        
        Args:
            max_retries: Maximum number of connection attempts
            retry_delay: Delay in seconds between retries
        
        Returns:
            bool: True if connection successful, False otherwise
        
        Raises:
            Exception: If connection fails after max_retries attempts
        """
        print(f"Attempting to connect to Redis at {self.host}:{self.port}...")
        
        for attempt in range(1, max_retries + 1):
            try:
                # Create Redis connection
                self.connection = redis.Redis(
                    host=self.host,
                    port=self.port,
                    decode_responses=True
                )
                
                # Test the connection
                self.connection.ping()
                print(f"Successfully connected to Redis")
                
                # Display server info
                info = self.connection.info('server')
                print(f"Redis version: {info['redis_version']}")
                
                return True
            
            except Exception as e:
                print(f"Attempt {attempt}/{max_retries} failed: {e}")
                if attempt < max_retries:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    raise Exception(f"Failed to connect to Redis after {max_retries} attempts")
        
        return False
    
    def get_hash_slot(self, key):
        """
        Calculate the Redis hash slot for a given key.
        Redis Cluster uses CRC16 to distribute keys across 16384 slots.
        """
        import crc16
        checksum = crc16.crc16xmodem(key.encode('utf-8'))
        slot = checksum % 16384
        return slot
    
    def get_cluster_node(self, slot):
        """
        Determine which cluster node would handle this slot in a 3-node cluster.
        """
        if slot <= 5460:
            return 1
        elif slot <= 10922:
            return 2
        else:
            return 3
    
    def display_cluster_info(self):
        """
        Display Redis Cluster configuration and slot distribution.
        """
        print("\n" + "="*70)
        print("REDIS CLUSTER CONFIGURATION (3-Node Setup)")
        print("="*70)
        print("\nSlot Distribution:")
        print("  Node 1 (Master): Slots 0     - 5460  (5,461 slots)")
        print("  Node 2 (Master): Slots 5461  - 10922 (5,462 slots)")
        print("  Node 3 (Master): Slots 10923 - 16383 (5,461 slots)")
        print("\nTotal Slots: 16,384")
        print("\nEach key is hashed using CRC16 to determine its slot,")
        print("and the slot determines which node stores the data.")
        print("="*70)
    
    def migrate_data(self, mysql_data):
        """
        Migrate data from MySQL to Redis.
        Transforms SQL rows into Redis Hashes and maintains relationships.
        
        Mapping Strategy:
        - SQL Tables → Redis Hashes (user:1, hotel:1, booking:1)
        - Foreign Keys → Redis Lists (user:1:bookings = [1, 2, 3])
        - Indexes → Redis Sets (users:all, hotels:city:NewYork)
        
        Args:
            mysql_data: Dictionary containing MySQL data
        
        Returns:
            dict: Statistics about the migration (counts of migrated records)
        """
        if not self.connection:
            print("Error: No active Redis connection")
            return None
        
        stats = {
            'users': 0,
            'hotels': 0,
            'bookings': 0
        }
        
        try:
            print("\n" + "="*70)
            print("MIGRATION: MySQL → Redis (Key-Value Store)")
            print("="*70)
            
            # Migrate Users
            print("\n--- Migrating Users ---")
            for user in mysql_data['users']:
                user_id = user['id']
                key = f"user:{user_id}"
                
                # Convert datetime to string for Redis
                user_data = {
                    'id': str(user['id']),
                    'name': user['name'],
                    'email': user['email'],
                    'created_at': str(user['created_at'])
                }
                
                # Store user as Redis Hash
                self.connection.hset(key, mapping=user_data)
                
                hash_slot = self.get_hash_slot(key)
                node = self.get_cluster_node(hash_slot)
                print(f"Migrated {key} -> Slot: {hash_slot} (Node {node}) | {user_data}")
                
                # Add to index
                self.connection.sadd('users:all', user_id)
                
                # Create email lookup index
                email_key = f"user:email:{user['email']}"
                self.connection.set(email_key, user_id)
                
                stats['users'] += 1
            
            # Migrate Hotels
            print("\n--- Migrating Hotels ---")
            for hotel in mysql_data['hotels']:
                hotel_id = hotel['id']
                key = f"hotel:{hotel_id}"
                
                # Convert datetime to string for Redis
                hotel_data = {
                    'id': str(hotel['id']),
                    'name': hotel['name'],
                    'city': hotel['city'],
                    'created_at': str(hotel['created_at'])
                }
                
                # Store hotel as Redis Hash
                self.connection.hset(key, mapping=hotel_data)
                
                hash_slot = self.get_hash_slot(key)
                node = self.get_cluster_node(hash_slot)
                print(f"Migrated {key} -> Slot: {hash_slot} (Node {node}) | {hotel_data}")
                
                # Add to indexes
                self.connection.sadd('hotels:all', hotel_id)
                city_key = f"hotels:city:{hotel['city']}"
                self.connection.sadd(city_key, hotel_id)
                
                stats['hotels'] += 1
            
            # Migrate Bookings
            print("\n--- Migrating Bookings ---")
            for booking in mysql_data['bookings']:
                booking_id = booking['id']
                user_id = booking['user_id']
                hotel_id = booking['hotel_id']
                key = f"booking:{booking_id}"
                
                booking_data = {
                    'id': str(booking['id']),
                    'user_id': str(booking['user_id']),
                    'hotel_id': str(booking['hotel_id']),
                    'date': str(booking['date']),
                    'created_at': str(booking['created_at'])
                }
                
                self.connection.hset(key, mapping=booking_data)
                
                hash_slot = self.get_hash_slot(key)
                node = self.get_cluster_node(hash_slot)
                print(f"Migrated {key} -> Slot: {hash_slot} (Node {node}) | {booking_data}")
                
                user_bookings_key = f"user:{user_id}:bookings"
                self.connection.lpush(user_bookings_key, booking_id)
                
                list_slot = self.get_hash_slot(user_bookings_key)
                list_node = self.get_cluster_node(list_slot)
                print(f"  -> Added to {user_bookings_key} (Slot: {list_slot}, Node {list_node})")
                
                date_key = f"bookings:date:{booking['date']}"
                self.connection.sadd(date_key, booking_id)
                self.connection.sadd('bookings:all', booking_id)
                
                stats['bookings'] += 1
            
            print("\n" + "="*70)
            print("MIGRATION COMPLETE")
            print("="*70)
            print(f"Users migrated: {stats['users']}")
            print(f"Hotels migrated: {stats['hotels']}")
            print(f"Bookings migrated: {stats['bookings']}")
            print("="*70)
            
            self.display_sharding_summary(mysql_data)
            
            return stats
        
        except Exception as e:
            print(f"Error during migration: {e}")
            return None
    
    def display_sharding_summary(self, mysql_data):
        """
        Display summary showing how data is distributed across cluster nodes.
        """
        print("\n" + "="*70)
        print("SHARDING DISTRIBUTION ACROSS NODES")
        print("="*70)
        
        node_data = {1: [], 2: [], 3: []}
        
        for user in mysql_data['users']:
            key = f"user:{user['id']}"
            slot = self.get_hash_slot(key)
            node = self.get_cluster_node(slot)
            node_data[node].append(f"{key} (slot {slot})")
        
        for hotel in mysql_data['hotels']:
            key = f"hotel:{hotel['id']}"
            slot = self.get_hash_slot(key)
            node = self.get_cluster_node(slot)
            node_data[node].append(f"{key} (slot {slot})")
        
        for booking in mysql_data['bookings']:
            key = f"booking:{booking['id']}"
            slot = self.get_hash_slot(key)
            node = self.get_cluster_node(slot)
            node_data[node].append(f"{key} (slot {slot})")
        
        for node_num in [1, 2, 3]:
            print(f"\nNode {node_num}:")
            if node_data[node_num]:
                for item in node_data[node_num]:
                    print(f"  - {item}")
            else:
                print("  - No keys")
        
        print("\n" + "="*70)
    
    def verify_migration(self):
        """
        Verify migrated data in Redis by querying some examples.
        """
        print("\n" + "="*70)
        print("VERIFICATION: Querying Redis Data")
        print("="*70)
        
        try:
            print("\n--- Sample Queries ---")
            
            # Get a user
            user1 = self.connection.hgetall('user:1')
            print(f"\nUser 1: {user1}")
            
            # Get user's bookings (using the relationship)
            user1_bookings = self.connection.lrange('user:1:bookings', 0, -1)
            print(f"User 1's booking IDs: {user1_bookings}")
            
            # Get booking details
            if user1_bookings:
                for booking_id in user1_bookings:
                    booking = self.connection.hgetall(f'booking:{booking_id}')
                    print(f"  Booking {booking_id}: {booking}")
            
            # Get all users
            all_users = self.connection.smembers('users:all')
            print(f"\nAll user IDs: {all_users}")
            
            # Get hotels in a city
            ny_hotels = self.connection.smembers('hotels:city:New York')
            print(f"\nHotels in New York: {ny_hotels}")
            
            print("\n" + "="*70)
            print("Verification complete!")
            print("="*70)
        
        except Exception as e:
            print(f"Error during verification: {e}")
    
    def close(self):
        """
        Close Redis connection.
        """
        if self.connection:
            print("Redis connection closed")
