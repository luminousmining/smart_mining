require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { exec } = require('child_process');
const { Pool } = require('pg');

const app = express();
app.use(cors());
app.use(express.json());

// Live dashboard data must never be cached (browser or reverse proxy).
app.use((_req, res, next) => {
  res.set('Cache-Control', 'no-store');
  next();
});

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

// Last activity per pool (for ON/OFF status)
app.get('/api/pool-status', async (_req, res) => {
  try {
    const result = await pool.query(`
      SELECT name, tag, MAX(mine_timestamp) AS last_seen
      FROM pool_stats
      GROUP BY name, tag
      ORDER BY name, tag
    `);
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ── API History ───────────────────────────────────────────────────────────────

const API_HISTORY_MAX_ROWS    = 5000;   // safety cap for raw (non-sampled) results
const API_HISTORY_MAX_BUCKETS = 20000;  // safety cap for downsampled output

app.get('/api/api-history', async (req, res) => {
  try {
    const { api_name, success, limit, from, to } = req.query;
    const params = [];
    const conditions = [];

    if (api_name) { params.push(api_name); conditions.push(`api_name = $${params.length}`); }
    if (success !== undefined) { params.push(success === 'true'); conditions.push(`success = $${params.length}`); }
    if (from) { params.push(from); conditions.push(`called_at >= $${params.length}`); }
    if (to)   { params.push(to);   conditions.push(`called_at <= $${params.length}`); }

    const where  = conditions.length ? ' WHERE ' + conditions.join(' AND ') : '';
    const sample = Math.max(1, parseInt(req.query.sample) || 1);

    let query;
    if (sample > 1) {
      // Downsample for the timeline: group `sample` consecutive calls per api_name
      // (ordered by time) into a single point. A group is "failed" (red) if it
      // contains at least one failure; duration is averaged; the representative
      // timestamp is the group's time-span midpoint. Scans the full range — output
      // is bounded by the number of buckets, not by a raw-row LIMIT.
      params.push(sample);
      const sampleIdx = params.length;
      query = `
        SELECT api_name,
               min(called_at) AS ts_start,
               max(called_at) AS ts_end,
               min(called_at) + (max(called_at) - min(called_at)) / 2 AS called_at,
               bool_and(success) AS success,
               count(*) AS total,
               count(*) FILTER (WHERE NOT success) AS fail_count,
               round(avg(duration_ms))::int AS duration_ms
        FROM (
          SELECT api_name, success, duration_ms, called_at,
                 (row_number() OVER (PARTITION BY api_name ORDER BY called_at) - 1) / $${sampleIdx}::int AS bucket
          FROM api_history${where}
        ) t
        GROUP BY api_name, bucket
        ORDER BY api_name, called_at
        LIMIT ${API_HISTORY_MAX_BUCKETS}`;
    } else {
      const maxRows = Math.min(parseInt(limit) || 200, API_HISTORY_MAX_ROWS);
      query = `SELECT id, api_name, success, duration_ms, message, called_at FROM api_history${where} ORDER BY called_at DESC LIMIT ${maxRows}`;
    }

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

// Last success/failure + 24h counters per API name
app.get('/api/api-status', async (_req, res) => {
  try {
    const result = await pool.query(`
      SELECT
        api_name,
        MAX(called_at) FILTER (WHERE success = true)  AS last_success,
        MAX(called_at) FILTER (WHERE success = false) AS last_failure,
        COUNT(*) FILTER (WHERE success = true  AND called_at > NOW() - INTERVAL '24h') AS success_24h,
        COUNT(*) FILTER (WHERE success = false AND called_at > NOW() - INTERVAL '24h') AS fail_24h
      FROM api_history
      GROUP BY api_name
      ORDER BY api_name
    `);
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Profile rankings
const PROFILE_QUERIES = {
  emission:         `SELECT * FROM profile_emission_usd()`,
  hash_usd:         `SELECT * FROM profile_hash_usd()`,
  usd_sec:          `SELECT name, tag, usd_sec FROM coins WHERE usd_sec IS NOT NULL ORDER BY usd_sec DESC`,
  market_cap:       `SELECT name, tag, market_cap FROM coins WHERE market_cap IS NOT NULL ORDER BY market_cap DESC`,
  network_hashrate: `SELECT name, tag, network_hashrate FROM coins WHERE network_hashrate IS NOT NULL ORDER BY network_hashrate DESC`,
};

app.get('/api/profile/:type', async (req, res) => {
  const query = PROFILE_QUERIES[req.params.type];
  if (!query) return res.status(400).json({ error: 'Unknown profile type' });
  try {
    const result = await pool.query(query);
    res.json(result.rows);
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
