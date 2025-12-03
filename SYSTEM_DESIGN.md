# Hotel Booking System - Architecture & Design

Complete visual guide to MySQL schema, Redis migration, and query operations.

---

## 1. MySQL Database Schema (Relational Design)

### Entity Relationship Diagram

```mermaid
erDiagram
    Users ||--o{ Bookings : makes
    Hotels ||--o{ Bookings : has
    
    Users {
        int id PK
        string name
        string email UK
        timestamp created_at
    }
    
    Hotels {
        int id PK
        string name
        string city
        timestamp created_at
    }
    
    Bookings {
        int id PK
        int user_id FK
        int hotel_id FK
        date date
        timestamp created_at
    }
```

### Relationships
- **Users → Bookings**: One user can make many bookings (1:N)
- **Hotels → Bookings**: One hotel can have many bookings (1:N)
- **Foreign Keys**: 
  - `Bookings.user_id` references `Users.id`
  - `Bookings.hotel_id` references `Hotels.id`

---

## 2. Redis Migration Process

### Data Transformation Flow

```mermaid
flowchart TB
    Start([Start Migration]) --> Connect[Connect to MySQL & Redis]
    Connect --> Fetch[Fetch All MySQL Data]
    
    Fetch --> ProcessUsers[Process Users Table]
    Fetch --> ProcessHotels[Process Hotels Table]
    Fetch --> ProcessBookings[Process Bookings Table]
    
    ProcessUsers --> HashUser[Transform to Redis Hash<br/>Key: user:ID]
    HashUser --> SlotUser[Calculate Hash Slot<br/>CRC16 mod 16384]
    SlotUser --> NodeUser[Determine Node<br/>Slot 0-5460 → Node 1<br/>Slot 5461-10922 → Node 2<br/>Slot 10923-16383 → Node 3]
    NodeUser --> StoreUser[Store in Redis]
    StoreUser --> IndexUser[Create Indexes<br/>users:all SET<br/>user:email:X KEY]
    
    ProcessHotels --> HashHotel[Transform to Redis Hash<br/>Key: hotel:ID]
    HashHotel --> SlotHotel[Calculate Hash Slot]
    SlotHotel --> NodeHotel[Determine Node]
    NodeHotel --> StoreHotel[Store in Redis]
    StoreHotel --> IndexHotel[Create Indexes<br/>hotels:all SET<br/>hotels:city:X SET]
    
    ProcessBookings --> HashBooking[Transform to Redis Hash<br/>Key: booking:ID]
    HashBooking --> SlotBooking[Calculate Hash Slot]
    SlotBooking --> NodeBooking[Determine Node]
    NodeBooking --> StoreBooking[Store in Redis]
    StoreBooking --> RelationshipList[Create Relationship List<br/>user:ID:bookings LIST]
    RelationshipList --> IndexBooking[Create Indexes<br/>bookings:all SET<br/>bookings:date:X SET]
    
    IndexUser --> Summary[Display Sharding Summary]
    IndexHotel --> Summary
    IndexBooking --> Summary
    
    Summary --> Verify[Verify Migration]
    Verify --> End([Migration Complete])
    
    style Start fill:#90EE90
    style End fill:#90EE90
    style SlotUser fill:#FFE4B5
    style SlotHotel fill:#FFE4B5
    style SlotBooking fill:#FFE4B5
    style NodeUser fill:#87CEEB
    style NodeHotel fill:#87CEEB
    style NodeBooking fill:#87CEEB
```

### Hash Slot Calculation

```mermaid
flowchart LR
    Key[Redis Key<br/>e.g., user:1] --> CRC16[Apply CRC16<br/>Hash Function]
    CRC16 --> Modulo[Modulo 16384<br/>Result: 0-16383]
    Modulo --> Slot[Hash Slot<br/>e.g., 10778]
    
    Slot --> Check{Which Node?}
    Check -->|0-5460| Node1[Node 1]
    Check -->|5461-10922| Node2[Node 2]
    Check -->|10923-16383| Node3[Node 3]
    
    style Slot fill:#FFD700
    style Node1 fill:#FF6B6B
    style Node2 fill:#4ECDC4
    style Node3 fill:#95E1D3
```

---

## 3. Redis Data Structure Mapping

### SQL Tables → Redis Structures

