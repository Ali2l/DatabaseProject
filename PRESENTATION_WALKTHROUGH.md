# 🎓 Presentation Walkthrough Guide
## Hotel Booking System - MySQL to Redis Migration

---

## 📁 Project Structure (Clean & Organized)

```
DatabaseProject/
├── main.py                    # ⭐ Main entry point - RUN THIS
├── modules/                   # 📦 All your classes organized here
│   ├── __init__.py           # Module initialization
│   ├── mysql_operations.py   # MySQL class
│   ├── redis_migration.py    # Migration class
│   └── redis_queries.py      # Query class
├── docker-compose.yml         # Infrastructure (MySQL + Redis)
├── requirements.txt           # Python dependencies
├── sql/                       # Database schema files
│   ├── 01_schema.sql         # Table definitions
│   └── 02_sample_data.sql    # Sample data
├── README.md                  # Project documentation
├── ARCHITECTURE.md            # Detailed module explanation
└── QUICK_REFERENCE.md         # Quick tips for presentation
```

---

## 🎯 What Each File Does

### **main.py** - The Orchestrator
**What it does:** Coordinates everything. This is your main program.

**Class:** `DatabaseMigrationProject`

**Methods:**
- `setup_mysql()` - Creates tables and inserts data
- `migrate_to_redis()` - Migrates data and shows sharding
- `execute_redis_queries()` - Runs queries on Redis only
- `print_summary()` - Shows final results

**To run:** `python3 main.py`

---

### **modules/mysql_operations.py** - MySQL Module
**What it does:** Everything related to MySQL database.

**Class:** `MySQLOperations`

**Key Methods:**
- `connect()` - Connects to MySQL with retry logic
- `create_tables()` - Creates Users, Hotels, Bookings tables
- `insert_data()` - Inserts records dynamically
- `get_all_data()` - Fetches all data for migration
- `close()` - Closes connection

**This demonstrates:** Relational database operations (SQL)

---

### **modules/redis_migration.py** - Migration Module
**What it does:** Migrates data from MySQL to Redis and shows sharding.

**Class:** `RedisMigration`

**Key Methods:**
- `connect()` - Connects to Redis
- `get_hash_slot()` - **IMPORTANT!** Calculates CRC16 hash slot (0-16383)
- `migrate_data()` - Transforms SQL tables to Redis structures
- `verify_migration()` - Verifies data was migrated

**This demonstrates:**
- ✅ **Sharding** - Hash slot calculation shows data distribution
- ✅ **Data transformation** - Tables → Hashes, Foreign Keys → Lists
- ✅ **NoSQL concepts** - Key-Value storage

**Hash Slot Calculation:**
```python
def get_hash_slot(self, key):
    checksum = crc16.crc16xmodem(key.encode('utf-8'))
    slot = checksum % 16384  # Redis has 16,384 slots
    return slot
```

---

### **modules/redis_queries.py** - Query Module
**What it does:** Queries Redis WITHOUT using MySQL.

**Class:** `RedisQueries`

**Key Methods:**
- `get_user_booking_history()` - Complex query showing relationship traversal
- `get_hotels_by_city()` - Search by city
- `get_user_by_email()` - Email lookup
- `get_bookings_by_date()` - Date search

**This demonstrates:**
- ✅ **Queries without SQL** - Using Redis data structures
- ✅ **Relationship handling** - Lists instead of JOINs
- ✅ **NoSQL querying** - Hash, List, Set operations

---

### **docker-compose.yml** - Infrastructure
**What it does:** Sets up MySQL and Redis containers.

**Services:**
- `mysql` - MySQL 8.0 on port 3306
- `redis` - Redis 7 on port 16379

**To start:** `docker-compose up -d`

---

## 🚀 Step-by-Step Execution Guide

### **STEP 1: Start Infrastructure** (First time only)

```bash
# Navigate to project folder
cd /Users/alialkhowaiter/Desktop/Uni/DatabaseProject

# Install Python dependencies
pip3 install -r requirements.txt

# Start Docker containers
docker-compose up -d

# Wait for services to be ready (important!)
sleep 10

# Verify services are running
docker-compose ps
```

