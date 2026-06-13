# Aggregator

Cryptocurrency mining profitability aggregator. Fetches data from 7 external APIs, merges it into unified data models, exports JSON snapshots to `dataset/`, and optionally syncs to PostgreSQL.

## Architecture

```
External APIs
  ├── Market:   Binance, CoinGecko
  ├── Mining:   Hashrate.no, WhatToMine, MinerStat
  ├── Pool:     2Miners, Nanopool
  └── Explorer: Ergo, Kaspa, Ravencoin, Monero, Conflux, Ethereum Classic
        ↓
  api/  →  workflow/  →  common/ (managers)  →  dataset/ JSON  →  PostgreSQL (optional)
```

### Layers

| Directory | Role |
| :--- | :--- |
| `api/` | HTTP clients, one per data source, all extending `ApiHTTP` |
| `workflow/` | Stateless functions: call a client, parse, update managers |
| `common/` | Data models (`Coin`, `Reward`, `Block`, `Pool`) and manager singletons |
| `apps/` | Execution modes: standalone (batch) and application (continuous) |
| `dataset/` | Output JSON snapshots written by managers |

### Execution Modes

- **Standalone** — runs the full pipeline once sequentially, exports JSON, optionally syncs DB, then exits. Best for cron/batch use.
- **Application** — infinite loop (100 ms sleep) where each workflow fires on its own timer (1–120 s intervals).

## Installation

```bash
pip install -r requirements.txt
cp config.json.example config.json
```

Edit `config.json` to add API keys and adjust settings (see [Configuration](#configuration)).

## Usage

```bash
# Fetch once and exit
python3 aggregator.py --config config.json --mode standalone

# Run continuously
python3 aggregator.py --config config.json --mode application

# Run benchmarks
python3 benchmark.py --config config.json
```

Logs are written to both the console and `aggregator.log`.

## Configuration

`config.json` is structured as follows:

```jsonc
{
  "log": "info",                  // Log level: debug | info | warning | error
  "folder_output": "dataset",     // Output directory for JSON exports

  "db": {
    "update": false,              // Set to true to enable PostgreSQL sync
    "host": "localhost",
    "database": "smart_mining",
    "username": "luminousminer",
    "password": "...",
    "port": 5432
  },

  "market": {
    "binance":   { "use_api": true, "host": "https://api.binance.com" },
    "coingecko": { "use_api": true, "api_key": "YOUR_KEY", "host": "..." }
  },

  "mining": {
    "hashrate_no": { ... },
    "whattomine":  { ... },
    "minerstat":   { ... }
  },

  "pool": {
    "2miners":  { ... },
    "nanopool": { ... }
  },

  "explorer": {
    "erg": { ... }, "kas": { ... }, "rvn": { ... },
    "xmr": { ... }, "cfx": { ... }, "etc": { ... }
  },

  "timers": {
    // Refresh interval in seconds for each source (application mode only)
    "market":   { "binance": 8,  "coingecko": 20 },
    "mining":   { "hashrate_no": 5, "whattomine": 10, "minerstat": 10 },
    "pool":     { "2miners": 5, "nanopool": 5 },
    "explorer": { "erg": 5, "kas": 5, "rvn": 5, "xmr": 5, "cfx": 5, "etc": 5 }
  }
}
```

Set `use_api: false` on any source to disable it and use the last cached response from `dataset/` instead.

## Output

JSON snapshots are written to `dataset/` after each full pipeline run:

| File | Content |
| :--- | :--- |
| `dataset/coin_manager/data.json` | All coins with profitability metrics |
| `dataset/pool_manager/data.json` | Pool statistics |
| `dataset/hardware_manager/data.json` | GPU/ASIC hardware reference data |
| `dataset/<source>/` | Raw API response cache per source |

`CoinManager.dump()` filters out coins missing `emission_usd` or `market_cap` before export.

## Data Models

**`Coin`** — one record per mineable coin: `name`, `tag`, `algorithm`, `block_height`, and a `Reward` object.

**`Reward`** — profitability metrics calculated by `Reward.update()` from raw values (block reward, network hashrate, coin price).

Data from multiple API sources is **merged** into existing records rather than overwritten, so each coin accumulates the best available data across sources.

## PostgreSQL Sync

When `db.update: true`, the aggregator calls stored procedures after each pipeline run:

- `insert_coin()` — upsert coin profitability data
- `insert_pool()` / `insert_pool_stats()` — upsert pool records
- `insert_hardware()` — upsert hardware mining stats

The database schema is defined in `../database/`. Initialize it with:

```bash
cd ../database && bash install_db.sh
```

## Docker

```bash
docker build -t smart_mining_aggregator .
docker run -d --name smart_mining_aggregator --network smart_mining_network smart_mining_aggregator
```

The container runs in **application mode** by default (continuous). Make sure the database and API containers are running first (see the root [`../CLAUDE.md`](../CLAUDE.md)).

## Dependencies

| Package | Purpose |
| :--- | :--- |
| `requests` | HTTP calls to external APIs |
| `psycopg2-binary` | PostgreSQL connector |
| `matplotlib` | Benchmark charts |
