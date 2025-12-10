# Questions & Answers

Potential questions the doctor might ask during the presentation.

---

## About the Database Schema

**Q: Why did you choose these 3 tables?**
> Users, Hotels, and Bookings represent a real-world hotel booking system. Bookings connects Users to Hotels using foreign keys, showing relational database concepts.

**Q: Where are the foreign keys defined?**
> In `mysql_operations.py`, the Bookings table has:
> - `FOREIGN KEY (user_id) REFERENCES Users(id)`
> - `FOREIGN KEY (hotel_id) REFERENCES Hotels(id)`

**Q: Can you show me the table creation code?**
> File: `modules/mysql_operations.py`, function: `create_tables()`

---

## About Data Mapping

**Q: How do you map a SQL row to Redis?**
> Each row becomes a Redis Hash. Example:
> - MySQL: `Users(id=1, name='Alice', email='alice@email.com')`
> - Redis: `user:1 = {id: '1', name: 'Alice', email: 'alice@email.com'}`

**Q: How do you handle foreign keys in Redis?**
> We use a Redis List. Instead of `Bookings.user_id = 1`, we store:
> - `user:1:bookings = [1, 2, 4]` (list of booking IDs belonging to user 1)

**Q: Where is the migration code?**
> File: `modules/redis_migration.py`, function: `migrate_data()`

---

## About Sharding

**Q: How does sharding work?**
> Redis uses CRC16 hash function to calculate a slot number (0-16383):
> ```
> slot = CRC16(key) % 16384
> ```
> Each master node handles a range of slots.

**Q: Which node stores which slots?**
> - Master 7001: slots 0-5460 (replica: 7004)
> - Master 7002: slots 5461-10922 (replica: 7005)
> - Master 7003: slots 10923-16383 (replica: 7006)

**Q: How do you know which node stores a key?**
> We query the actual cluster using `CLUSTER SLOTS` command, which returns the real topology:
> ```python
> cluster_slots = self.connection.cluster_slots()
> # Returns: {(0, 5460): {'primary': ('127.0.0.1', 7001), 'replicas': [('127.0.0.1', 7004)]}, ...}
> ```
> This is dynamic - if a master fails and replica takes over, it updates automatically.

**Q: Where is the hash slot calculation?**
> File: `modules/redis_migration.py`, function: `get_hash_slot()`

**Q: Where do you get the node info from?**
> File: `modules/redis_migration.py`, function: `get_node_for_slot()` - queries `CLUSTER SLOTS`

**Q: Why is data distributed unevenly across nodes?**
> The CRC16 hash distributes keys randomly. With small data, some nodes may have more keys than others. With larger datasets, distribution becomes more even.

---

## About the Cluster

**Q: Why 6 nodes?**
> 3 masters (store data) + 3 replicas (backup copies). If a master fails, its replica takes over.

**Q: What is replication?**
> Each master automatically copies its data to a replica. This provides fault tolerance.
> - Master 7001 → Replica 7004
> - Master 7002 → Replica 7005
> - Master 7003 → Replica 7006

**Q: How do you show both master and replica in the output?**
> During migration and queries, we display both:
> ```
> user:1 -> slot 10778 -> master 7002, replica 7005
> ```
> This info is queried from the live cluster, not hardcoded.

**Q: Where do you create the cluster?**
> File: `setup_cluster.py`, function: `create_cluster()`

---

## About Queries

**Q: How do you query data without SQL?**
> We use Redis commands:
> - `HGETALL user:1` - get all fields of a hash
> - `LRANGE user:1:bookings 0 -1` - get all items in a list
> - `SMEMBERS hotels:city:Miami` - get all members of a set

**Q: How do you replace SQL JOIN?**
> In SQL: `SELECT * FROM Bookings JOIN Hotels ON ...`
> In Redis:
> 1. Get booking IDs: `LRANGE user:1:bookings 0 -1`
> 2. For each booking: `HGETALL booking:1`
> 3. Get hotel: `HGETALL hotel:2`

**Q: Where is the query code?**
> File: `modules/redis_queries.py`, function: `query_user_bookings()`

---

## About the Code

**Q: What does main.py do?**
> 1. Connects to MySQL
> 2. Creates tables
> 3. Gets all data
> 4. Connects to Redis Cluster
> 5. Migrates data to Redis
> 6. Runs interactive query menu

**Q: What library do you use for Redis?**
> `redis-py` with `RedisCluster` class for cluster support.

**Q: What library do you use for MySQL?**
> `mysql-connector-python`

---

## Quick Function Reference

| Question | File | Function |
|----------|------|----------|
| Where are tables created? | `mysql_operations.py` | `create_tables()` |
| Where is data migrated? | `redis_migration.py` | `migrate_data()` |
| Where is hash slot calculated? | `redis_migration.py` | `get_hash_slot()` |
| Where is node info queried? | `redis_migration.py` | `get_node_for_slot()` |
| Where are Redis queries? | `redis_queries.py` | `run_interactive()` |
| Where is key info shown? | `redis_queries.py` | `show_key_info()` |
| Where is cluster created? | `setup_cluster.py` | `create_cluster()` |
