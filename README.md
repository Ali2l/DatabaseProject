# Hotel Booking System

MySQL (Relational) → Redis Cluster (Key-Value)

---

## Quick Start

```bash
# 1. Start MySQL (Docker)
docker-compose up -d

# 2. Start Redis Cluster (requires: brew install redis)
python3 setup_cluster.py

# 3. Run the project
python3 main.py

# 4. Stop when done
python3 stop_cluster.py
```

---

## Project Structure

```
DatabaseProject/
├── main.py                  # Main program
├── setup_cluster.py         # Start 6-node Redis Cluster
├── stop_cluster.py          # Stop the cluster
├── modules/
│   ├── mysql_operations.py  # MySQL operations
│   ├── redis_migration.py   # Data migration + sharding
│   └── redis_queries.py     # Interactive queries
├── sql/
│   ├── 01_schema.sql        # Table definitions
│   └── 02_sample_data.sql   # Sample data
└── docker-compose.yml       # MySQL container
```

---

## The 3 Tables

| Table | Columns | Purpose |
|-------|---------|---------|
| Users | id, name, email | Store user info |
| Hotels | id, name, city | Store hotel info |
| Bookings | id, user_id, hotel_id, date | Link users to hotels |

---

## Data Mapping (MySQL → Redis)

| MySQL | Redis | Example |
|-------|-------|---------|
| Row | Hash | `user:1` = {id, name, email} |
| Foreign Key | List | `user:1:bookings` = [1, 2] |
| Index | Set | `hotels:city:Miami` = {2} |

---

## Redis Cluster (6 Nodes)

| Port | Role | Hash Slots |
|------|------|------------|
| 7001 | Master | 0-5460 |
| 7002 | Master | 5461-10922 |
| 7003 | Master | 10923-16383 |
| 7004 | Replica | backup |
| 7005 | Replica | backup |
| 7006 | Replica | backup |

**Sharding formula:** `slot = CRC16(key) % 16384`

---

## Requirements Met

1. ✅ Small relational database (3 tables)
2. ✅ Map to Key-Value database
3. ✅ Choose Key-Value store (Redis)
4. ✅ Sharding & Replication (6-node cluster)
5. ✅ Insert data (migration)
6. ✅ Write queries (interactive menu)
