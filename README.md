# Hotel Booking System - Database Migration Project

## 🎓 University Project: SQL to NoSQL Migration

**Author:** Ali Alkhowaiter  
**Course:** Database Systems  
**Topic:** Relational Database to Key-Value Store Migration

---

## 📋 Project Overview

This project demonstrates a complete migration from **MySQL (Relational Database)** to **Redis (Key-Value Store)**. It showcases:

✅ **Relational database design** (2-3 tables)  
✅ **Data transformation** from SQL to NoSQL  
✅ **Sharding concepts** through hash slot calculation  
✅ **Relationship handling** without SQL JOINs  
✅ **Complex queries** on Key-Value store  

---

## 🏗️ Architecture - Modular Design

The project is organized into **4 separate modules** for clarity and presentation:

```
main.py                  # Parent orchestrator class
mysql_operations.py      # MySQL database operations
redis_migration.py       # Data migration & sharding
redis_queries.py         # Redis query operations
```

### Module Breakdown:

1. **main.py** - Coordinates the entire workflow
2. **mysql_operations.py** - Handles MySQL connection, tables, and data
3. **redis_migration.py** - Migrates data and demonstrates sharding
4. **redis_queries.py** - Executes queries on Redis without MySQL

📖 **See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed documentation**

---

## 📊 Database Schema

### MySQL (Relational):

```sql
Users (id, name, email, created_at)
Hotels (id, name, city, created_at)
Bookings (id, user_id, hotel_id, date, created_at)
```

### Redis (Key-Value):

```
Hashes:
  user:1 → {id, name, email, created_at}
  hotel:1 → {id, name, city, created_at}
  booking:1 → {id, user_id, hotel_id, date, created_at}

Lists (Relationships):
  user:1:bookings → [1, 2, 3]
  hotel:1:bookings → [1, 3]

Sets (Indexes):
  users:all → {1, 2, 3}
  hotels:city:NewYork → {1, 4}
```

---

## 🚀 Quick Start

### Prerequisites:
- Docker & Docker Compose
- Python 3.x
- pip (Python package manager)

### 1. Install Dependencies

```bash
pip3 install -r requirements.txt
```

### 2. Start Infrastructure

```bash
# Clean start
docker-compose down -v
docker-compose up -d

# Wait for services to be healthy
sleep 10
```

### 3. Run Migration

```bash
python3 main.py
```

That's it! The script will:
1. ✅ Connect to MySQL and create tables
2. ✅ Insert sample data
3. ✅ Migrate to Redis with hash slot display
4. ✅ Execute queries on Redis (NO MySQL)
5. ✅ Show complete summary

---

## 📦 What Each Module Does

### main.py (Orchestrator)
```python
class DatabaseMigrationProject:
    - setup_mysql()           # Step 1: MySQL setup
    - migrate_to_redis()      # Step 2: Migration
    - execute_redis_queries() # Step 3: Queries
    - print_summary()         # Final report
```

### mysql_operations.py (SQL Module)
```python
class MySQLOperations:
    - connect()               # Connect to MySQL
    - create_tables()         # Create schema
    - insert_data()           # Insert records
    - get_all_data()          # Fetch for migration
```

### redis_migration.py (Migration Module)
```python
class RedisMigration:
    - connect()               # Connect to Redis
    - migrate_data()          # Transform & migrate
    - get_hash_slot()         # Calculate sharding
    - verify_migration()      # Verify data
```

### redis_queries.py (Query Module)
```python
class RedisQueries:
    - get_user_booking_history()  # Complex query
    - get_hotels_by_city()        # City search
    - get_user_by_email()         # Email lookup
    - get_bookings_by_date()      # Date search
```

---

## 🎯 Addressing Requirements

| Requirement | Implementation | Module |
|------------|----------------|---------|
| **2-3 Tables** | Users, Hotels, Bookings | `mysql_operations.py` |
| **Map to Key-Value** | Tables → Hashes, FKs → Lists | `redis_migration.py` |
| **Choose KV Store** | Redis 7 (open-source) | `docker-compose.yml` |
| **Sharding** | Hash slot calculation (CRC16) | `redis_migration.py` |
| **Replication** | Demonstrated via slot distribution | `redis_migration.py` |
| **Insert Data** | Complete migration with verification | `redis_migration.py` |
| **Write Queries** | 4+ query types without MySQL | `redis_queries.py` |

---

## 🔍 Sample Output

