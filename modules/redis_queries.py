#!/usr/bin/env python3
"""
Redis Queries - Interactive queries on Redis Cluster
"""

import crc16


class RedisQueries:
    """Interactive query interface for Redis Cluster."""
    
    def __init__(self, redis_connection):
        self.connection = redis_connection
    
    def get_hash_slot(self, key):
        """Calculate hash slot for a key."""
        return crc16.crc16xmodem(key.encode('utf-8')) % 16384
    
    def get_node_for_key(self, key):
        """Get the actual master and replica nodes for a key from the cluster."""
        slot = self.get_hash_slot(key)
        
        # Get all slot ranges from the cluster
        # Format: {(start, end): {'primary': (host, port), 'replicas': [(host, port), ...]}}
        cluster_slots = self.connection.cluster_slots()
        
        for (start_slot, end_slot), node_info in cluster_slots.items():
            if start_slot <= slot <= end_slot:
                master_port = node_info['primary'][1]
                
                replica_port = None
                if node_info['replicas']:
                    replica_port = node_info['replicas'][0][1]
                
                return master_port, replica_port
        
        return None, None
    
    def run_interactive(self):
        """Run interactive query menu."""
        while True:
            print("\nQuery Menu:")
            print("1. Get user by ID")
            print("2. Get user by email")
            print("3. Get user's bookings")
            print("4. Get hotel by ID")
            print("5. Get hotels by city")
            print("6. Get booking by ID")
            print("7. List all users")
            print("8. List all hotels")
            print("9. List all bookings")
            print("10. Show key info")
            print("0. Exit")
            
            choice = input("Choice: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self.query_user_by_id()
            elif choice == "2":
                self.query_user_by_email()
            elif choice == "3":
                self.query_user_bookings()
            elif choice == "4":
                self.query_hotel_by_id()
            elif choice == "5":
                self.query_hotels_by_city()
            elif choice == "6":
                self.query_booking_by_id()
            elif choice == "7":
                self.list_all_users()
            elif choice == "8":
                self.list_all_hotels()
            elif choice == "9":
                self.list_all_bookings()
            elif choice == "10":
                self.show_key_info()
    
    def query_user_by_id(self):
        """Get user by ID."""
        user_id = input("User ID: ").strip()
        if not user_id:
            return
        
        key = f"user:{user_id}"
        slot = self.get_hash_slot(key)
        master_port, replica_port = self.get_node_for_key(key)
        user = self.connection.hgetall(key)
        
        if user:
            print(f"Key: {key}, Slot: {slot}, Master: {master_port}, Replica: {replica_port}")
            print(f"Name: {user.get('name')}, Email: {user.get('email')}")
        else:
            print("User not found")
    
    def query_user_by_email(self):
        """Get user by email."""
        email = input("Email: ").strip()
        if not email:
            return
        
        user_id = self.connection.get(f"user:email:{email}")
        if not user_id:
            print("User not found")
            return
        
        user = self.connection.hgetall(f"user:{user_id}")
        print(f"ID: {user_id}, Name: {user.get('name')}, Email: {user.get('email')}")
    
    def query_user_bookings(self):
        """Get user's bookings."""
        user_id = input("User ID: ").strip()
        if not user_id:
            return
        
        user = self.connection.hgetall(f"user:{user_id}")
        if not user:
            print("User not found")
            return
        
        print(f"User: {user['name']}")
        
        booking_ids = self.connection.lrange(f"user:{user_id}:bookings", 0, -1)
        if not booking_ids:
            print("No bookings")
            return
        
        for bid in booking_ids:
            booking = self.connection.hgetall(f"booking:{bid}")
            hotel = self.connection.hgetall(f"hotel:{booking['hotel_id']}")
            key = f"booking:{bid}"
            slot = self.get_hash_slot(key)
            master_port, replica_port = self.get_node_for_key(key)
            print(f"Booking {bid}: {booking['date']} at {hotel['name']} (slot {slot}, master {master_port}, replica {replica_port})")
    
    def query_hotel_by_id(self):
        """Get hotel by ID."""
        hotel_id = input("Hotel ID: ").strip()
        if not hotel_id:
            return
        
        key = f"hotel:{hotel_id}"
        slot = self.get_hash_slot(key)
        master_port, replica_port = self.get_node_for_key(key)
        hotel = self.connection.hgetall(key)
        
        if hotel:
            print(f"Key: {key}, Slot: {slot}, Master: {master_port}, Replica: {replica_port}")
            print(f"Name: {hotel.get('name')}, City: {hotel.get('city')}")
        else:
            print("Hotel not found")
    
    def query_hotels_by_city(self):
        """Get hotels by city."""
        city = input("City: ").strip()
        if not city:
            return
        
        hotel_ids = self.connection.smembers(f"hotels:city:{city}")
        if not hotel_ids:
            print("No hotels found")
            return
        
        for hid in hotel_ids:
            hotel = self.connection.hgetall(f"hotel:{hid}")
            print(f"{hotel['name']}")
    
    def query_booking_by_id(self):
        """Get booking by ID."""
        booking_id = input("Booking ID: ").strip()
        if not booking_id:
            return
        
        key = f"booking:{booking_id}"
        slot = self.get_hash_slot(key)
        booking = self.connection.hgetall(key)
        
        if booking:
            user = self.connection.hgetall(f"user:{booking['user_id']}")
            hotel = self.connection.hgetall(f"hotel:{booking['hotel_id']}")
            master_port, replica_port = self.get_node_for_key(key)
            print(f"Key: {key}, Slot: {slot}, Master: {master_port}, Replica: {replica_port}")
            print(f"Date: {booking['date']}, User: {user['name']}, Hotel: {hotel['name']}")
        else:
            print("Booking not found")
    
    def list_all_users(self):
        """List all users."""
        user_ids = self.connection.smembers('users:all')
        for uid in sorted(user_ids):
            user = self.connection.hgetall(f"user:{uid}")
            key = f"user:{uid}"
            master_port, replica_port = self.get_node_for_key(key)
            print(f"[{uid}] {user['name']} - master {master_port}, replica {replica_port}")
    
    def list_all_hotels(self):
        """List all hotels."""
        hotel_ids = self.connection.smembers('hotels:all')
        for hid in sorted(hotel_ids):
            hotel = self.connection.hgetall(f"hotel:{hid}")
            key = f"hotel:{hid}"
            master_port, replica_port = self.get_node_for_key(key)
            print(f"[{hid}] {hotel['name']} in {hotel['city']} - master {master_port}, replica {replica_port}")
    
    def list_all_bookings(self):
        """List all bookings."""
        # Get all booking IDs by checking users' booking lists
        all_bookings = set()
        user_ids = self.connection.smembers('users:all')
        for uid in user_ids:
            booking_ids = self.connection.lrange(f"user:{uid}:bookings", 0, -1)
            all_bookings.update(booking_ids)
        
        for bid in sorted(all_bookings):
            booking = self.connection.hgetall(f"booking:{bid}")
            user = self.connection.hgetall(f"user:{booking['user_id']}")
            hotel = self.connection.hgetall(f"hotel:{booking['hotel_id']}")
            key = f"booking:{bid}"
            master_port, replica_port = self.get_node_for_key(key)
            print(f"[{bid}] {user['name']} booked {hotel['name']} on {booking['date']} - master {master_port}, replica {replica_port}")
    
    def show_key_info(self):
        """Show info for any key."""
        key = input("Key (e.g. user:1): ").strip()
        if not key:
            return
        
        slot = self.get_hash_slot(key)
        master_port, replica_port = self.get_node_for_key(key)
        
        if not self.connection.exists(key):
            print(f"Key '{key}' does NOT exist in Redis")
            print(f"(Would be at Slot: {slot}, Master: {master_port}, Replica: {replica_port})")
            return
        
        print(f"Key: {key}, Slot: {slot}, Master: {master_port}, Replica: {replica_port}")
        
        key_type = self.connection.type(key)
        print(f"Type: {key_type}")
        
        if key_type == 'hash':
            print(f"Data: {self.connection.hgetall(key)}")
        elif key_type == 'list':
            print(f"Data: {self.connection.lrange(key, 0, -1)}")
        elif key_type == 'set':
            print(f"Data: {self.connection.smembers(key)}")
        elif key_type == 'string':
            print(f"Data: {self.connection.get(key)}")
