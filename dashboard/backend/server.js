require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { Pool } = require('pg');

const app = express();
app.use(cors());
app.use(express.json());

const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT) || 5432,
  database: process.env.DB_NAME || 'mining',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || '',
});

const INTERVALS = {
  '1h':  "now() - interval '1 hour'",
  '24h': "now() - interval '24 hours'",
  '7d':  "now() - interval '7 days'",
  '30d': "now() - interval '30 days'",
  'all': null,
};

// ── Coins ─────────────────────────────────────────────────────────────────────

app.get('/api/coins', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM coins ORDER BY usd DESC NULLS LAST');
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/api/coin-names', async (req, res) => {
  try {
    const result = await pool.query(
      'SELECT DISTINCT name, tag FROM coin_history ORDER BY name'
    );
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/api/coin-history', async (req, res) => {
  try {
    const { name, range = '24h' } = req.query;
    const interval = INTERVALS[range] ?? INTERVALS['24h'];

    let query = `
      SELECT name, tag, usd, difficulty, network_hashrate, hash_usd,
             emission_usd, market_cap, created_at
      FROM coin_history
    `;
    const params = [];

    if (name) {
      query += ' WHERE name = $1';
      params.push(name);
      if (interval) query += ` AND created_at >= ${interval}`;
    } else if (interval) {
      query += ` WHERE created_at >= ${interval}`;
    }

    query += ' ORDER BY created_at ASC';
    const result = await pool.query(query, params);
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Multi-coin history for comparison view
app.get('/api/coin-history-multi', async (req, res) => {
  try {
    const { names, range = '24h' } = req.query;
    if (!names) return res.json([]);

    const nameList = names.split(',').map(n => n.trim()).filter(Boolean);
    if (!nameList.length) return res.json([]);

    const interval = INTERVALS[range] ?? INTERVALS['24h'];
    const placeholders = nameList.map((_, i) => `$${i + 1}`).join(', ');

    let query = `
      SELECT name, tag, usd, difficulty, network_hashrate, hash_usd,
             emission_usd, market_cap, created_at
      FROM coin_history
      WHERE name IN (${placeholders})
    `;
    if (interval) query += ` AND created_at >= ${interval}`;
    query += ' ORDER BY created_at ASC';

    const result = await pool.query(query, nameList);
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ── Hardware ──────────────────────────────────────────────────────────────────

app.get('/api/hardware', async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT h.id, h.name AS hardware, hm.algo, hm.hashrate, hm.power
      FROM hardware h
      LEFT JOIN hardware_mining hm ON h.id = hm.hardware_id
      ORDER BY h.name, hm.algo
    `);
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ── Pools ─────────────────────────────────────────────────────────────────────

app.get('/api/pools', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM pools ORDER BY name, tag');
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/api/pool-stats', async (req, res) => {
  try {
    const { tag } = req.query;
    let query = 'SELECT * FROM pool_stats';
    const params = [];
    if (tag) { query += ' WHERE tag = $1'; params.push(tag); }
    query += ' ORDER BY name, tag, block_height DESC';
    const result = await pool.query(query, params);
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Distinct pool names (optionally filtered by tag)
app.get('/api/pool-names', async (req, res) => {
  try {
    const { tag } = req.query;
    let query = 'SELECT DISTINCT name FROM pool_stats';
    const params = [];
    if (tag) { query += ' WHERE tag = $1'; params.push(tag); }
    query += ' ORDER BY name';
    const result = await pool.query(query, params);
    res.json(result.rows.map(r => r.name));
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Pool history: stats for a single pool ordered by mine_timestamp
app.get('/api/pool-history', async (req, res) => {
  try {
    const { name, tag } = req.query;
    if (!name) return res.json([]);
    const params = [name];
    let query = 'SELECT * FROM pool_stats WHERE name = $1';
    if (tag) { query += ' AND tag = $2'; params.push(tag); }
    query += ' ORDER BY mine_timestamp ASC';
    const result = await pool.query(query, params);
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Distinct tags available in pool_stats (for filters)
app.get('/api/pool-tags', async (req, res) => {
  try {
    const result = await pool.query(
      'SELECT DISTINCT tag FROM pool_stats ORDER BY tag'
    );
    res.json(result.rows.map(r => r.tag));
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ─────────────────────────────────────────────────────────────────────────────

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => console.log(`Backend running on http://localhost:${PORT}`));