```
======================================================================
STEP 1: MySQL Setup (Relational Database)
======================================================================
Successfully connected to MySQL Server version 8.0.44
Table 'Users' created successfully
Successfully inserted into Users (ID: 1): {'name': 'Alice Johnson', ...}

======================================================================
STEP 2: Data Migration (MySQL → Redis)
======================================================================
--- Migrating Users ---
✓ Migrated user:1 → Hash Slot: 15495 | Data: {...}
✓ Migrated user:2 → Hash Slot: 13171 | Data: {...}

--- Migrating Hotels ---
✓ Migrated hotel:1 → Hash Slot: 10653 | Data: {...}
✓ Migrated hotel:2 → Hash Slot: 6654 | Data: {...}

--- Migrating Bookings ---
✓ Migrated booking:1 → Hash Slot: 6030 | Data: {...}
  → Added to user:1:bookings (Hash Slot: 8131)

======================================================================
STEP 3: Redis Queries (NO MySQL)
======================================================================
📋 Fetching booking list from: user:1:bookings (Hash Slot: 8131)
   Found 2 booking(s): ['2', '1']

   Booking #1:
   ├─ Booking ID: 2 (Hash Slot: 10221)
   ├─ Date: 2025-12-20
   ├─ Hotel: Ocean View Resort (ID: 2, Hash Slot: 6654)
   └─ City: Miami

✅ Retrieved 2 booking(s) from Redis (NO MySQL USED)
```

---

## 🎓 Sharding & Replication Explained

### Sharding Implementation:
- **Hash Slot Calculation:** CRC16 % 16384
- **Range:** 0-16383 (16,384 total slots)
- **Distribution:** Each key maps to a specific slot

### How It Works:
```
user:1 → Hash Slot: 15495
user:2 → Hash Slot: 13171
hotel:1 → Hash Slot: 10653
booking:1 → Hash Slot: 6030
```

### In Production Redis Cluster:
- Node 1: Slots 0-5460
- Node 2: Slots 5461-10922
- Node 3: Slots 10923-16383

**Our code shows which slot each key maps to, demonstrating how data would be distributed across nodes!**

---

## 📝 Files Overview

### Core Files:
- `main.py` - Orchestrator (run this!)
- `mysql_operations.py` - MySQL module
- `redis_migration.py` - Migration module
- `redis_queries.py` - Query module

### Configuration:
- `docker-compose.yml` - Infrastructure (MySQL + Redis)
- `requirements.txt` - Python dependencies

### Documentation:
- `README_NEW.md` - This file
- `ARCHITECTURE.md` - Detailed module documentation
- `PORT_CONFIGURATION.md` - Technical details

### Backup:
- `project_main_old_backup.py` - Original monolithic version

---

## 🛠️ Technical Stack

- **MySQL 8.0** - Relational database
- **Redis 7** - Key-Value store
- **Python 3** - Programming language
- **Docker** - Containerization
- **Libraries:** `mysql-connector-python`, `redis`, `crc16`

---

## 🎤 Presentation Tips

### Demo Flow:
1. **Show Infrastructure** - `docker-compose.yml`
2. **Explain Modules** - Show 4 separate files
3. **Run Live** - `python3 main.py`
4. **Highlight Output:**
   - Hash slots (sharding)
   - Relationship traversal (no JOINs)
   - Complex queries on Redis

### Key Points:
- ✅ Professional modular architecture
- ✅ Clear separation of concerns
- ✅ Hash slot calculation demonstrates sharding
- ✅ Lists replace SQL JOINs
- ✅ All requirements met

---

## 🔧 Troubleshooting

### Problem: Port 16379 in use
```bash
lsof -i :16379
# Kill the process or change port in docker-compose.yml
```

### Problem: Containers not starting
```bash
docker-compose logs
docker-compose down -v
docker-compose up -d
```

### Problem: Duplicate key errors
```bash
# Clean slate
docker-compose down -v
docker-compose up -d
sleep 10
python3 main.py
```

---

## 📞 Support

For questions or issues:
1. Check `ARCHITECTURE.md` for detailed documentation
2. Check `PORT_CONFIGURATION.md` for technical details
3. Review Docker logs: `docker-compose logs`

---

## ✅ Summary

✨ **What This Project Demonstrates:**
- Complete SQL → NoSQL migration
- Modular, professional code architecture
- Sharding concepts through hash slots
- Relationship handling without JOINs
- Complex queries on Key-Value store

🎯 **Ready for presentation!**

---

**Note:** This project uses standalone Redis for simplicity, but demonstrates sharding concepts through hash slot calculation, showing exactly how data would distribute in a production Redis Cluster.
