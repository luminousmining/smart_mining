# Aggregator

Cryptocurrency mining profitability aggregator. Fetches data from 7 external APIs, merges it into unified data models, exports JSON snapshots to `dataset/`, and optionally syncs to PostgreSQL.

## Architecture

```
External APIs
  ├── Market
  │     ├── Binance
  │     └── CoinGecko
  ├── Mining
  │     ├── Hashrate.no
  │     ├── WhatToMine
  │     └── MinerStat
  ├── Pool
  │     ├── 2Miners
  │     └── Nanopool
  └── Explorer
        ├── Ergo · Kaspa · Ravencoin · Monero · Conflux · Ethereum Classic
        ├── Bitcoin · Litecoin · Fractal Bitcoin              (mempool.space family)
        ├── Bitcoin Cash · Dogecoin · Dash · Zcash · eCash    (Blockchair)
        ├── Dingocoin · Pepecoin · Radiant                    (eIquidus)
        └── Nervos · Salvium · QRL · Alephium · Bitcoin SV · Pirate Chain
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

## API Sources

Endpoints are configured in `config.json` (see `config.json.example`). Sources with an `api_key` field require a key.

### Market

| API | Endpoint | API Key | Rate Limit (free) |
| :--- | :--- | :---: | :--- |
| Binance | `https://api.binance.com` | No | ~1,200 weight/min per IP |
| CoinGecko | `https://api.coingecko.com/api/v3` | **Yes** | 30/min · 10k/month |
| Coinpaprika | `https://api.coinpaprika.com` | No | 10/s · 20k/month |
| CoinMarketCap | `https://pro-api.coinmarketcap.com/v1` | **Yes** | 30/min · 10k credits/month |
| CoinCap | `https://rest.coincap.io` | **Yes** | 100 free credits (prepaid) |
| Messari | `https://api.messari.io/metrics/v2` | **Yes** | 30/min · 2k/day |

### Mining

| API | Endpoint | API Key | Rate Limit (free) |
| :--- | :--- | :---: | :--- |
| Hashrate.no | `https://api.hashrate.no/api/v2` | **Yes** | Not specified |
| WhatToMine | `https://whattomine.com` | No | Not specified |
| MinerStat | `https://api.minerstat.com` | **Yes** | Not specified |

### Pool

| API | Endpoint | API Key | Rate Limit (free) |
| :--- | :--- | :---: | :--- |
| 2Miners | `https://<TAG>.2miners.com/api` | No | Not specified |
| Nanopool | `https://api.nanopool.org/v1` | No | Not specified |

### Explorer

| API | Endpoint | API Key | Rate Limit (free) |
| :--- | :--- | :---: | :--- |
| Ergo (erg) | `https://api.ergoplatform.com` | No | Not specified |
| Kaspa (kas) | `https://api.kaspa.org` | No | Not specified |
| Ravencoin (rvn) | `https://rvn-rpc-mainnet.ting.finance/rpc` | No¹ | Not specified |
| Monero (xmr) | `https://xmrchain.net` | No | Not specified |
| Conflux (cfx) | `https://api.confluxscan.io` | No | Not specified |
| Ethereum Classic (etc) | `https://etc.blockscout.com` | No | Not specified |
| Bitcoin (btc) | `https://mempool.space` | No | Not specified |
| Litecoin (ltc) | `https://litecoinspace.org` | No | Not specified |
| Fractal Bitcoin (fb) | `https://mempool.fractalbitcoin.io` | No | Not specified |
| Bitcoin Cash (bch) | `https://api.blockchair.com/bitcoin-cash` | No | ~30/min · ~1,440/day |
| Dogecoin (doge) | `https://api.blockchair.com/dogecoin` | No | ~30/min · ~1,440/day |
| Dash (dash) | `https://api.blockchair.com/dash` | No | ~30/min · ~1,440/day |
| Zcash (zec) | `https://api.blockchair.com/zcash` | No | ~30/min · ~1,440/day |
| eCash (xec) | `https://api.blockchair.com/ecash` | No | ~30/min · ~1,440/day |
| Dingocoin (dingo) | `https://explorer.dingocoin.com` | No | Not specified |
| Pepecoin (pep) | `https://pepeblocks.com` | No⁵ | Not specified |
| Radiant (rxd) | `https://radiantexplorer.com` | No | Not specified |
| Nervos (ckb) | `https://mainnet-api.explorer.nervos.org` | No⁶ | Not specified |
| Salvium (sal) | `https://explorer.salvium.io` | No | Not specified |
| QRL (qrl) | `https://explorer.theqrl.org` | No⁵ | Not specified |
| Alephium (alph) | `https://backend.mainnet.alephium.org` | No | Not specified |
| Bitcoin SV (bsv) | `https://api.whatsonchain.com/v1/bsv/main` | No³ | Not specified |
| Pirate Chain (arrr) | `https://explorer.pirate.black` | No⁴ ⁵ | Not specified |

