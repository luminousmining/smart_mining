require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { exec } = require('child_process');
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

// ── Coins ─────────────────────────────────────────────────────────────────────

app.get('/api/coins', async (_req, res) => {
  try {
    const result = await pool.query('SELECT * FROM coins ORDER BY usd DESC NULLS LAST');
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/api/coin-names', async (_req, res) => {
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
    const { name, from, to } = req.query;
    const params = [];
    const conditions = [];

    if (name) { params.push(name); conditions.push(`name = $${params.length}`); }
    if (from) { params.push(from); conditions.push(`created_at >= $${params.length}::date`); }
    if (to)   { params.push(to);   conditions.push(`created_at < ($${params.length}::date + interval '1 day')`); }

    let query = `SELECT name, tag, usd, difficulty, network_hashrate, hash_usd, emission_usd, market_cap, created_at FROM coin_history`;
    if (conditions.length) query += ' WHERE ' + conditions.join(' AND ');
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
    const { names, from, to } = req.query;
    if (!names) return res.json([]);

    const nameList = names.split(',').map(n => n.trim()).filter(Boolean);
    if (!nameList.length) return res.json([]);

    const params = [...nameList];
    const placeholders = nameList.map((_, i) => `$${i + 1}`).join(', ');
    const conditions = [`name IN (${placeholders})`];

    if (from) { params.push(from); conditions.push(`created_at >= $${params.length}::date`); }
    if (to)   { params.push(to);   conditions.push(`created_at < ($${params.length}::date + interval '1 day')`); }

    const query = `SELECT name, tag, usd, difficulty, network_hashrate, hash_usd, emission_usd, market_cap, created_at FROM coin_history WHERE ${conditions.join(' AND ')} ORDER BY created_at ASC`;
    const result = await pool.query(query, params);
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ── Hardware ──────────────────────────────────────────────────────────────────

app.get('/api/hardware', async (_req, res) => {
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

app.get('/api/pools', async (_req, res) => {
  try {
    const result = await pool.query('SELECT * FROM pools ORDER BY name, tag');
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/api/pool-stats', async (req, res) => {
  try {
    const { tag, limit } = req.query;
    const maxRows = Math.min(parseInt(limit) || 200, 2000);
    const params = [];
    const where = tag ? (params.push(tag), 'WHERE tag = $1') : '';
    const query = `
      SELECT DISTINCT ON (name, tag, block_height) *
      FROM pool_stats
      ${where}
      ORDER BY name, tag, block_height DESC,
        CASE LOWER(block_status)
          WHEN 'matured'   THEN 3
          WHEN 'immature'  THEN 2
          WHEN 'candidate' THEN 1
          ELSE 0
        END DESC
      LIMIT ${maxRows}
    `;
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
    const { name, tag, from, to } = req.query;
    if (!name) return res.json([]);

    const params = [name];
    const conditions = ['name = $1'];
    if (tag)  { params.push(tag);  conditions.push(`tag = $${params.length}`); }
    if (from) { params.push(from); conditions.push(`mine_timestamp >= EXTRACT(EPOCH FROM $${params.length}::date)::bigint`); }
    if (to)   { params.push(to);   conditions.push(`mine_timestamp < (EXTRACT(EPOCH FROM ($${params.length}::date + interval '1 day'))::bigint)`); }

    const query = `SELECT * FROM pool_stats WHERE ${conditions.join(' AND ')} ORDER BY mine_timestamp ASC`;
    const result = await pool.query(query, params);
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Distinct tags available in pool_stats (for filters)
app.get('/api/pool-tags', async (_req, res) => {
  try {
    const result = await pool.query(
      'SELECT DISTINCT tag FROM pool_stats ORDER BY tag'
    );
    res.json(result.rows.map(r => r.tag));
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ── API History ───────────────────────────────────────────────────────────────

app.get('/api/api-history', async (req, res) => {
  try {
    const { api_name, success, limit, from, to } = req.query;
    const params = [];
    const conditions = [];

    if (api_name) { params.push(api_name); conditions.push(`api_name = $${params.length}`); }
    if (success !== undefined) { params.push(success === 'true'); conditions.push(`success = $${params.length}`); }
    if (from) { params.push(from); conditions.push(`called_at >= $${params.length}`); }
    if (to)   { params.push(to);   conditions.push(`called_at <= $${params.length}`); }

    const maxRows = Math.min(parseInt(limit) || 200, 5000);
    let query = 'SELECT id, api_name, success, duration_ms, message, called_at FROM api_history';
    if (conditions.length) query += ' WHERE ' + conditions.join(' AND ');
    query += ` ORDER BY called_at DESC LIMIT ${maxRows}`;

    const result = await pool.query(query, params);
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/api/api-history-names', async (_req, res) => {
  try {
    const result = await pool.query('SELECT DISTINCT api_name FROM api_history ORDER BY api_name');
    res.json(result.rows.map(r => r.api_name));
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ── Services ──────────────────────────────────────────────────────────────────

app.get('/api/aggregator-status', (_req, res) => {
  exec('tmux has-session -t aggregator', (error) => {
    res.json({ running: !error });
  });
});

// ─────────────────────────────────────────────────────────────────────────────

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => console.log(`Backend running on http://localhost:${PORT}`));
