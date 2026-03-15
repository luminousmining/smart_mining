# Installation & Setup

## Prerequisites

- **Node.js** >= 18
- **npm** >= 9
- A running **PostgreSQL** instance with the Smart Mining database initialized

---

## 1. Backend

```bash
cd dashboard/backend
```

Install dependencies:

```bash
npm install
```

Create the environment file from the example:

```bash
cp .env.example .env
```

Edit `.env` with your database credentials:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=smart_mining
DB_USER=luminousminer
DB_PASSWORD=password
PORT=3001
```

Start the backend:

```bash
npm start
# or with auto-reload during development:
npm run dev
```

The API will be available at `http://localhost:3001`.

---

## 2. Frontend

```bash
cd dashboard/frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The dashboard will be available at `http://localhost:3000`.

> The Vite dev server automatically proxies all `/api/*` requests to `http://localhost:3001`, so no additional configuration is needed.

---

## 3. Production Build

To build the frontend for production:

```bash
cd dashboard/frontend
npm run build
```

The output will be in `dashboard/frontend/dist/`.
You can then serve it with any static file server, or configure Express to serve it directly.

---

## Running Both Simultaneously

Open two terminals:

**Terminal 1 — Backend:**
```bash
cd dashboard/backend && npm start
```

**Terminal 2 — Frontend:**
```bash
cd dashboard/frontend && npm run dev
```

Then open `http://localhost:3000` in your browser.