¹ Ravencoin uses basic RPC authentication (`rpc_user` / `rpc_password`, default `anonymous`), not an API key.

² *Rate Limit (free)* reflects the **free / free-API-key** mode only (paid tiers are not listed). "Not specified" means the provider publishes no documented free-tier limit.

³ Bitcoin SV exposes difficulty only; network hashrate is derived as `difficulty · 2³² / 600`.

⁴ Pirate Chain exposes difficulty only (Equihash Sol/s hashrate is not published); network hashrate falls back to Hashrate.no. Alephium is the mirror case — hashrate only, difficulty falls back to Hashrate.no.

⁵ Pepecoin, QRL and Pirate Chain require a browser `User-Agent` header (Cloudflare / CDN blocks the default one).

⁶ Nervos requires JSON:API headers (`Accept` / `Content-Type: application/vnd.api+json`).

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
    "binance": {
      "use_api": true,
      "host": "https://api.binance.com"
    },
    "coingecko": {
      "use_api": true,
      "api_key": "YOUR_KEY",
      "host": "https://api.coingecko.com/api/v3"
    }
  },

  "mining": {
    "hashrate_no": {
      "use_api": true,
      "api_key": "YOUR_KEY",
      "host": "https://api.hashrate.no/api/v2"
    },
    "whattomine": {
      "use_api": true,
      "host": "https://whattomine.com"
    },
    "minerstat": {
      "use_api": true,
      "api_key": "YOUR_KEY",
      "host": "https://api.minerstat.com"
    }
  },

  "pool": {
    "2miners": {
      "use_api": true,
      "host": "https://<TAG>.2miners.com/api"
    },
    "nanopool": {
      "use_api": true,
      "host": "https://api.nanopool.org/v1"
    }
  },

  "explorer": {
    "erg": {
      "use_api": true,
      "host": "https://api.ergoplatform.com"
    },
    "kas": {
      "use_api": true,
      "host": "https://api.kaspa.org"
    },
    "rvn": {
      "use_api": true,
      "host": "https://rvn-rpc-mainnet.ting.finance/rpc",
      "rpc_user": "anonymous",
      "rpc_password": "anonymous"
    },
    "xmr": {
      "use_api": true,
      "host": "https://xmrchain.net"
    },
    "cfx": {
      "use_api": true,
      "host": "https://api.confluxscan.io"
    },
    "etc": {
      "use_api": true,
      "host": "https://etc.blockscout.com"
    }
    // ... plus btc, ltc, fb, bch, doge, dash, zec, xec, dingo, pep, rxd,
    //     ckb, sal, qrl, alph, bsv, arrr — see config.json.example for hosts
  },

  "timers": {
    // Refresh interval in seconds for each source (application mode only)
    "market": {
      "binance": 8,
      "coingecko": 20
    },
    "mining": {
      "hashrate_no": 5,
      "whattomine": 10,
      "minerstat": 10
    },
    "pool": {
      "2miners": 5,
      "nanopool": 5
    },
    "explorer": {
      "erg": 5,
      "kas": 5,
      "rvn": 5,
      "xmr": 5,
      "cfx": 5,
      "etc": 5
      // ... one entry per explorer tag. Blockchair coins (bch/doge/dash/zec/xec)
      //     share one endpoint: 375s each = ~80% of the 1,440 req/day free budget.
    }
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
