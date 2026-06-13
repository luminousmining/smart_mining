# Data Qualification

This document explains how the aggregator collects data from multiple external sources, why each source is queried, and how the data is merged and qualified to produce a dataset that the proxy can act on.

---

## 1. The problem: fragmented data

No single external source provides all the information needed to calculate a coin's mining profitability.
Each service only has access to part of the picture:

- Hashrate.no knows the daily emission but not the market cap
- WhatToMine knows the market cap but approximates the emission
- Binance knows the real-time spot price but nothing about the blockchain
- Blockchain explorers know the actual network hashrate but nothing about the price

The system solves this by **accumulating contributions** from each source into a single data model, then computing the final metrics once all data has been consolidated.

---

## 2. Data sources and their precise role

### 2.1 Coin sources

| Source | Data provided | Why this source |
| :--- | :--- | :--- |
| **Hashrate.no** | name, ticker, algorithm, network hashrate, difficulty, daily emission (coin and USD), price | Primary source — the only one that directly provides total USD emitted in 24h without intermediate calculation |
| **WhatToMine** | difficulty, network hashrate, market cap, calculated emission | The most consistently up-to-date source for market cap. Also calculates emission from block reward and block time |
| **MinerStat** | price, network hashrate, difficulty, market cap (via volume) | Update source: replaces existing values with more recent data |
| **Binance** | spot price | Real-time price, the most reliable price source for listed coins |
| **CoinGecko** | (future enrichment) | Price fallback for coins not listed on Binance |

### 2.2 Pool sources

| Source | Data provided | Why this source |
| :--- | :--- | :--- |
| **2Miners** | found blocks (height, timestamp, difficulty, luck, status), miner count, hashrate per coin | Operational source: real mining activity, found blocks, connected miners |
| **Nanopool** | average block time, last block number, block stats | Block timing statistics *(integration in progress)* |
| **MinerStat (pool)** | algorithm, fees, anonymity, registration required | Pool metadata: fees charged, access conditions |

### 2.3 Blockchain explorer sources

Explorers are the **on-chain sources of truth**.
They replace third-party estimates with values measured directly on the blockchain.

| Coin | Extracted data |
| :--- | :--- |
| Ergo (ERG) | network hashrate, difficulty, block height |
| Kaspa (KAS) | network hashrate, difficulty, DAA score |
| Ravencoin (RVN) | network hashrate, difficulty, block height |
| Monero (XMR) | network hashrate, difficulty, block height |
| Conflux (CFX) | network hashrate, difficulty |
| Ethereum Classic (ETC) | network hashrate, difficulty, total block count |

---

## 3. Merge strategy

### 3.1 Independent sources, continuous collection

In production, each data source operates **autonomously and independently**: it queries its APIs at its own refresh frequency, without waiting for the others.
There is no fixed order between sources — each one contributes as soon as it has new data available.

Continuous collection:
```
│
├── Hashrate.no   → every N seconds ┐
├── WhatToMine    → every N seconds │  Coin sources — each runs at its own pace,
├── MinerStat     → every N seconds │  no guaranteed order between them.
├── Binance       → every N seconds │  The first to encounter a coin creates it,
├── CoinGecko     → every N seconds │  the following ones complete or update it
├── Explorers     → every N seconds ┘  according to their role.
│
├── 2Miners       → every N seconds ┐
├── Nanopool      → every N seconds │  Pool sources — data merged on every update.
├── MinerStat     → every N seconds ┘
│
└── Qualification → every N seconds → metrics calculation + filtering of incomplete coins
    Pools         → every N seconds → pool data consolidation
    Database      → every N seconds → persistence
```

No source has a fixed role.
It is solely each source's refresh frequency that determines which one reaches a coin first.
What is guaranteed is that incoming data is always integrated consistently: if the coin is unknown, it is created; if it already exists, the new data is merged without overwriting what is already reliable.

### 3.2 Two merge modes

Each source can contribute in two different ways depending on the nature of its data.

**Enrichment — filling in what is missing**

The new data only applies if the field is still empty.
A value already present will never be overwritten by this source.
This is the default behavior: the first source to fill a field retains ownership of it.

**Update — replacing with a more recent value**

The new data systematically replaces the existing value.
This is the behavior of sources considered more reliable or fresher, such as blockchain explorers that measure the network in real time.

**Example coin lifecycle (progressive convergence):**

| Time | Source | Result |
| :--- | :--- | :--- |
| T+0s | Hashrate.no | Coin created with daily emission, network hashrate, price |
| T+5s | WhatToMine | Market cap added |
| T+8s | Binance | Spot price updated in real time |
| T+10s | MinerStat | Price and network hashrate updated |
| T+10s | Explorer | Network hashrate replaced by on-chain value |
| T+30s | Qualification | Hashrate profitability and revenue per second calculated on consolidated values |

### 3.3 No duplicate entries

The system recognizes the same coin regardless of how a source names it.
If one source calls it "ethereum-classic" and another "etc", they are recognized as the same coin and merged into a single entry.
No duplicate can exist in the final dataset.

