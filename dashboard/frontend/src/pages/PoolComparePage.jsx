import { useState, useEffect, useCallback, useMemo } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, ReferenceLine,
} from 'recharts';
import { api } from '../api';
import Card from '../components/Card';
import PageHeader from '../components/PageHeader';
import Spinner from '../components/Spinner';
import DataTable from '../components/DataTable';

const PALETTE = ['#00d4aa', '#6366f1', '#f59e0b', '#ef4444', '#a78bfa', '#34d399', '#f472b6', '#60a5fa'];
const METRICS  = [
  { key: 'luck',       label: 'Luck',       fmt: (v) => `${(Number(v) * 100).toFixed(1)}%` },
  { key: 'difficulty', label: 'Difficulty', fmt: (v) => Number(v).toLocaleString('en-US', { notation: 'compact', maximumFractionDigits: 2 }) },
];

function mergePoolData(stats, pools, metricKey) {
  // x-axis = block_height (numeric), one value per pool
  const byPool = {};
  pools.forEach((p) => { byPool[p] = {}; });
  stats.forEach((row) => {
    if (!byPool[row.name]) return;
    byPool[row.name][Number(row.block_height)] = Number(row[metricKey]);
  });
  const allBlocks = [...new Set(stats.map((r) => Number(r.block_height)))].sort((a, b) => a - b);
  return allBlocks.map((h) => {
    const item = { block: h };
    pools.forEach((p) => { item[p] = byPool[p]?.[h] ?? null; });
    return item;
  });
}

function summaryRows(stats, pools) {
  return pools.map((pool, i) => {
    const rows = stats.filter((r) => r.name === pool);
    if (!rows.length) return { pool, blocks: 0, avgLuck: null, color: PALETTE[i % PALETTE.length] };
    const lucks    = rows.map((r) => Number(r.luck)).filter((v) => !isNaN(v));
    const statuses = rows.reduce((acc, r) => {
      acc[r.block_status] = (acc[r.block_status] ?? 0) + 1;
      return acc;
    }, {});
    return {
      pool,
      blocks:     rows.length,
      avgLuck:    lucks.length ? lucks.reduce((a, b) => a + b, 0) / lucks.length : null,
      confirmed:  statuses['confirmed'] ?? 0,
      orphaned:   statuses['orphaned'] ?? 0,
      color:      PALETTE[i % PALETTE.length],
    };
  });
}

const CustomTooltip = ({ active, payload, label, metricFmt }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: '#0d0e1a', border: '1px solid #2a2c45', borderRadius: 8, padding: '10px 14px', fontSize: 12, minWidth: 160 }}>
      <div style={{ color: '#6b6d8a', marginBottom: 8, fontSize: 11 }}>Block #{Number(label).toLocaleString()}</div>
      {payload.map((p) => (
        <div key={p.dataKey} style={{ display: 'flex', justifyContent: 'space-between', gap: 16, marginBottom: 3 }}>
          <span style={{ color: p.color, fontWeight: 600 }}>{p.dataKey}</span>
          <span style={{ color: '#e4e4f0', fontVariantNumeric: 'tabular-nums' }}>{metricFmt(p.value)}</span>
        </div>
      ))}
    </div>
  );
};

