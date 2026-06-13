# Missing / Recommended APIs

## Already Implemented

| API | Purpose |
|-----|---------|
| Binance | Coin prices (exchange) |
| CoinGecko | Coin list + market data |
| Hashrate.no | Mining profitability, coin hashrate |
| WhatToMine | Mining profitability |
| MinerStat | Coins, GPU hardware, pools |
| 2Miners | Pool stats (blocks, hashrate, miners) |
| Nanopool | Pool stats (blocks, earnings, price) |

---

## Recommended APIs to Add

### Priority 1 — Coin Price & Hashrate

#### [CryptoCompare](https://www.cryptocompare.com/api#)
- **Auth**: None (generous free tier)
- **HTTPS**: Yes
- **Interest**: Provides **network hashrate** for minable coins, multi-exchange price, and mining data (block time, block reward, difficulty). Directly relevant to mining. Probably the best source for network hashrate of alternative coins.
- **Useful endpoints**:
  - `GET /data/blockchain/latest?fsym={COIN}` — network hashrate, difficulty, block time
  - `GET /data/price?fsym={COIN}&tsyms=USD` — simple price
  - `GET /data/pricemulti?fsyms={LIST}&tsyms=USD` — batch price

#### [CoinMarketCap](https://coinmarketcap.com/api/)
- **Auth**: apiKey (free tier available)
- **HTTPS**: Yes
- **Interest**: Industry reference for prices. Also provides volume, market cap, and useful metrics for filtering/ranking coins. Good complement to Binance for coins not listed on Binance.
- **Useful endpoints**:
  - `GET /v1/cryptocurrency/listings/latest` — full list with prices
  - `GET /v2/cryptocurrency/quotes/latest?symbol={LIST}` — batch price

#### [Coinpaprika](https://api.coinpaprika.com)
- **Auth**: None
- **HTTPS**: Yes
- **Interest**: Free without API key, provides price, volume, and info on minable coins (algorithm, network hashrate). Good fallback if CoinGecko or CoinMarketCap are unavailable.
- **Useful endpoints**:
  - `GET /v1/coins` — coin list with algorithm
  - `GET /v1/tickers` — price and volume for all coins

---

### Priority 2 — Pool Mining

#### [NiceHash](https://docs.nicehash.com/)
- **Auth**: apiKey
- **HTTPS**: Yes
- **Interest**: Largest hashrate marketplace. Provides **hashrate price per algorithm** (very useful for estimating profitability), as well as NiceHash pool stats. Unique data not available elsewhere.
- **Useful endpoints**:
  - `GET /api/v2/mining/algorithms` — hashrate price per algorithm
  - `GET /api/v2/public/stats/global/current` — global stats per algo

#### [Flexpool](https://flexpool.io/docs/api/)
- **Auth**: None
- **HTTPS**: Yes
- **Note**: Not listed in public-api-lists but highly relevant
- **Interest**: Multi-coin pool (ETH, ETC, ZIL, etc.). Public API providing luck, pool hashrate, recent blocks.
- **Useful endpoints**:
  - `GET /api/v2/pool/stats` — total pool hashrate, miners
  - `GET /api/v2/pool/blocks` — recent blocks with luck

#### [Hiveon Pool](https://hiveon.com/api/)
- **Auth**: None
- **HTTPS**: Yes
- **Note**: Not listed in public-api-lists but highly relevant
- **Interest**: Large ETH/ETC pool. Provides pool hashrate, luck, and block statistics.

#### [F2Pool](https://www.f2pool.com/api)
- **Auth**: None for public data
- **HTTPS**: Yes
- **Note**: Not listed in public-api-lists but highly relevant
- **Interest**: One of the largest multi-coin pools. Hashrate and block data publicly available per coin.
- **Useful endpoints**:
  - `GET /api/{coin}/stats` — hashrate, miners, latest blocks

---

### Priority 3 — Supplementary Data

#### [CoinAPI](https://docs.coinapi.io/)
- **Auth**: apiKey (limited free tier)
- **HTTPS**: Yes
- **Interest**: Aggregates price data from all exchanges under a single API. Useful for getting prices from exchanges not supported by Binance (Kraken, Bitfinex, etc.).

#### [Gate.io](https://www.gate.io/api2)
- **Auth**: None for public data
- **HTTPS**: Yes
- **Interest**: Exchange listing many alternative minable coins absent from Binance. Good complement for niche coin prices.
- **Useful endpoints**:
  - `GET /api2/1/pairs` — list of pairs
  - `GET /api2/1/ticker/{pair}` — price of a pair

---

## Needs Summary

| Need | Already covered by | To add |
|------|--------------------|--------|
| Coin price | Binance, CoinGecko | CryptoCompare, CoinMarketCap (coins not listed on Binance) |
| Coin network hashrate | Hashrate.no, WhatToMine, MinerStat | **CryptoCompare** (direct network hashrate, free) |
| Pool luck | 2Miners, Nanopool | **Flexpool**, **Hiveon**, **F2Pool** |
| Pool hashrate | 2Miners, Nanopool, MinerStat | **NiceHash** (hashrate per algo), **Flexpool**, **F2Pool** |
| Pool blocks | 2Miners, Nanopool | **Flexpool**, **F2Pool** |
