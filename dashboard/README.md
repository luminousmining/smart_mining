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
│  React Frontend     │  :3000
│  - Recharts         │
│  - Auto-refresh 30s │
└────────┬────────────┘
         │ /api/*  (proxied)
         ↓
┌─────────────────────┐
│  Express Backend    │  :3001
│  - REST API         │
│  - pg client        │
└────────┬────────────┘
         │ SQL queries
         ↓
┌─────────────────────┐
│  PostgreSQL         │  :5432
│  Smart Mining DB    │
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

---

## INSTALL — Deploy on VPS (NGINX + PM2)

### 1. Prerequisites on the server

```bash
# Node.js >= 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# PM2 — process manager to keep the backend alive
sudo npm install -g pm2
```

---

### 2. Backend

```bash
cd backend
npm install
cp .env.example .env
nano .env        # fill in your PostgreSQL credentials
```

Start with PM2 and persist across reboots:

```bash
pm2 start server.js --name mining-dashboard-backend
pm2 save
pm2 startup      # run the printed command to enable autostart
```

The API will run on `http://localhost:3001` (local only, exposed through NGINX).

---

### 3. Frontend — Production build

```bash
cd frontend
npm install
npm run build
```

Static files are output to `frontend/dist/`.

---

### 4. NGINX configuration

Create `/etc/nginx/sites-available/mining-dashboard`:

```nginx
server {
    listen 8080;
    listen [::]:8080;

    root <FULLPATH_FRONTEND>/dist;
    index index.html;

    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/html text/css application/javascript application/json image/svg+xml;

    # Proxy API calls to the Express backend
    location /api/ {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # SPA fallback — all other routes serve index.html
    location / {
        try_files $uri /index.html;
    }
}
```

Enable and reload:

```bash
sudo ln -s /etc/nginx/sites-available/mining-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

The dashboard is now accessible at `http://<VPS_IP>:8080`.

---

### 5. Updates

To redeploy after changes:

```bash
npm run build                        # rebuild frontend
pm2 restart mining-dashboard-backend # restart backend if changed
```

---

### PM2 useful commands

```bash
pm2 status                           # check backend status
pm2 logs mining-dashboard-backend    # view live logs
pm2 restart mining-dashboard-backend
```
