# 🧠 Smart Mining

Smart Mining is a modular system designed to automatically optimize cryptocurrency mining profitability by dynamically selecting the most profitable coins, pools, and algorithms in real time.  
The project is based on a distributed architecture, built to be scalable, extensible, and performance‑oriented.  

# 🎯 Project Goals

* 📊 Collect reliable and up‑to‑date market and mining data
* 🧮 Calculate real mining profitability
* 🔄 Perform dynamic switching during mining
* 💰 Maximize USD earnings
* ⚙️ Enable customizable mining strategies through profiles

# 🧩 Architecture Overview

```
┌──────────────────┐
│ External APIs    │
│ - Binance        │
│ - CoinGecko      │
│ - Hashrate.no    │
│ - Minerstat      │
│ - Nanopool       │
│ - 2Miners        │
│ - WhatToMine     │
└────────┬─────────┘
         │ (1) Fetch data
         ↓
┌──────────────────┐
│   AGGREGATOR     │
│  - Collect       │
│  - Normalize     │
│  - Calculate     │
│    profitability │
└────────┬─────────┘
         │ (2) Insert / Update
         ↓
┌──────────────────┐
│   PostgreSQL     │
│  - Realtime data │
│  - History data  │
└────────┬─────────┘
         │ (3) SQL Queries
         ↓
┌──────────────────┐
│       API        │
│  - REST          │
│  - Decision data │
└────────┬─────────┘
         │ (4) Best strategy
         ↓
┌──────────────────┐
│      PROXY       │
│  - Stratum       │
│  - Smart switch  │
└────────┬─────────┘
         │ (5) Redirect mining
         ↓
┌──────────────────┐
│ External Pools   │
│ Pool A / B / C   │
└──────────────────┘
```


# 📦 The 3 Repositories
## 1️⃣ Aggregator
📌 RoleCollect, normalize, and store all data required for Smart Mining.  
  
🛠️ Technology  
- Python  
  
🔌 External APIs Used:
* Binance
* CoinGecko
* Hashrate.no
* Minerstat
* Nanopool
* 2Miners
* WhatToMine

## 📥 Features

* Data collection:
  * Coin prices
  * Network difficulty
  * Hashrates
  * Mining pools
  * Hardware performance
* Profitability calculation
* Real‑time data insertion
* Historical data storage

## ⏱️ Execution
* Automatic
* Runs every X seconds
* Ensures data is always up to date

# 2️⃣ API
📌 RoleExpose data and act as the decision layer for the proxy.  
  
## 🛠️ Technology  
- Node.js

## 🔌 Features
* REST endpoints
* Access to real‑time and historical data
* Additional calculations
* Optimized JSON responses

## 📍 Position in the architecture
* Single interface between:
* PostgreSQL
* Proxy

# 3️⃣ Proxy
📌 RoleImplement real‑time Smart Mining logic.
## 🛠️ Technology
- C++ 20
- Boost 1.86

## ⚡ Features
* TCP server
* Stratum protocol implementation
* Miner (mining software) connections
* Support for:
  * Multiple pools
  * Multiple coins
  * Multiple algorithms
* Dynamic switching based on profitability

## 🎯 Objective
Continuously optimize mining yield and USD earnings.

# 🔄 Global Workflow
## Aggregator
Fetches external data  
Updates real‑time tables  
Archives historical data  

## API
Exposes data via REST  
Acts as the decision engine  

## Proxy
Queries the API  
Manages connected miners  
Applies Smart Mining strategies  

# 🧠 Profile Concept
A profile represents a user mining strategy.

## 🔑 Principle
* Each miner selects a profile upon connection
* The proxy adapts its behavior based on this profile

## 📋 Profile Examples
* 💰 Mine the coin generating the highest USD
* ⚡ Follow the most profitable hashrate in USD

## ⚙️ Characteristics
* Multiple profiles available
* Fully customizable
* Easily extensible

# 🗄️ Database (PostgreSQL)
## 📌 Main Tables
| Table           | Description                      |
| :-------------- | :------------------------------- |
| coins           | Coin information at time T       |
| coin_history    | Historical coin data             |
| pools           | Pool information at time T       |
| pool_history    | Historical pool data             |
| hardware        | Hardware information (GPU / CPU) |
| hardware_mining | Mining performance per hardware  |


## 🔍 Details
* Realtime data
  * coins
  * pools
* Historical data
  * coin_history
  * pool_history
* Hardware data
  * hardware: hardware specifications
  * hardware_mining: hashrate, power usage, algorithms

# 🐳 Docker
## 📀 Database
```bash
docker build -t smart_mining_database .
docker run -d \
  -p 5432:5432 \
  --name smart_mining_database \
  --network smart_mining_network \
  smart_mining_database
```

## 🌐 API
```bash
docker build -t smart_mining_api .
docker run -d \
  -p 3000:3000 \
  --name smart_mining_api \
  --network smart_mining_network \
  smart_mining_api
```

## 🔁 Aggregator
```bash
docker build -t smart_mining_aggregator .
docker run -d \
  --name smart_mining_aggregator \
  --network smart_mining_network \
  smart_mining_aggregator
```


# ✅ Summary
The Aggregator collects and stores historical data.
The API exposes the data and makes decisions.
The Proxy applies Smart Mining strategies based on user profiles, to automatically optimize mining profitability.