export default function PoolComparePage() {
  const [allStats, setAllStats]   = useState([]);
  const [tags, setTags]           = useState([]);
  const [tagFilter, setTagFilter] = useState('');
  const [selected, setSelected]   = useState([]);
  const [metric, setMetric]       = useState('luck');
  const [loading, setLoading]     = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);

  const load = useCallback(async () => {
    try {
      const [st, tg] = await Promise.all([api.poolStats(tagFilter || undefined), api.poolTags()]);
      setAllStats(st);
      setTags(tg);
      setLastUpdate(new Date());
    } finally {
      setLoading(false);
    }
  }, [tagFilter]);

  useEffect(() => { load(); }, [load]);
  useEffect(() => {
    const id = setInterval(load, 30_000);
    return () => clearInterval(id);
  }, [load]);

  // Pool names available for the current tag filter
  const availablePools = useMemo(
    () => [...new Set(allStats.map((r) => r.name))].sort(),
    [allStats]
  );

  // Reset selection when tag changes
  useEffect(() => { setSelected([]); }, [tagFilter]);

  const filteredStats = useMemo(
    () => selected.length ? allStats.filter((r) => selected.includes(r.name)) : allStats,
    [allStats, selected]
  );

  const displayPools = selected.length ? selected : availablePools;
  const metricDef    = METRICS.find((m) => m.key === metric) ?? METRICS[0];
  const chartData    = useMemo(() => mergePoolData(filteredStats, displayPools, metric), [filteredStats, displayPools, metric]);
  const summary      = useMemo(() => summaryRows(filteredStats, displayPools), [filteredStats, displayPools]);

  const togglePool = (p) =>
    setSelected((prev) => prev.includes(p) ? prev.filter((x) => x !== p) : [...prev, p]);

  const SUMMARY_COLS = [
    { key: 'pool',      label: 'Pool',      render: (v, row) => <span style={{ color: row.color, fontWeight: 600 }}>{v}</span> },
    { key: 'blocks',    label: 'Blocks',    align: 'right' },
    { key: 'avgLuck',   label: 'Avg Luck',  align: 'right', render: (v) => {
      if (v == null) return null;
      const pct = Number(v) * 100;
      const color = pct >= 100 ? '#22c55e' : pct >= 80 ? '#f59e0b' : '#ef4444';
      return <span style={{ color, fontWeight: 600 }}>{pct.toFixed(1)}%</span>;
    }},
    { key: 'confirmed', label: 'Confirmed', align: 'right', render: (v) => <span style={{ color: '#22c55e' }}>{v ?? 0}</span> },
    { key: 'orphaned',  label: 'Orphaned',  align: 'right', render: (v) => <span style={{ color: v > 0 ? '#ef4444' : '#4a4c6a' }}>{v ?? 0}</span> },
  ];

  const sub = lastUpdate ? `Updated ${lastUpdate.toLocaleTimeString()} · refresh 30s` : 'Loading…';

  return (
    <div>
      <PageHeader
        title="Compare Pools"
        subtitle={sub}
        action={
          <div style={s.filterWrap}>
            <span style={s.filterLabel}>Coin</span>
            <select style={s.select} value={tagFilter} onChange={(e) => setTagFilter(e.target.value)}>
              <option value="">All coins</option>
              {tags.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
        }
      />

      {loading ? <Spinner /> : (
        <div style={s.layout}>
          {/* ── Left: pool selector ── */}
          <div style={s.panel}>
            <div style={s.panelHead}>
              <span style={s.panelTitle}>Pools</span>
              <span style={s.panelCount}>{selected.length || 'All'}</span>
            </div>
            <div style={s.poolList}>
              {availablePools.map((pool, i) => {
                const on    = selected.includes(pool);
                const color = PALETTE[i % PALETTE.length];
                return (
                  <button
                    key={pool}
                    style={{ ...s.poolBtn, ...(on ? { ...s.poolBtnOn, borderColor: color } : {}) }}
                    onClick={() => togglePool(pool)}
                  >
                    {on && <span style={{ ...s.dot, background: color }} />}
                    <span style={s.poolName}>{pool}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* ── Right: charts + summary ── */}
          <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', gap: 12 }}>
            {/* Metric selector */}
            <div style={s.controls}>
              {METRICS.map((m) => (
                <button
                  key={m.key}
                  style={{ ...s.metricBtn, ...(metric === m.key ? s.metricBtnOn : {}) }}
                  onClick={() => setMetric(m.key)}
                >
                  {m.label}
                </button>
              ))}
            </div>

            {/* Chart */}
            <Card>
              {chartData.length === 0 ? (
                <div style={s.empty}>No data for selected filters.</div>
              ) : (
                <ResponsiveContainer width="100%" height={360}>
                  <LineChart data={chartData} margin={{ top: 8, right: 8, left: 8, bottom: 8 }}>
                    <CartesianGrid strokeDasharray="1 4" stroke="#1a1b2e" vertical={false} />
                    {metric === 'luck' && (
                      <ReferenceLine y={1} stroke="#3a3c55" strokeDasharray="4 4" />
                    )}
                    <XAxis
                      dataKey="block"
                      tickFormatter={(v) => `#${Number(v).toLocaleString()}`}
                      tick={{ fontSize: 10, fill: '#3a3c55' }}
                      tickLine={false}
                      axisLine={false}
                      interval="preserveStartEnd"
                    />
                    <YAxis
                      tickFormatter={metricDef.fmt}
                      tick={{ fontSize: 10, fill: '#3a3c55' }}
                      tickLine={false}
                      axisLine={false}
                      width={72}
                    />
                    <Tooltip content={<CustomTooltip metricFmt={metricDef.fmt} />} />
                    <Legend
                      wrapperStyle={{ fontSize: 11, paddingTop: 12 }}
                      formatter={(v) => <span style={{ color: '#c8c8e0' }}>{v}</span>}
                    />
                    {displayPools.map((pool, i) => (
                      <Line
                        key={pool}
                        type="monotone"
                        dataKey={pool}
                        stroke={PALETTE[i % PALETTE.length]}
                        strokeWidth={1.5}
                        dot={{ r: 3, fill: PALETTE[i % PALETTE.length], strokeWidth: 0 }}
                        activeDot={{ r: 4, strokeWidth: 0 }}
                        connectNulls={false}
                      />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
              )}
            </Card>

            {/* Summary table */}
            <Card title="Summary">
              <DataTable columns={SUMMARY_COLS} rows={summary} keyField="pool" />
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}

const s = {
  layout: { display: 'flex', gap: 16, alignItems: 'flex-start' },
  panel: {
    width: 180, flexShrink: 0, background: '#111221', borderRadius: 12,
    border: '1px solid #1e2038', padding: '14px 12px',
    display: 'flex', flexDirection: 'column', gap: 10,
  },
  panelHead:  { display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
  panelTitle: { fontSize: 11, fontWeight: 600, color: '#6b6d8a', textTransform: 'uppercase', letterSpacing: '0.7px' },
  panelCount: { fontSize: 11, color: '#00d4aa' },
  poolList:   { display: 'flex', flexDirection: 'column', gap: 4 },
  poolBtn: {
    display: 'flex', alignItems: 'center', gap: 6, padding: '7px 8px',
    borderRadius: 7, border: '1px solid #1e2038', background: 'transparent',
    cursor: 'pointer', transition: 'all 0.15s', textAlign: 'left',
  },
  poolBtnOn: { background: '#131425' },
  dot:       { width: 6, height: 6, borderRadius: '50%', flexShrink: 0 },
  poolName:  { fontSize: 12, fontWeight: 500, color: '#c8c8e0' },

  filterWrap:  { display: 'flex', alignItems: 'center', gap: 8 },
  filterLabel: { fontSize: 11, color: '#4a4c6a', textTransform: 'uppercase', letterSpacing: '0.5px' },
  select: {
    padding: '6px 10px', borderRadius: 7, border: '1px solid #1e2038',
    fontSize: 12, color: '#c8c8e0', background: '#111221', cursor: 'pointer', outline: 'none',
  },
  controls:    { display: 'flex', gap: 8 },
  metricBtn: {
    padding: '6px 14px', borderRadius: 7, border: '1px solid #1e2038',
    fontSize: 12, fontWeight: 500, color: '#4a4c6a', background: 'transparent', cursor: 'pointer', transition: 'all 0.15s',
  },
  metricBtnOn: { background: '#1a1b2e', color: '#00d4aa', borderColor: '#00d4aa44' },
  empty: { color: '#4a4c6a', fontSize: 13, padding: '48px 0', textAlign: 'center' },
};
