# System Design

## 1. Database Schema

```mermaid
erDiagram
    Users ||--o{ Bookings : makes
    Hotels ||--o{ Bookings : has
    
    Users {
        int id PK
        string name
        string email
    }
    
    Hotels {
        int id PK
        string name
        string city
    }
    
    Bookings {
        int id PK
        int user_id FK
        int hotel_id FK
        date date
    }
```

---

## 2. Data Mapping

```mermaid
flowchart LR
    subgraph MySQL
        Row[SQL Row<br/>id, name, email]
        FK[Foreign Key<br/>user_id = 1]
    end
    
    subgraph Redis
        Hash[Hash<br/>user:1 = &#123;id, name, email&#125;]
        List[List<br/>user:1:bookings = &#91;1, 2&#93;]
    end
    
    Row --> Hash
    FK --> List
```

---

## 3. Sharding

```mermaid
flowchart TD
    Key[Key: user:1] --> CRC[CRC16 Hash]
    CRC --> Slot[Slot: 10778]
    Slot --> Check{Which Master?}
    Check -->|0-5460| P7001[Port 7001]
    Check -->|5461-10922| P7002[Port 7002]
    Check -->|10923-16383| P7003[Port 7003]
```

---

## 4. Cluster Architecture

```mermaid
flowchart TD
    Client[Python App] --> M1[Master 7001<br/>slots 0-5460]
    Client --> M2[Master 7002<br/>slots 5461-10922]
    Client --> M3[Master 7003<br/>slots 10923-16383]
    
    M1 -.-> R1[Replica 7004]
    M2 -.-> R2[Replica 7005]
    M3 -.-> R3[Replica 7006]
```

---

## 5. Query Flow (No SQL)

```mermaid
flowchart LR
    A[Get user bookings] --> B[LRANGE user:1:bookings]
    B --> C[Returns: 1, 2]
    C --> D[HGETALL booking:1]
    D --> E[HGETALL hotel:2]
    E --> F[Combined Result]
```

---

## 6. Key Files

| File | Purpose |
|------|---------|
| `mysql_operations.py` | Connect to MySQL, create tables |
| `redis_migration.py` | Migrate data, calculate hash slots |
| `redis_queries.py` | Query Redis interactively |
| `main.py` | Run everything |
