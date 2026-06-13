# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Structure

This is a monorepo containing five components that form a complete smart mining system:

| Component | Language | Purpose |
| :--- | :--- | :--- |
| `aggregator/` | Python | Fetches data from 7 external APIs, calculates profitability, stores to PostgreSQL |
| `api/` | Node.js/Express | REST API exposing profitability data to the proxy (port 3000) |
| `proxy/` | C++20 | Stratum proxy that switches miners between coins based on real-time profitability |
| `database/` | PostgreSQL/SQL | Schema definitions and Docker setup |
| `dashboard/` | React + Express | Web UI for monitoring (frontend :3000, backend :3001) |

Each component has its own `CLAUDE.md` with detailed build/run instructions:
- [`proxy/CLAUDE.md`](proxy/CLAUDE.md) — C++ build, CMake, architecture, threading model
- [`aggregator/CLAUDE.md`](aggregator/CLAUDE.md) — Python commands, config, data flow

## System Data Flow

```
External APIs (Binance, CoinGecko, Hashrate.no, Minerstat, Nanopool, 2Miners, WhatToMine)
    ↓ (aggregator fetches & normalizes)
PostgreSQL  ←→  API (port 3000)  ←→  Proxy (port 7878)  →  Mining Pools
                                          ↑
                                      Miners connect here
```

The proxy's `Brain` thread polls the API every 2 minutes to reload profitability data, then evaluates each connected miner session every 10 seconds to switch to a better coin if warranted.

## Docker (full stack)

All components run in a shared Docker network `smart_mining_network`.

```bash
# Database
docker build -t smart_mining_database ./database
docker run -d -p 5432:5432 --name smart_mining_database --network smart_mining_network smart_mining_database

# API
docker build -t smart_mining_api ./api
docker run -d -p 3000:3000 --name smart_mining_api --network smart_mining_network smart_mining_api

# Aggregator
docker build -t smart_mining_aggregator ./aggregator
docker run -d --name smart_mining_aggregator --network smart_mining_network smart_mining_aggregator
```

## Database

PostgreSQL database name: `smart_mining`, user: `luminousminer`.

```bash
cd database && bash install_db.sh   # initialize schema (coins, hardware, pool, profile tables)
```

Key tables: `coins`, `coin_history`, `pools`, `pool_history`, `hardware`, `hardware_mining`.

## API

```bash
cd api
cp config.json.example config.json  # fill in DB credentials
npm install
npm start       # production
npm run dev     # development with nodemon (auto-reload)
```

All requests require `?api_key=<key>` query param. The proxy uses `api_key=123456` by default.

Routes: `/info/coins`, `/info/coin`, `/profile/emission`, `/profile/hash_usd`, `/profile/usd_sec`, `/profile/market_cap`, `/profile/network_hashrate`.

## Dashboard

```bash
cd dashboard/backend && cp .env.example .env && npm install && npm start   # port 3001
cd dashboard/frontend && npm install && npm run dev                        # port 3000
```

Vite proxies all `/api/*` requests to the backend. All pages auto-refresh every 30 seconds. Production deployment uses NGINX + PM2 (see [`dashboard/README.md`](dashboard/README.md)).

## Proxy (C++)

See [`proxy/CLAUDE.md`](proxy/CLAUDE.md) for full build instructions. Summary:

- **Dependencies:** CMake ≥ 3.22, clang-15, Boost 1.91.0 (exact), OpenSSL 1.1.1, GnuTLS, cppcheck
- **Build output:** `proxy/bin/proxy` (main), `proxy/bin/proxy_test` (unit tests)

```bash
cd proxy && mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release
./bin/proxy_test   # run unit tests
```

## Aggregator (Python)

See [`aggregator/CLAUDE.md`](aggregator/CLAUDE.md) for full details. Summary:

```bash
cd aggregator
pip install -r requirements.txt
cp config.json.example config.json
python3 aggregator.py --config config.json --mode standalone     # run once
python3 aggregator.py --config config.json --mode application    # continuous
```

Set `db.update: true` in `config.json` to enable PostgreSQL sync (disabled by default).