```mermaid
graph TB
    subgraph MySQL["MySQL (Relational)"]
        UserTable[Users Table<br/>Rows with columns]
        HotelTable[Hotels Table<br/>Rows with columns]
        BookingTable[Bookings Table<br/>Foreign Keys]
    end
    
    subgraph Redis["Redis (Key-Value)"]
        UserHash[User Hashes<br/>user:1 → Hash<br/>user:2 → Hash]
        HotelHash[Hotel Hashes<br/>hotel:1 → Hash<br/>hotel:2 → Hash]
        BookingHash[Booking Hashes<br/>booking:1 → Hash<br/>booking:2 → Hash]
        
        UserList[Relationship Lists<br/>user:1:bookings → List]
        UserSet[User Index<br/>users:all → Set]
        EmailIndex[Email Index<br/>user:email:X → String]
        CitySet[City Index<br/>hotels:city:NY → Set]
    end
    
    UserTable -->|Transform| UserHash
    UserTable -->|Index| UserSet
    UserTable -->|Index| EmailIndex
    
    HotelTable -->|Transform| HotelHash
    HotelTable -->|Index| CitySet
    
    BookingTable -->|Transform| BookingHash
    BookingTable -->|Replace FK| UserList
    
    style MySQL fill:#E8F4F8
    style Redis fill:#FFF4E6
```

---

## 4. Redis Query Operations (Without MySQL)

### Query Flow Diagram

```mermaid
flowchart TB
    Start([Redis Query Request]) --> Type{Query Type?}
    
    Type -->|Search User by ID| Q1[Query: user:ID]
    Q1 --> HGETALL1[HGETALL user:ID]
    HGETALL1 --> Return1[Return User Data]
    
    Type -->|Get Booking History| Q2[Query: User Bookings]
    Q2 --> Step1[1. HGETALL user:ID<br/>Get user info]
    Step1 --> Step2[2. LRANGE user:ID:bookings<br/>Get booking IDs]
    Step2 --> Step3[3. For each booking ID:<br/>HGETALL booking:ID]
    Step3 --> Step4[4. For each hotel ID:<br/>HGETALL hotel:ID]
    Step4 --> Combine[Combine All Data]
    Combine --> Return2[Return Complete History]
    
    Type -->|Hotels by City| Q3[Query: Hotels in City]
    Q3 --> CitySet[SMEMBERS hotels:city:X<br/>Get hotel IDs]
    CitySet --> CityHash[For each ID:<br/>HGETALL hotel:ID]
    CityHash --> Return3[Return Hotel List]
    
    Type -->|User by Email| Q4[Query: User by Email]
    Q4 --> EmailKey[GET user:email:X<br/>Get user ID]
    EmailKey --> EmailHash[HGETALL user:ID<br/>Get user data]
    EmailHash --> Return4[Return User Data]
    
    Return1 --> End([Return Results])
    Return2 --> End
    Return3 --> End
    Return4 --> End
    
    style Start fill:#90EE90
    style End fill:#90EE90
    style HGETALL1 fill:#FFE4B5
    style Step2 fill:#87CEEB
    style CitySet fill:#DDA0DD
    style EmailKey fill:#F0E68C
```

### Relationship Traversal (Without JOINs)

```mermaid
sequenceDiagram
    participant Client
    participant Redis
    
    Note over Client,Redis: Get User 1 Booking History
    
    Client->>Redis: HGETALL user:1
    Redis-->>Client: {id:1, name:Alice, email:alice@...}
    
    Client->>Redis: LRANGE user:1:bookings 0 -1
    Redis-->>Client: [2, 1]
    
    loop For each booking ID
        Client->>Redis: HGETALL booking:2
        Redis-->>Client: {id:2, user_id:1, hotel_id:2, date:...}
        
        Client->>Redis: HGETALL hotel:2
        Redis-->>Client: {id:2, name:Ocean View, city:Miami}
    end
    
    Note over Client,Redis: All data combined without SQL JOINs
```

---

## 5. Cluster Sharding Distribution

### 3-Node Cluster Architecture

