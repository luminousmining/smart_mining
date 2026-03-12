# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build

**Dependencies:** CMake >= 3.22, clang-15, Boost 1.86.0, OpenSSL 1.1.1, GnuTLS, cppcheck

Install system dependencies:
```sh
sudo apt install -y build-essential libstdc++-12-dev gnutls-dev cppcheck checkinstall clang-15 libx11-dev
```

Build:
```sh
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release
```

Debug build:
```sh
cmake .. -DCMAKE_BUILD_TYPE=Debug
cmake --build . --config Debug
```

Outputs: `bin/proxy` (main executable), `bin/proxy_test` (unit tests).

## Testing

```sh
./bin/proxy_test          # run all unit tests
cd build && ctest         # run via CMake test runner
```

## Linting

`cppcheck` runs automatically during CMake compilation (configured via `CMAKE_CXX_CPPCHECK`). No separate lint step needed.

## Architecture

This is a **Stratum mining proxy** that intelligently switches miners between coins/algorithms based on real-time profitability data.

### Data Flow

```
Miners (port 7878) → ServerTCP → SessionManager → Session ↔ ClientTCP → Mining Pool
                                        ↑
                                      Brain (background thread)
                                        ↑
                                    Database ← API (localhost:3000)
                                        ↑
                                   ProfileManager
```

### Core Components

- **`network/server`** — TCP server; accepts miner connections on port 7878
- **`network/session/session`** — Bidirectional proxy session between one miner and its pool; handles Stratum message routing and coin switching
- **`network/session/session_manager`** — Registry of all active sessions
- **`network/client_tcp`** — Outbound TCP connection to a mining pool
- **`mining/brain`** — Background thread: reloads market data every 2 minutes, processes sessions every 10 seconds to switch to better coins
- **`mining/database`** — Holds coin/algorithm profitability table loaded from the API
- **`mining/api`** — HTTP client that fetches profitability JSON from `localhost:3000` (API_KEY: `123456`)
- **`profile/profile_manager`** — Analyzes market data profiles (emission, hash/USD, market cap, network hashrate) to select the best coin
- **`algo/algo_type`** — Algorithm enum (`AlgoType`) and string/enum conversion utilities
- **`stratum/stratum.hpp`** — Stratum protocol JSON field names and custom `smart_mining` extensions (`set_algo`, `set_extra_nonce`, `set_profile`)

### Threading Model

- **Main thread**: `boost::asio io_context.run()` — handles all async TCP I/O
- **Brain thread**: periodic timer-driven background work (coin profitability reload + session processing)

### Key Data Structures

- `mining/coin_table.hpp` — Per-coin profitability entry
- `mining/miner_table.hpp` — Miner hardware capabilities
- `network/session/miner_data.hpp` — Per-session miner state
- `network/session/pool_data.hpp` — Per-session pool connection state
- `profile/data_*.hpp` — Typed profitability profile data (emission, hash_usd, market_cap, network_hashrate)

### Logging

Use macros from `common/log/log.hpp`: `logInfo(...)`, `logErr(...)`, `logWarn(...)`, `logDebug(...)`. These are the only logging mechanism in the project.
