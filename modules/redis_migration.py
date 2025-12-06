#!/usr/bin/env python3
"""
Redis Migration - Migrates data from MySQL to Redis Cluster
"""

from redis.cluster import RedisCluster
from redis.cluster import ClusterNode
import crc16
import time


class RedisMigration:
    """Migrates data from MySQL to Redis Cluster."""
    
    def __init__(self):
        self.startup_nodes = [
            ClusterNode("127.0.0.1", 7001),
            ClusterNode("127.0.0.1", 7002),
            ClusterNode("127.0.0.1", 7003),
        ]
        self.connection = None
    
    def connect(self):
        """Connect to Redis Cluster."""
        for attempt in range(10):
            try:
                self.connection = RedisCluster(
                    startup_nodes=self.startup_nodes,
                    decode_responses=True
                )
                self.connection.ping()
                return True
            except:
                time.sleep(2)
        raise Exception("Could not connect to Redis Cluster")
    
    def get_hash_slot(self, key):
        """Calculate hash slot for a key (0-16383)."""
        checksum = crc16.crc16xmodem(key.encode('utf-8'))
        return checksum % 16384
    
    def get_node(self, slot):
        """Get which master node handles this slot."""
        if slot <= 5460:
            return 7001
        elif slot <= 10922:
            return 7002
        else:
            return 7003
    
    def migrate_data(self, mysql_data):
        """Migrate MySQL data to Redis."""
        stats = {'users': 0, 'hotels': 0, 'bookings': 0}
        
        # Migrate Users (SQL row -> Redis Hash)
        for user in mysql_data['users']:
            key = f"user:{user['id']}"
            # Insert user as Hash
            self.connection.hset(key, mapping={
                'id': str(user['id']),
                'name': user['name'],
                'email': user['email']
            })
            slot = self.get_hash_slot(key)
            port = self.get_node(slot)
            print(f"    {key} -> slot {slot} -> port {port}")
            
            # Insert into index Set
            self.connection.sadd('users:all', user['id'])
            self.connection.set(f"user:email:{user['email']}", user['id'])
            stats['users'] += 1
        
        # Migrate Hotels
        for hotel in mysql_data['hotels']:
            key = f"hotel:{hotel['id']}"
            self.connection.hset(key, mapping={
                'id': str(hotel['id']),
                'name': hotel['name'],
                'city': hotel['city']
            })
            slot = self.get_hash_slot(key)
            port = self.get_node(slot)
            print(f"    {key} -> slot {slot} -> port {port}")
            
            self.connection.sadd('hotels:all', hotel['id'])
            self.connection.sadd(f"hotels:city:{hotel['city']}", hotel['id'])
            stats['hotels'] += 1
        
        # Migrate Bookings (Foreign key -> Redis List)
        for booking in mysql_data['bookings']:
            key = f"booking:{booking['id']}"
            self.connection.hset(key, mapping={
                'id': str(booking['id']),
                'user_id': str(booking['user_id']),
                'hotel_id': str(booking['hotel_id']),
                'date': str(booking['date'])
            })
            slot = self.get_hash_slot(key)
            port = self.get_node(slot)
            print(f"    {key} -> slot {slot} -> port {port}")
            
            # Foreign key replacement: add booking ID to user's list
            self.connection.lpush(f"user:{booking['user_id']}:bookings", booking['id'])
            stats['bookings'] += 1
        
        return stats
    
    def close(self):
        """Close Redis connection."""
        pass
