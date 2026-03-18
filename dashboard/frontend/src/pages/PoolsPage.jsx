import { useState, useEffect, useCallback, useMemo } from 'react';
import { api } from '../api';
import Card from '../components/Card';
import DataTable from '../components/DataTable';
import PageHeader from '../components/PageHeader';
import Spinner from '../components/Spinner';

const STATUS = {
  matured:   { bg: '#0d2a18', color: '#22c55e' },
  candidate: { bg: '#0d2030', color: '#00d4aa' },
  immature:  { bg: '#2a0d0d', color: '#ef4444' },
};

const STATUS_PRIORITY = { matured: 3, immature: 2, candidate: 1 };

function deduplicateBlocks(rows) {
  const map = new Map();
  for (const row of rows) {
    const key = `${row.name}|${row.tag}|${row.block_height}`;
    const existing = map.get(key);
    const rowPrio = STATUS_PRIORITY[row.block_status?.toLowerCase()] ?? 0;
    const existPrio = existing ? (STATUS_PRIORITY[existing.block_status?.toLowerCase()] ?? 0) : -1;
    if (!existing || rowPrio > existPrio) map.set(key, row);
  }
  return [...map.values()];
}

function StatusBadge({ value }) {
  if (!value) return <span style={{ color: '#3a3c55' }}>—</span>;
  const { bg, color } = STATUS[value.toLowerCase()] ?? { bg: '#1a1b2e', color: '#6b6d8a' };
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5, padding: '3px 8px', borderRadius: 5, fontSize: 11, fontWeight: 600, background: bg, color }}>
      <span style={{ width: 5, height: 5, borderRadius: '50%', background: color, display: 'inline-block' }} />
      {value}
    </span>
  );
}

function LuckCell({ value }) {
  if (value == null) return <span style={{ color: '#3a3c55' }}>—</span>;
  const pct = Number(value);
  const color = pct >= 100 ? '#22c55e' : pct >= 80 ? '#f59e0b' : '#ef4444';
  return <span style={{ color, fontWeight: 600 }}>{pct.toFixed(1)}%</span>;
}

function buildPoolCols(onNavigate) {
  return [
    {
      key: '_hist',
      label: '',
      render: (_, row) => (
        <button style={s.histBtn} title="View History" onClick={() => onNavigate('poolhistory', { pool: row.name, tag: row.tag })}>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
          </svg>
        </button>
      ),
    },
    { key: 'id',   label: '#',    align: 'right', render: (v) => <span style={{ color: '#4a4c6a' }}>{v}</span> },
    { key: 'name', label: 'Name', render: (v) => <strong style={{ color: '#e4e4f0' }}>{v}</strong> },
    { key: 'tag',  label: 'Tag',  render: (v) => v ? <span style={{ padding: '2px 7px', borderRadius: 4, fontSize: 11, fontWeight: 600, background: '#0d2030', color: '#00d4aa' }}>{v}</span> : null },
  ];
}