```mermaid
graph TB
    subgraph Input["Data Input"]
        Keys[Redis Keys<br/>user:1, hotel:2, booking:3, etc.]
    end
    
    Keys --> Hash[CRC16 Hash Function]
    Hash --> Slots[Hash Slots<br/>0 - 16383]
    
    Slots --> Distribution{Slot Range?}
    
    Distribution -->|0-5460| Node1
    Distribution -->|5461-10922| Node2
    Distribution -->|10923-16383| Node3
    
    subgraph Node1["Node 1 (Master)<br/>Slots: 0-5460"]
        N1Data[user:3<br/>hotel:3<br/>booking:4]
    end
    
    subgraph Node2["Node 2 (Master)<br/>Slots: 5461-10922"]
        N2Data[user:1<br/>user:2<br/>hotel:1<br/>hotel:2<br/>booking:1<br/>booking:2]
    end
    
    subgraph Node3["Node 3 (Master)<br/>Slots: 10923-16383"]
        N3Data[hotel:4<br/>booking:3]
    end
    
    Node1 -.Replicate.-> Replica1[Replica 1]
    Node2 -.Replicate.-> Replica2[Replica 2]
    Node3 -.Replicate.-> Replica3[Replica 3]
    
    style Node1 fill:#FF6B6B
    style Node2 fill:#4ECDC4
    style Node3 fill:#95E1D3
    style Replica1 fill:#FFA07A
    style Replica2 fill:#7FCDCD
    style Replica3 fill:#B0E6DF
```

### Data Distribution Example

```mermaid
pie title Current Data Distribution Across Nodes
    "Node 1" : 3
    "Node 2" : 6
    "Node 3" : 2
```

---

## 6. Complete System Architecture

### End-to-End Flow

```mermaid
flowchart TB
    subgraph Client["Client Application"]
        App[Python Main Script]
    end
    
    subgraph MySQL["MySQL Database"]
        SQLTables[(Users<br/>Hotels<br/>Bookings)]
    end
    
    subgraph Redis["Redis Cluster"]
        direction TB
        RedisNode1[Node 1<br/>Slots 0-5460]
        RedisNode2[Node 2<br/>Slots 5461-10922]
        RedisNode3[Node 3<br/>Slots 10923-16383]
    end
    
    App -->|1. Create Schema| SQLTables
    App -->|2. Insert Data| SQLTables
    App -->|3. Fetch Data| SQLTables
    SQLTables -->|4. Return Data| App
    
    App -->|5. Calculate Hash Slots| HashCalc[Hash Calculator<br/>CRC16]
    HashCalc -->|6. Migrate Data| RedisNode1
    HashCalc -->|6. Migrate Data| RedisNode2
    HashCalc -->|6. Migrate Data| RedisNode3
    
    App -->|7. Query Data| RedisNode1
    App -->|7. Query Data| RedisNode2
    App -->|7. Query Data| RedisNode3
    
    RedisNode1 -->|8. Return Results| App
    RedisNode2 -->|8. Return Results| App
    RedisNode3 -->|8. Return Results| App
    
    style MySQL fill:#E8F4F8
    style Redis fill:#FFF4E6
    style App fill:#E6F3E6
```

---

## Key Concepts Summary

### Data Transformation Rules

| MySQL Concept | Redis Equivalent | Example |
|---------------|------------------|---------|
| **Table Row** | Hash | `user:1` → `{id:1, name:Alice, email:...}` |
| **Primary Key** | Key Suffix | `user:1`, `hotel:2`, `booking:3` |
| **Foreign Key** | List/Reference | `user:1:bookings` → `[1, 2, 3]` |
| **Index** | Set | `users:all` → `{1, 2, 3}` |
| **Unique Constraint** | Key Mapping | `user:email:alice@...` → `1` |
| **SQL JOIN** | Multiple Hash Fetches | LRANGE + HGETALL loop |

### Sharding Strategy

1. **Hash Function**: CRC16 (same as Redis Cluster)
2. **Slot Range**: 0-16383 (16,384 total slots)
3. **Distribution**: Evenly across 3 nodes (~5,461 slots each)
4. **Key Format**: `{prefix}:{id}` determines slot
5. **Replication**: Each master has replica(s) for failover

### Query Patterns

1. **Direct Lookup**: `HGETALL user:1`
2. **Index Scan**: `SMEMBERS hotels:city:Miami` → `HGETALL hotel:X`
3. **Relationship Traversal**: `LRANGE user:1:bookings` → `HGETALL booking:X`
4. **Reverse Lookup**: `GET user:email:X` → `HGETALL user:Y`

---

## Implementation Files

- **MySQL Operations**: `modules/mysql_operations.py`
- **Redis Migration**: `modules/redis_migration.py`
- **Redis Queries**: `modules/redis_queries.py`
- **Main Orchestrator**: `main.py`

---

*Generated for Hotel Booking System - Database Migration Project*
