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
  { key: 'luck',       label: 'Luck',       fmt: (v) => `${Number(v).toFixed(1)}%` },
  { key: 'difficulty', label: 'Difficulty', fmt: (v) => Number(v).toLocaleString('en-US', { notation: 'compact', maximumFractionDigits: 2 }) },
];

const STATUS_PRIORITY = { matured: 3, immature: 2, candidate: 1 };

function deduplicateBlocks(rows) {
  const map = new Map();
  for (const row of rows) {
    const key = `${row.name}|${row.tag}|${row.block_height}`;
    const existing = map.get(key);
    const rowPrio   = STATUS_PRIORITY[row.block_status?.toLowerCase()] ?? 0;
    const existPrio = existing ? (STATUS_PRIORITY[existing.block_status?.toLowerCase()] ?? 0) : -1;
    if (!existing || rowPrio > existPrio) map.set(key, row);
  }
  return [...map.values()];
}

function mergePoolData(stats, pools, metricKey) {
  const byPool = {};
  pools.forEach((p) => { byPool[p] = {}; });

  const blockToTime = {};
  stats.forEach((row) => {
    if (!byPool[row.name]) return;
    byPool[row.name][Number(row.block_height)] = Number(row[metricKey]);
    if (row.mine_timestamp) blockToTime[Number(row.block_height)] = Number(row.mine_timestamp) * 1000;
  });

  const allBlocks = [...new Set(stats.map((r) => Number(r.block_height)))].sort((a, b) => a - b);
  return allBlocks.map((h) => {
    const item = { block: h, time: blockToTime[h] ?? null };
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
      candidate:  statuses['candidate'] ?? 0,
      immature:   statuses['immature']  ?? 0,
      matured:    statuses['matured']   ?? 0,
      color:      PALETTE[i % PALETTE.length],
    };
  });
}

const CustomTooltip = ({ active, payload, label, metricFmt }) => {
  if (!active || !payload?.length) return null;
  const item = payload[0]?.payload;
  return (
    <div style={{ background: '#0d0e1a', border: '1px solid #2a2c45', borderRadius: 8, padding: '10px 14px', fontSize: 12, minWidth: 160 }}>
      <div style={{ color: '#6b6d8a', marginBottom: 4, fontSize: 11 }}>
        {label ? new Date(label).toLocaleString() : ''}
      </div>
      <div style={{ color: '#3a3c55', marginBottom: 8, fontSize: 11 }}>
        Block #{Number(item?.block).toLocaleString()}
      </div>
      {payload.map((p) => (
        <div key={p.dataKey} style={{ display: 'flex', justifyContent: 'space-between', gap: 16, marginBottom: 3 }}>
          <span style={{ color: p.color, fontWeight: 600 }}>{p.dataKey}</span>
          <span style={{ color: '#e4e4f0', fontVariantNumeric: 'tabular-nums' }}>{metricFmt(p.value)}</span>
        </div>
      ))}
    </div>
  );
};