**What you should see:**
```
NAME              STATUS
hotel_mysql       Up (healthy)
hotel_redis       Up (healthy)
```

---

### **STEP 2: Run the Migration** (Every time you demo)

```bash
# Clean restart (recommended for demo)
docker-compose down -v
docker-compose up -d
sleep 10

# Run the migration
python3 main.py
```

---

## 📊 Understanding the Output

### **Part 1: MySQL Setup**
```
STEP 1: MySQL Setup (Relational Database)
Successfully connected to MySQL Server version 8.0.44
Creating table: Users...
Successfully inserted into Users (ID: 1): {'name': 'Alice Johnson', ...}
```

**What's happening:**
- Connecting to MySQL
- Creating 3 tables (Users, Hotels, Bookings)
- Inserting sample data

---

### **Part 2: Data Migration** ⭐ MOST IMPORTANT FOR PRESENTATION
```
STEP 2: Data Migration (MySQL → Redis)

--- Migrating Users ---
✓ Migrated user:1 → Hash Slot: 15495 | Data: {...}
✓ Migrated user:2 → Hash Slot: 13171 | Data: {...}

--- Migrating Bookings ---
✓ Migrated booking:1 → Hash Slot: 6030 | Data: {...}
  → Added to user:1:bookings (Hash Slot: 8131)
```

**What's happening:**
- Each SQL row becomes a Redis Hash
- **Hash Slot numbers show sharding!** 
- Relationships stored as Lists (user:1:bookings)

**EXPLAIN THIS:** 
> "See the hash slot numbers? In a Redis Cluster with 3 nodes:
> - Node 1 handles slots 0-5460
> - Node 2 handles slots 5461-10922
> - Node 3 handles slots 10923-16383
>
> So user:1 (slot 15495) would go to Node 3, while booking:1 (slot 6030) would go to Node 2. This demonstrates data sharding across distributed nodes!"

---

### **Part 3: Redis Queries**
```
STEP 3: Redis Queries (NO MySQL)

📋 Fetching booking list from: user:1:bookings (Hash Slot: 8131)
   Found 2 booking(s): ['2', '1']

   Booking #1:
   ├─ Booking ID: 2 (Hash Slot: 10221)
   ├─ Hotel: Ocean View Resort (ID: 2, Hash Slot: 6654)
```

**What's happening:**
- Querying ONLY Redis (MySQL not used!)
- Traversing relationships via Lists
- Fetching data from multiple Hashes

**EXPLAIN THIS:**
> "Notice we're querying Redis without any SQL! We:
> 1. Get the list of booking IDs from user:1:bookings
> 2. Fetch each booking's details from its Hash
> 3. Fetch hotel details from another Hash
> 4. Combine everything - no JOINs needed!"

---

## 🎤 Presentation Script

### **Opening (1 minute)**
"Hello! I'll demonstrate a database migration from MySQL (relational) to Redis (key-value store). My project has 3 tables: Users, Hotels, and Bookings. Let me show you the code organization first."

**Show folder structure:**
```
main.py          → Orchestrator
modules/         → Organized classes
  mysql_operations.py
  redis_migration.py
  redis_queries.py
```

---

### **Demo (3 minutes)**
"Let me run the migration live."

```bash
python3 main.py
```

**Point out during execution:**

1. **MySQL Setup:**
   "First, it creates our relational tables with foreign keys."

2. **Migration (MOST IMPORTANT):**
   "Now watch the hash slot numbers! Each key shows its slot (0-16383). This demonstrates how Redis distributes data across nodes for sharding."
   
   Point to output:
   ```
   user:1 → Hash Slot: 15495
   booking:1 → Hash Slot: 6030
   ```
   
   "In a 3-node cluster, these would go to different nodes based on their hash slots!"

3. **Queries:**
   "Finally, complex queries using ONLY Redis - no MySQL. We traverse relationships using Lists instead of SQL JOINs."

---

### **Code Walkthrough (2 minutes)**
"Let me show you the sharding code."

**Open:** `modules/redis_migration.py`

**Show method:**
```python
def get_hash_slot(self, key):
    checksum = crc16.crc16xmodem(key.encode('utf-8'))
    slot = checksum % 16384
    return slot
```

