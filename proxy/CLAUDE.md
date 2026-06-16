# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build

**Dependencies:** CMake >= 3.22, clang-15, Boost 1.91.0 (EXACT version required), OpenSSL 1.1.1, GnuTLS, cppcheck

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

Boost is expected at `/usr/local/include` and `/usr/local/lib` (hardcoded in CMakeLists.txt). Static libs, multithreaded. The CMakeLists uses `EXACT` version matching — Boost 1.91.0 is mandatory.

## Testing

```sh
./bin/proxy_test           # run all tests
cd build && ctest          # run via CMake test runner
```

Tests are in `algo/tests/`. The `proxy_unit_test.cpp` entry point calls `RUN_ALL_TESTS()`. GoogleTest is fetched automatically by CMake (v1.15.2).

## Linting

`cppcheck` runs automatically during CMake compilation (configured via `CMAKE_CXX_CPPCHECK`). No separate lint step needed.

## Logging

Use macros from `common/log/log.hpp` — **never use `std::cout` or `printf`**:

```cpp
logInfo()  << "message";
logErr()   << "message";
logWarn()  << "message";
logDebug() << "message";
logTrace() << "message";
```

Log level is set at startup via `setLogLevel(common::TYPELOG::__DEBUG)` in `proxy.cpp`.

## Architecture

This is a **Stratum mining proxy** that switches miners between coins/algorithms based on real-time profitability.

### Data Flow

```
Miners (port 7878) → ServerTCP → SessionManager → Session ↔ ClientTCP → Mining Pool
                                        ↑
                                      Brain (boost::thread)
                                        ↑
                                    Database ← API (localhost:3000, API_KEY: 123456)
                                        ↑
                                   ProfileManager
```

### Threading Model

- **Main thread**: `boost::asio io_context` — all async TCP I/O via Boost.Asio
- **Brain thread**: `boost::thread` polling loop — `PROCESS_SESSION_INTERVAL = 10s` (session switching), `RELOAD_DATABASE_INTERVAL = 2min` (market data fetch)
- `boost::mutex` in `SessionManager` and `Database` guards cross-thread access

### Session Lifecycle

Each miner connection creates a `Session` (in `SessionManager::createSession`). A session holds:
- `MinerData` — the inbound miner stream (`IOStream*`) and its `MinerTable` (list of supported coins/wallets/pools per algorithm)
- `PoolData` — the outbound pool connection (`ClientTCP`, extranonce, worker fullname)
- `currentCoin` (`CoinMiner`) — active coin being mined

When Brain decides to switch coins, it calls `Session::switchCoin(coinTag)` which reconnects the pool side and sends `smart_mining.set_algo` + `smart_mining.set_extra_nonce` to the miner.

### Profitability Selection

`Database` holds six profitability vectors (loaded from API):
- `profileEmission`, `profileHashUsd`, `profileUsdSec`, `profileMarketCap`
- `profileNetworkHashrateGreater`, `profileNetworkHashrateLess`

`Database::getBestCoin(listCoinMiner)` calls `ProfileManager::findBestCoin(MinerTable, profileVector)` for each profile and picks the coin that appears most often (majority vote across profiles). Only coins present in the miner's `MinerTable` are candidates.

### Stratum Protocol Extensions

The proxy extends standard Stratum with three custom methods (defined in `stratum/stratum.hpp`):
- `smart_mining.set_algo` — tells the miner to switch hashing algorithm
- `smart_mining.set_extra_nonce` — sends extranonce after a coin switch
- `smart_mining.set_profile` — miner sends its supported coin list and pool config (triggers `MinerTable` population)

Standard Stratum IDs used: `SUBSCRIBE=1`, `AUTHORIZE=2`, `SUBMIT_MINIMAL=3`.

### Key Types

| Type | File | Purpose |
| :--- | :--- | :--- |
| `algo::ALGORITHM` | `algo/algo_type.hpp` | Enum for all supported algorithms (SHA256, ETHASH, KAWPOW, etc.) |
| `mining::CoinTable` | `mining/coin_table.hpp` | API coin entry (name, tag, algo, usd, difficulty, network hashrate, emission) |
| `mining::CoinMiner` | `mining/coin_miner.hpp` | Per-session coin config (coinTag, hostname, port, wallet, algorithm) |
| `mining::MinerTable` | `mining/miner_table.hpp` | Miner's supported coins + worker credentials |
| `network::IOStream` | `network/stream.hpp` | Boost.Asio TCP/SSL socket wrapper with line-buffered read |
| `profile::ProfileData*` | `profile/data_*.hpp` | Typed profitability data structs (all extend `ProfileDataBase`) |