export default function PoolComparePage({ refreshInterval = 30_000 }) {
  const [allStats, setAllStats]   = useState([]);
  const [tags, setTags]           = useState([]);
  const [tagFilter, setTagFilter]       = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [selected, setSelected]         = useState([]);
  const [metric, setMetric]             = useState('luck');
  const [loading, setLoading]     = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);

  const load = useCallback(async () => {
    try {
      const [st, tg] = await Promise.all([api.poolStats(tagFilter || undefined), api.poolTags()]);
      setAllStats(deduplicateBlocks(st));
      setTags(tg);
      setLastUpdate(new Date());
    } finally {
      setLoading(false);
    }
  }, [tagFilter]);

  useEffect(() => { load(); }, [load]);
  useEffect(() => {
    const id = setInterval(load, refreshInterval ?? 30_000);
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
    () => allStats.filter((r) =>
      (!selected.length  || selected.includes(r.name)) &&
      (!statusFilter     || r.block_status === statusFilter)
    ),
    [allStats, selected, statusFilter]
  );

  const displayPools = selected.length ? selected : availablePools;
  const metricDef    = METRICS.find((m) => m.key === metric) ?? METRICS[0];
  const chartData    = useMemo(() => mergePoolData(filteredStats, displayPools, metric), [filteredStats, displayPools, metric]);

  const yDomain = useMemo(() => {
    const vals = chartData.flatMap((d) => displayPools.map((p) => d[p])).filter((v) => v != null && !isNaN(v));
    if (!vals.length) return ['auto', 'auto'];
    const min = Math.min(...vals);
    const max = Math.max(...vals);
    const pad = (max - min) * 0.1 || 10;
    return [min - pad, max + pad];
  }, [chartData, displayPools]);
  const summary      = useMemo(() => summaryRows(filteredStats, displayPools), [filteredStats, displayPools]);

  const togglePool = (p) =>
    setSelected((prev) => prev.includes(p) ? prev.filter((x) => x !== p) : [...prev, p]);

  const SUMMARY_COLS = [
    { key: 'pool',      label: 'Pool',      render: (v, row) => <span style={{ color: row.color, fontWeight: 600 }}>{v}</span> },
    { key: 'blocks',    label: 'Blocks',    align: 'right' },
    { key: 'avgLuck',   label: 'Avg Luck',  align: 'right', render: (v) => {
      if (v == null) return null;
      const pct = Number(v);
      const color = pct >= 100 ? '#22c55e' : pct >= 80 ? '#f59e0b' : '#ef4444';
      return <span style={{ color, fontWeight: 600 }}>{pct.toFixed(1)}%</span>;
    }},
    { key: 'candidate', label: '🧱 Candidate', align: 'right', render: (v) => <span style={{ color: v > 0 ? '#f59e0b' : '#4a4c6a' }}>{v ?? 0}</span> },
    { key: 'immature',  label: '⏳ Immature',  align: 'right', render: (v) => <span style={{ color: v > 0 ? '#6366f1' : '#4a4c6a' }}>{v ?? 0}</span> },
    { key: 'matured',   label: '💰 Matured',   align: 'right', render: (v) => <span style={{ color: v > 0 ? '#22c55e' : '#4a4c6a' }}>{v ?? 0}</span> },
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
            <span style={s.filterLabel}>Status</span>
            <select style={s.select} value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              <option value="">All</option>
              <option value="candidate">Candidate</option>
              <option value="immature">Immature</option>
              <option value="matured">Matured</option>
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
                      <ReferenceLine y={100} stroke="#3a3c55" strokeDasharray="4 4" />
                    )}
                    <XAxis
                      dataKey="time"
                      tickFormatter={(v) => v ? new Date(v).toLocaleDateString([], { month: 'short', day: 'numeric' }) : ''}
                      tick={{ fontSize: 10, fill: '#3a3c55' }}
                      tickLine={false}
                      axisLine={false}
                      interval="preserveStartEnd"
                    />
                    <YAxis
                      domain={yDomain}
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
                        stroke={metric === 'luck' ? '#6b6d8a' : PALETTE[i % PALETTE.length]}
                        strokeWidth={1.5}
                        dot={metric === 'luck'
                          ? (props) => {
                              const luck = Number(props.payload?.[pool]);
                              const fill = luck >= 100 ? '#22c55e' : luck >= 80 ? '#f59e0b' : '#ef4444';
                              return <circle key={props.key} cx={props.cx} cy={props.cy} r={4} fill={fill} />;
                            }
                          : { r: 3, fill: PALETTE[i % PALETTE.length], strokeWidth: 0 }
                        }
                        activeDot={metric === 'luck'
                          ? (props) => {
                              const luck = Number(props.payload?.[pool]);
                              const fill = luck >= 100 ? '#22c55e' : luck >= 80 ? '#f59e0b' : '#ef4444';
                              return <circle key={props.key} cx={props.cx} cy={props.cy} r={6} fill={fill} />;
                            }
                          : { r: 4, strokeWidth: 0 }
                        }
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
