# Missing / Recommended APIs

## Already Implemented

| API | Purpose |
|-----|---------|
| Binance | Prix des coins (exchange) |
| CoinGecko | Liste des coins + market data |
| Hashrate.no | Profitabilité minière, hashrate des coins |
| WhatToMine | Profitabilité minière |
| MinerStat | Coins, hardware GPU, pools |
| 2Miners | Stats pool (blocs, hashrate, miners) |
| Nanopool | Stats pool (blocs, earnings, prix) |

---

## APIs Recommandées à Ajouter

### Priorité 1 — Prix & Hashrate des coins

#### [CryptoCompare](https://www.cryptocompare.com/api#)
- **Auth**: Aucune (tier gratuit généreux)
- **HTTPS**: Oui
- **Intérêt**: Fournit le **hashrate réseau** des coins minables, le prix multi-exchange, et des données de mining (block time, block reward, difficulty). Directement pertinent pour le mining. Probablement la meilleure source pour le hashrate réseau de coins alternatifs.
- **Endpoints utiles**:
  - `GET /data/blockchain/latest?fsym={COIN}` — hashrate réseau, difficulté, block time
  - `GET /data/price?fsym={COIN}&tsyms=USD` — prix simple
  - `GET /data/pricemulti?fsyms={LIST}&tsyms=USD` — prix en batch

#### [CoinMarketCap](https://coinmarketcap.com/api/)
- **Auth**: apiKey (tier gratuit disponible)
- **HTTPS**: Oui
- **Intérêt**: Référence industrie pour les prix. Fournit aussi le volume, le market cap, et des métriques utiles pour filtrer/ranger les coins. Bon complément à Binance pour les coins non listés sur Binance.
- **Endpoints utiles**:
  - `GET /v1/cryptocurrency/listings/latest` — liste complète avec prix
  - `GET /v2/cryptocurrency/quotes/latest?symbol={LIST}` — prix en batch

#### [Coinpaprika](https://api.coinpaprika.com)
- **Auth**: Aucune
- **HTTPS**: Oui
- **Intérêt**: Gratuit sans clé API, fournit prix, volume, et des infos sur les coins minables (algorithme, hashrate réseau). Bon fallback si CoinGecko ou CoinMarketCap sont indisponibles.
- **Endpoints utiles**:
  - `GET /v1/coins` — liste des coins avec algorithme
  - `GET /v1/tickers` — prix et volume de tous les coins

---

### Priorité 2 — Pool Mining

#### [NiceHash](https://docs.nicehash.com/)
- **Auth**: apiKey
- **HTTPS**: Oui
- **Intérêt**: Plus grand marketplace de hashrate. Fournit le **prix du hashrate par algorithme** (très utile pour estimer la profitabilité), ainsi que les stats de pool NiceHash. Données uniques non disponibles ailleurs.
- **Endpoints utiles**:
  - `GET /api/v2/mining/algorithms` — prix du hashrate par algorithme
  - `GET /api/v2/public/stats/global/current` — stats globales par algo

#### [Flexpool](https://flexpool.io/docs/api/)
- **Auth**: Aucune
- **HTTPS**: Oui
- **Note**: Non listé dans public-api-lists mais très pertinent
- **Intérêt**: Pool multi-coins (ETH, ETC, ZIL, etc.). API publique fournissant luck, hashrate du pool, blocs récents.
- **Endpoints utiles**:
  - `GET /api/v2/pool/stats` — hashrate total du pool, miners
  - `GET /api/v2/pool/blocks` — blocs récents avec luck

#### [Hiveon Pool](https://hiveon.com/api/)
- **Auth**: Aucune
- **HTTPS**: Oui
- **Note**: Non listé dans public-api-lists mais très pertinent
- **Intérêt**: Grand pool ETH/ETC. Fournit hashrate du pool, luck, et statistiques de blocs.

#### [F2Pool](https://www.f2pool.com/api)
- **Auth**: Aucune pour les données publiques
- **HTTPS**: Oui
- **Note**: Non listé dans public-api-lists mais très pertinent
- **Intérêt**: Un des plus grands pools multi-coins. Données de hashrate et blocs disponibles publiquement par coin.
- **Endpoints utiles**:
  - `GET /api/{coin}/stats` — hashrate, miners, derniers blocs

---

### Priorité 3 — Données complémentaires

#### [CoinAPI](https://docs.coinapi.io/)
- **Auth**: apiKey (tier gratuit limité)
- **HTTPS**: Oui
- **Intérêt**: Agrège les données de prix de tous les exchanges sous une seule API. Utile pour avoir des prix sur des exchanges non supportés par Binance (Kraken, Bitfinex, etc.).

#### [Gates.io](https://www.gate.io/api2)
- **Auth**: Aucune pour les données publiques
- **HTTPS**: Oui
- **Intérêt**: Exchange listant beaucoup de coins alternatifs minables absents de Binance. Bon complément pour les prix de coins de niche.
- **Endpoints utiles**:
  - `GET /api2/1/pairs` — liste des paires
  - `GET /api2/1/ticker/{pair}` — prix d'une paire

---

## Récapitulatif des besoins

| Besoin | Déjà couvert par | À ajouter |
|--------|-----------------|-----------|
| Prix coin | Binance, CoinGecko | CryptoCompare, CoinMarketCap (coins non listés sur Binance) |
| Hashrate réseau coin | Hashrate.no, WhatToMine, MinerStat | **CryptoCompare** (hashrate réseau direct et gratuit) |
| Pool luck | 2Miners, Nanopool | **Flexpool**, **Hiveon**, **F2Pool** |
| Pool hashrate | 2Miners, Nanopool, MinerStat | **NiceHash** (hashrate par algo), **Flexpool**, **F2Pool** |
| Pool blocs | 2Miners, Nanopool | **Flexpool**, **F2Pool** |