const STATS_COLS = [
  { key: 'name',           label: 'Pool',       render: (v) => <strong style={{ color: '#e4e4f0' }}>{v}</strong> },
  { key: 'tag',            label: 'Tag',        render: (v) => v ? <span style={{ padding: '2px 7px', borderRadius: 4, fontSize: 11, fontWeight: 600, background: '#0d2030', color: '#00d4aa' }}>{v}</span> : null },
  { key: 'block_height',   label: 'Block',      align: 'right', render: (v) => v != null ? <span style={{ color: '#a78bfa' }}>#{Number(v).toLocaleString()}</span> : null },
  { key: 'mine_timestamp', label: 'Mined At',   render: (v) => v != null ? <span style={{ color: '#6b6d8a', fontSize: 12 }}>{new Date(Number(v) * 1000).toLocaleString()}</span> : null },
  { key: 'difficulty',     label: 'Difficulty', align: 'right', render: (v) => v != null ? Number(v).toLocaleString('en-US', { notation: 'compact', maximumFractionDigits: 2 }) : null },
  { key: 'luck',           label: 'Luck',       align: 'right', render: (v) => <LuckCell value={v} /> },
  { key: 'block_status',   label: 'Status',     render: (v) => <StatusBadge value={v} /> },
];

export default function PoolsPage({ onNavigate, refreshInterval = 30_000 }) {
  const [pools, setPools]     = useState([]);
  const [allStats, setStats]  = useState([]);
  const [tags, setTags]       = useState([]);
  const [tagFilter, setTagFilter]       = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [heightMin, setHeightMin]       = useState('');
  const [heightMax, setHeightMax]       = useState('');
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);

  const load = useCallback(async () => {
    try {
      const [p, st, tg] = await Promise.all([api.pools(), api.poolStats(), api.poolTags()]);
      setPools(p);
      setStats(deduplicateBlocks(st));
      setTags(tg);
      setLastUpdate(new Date());
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    const id = setInterval(load, refreshInterval ?? 30_000);
    return () => clearInterval(id);
  }, [load]);

  // Compute block_height range from deduplicated data
  const { minHeight, maxHeight } = useMemo(() => {
    if (!allStats.length) return { minHeight: 0, maxHeight: 0 };
    const heights = allStats.map((r) => Number(r.block_height)).filter((v) => !isNaN(v));
    return { minHeight: Math.min(...heights), maxHeight: Math.max(...heights) };
  }, [allStats]);

  const stats = useMemo(() => {
    const lo = heightMin !== '' ? Number(heightMin) : null;
    const hi = heightMax !== '' ? Number(heightMax) : null;
    return allStats.filter((r) =>
      (!tagFilter    || r.tag          === tagFilter) &&
      (!statusFilter || r.block_status === statusFilter) &&
      (lo === null   || Number(r.block_height) >= lo) &&
      (hi === null   || Number(r.block_height) <= hi)
    );
  }, [allStats, tagFilter, statusFilter, heightMin, heightMax]);

  const filteredPools = useMemo(
    () => tagFilter ? pools.filter((p) => p.tag === tagFilter) : pools,
    [pools, tagFilter]
  );

  const sub = lastUpdate ? `Updated ${lastUpdate.toLocaleTimeString()} · refresh 30s` : 'Loading…';

  return (
    <div>
      <PageHeader
        title="Pools"
        subtitle={sub}
        action={
          <div style={s.filterWrap}>
            <span style={s.filterLabel}>Coin</span>
            <select style={s.select} value={tagFilter} onChange={(e) => setTagFilter(e.target.value)}>
              <option value="">All coins</option>
              {tags.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
            <span style={s.filterLabel}>Status</span>
            <select style={s.select} value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              <option value="">All</option>
              <option value="candidate">Candidate</option>
              <option value="immature">Immature</option>
              <option value="matured">Matured</option>
            </select>
            <span style={s.filterLabel}>Block</span>
            <input
              type="number" style={s.heightInput}
              placeholder={minHeight || '—'}
              value={heightMin}
              onChange={(e) => setHeightMin(e.target.value)}
            />
            <span style={{ color: '#4a4c6a', fontSize: 11 }}>→</span>
            <input
              type="number" style={s.heightInput}
              placeholder={maxHeight || '—'}
              value={heightMax}
              onChange={(e) => setHeightMax(e.target.value)}
            />
          </div>
        }
      />

      {loading ? (
        <Spinner />
      ) : (
        <>
          <Card title="Registered Pools" style={{ marginBottom: 12 }}>
            <DataTable columns={buildPoolCols(onNavigate)} rows={filteredPools} />
          </Card>
          <Card title="Block Statistics">
            <DataTable columns={STATS_COLS} rows={stats} />
          </Card>
        </>
      )}
    </div>
  );
}

const s = {
  histBtn: {
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    width: 24, height: 24, borderRadius: 6, border: '1px solid #1e2038',
    background: 'transparent', color: '#4a4c6a', cursor: 'pointer', transition: 'all 0.15s',
  },
  filterWrap: { display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' },
  filterLabel: { fontSize: 11, color: '#4a4c6a', textTransform: 'uppercase', letterSpacing: '0.5px' },
  heightInput: {
    padding: '5px 8px', borderRadius: 7, border: '1px solid #1e2038',
    fontSize: 12, color: '#c8c8e0', background: '#111221', outline: 'none',
    width: 100,
  },
  select: {
    padding: '6px 10px', borderRadius: 7, border: '1px solid #1e2038',
    fontSize: 12, color: '#c8c8e0', background: '#111221', cursor: 'pointer', outline: 'none',
  },
};
