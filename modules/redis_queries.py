#!/usr/bin/env python3
"""
Redis Queries Module
Handles querying data from Redis without using MySQL.
Demonstrates how to retrieve and join data using Redis data structures.
"""


class RedisQueries:
    """
    Class to handle Redis query operations.
    Demonstrates:
    - Querying data from Key-Value store without SQL
    - Relationship traversal without JOINs
    - Using Lists, Hashes, and Sets for data retrieval
    """
    
    def __init__(self, redis_connection):
        """
        Initialize with an existing Redis connection.
        
        Args:
            redis_connection: Active Redis connection object
        """
        self.connection = redis_connection
    
    def get_hash_slot(self, key):
        """
        Calculate the Redis hash slot for a given key.
        
        Args:
            key: Redis key string
        
        Returns:
            int: Hash slot number (0-16383)
        """
        import crc16
        checksum = crc16.crc16xmodem(key.encode('utf-8'))
        slot = checksum % 16384
        return slot
    
    def get_user_booking_history(self, user_id):
        """
        Query a user's complete booking history from Redis WITHOUT using MySQL.
        Demonstrates how to handle relationships in Redis without SQL JOINs.
        
        Args:
            user_id: The user ID to query
        
        Returns:
            list: List of booking details with hotel information
        
        Process:
            1. Fetch the list of booking IDs from user's list key (user:X:bookings)
            2. For each booking ID, fetch booking details from Hash (booking:X)
            3. For each booking, fetch hotel details from Hash (hotel:X)
            4. Combine and return all information
        """
        print("\n" + "="*70)
        print(f"REDIS QUERY: Get User {user_id} Booking History (NO MySQL)")
        print("="*70)
        
        if not self.connection:
            print("Error: No active Redis connection")
            return []
        
        try:
            # Step 1: Get user details
            user_key = f"user:{user_id}"
            user_data = self.connection.hgetall(user_key)
            
            if not user_data:
                print(f"User {user_id} not found in Redis")
                return []
            
            print(f"\nUser Information:")
            print(f"   ID: {user_data.get('id')}")
            print(f"   Name: {user_data.get('name')}")
            print(f"   Email: {user_data.get('email')}")
            
            # Step 2: Fetch the list of booking IDs from the user's list
            user_bookings_key = f"user:{user_id}:bookings"
            booking_ids = self.connection.lrange(user_bookings_key, 0, -1)
            
            hash_slot = self.get_hash_slot(user_bookings_key)
            print(f"\nFetching booking list from: {user_bookings_key} (Hash Slot: {hash_slot})")
            print(f"   Found {len(booking_ids)} booking(s): {booking_ids}")
            
            if not booking_ids:
                print(f"   User {user_id} has no bookings")
                return []
            
            print(f"\nBooking Details:")
            print("-" * 70)
            
            booking_history = []
            
            for idx, booking_id in enumerate(booking_ids, 1):
                # Fetch booking hash
                booking_key = f"booking:{booking_id}"
                booking_data = self.connection.hgetall(booking_key)
                
                if not booking_data:
                    print(f"   Warning: Booking {booking_id} not found")
                    continue
                
                booking_slot = self.get_hash_slot(booking_key)
                
                # Fetch hotel details for this booking
                hotel_id = booking_data.get('hotel_id')
                hotel_key = f"hotel:{hotel_id}"
                hotel_data = self.connection.hgetall(hotel_key)
                hotel_slot = self.get_hash_slot(hotel_key)
                
                # Combine information
                combined_info = {
                    'booking_id': booking_data.get('id'),
                    'date': booking_data.get('date'),
                    'hotel_id': hotel_data.get('id'),
                    'hotel_name': hotel_data.get('name'),
                    'hotel_city': hotel_data.get('city'),
                    'created_at': booking_data.get('created_at')
                }
                
                booking_history.append(combined_info)
                
                # Print formatted output
                print(f"\n   Booking #{idx}:")
                print(f"   ├─ Booking ID: {booking_data.get('id')} (Hash Slot: {booking_slot})")
                print(f"   ├─ Date: {booking_data.get('date')}")
                print(f"   ├─ Hotel: {hotel_data.get('name')} (ID: {hotel_id}, Hash Slot: {hotel_slot})")
                print(f"   ├─ City: {hotel_data.get('city')}")
                print(f"   └─ Booked on: {booking_data.get('created_at')}")
            
            print("-" * 70)
            print(f"Retrieved {len(booking_history)} booking(s) from Redis (NO MySQL USED)")
            print("="*70)
            
            return booking_history
        
        except Exception as e:
            print(f"Error querying user history: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_hotels_by_city(self, city):
        """
        Query all hotels in a specific city.
        
        Args:
            city: City name to search for
        
        Returns:
            list: List of hotel details
        """
        print(f"\n--- Query: Hotels in {city} ---")
        
        try:
            # Get hotel IDs from city index
            city_key = f"hotels:city:{city}"
            hotel_ids = self.connection.smembers(city_key)
            
            if not hotel_ids:
                print(f"No hotels found in {city}")
                return []
            
            hotels = []
            for hotel_id in hotel_ids:
                hotel_key = f"hotel:{hotel_id}"
                hotel_data = self.connection.hgetall(hotel_key)
                if hotel_data:
                    hotels.append(hotel_data)
                    print(f"  {hotel_data.get('name')} (ID: {hotel_id})")
            
            return hotels
        
        except Exception as e:
            print(f"Error querying hotels by city: {e}")
            return []
    
    def get_bookings_by_date(self, date):
        """
        Query all bookings for a specific date.
        
        Args:
            date: Date to search for (YYYY-MM-DD format)
        
        Returns:
            list: List of booking details
        """
        print(f"\n--- Query: Bookings on {date} ---")
        
        try:
            # Get booking IDs from date index
            date_key = f"bookings:date:{date}"
            booking_ids = self.connection.smembers(date_key)
            
            if not booking_ids:
                print(f"No bookings found on {date}")
                return []
            
            bookings = []
            for booking_id in booking_ids:
                booking_key = f"booking:{booking_id}"
                booking_data = self.connection.hgetall(booking_key)
                if booking_data:
                    bookings.append(booking_data)
                    print(f"  Booking {booking_id}: User {booking_data.get('user_id')} → Hotel {booking_data.get('hotel_id')}")
            
            return bookings
        
        except Exception as e:
            print(f"Error querying bookings by date: {e}")
            return []
    
    def get_user_by_email(self, email):
        """
        Find a user by email address.
        
        Args:
            email: User's email address
        
        Returns:
            dict: User data or None if not found
        """
        print(f"\n--- Query: User with email {email} ---")
        
        try:
            # Use email index to find user ID
            email_key = f"user:email:{email}"
            user_id = self.connection.get(email_key)
            
            if not user_id:
                print(f"No user found with email {email}")
                return None
            
            # Fetch user data
            user_key = f"user:{user_id}"
            user_data = self.connection.hgetall(user_key)
            
            if user_data:
                print(f"  Found: {user_data.get('name')} (ID: {user_id})")
            
            return user_data
        
        except Exception as e:
            print(f"Error querying user by email: {e}")
            return None
    
    def get_all_users(self):
        """
        Retrieve all users from Redis.
        
        Returns:
            list: List of all user data
        """
        print("\n--- Query: All Users ---")
        
        try:
            user_ids = self.connection.smembers('users:all')
            users = []
            
            for user_id in user_ids:
                user_key = f"user:{user_id}"
                user_data = self.connection.hgetall(user_key)
                if user_data:
                    users.append(user_data)
                    print(f"  {user_data.get('name')} ({user_data.get('email')})")
            
            return users
        
        except Exception as e:
            print(f"Error querying all users: {e}")
            return []
    
    def search_user_by_id(self, user_id):
        """
        Search for a specific user by ID and display data.
        Demonstrates both HASH commands (HGETALL) and simple GET.
        
        Args:
            user_id: The user ID to search for
        
        Returns:
            dict: User data or None if not found
        """
        print("\n" + "="*70)
        print(f"SEARCH: User ID {user_id}")
        print("="*70)
        
        try:
            user_key = f"user:{user_id}"
            hash_slot = self.get_hash_slot(user_key)
            
            print(f"\nSearching for key: {user_key}")
            print(f"   Hash Slot: {hash_slot}")
            
            print(f"\nMethod 1: Using HGETALL (Hash)")
            print(f"   Command: HGETALL {user_key}")
            user_data = self.connection.hgetall(user_key)
            
            if not user_data:
                print(f"   User {user_id} not found")
                return None
            
            print(f"   Found user data:")
            print(f"   ├─ ID: {user_data.get('id')}")
            print(f"   ├─ Name: {user_data.get('name')}")
            print(f"   ├─ Email: {user_data.get('email')}")
            print(f"   └─ Created: {user_data.get('created_at')}")
            
            print(f"\nMethod 2: Using HGET (Individual fields)")
            print(f"   Command: HGET {user_key} name")
            name = self.connection.hget(user_key, 'name')
            print(f"   Result: {name}")
            
            print(f"\n   Command: HGET {user_key} email")
            email = self.connection.hget(user_key, 'email')
            print(f"   Result: {email}")
            
            print(f"\nMethod 3: Using EXISTS")
            print(f"   Command: EXISTS {user_key}")
            exists = self.connection.exists(user_key)
            print(f"   Result: {exists} (1 = exists, 0 = does not exist)")
            
            bookings_key = f"user:{user_id}:bookings"
            bookings_slot = self.get_hash_slot(bookings_key)
            print(f"\nRelated Data:")
            print(f"   Command: LRANGE {bookings_key} 0 -1")
            booking_ids = self.connection.lrange(bookings_key, 0, -1)
            print(f"   Booking IDs: {booking_ids if booking_ids else 'None'}")
            print(f"   Hash Slot: {bookings_slot}")
            
            print("\n" + "="*70)
            return user_data
        
        except Exception as e:
            print(f"Error searching for user: {e}")
            return None
