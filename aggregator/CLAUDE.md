# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run in standalone mode (fetch once and exit)
python3 aggregator.py --config config.json --mode standalone

# Run in application mode (continuous, timer-based)
python3 aggregator.py --config config.json --mode application

# Run benchmarks
python3 benchmark.py --config config.json

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Copy `config.json.example` to `config.json` before running. Key settings:
- `db.update`: set to `true` to enable PostgreSQL sync (disabled by default)
- `api.*`: each API source has its own config block (URLs, keys, coin lists)
- `benchmark.filters.coins`: list of coin tags to benchmark

## Architecture

The aggregator fetches cryptocurrency mining profitability data from 7 external APIs, merges it into unified data models, exports JSON to `dataset/`, and optionally syncs to PostgreSQL.

**Data flow:**
```
External APIs → api/ clients → workflow/ processors → Managers → dataset/ JSON → (optional) PostgreSQL
```

### Execution Modes

- **Standalone** ([apps/standalone.py](apps/standalone.py)): Runs the full pipeline once sequentially. Best for cron/batch use.
- **Application** ([apps/application.py](apps/application.py)): Runs continuously with a `TimerHandler` that invokes each workflow at its own interval. Uses a 100ms sleep loop.

### Core Layers

**`api/`** — HTTP clients, one per data source: `HashRateNoAPI`, `WhatToMineAPI`, `MinerStatAPI`, `BinanceAPI`, `CoinGeckoAPI`, `TwoMinersAPI`, `NanopoolAPI`. All extend `ApiHTTP`.

**`workflow/`** — Stateless functions that call an API client, parse the response, and update managers. Each workflow specifies its refresh interval (1–20 seconds). Coin workflows and pool workflows are separate.

**`common/`** — Data models (`Coin`, `Reward`, `Block`, `Pool`, `CoinPool`) and manager singletons (`CoinManager`, `PoolManager`, `HardwareManager`, `PostgreSQL`). Managers hold in-memory state and expose `dump()` to write JSON to `dataset/`.

**`dataset/`** — Output directory for JSON snapshots: `coin_manager/data.json`, `pool_manager/data.json`, `hardware_manager/data.json`.

### Data Models

- `Coin` holds a `Reward` object. `Reward.update()` calculates derived profitability metrics from raw values.
- Each manager has a `merge()` pattern: new data from different API sources is merged into the existing record rather than overwritten.
- `CoinManager.dump()` filters out coins missing `emission_usd` or `market_cap` before export.
- `PostgreSQL.update()` calls stored procedures: `insert_coin()`, `insert_pool()`, `insert_pool_stats()`, `insert_hardware()`.