---

## 4. Coin qualification

This is the core of the system.
Once data has been collected and merged, two key metrics are calculated, then coins that are too incomplete are discarded.

### 4.1 Trigger

Qualification runs on its own cycle, independently of data collection.
It works on the data available **at the moment it is triggered** — all sources that have already collected at least once have contributed.

### 4.2 Profitability metrics calculation

Two metrics are computed entirely by the system — they are not provided by any external source.

---

#### Metric 1: Network revenue per second

```
revenue_per_second = daily_emission_USD / 86400
```

The daily emission represents the total mining rewards distributed by the entire network over 24 hours, expressed in USD.
It is the mass of money injected into the network each day.

**Why divide by second?**
Comparing the daily emission directly between two coins would be misleading if their blocks have very different frequencies.
Kaspa produces roughly 1 block per second, Bitcoin 1 block every 10 minutes — their emission pace is not comparable at the "24h" scale.
Bringing this revenue down to the second allows any coin to be compared on a uniform time basis.

**Precondition:** if the daily emission is zero or absent, this metric cannot be calculated and the coin will be eliminated in the next step.

---

#### Metric 2: Profitability per unit of hashrate (`hash_usd`)

```
hash_usd = daily_emission_USD / network_hashrate
```

This is **the central metric of the entire system**.
It answers the miner's fundamental question: *"For each unit of computing power I contribute to the network, how much do I earn?"*

The network hashrate is the sum of the computing power of all connected miners.
The higher it is, the stronger the competition and the smaller each miner's share.

**Concrete example:**
- Coin A: $100,000/day emission, 1,000,000 GH/s network hashrate → **$0.10/GH**
- Coin B: $50,000/day emission, 200,000 GH/s network hashrate → **$0.25/GH**

Even though Coin A generates more absolute revenue, Coin B is 2.5× more profitable for a fixed-size miner.
A miner with 10 GH/s would earn $1/day on A and $2.50/day on B.

**Usage in the proxy:** this is the value read in real time to decide which coin to redirect miners to.
The coin with the highest `hash_usd` for the current algorithm wins the decision.

**Why calculate here and not in the sources?**
Because no single source holds both ingredients at once.
The daily emission may come from Hashrate.no, but the network hashrate is preferably replaced by the value measured directly on-chain.
This calculation is only possible after both values have been fully consolidated.

### 4.3 Filtering — eliminating incomplete coins

After metrics are calculated, coins that do not meet the minimum criteria are **permanently discarded** from the dataset.
They will neither be exported nor sent to the database.

---

**Criterion 1: daily emission is zero or absent**

- The coin generates no measurable revenue over 24h
- Possible causes: data missing from all sources, inactive or stopped coin, coin too recent to be indexed
- Consequence: hashrate profitability would be zero or incalculable — unusable for decision-making

---

**Criterion 2: market cap is absent**

- The coin has no verifiable market capitalization
- Possible causes: coin too small to be referenced on tracking platforms, data missing from all sources
- Consequence: without a market cap, it is impossible to assess liquidity. A miner who mines an illiquid coin risks being unable to sell their reward at the displayed price — the calculated profitability would be fictitious

---

Discarded coins are recorded in the logs to allow diagnosis: which source failed, which fields are missing.

### 4.4 Active algorithm list

After filtering, the system compiles the list of all mining algorithms represented by qualified coins.
This list is exported alongside the coins and allows the proxy to instantly know which algorithms are available without scanning all the data.

---

## 5. Pool qualification — merge and block lifecycle

Unlike coins, there is no explicit filtering on pools: all accepted data passes through to export.
Qualification operates solely through merge logic, which guarantees dataset consistency.

### 5.1 Pool coin deduplication

When multiple collection runs bring data on the same coin from the same pool, they are merged into a single entry.
For example, the hashrate (from the stats endpoint) and the miner count (from another endpoint) are combined automatically.

### 5.2 Block deduplication

A block is uniquely identified by its coin and its height.
If the same block arrives multiple times (through different collection runs), it is updated rather than duplicated.

### 5.3 Block lifecycle

A block goes through three states from discovery to confirmation:

```
CANDIDATE  →  IMMATURE  →  MATURED
    ↑              ↑            ↑
 Found by      Waiting for  Confirmed
 the pool      confirmation definitively
```

A confirmed block (MATURED) is **immutable** — it can never be modified again.
This protects against late updates or duplicates that would attempt to downgrade an already confirmed block.

---

## 6. Export

Once qualification is complete, data is written to its output files:

| Data | Output file | Content |
| :--- | :--- | :--- |
| Qualified coins | `dataset/coin_manager/data.json` | Active algorithms + coins with all their profitability metrics |
| Pools | `dataset/pool_manager/data.json` | Pools with their active coins and block history |
| Hardware | `dataset/hardware_manager/data.json` | GPUs with their performance per algorithm |

The export reflects the qualified and consolidated state of all sources.