**Explain:**
"This calculates which of 16,384 slots a key belongs to using CRC16 - the same algorithm Redis Cluster uses. Each slot maps to a specific node in the cluster."

---

### **Q&A Preparation**

**Q: Why standalone Redis not cluster?**
> "For demonstration simplicity, but the hash slot calculation is identical to what Redis Cluster uses. Every key shows its slot number, proving the sharding concept."

**Q: How does sharding work?**
> "Redis uses CRC16 to hash each key to one of 16,384 slots. Slots are distributed across nodes. Our code shows exactly which slot each key maps to."

**Q: How about replication?**
> "In production, each master node handling a slot range has replica nodes. Our hash slot calculation demonstrates the foundation - how data partitions before replication."

**Q: How do you query without JOINs?**
> "We maintain relationships as Lists. See `user:1:bookings` - it stores booking IDs. We fetch each booking by ID from its Hash. All in `redis_queries.py`."

---

## 🎯 Professor's Requirements - Where to Find Them

| Requirement | File/Class | Line/Method |
|-------------|-----------|-------------|
| 2-3 tables | `modules/mysql_operations.py` | `create_tables()` method |
| Map to Key-Value | `modules/redis_migration.py` | `migrate_data()` method |
| Choose KV store | `docker-compose.yml` | Redis service |
| Sharding | `modules/redis_migration.py` | `get_hash_slot()` method |
| Insert data | `modules/redis_migration.py` | `migrate_data()` method |
| Write queries | `modules/redis_queries.py` | All methods |

---

## ⚡ Common Issues & Fixes

### Issue: Duplicate entry errors
**Fix:**
```bash
docker-compose down -v  # -v removes old data
docker-compose up -d
sleep 10
python3 main.py
```

### Issue: Port already in use
**Fix:**
```bash
lsof -i :16379  # Check what's using port
docker-compose down
docker-compose up -d
```

### Issue: Container not healthy
**Fix:**
```bash
docker-compose logs mysql
docker-compose logs redis
# Check for errors
```

---

## 📝 Pre-Presentation Checklist

Before your presentation:

- [ ] Docker Desktop is running
- [ ] Run clean test: `docker-compose down -v && docker-compose up -d && sleep 10`
- [ ] Test run: `python3 main.py` works perfectly
- [ ] Have VS Code open with `modules/` folder visible
- [ ] Have `redis_migration.py` open to show `get_hash_slot()`
- [ ] Understand hash slot numbers in output
- [ ] Know how to explain sharding concept
- [ ] Terminal ready at project folder

---

## 🎓 Key Talking Points

### 1. Modular Architecture
"I organized my code into separate modules - MySQL operations, migration logic, and query operations. This follows professional software engineering practices."

### 2. Sharding Demonstration
"Every key displays its hash slot number. This CRC16 calculation is how Redis Cluster distributes data across nodes. For example, user:1 maps to slot 15495, which would be on Node 3 in a typical 3-node cluster."

### 3. Data Transformation
"SQL tables become Redis Hashes. Foreign keys become Lists. For instance, `user:1:bookings` is a List containing booking IDs, replacing the SQL foreign key relationship."

### 4. NoSQL Querying
"My `redis_queries.py` module shows complex queries using only Redis - no SQL. We traverse relationships by fetching Lists, then fetching Hashes by ID."

---

## 🚀 Final Run Command

**For your presentation, run:**

```bash
# Clean everything first
docker-compose down -v

# Start fresh
docker-compose up -d && sleep 10

# Run migration
python3 main.py
```

**This ensures:**
- No duplicate data errors
- Clean output
- All hash slots recalculated fresh
- Professional presentation

---

## ✅ Summary

**You have:**
- ✅ Clean folder structure (`modules/` for classes)
- ✅ Professional code organization
- ✅ All professor requirements met
- ✅ Sharding demonstrated via hash slots
- ✅ Working migration and queries
- ✅ Easy-to-explain architecture

**Just run:** `python3 main.py`

**And explain the hash slot numbers as sharding!**

Good luck! 🎓✨
