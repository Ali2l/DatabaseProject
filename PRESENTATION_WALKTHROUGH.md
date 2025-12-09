# Presentation Walkthrough

## How to Run

```bash
# 1. Start MySQL
docker-compose up -d

# 2. Start Redis Cluster
python3 setup_cluster.py

# 3. Run the project
python3 main.py

# 4. Stop when done
python3 stop_cluster.py
```

---

## What Each File Does

| File | What it does |
|------|--------------|
| `main.py` | Runs everything in order |
| `setup_cluster.py` | Starts 6 Redis nodes |
| `mysql_operations.py` | Creates tables, gets data |
| `redis_migration.py` | Migrates data, calculates slots |
| `redis_queries.py` | Interactive query menu |

---

## Step-by-Step Demo

### Step 1: Show MySQL Tables

```sql
CREATE TABLE Users (id, name, email)
CREATE TABLE Hotels (id, name, city)
CREATE TABLE Bookings (id, user_id, hotel_id, date)
```

"We have 3 tables. Bookings has foreign keys to Users and Hotels."

---

### Step 2: Show Data Mapping

```
MySQL:                          Redis:
+----+-------+                  user:1 = {id, name, email}
| id | name  |        -->       
+----+-------+                  user:1:bookings = [1, 2]
| 1  | Alice |                  (list replaces foreign key)
+----+-------+
```

"Each row becomes a Redis Hash. Foreign keys become Lists."

---

### Step 3: Show Sharding

```
user:1 -> slot 10778 -> port 7002
user:3 -> slot 2648  -> port 7001
hotel:4 -> slot 14648 -> port 7003
```

"Redis uses CRC16 to hash the key. The slot determines which node stores the data."

---

### Step 4: Show Query

```
# Get user's bookings (like SQL JOIN)
LRANGE user:1:bookings 0 -1  → [1, 2]
HGETALL booking:1            → {hotel_id: 1, ...}
HGETALL hotel:1              → {name: "Grand Hotel"}
```

"No SQL needed. We get booking IDs from the list, then fetch each one."

---

```
# 1. Show cluster slot distribution
redis-cli -p 7001 CLUSTER SLOTS

# 2. Check which slot a key belongs to
redis-cli -p 7001 CLUSTER KEYSLOT "user:1"

# 3. Count keys on EACH master (proves data is split)
redis-cli -p 7001 DBSIZE
redis-cli -p 7002 DBSIZE
redis-cli -p 7003 DBSIZE

# 4. Show keys stored on each specific node
redis-cli -p 7001 KEYS "*"
redis-cli -p 7002 KEYS "*"
redis-cli -p 7003 KEYS "*"
```

## Key Points to Mention

1. **3 Tables** - Users, Hotels, Bookings with foreign keys
2. **Data Mapping** - Row → Hash, Foreign Key → List
3. **6-Node Cluster** - 3 masters + 3 replicas
4. **Sharding** - CRC16 hash → 16384 slots → 3 nodes
5. **Queries** - No SQL, just Redis commands
