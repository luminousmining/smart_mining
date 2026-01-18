# smart_mining

## Archi

```
┌──────────────────┐
│ External APIs    │
│ Blockchains      │
│ - CoinGecko      │
│ - Blockchain RPC │
│ - Pool APIs      │
└────────┬─────────┘
         │ (1) Fetch data
         │     - Prices
         │     - Difficulty
         │     - Hashrates
         ↓
┌──────────────────┐
│   AGGREGATOR     │
│  - Parse data    │
│  - Calculate     │
│    profitability │
│  - Transform     │
└────────┬─────────┘
         │ (2) INSERT/UPDATE
         │     - Coins info
         │     - Pools data
         │     - Profitability
         ↓
┌──────────────────┐
│   PostgreSQL     │
│  Tables:         │
│  - coins         │
│  - pools         │
│  - profitability │
└──────────────────┘
```

```
┌──────────────────┐
│     Miner        │
│   (End User)     │
└────────┬─────────┘
         │ (1) Connect to proxy
         │     - Mining software
         │     - Stratum protocol
         ↓
┌──────────────────┐         (2) Request best pool
│      PROXY       │         GET /api/best-pool?algo=sha256
│  - Accept conn   │────────────────────────────────────┐
│  - Authenticate  │                                    │
└────────┬─────────┘                                    │
         │                                              ↓
         │                                    ┌──────────────────┐
         │                                    │       API        │
         │                                    │  - Query DB      │
         │                                    │  - Calculate     │
         │                                    │  - Return JSON   │
         │                                    └────────┬─────────┘
         │                                             │
         │                                             │ (3) SQL Query
         │                                             ↓
         │                                    ┌──────────────────┐
         │ (5) Redirect/Proxy connection      │   PostgreSQL     │
         │     to selected pool               │  - Get pools     │
         │                                    │  - Get profit    │
         ↓                                    └────────┬─────────┘
┌──────────────────┐
│  External Pool   │
│  - Pool A        │
│  - Pool B        │
│  - Pool C        │
└──────────────────┘
```

```
┌─────────────────────────────────────────────────────────────────┐
│                        COMPLETE FLOW                            │
└─────────────────────────────────────────────────────────────────┘

External Sources                SmartMining                End Users
       │                          │                         │
       │    ┌──────────────┐      │                         │
       └───→│ AGGREGATOR   │──────┤                         │
            │ (Collector)  │      │                         │
            └──────────────┘      │                         │
                                  │                         │
                            ┌─────▼──────┐                  │
                            │ PostgreSQL │                  │
                            │  Storage   │                  │
                            └─────┬──────┘                  │
                                  │                         │
                            ┌─────▼──────┐                  │
                            │    API     │                  │
                            │ (Decision) │                  │
                            └─────┬──────┘                  │
                                  │                         │
                            ┌─────▼──────┐                  │
                            │   PROXY    │←─────────────────┘
                            │  (Router)  │
                            └─────┬──────┘
                                  │
                            ┌─────▼──────┐
                            │External    │
                            │Pools       │
                            └────────────┘
```


## Dockers

### Database
Build
```sh
docker build -t smart_mining_database .
```

Run
```sh
docker run -d -p 5432:5432 --name smart_mining_database --network smart_mining_network smart_mining_database
```

### API
Build
```sh
docker build -t smart_mining_api .
```

Run
```sh
docker run -d -p 3000:3000 --name smart_mining_api --network smart_mining_network smart_mining_api
```

### Aggregator
Build
```sh
docker build -t smart_mining_aggregator .
```

Run
```sh
docker run -d --name smart_mining_aggregator --network smart_mining_network smart_mining_aggregator
```
