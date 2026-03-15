# Mining Dashboard

A real-time web visualization interface for the Smart Mining system.
Built with **React** (frontend) and **Express + PostgreSQL** (backend).

---

## Overview

The dashboard connects directly to the Smart Mining PostgreSQL database and exposes a clean, real-time interface to monitor all collected data.
All pages auto-refresh every **30 seconds**.

---

## Pages

| Page | Description |
| :--- | :---------- |
| **Coins** | Current state of all tracked coins (price, difficulty, hashrate, profitability) |
| **Coin History** | Time series charts per coin — price, market cap, difficulty, network hashrate, hash USD, emission USD |
| **Hardware** | Registered hardware and their mining performance per algorithm (hashrate, power, efficiency) |
| **Pools** | Registered pools and their block statistics (height, difficulty, luck, status) |

---

## Architecture

```
┌─────────────────────┐
│  React Frontend      │  :3000
│  - Recharts          │
│  - Auto-refresh 30s  │
└────────┬────────────┘
         │ /api/*  (proxied)
         ↓
┌─────────────────────┐
│  Express Backend     │  :3001
│  - REST API          │
│  - pg client         │
└────────┬────────────┘
         │ SQL queries
         ↓
┌─────────────────────┐
│  PostgreSQL          │  :5432
│  Smart Mining DB     │
└─────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
| :---- | :--------- |
| Frontend | React 18, Vite, Recharts |
| Backend | Node.js, Express, node-postgres (pg) |
| Database | PostgreSQL (shared with Smart Mining) |

---

## Database Tables Used

| Table | Visualization |
| :---- | :------------ |
| `coins` | Table — current state |
| `coin_history` | Line charts over time |
| `hardware` | Table |
| `hardware_mining` | Table (joined with hardware) |
| `pools` | Table |
| `pool_stats` | Table with colored status badges |
