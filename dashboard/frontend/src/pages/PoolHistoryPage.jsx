import { useState, useEffect, useCallback, useMemo } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine,
} from 'recharts';
import { api } from '../api';
import Card from '../components/Card';
import PageHeader from '../components/PageHeader';
import Spinner from '../components/Spinner';

const STATUS = {
  confirmed: '#22c55e',
  orphaned:  '#ef4444',
  pending:   '#f59e0b',
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

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  const item = payload[0]?.payload;
  return (
    <div style={{ background: '#0d0e1a', border: '1px solid #2a2c45', borderRadius: 8, padding: '10px 14px', fontSize: 12, minWidth: 180 }}>
      <div style={{ color: '#6b6d8a', marginBottom: 4, fontSize: 11 }}>
        {label ? new Date(Number(label) * 1000).toLocaleString() : ''}
      </div>
      <div style={{ color: '#3a3c55', marginBottom: 8, fontSize: 11 }}>
        Block #{item?.block_height != null ? Number(item.block_height).toLocaleString() : '—'}
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16, marginBottom: 3 }}>
        <span style={{ color: '#6b6d8a' }}>Pool</span>
        <span style={{ color: '#e4e4f0', fontWeight: 600 }}>{item?.name ?? '—'}</span>
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16 }}>
        <span style={{ color: '#6b6d8a' }}>Luck</span>
        <span style={{ color: Number(item?.luck) >= 100 ? '#22c55e' : Number(item?.luck) >= 80 ? '#f59e0b' : '#ef4444', fontWeight: 600, fontVariantNumeric: 'tabular-nums' }}>
          {item?.luck != null ? `${Number(item.luck).toFixed(1)}%` : '—'}
        </span>
      </div>
    </div>
  );
};

function LuckChart({ data }) {
  const vals  = data.map((d) => Number(d.luck)).filter((v) => !isNaN(v));
  const min   = vals.length ? Math.min(...vals) : 0;
  const max   = vals.length ? Math.max(...vals) : 200;
  const pad   = (max - min) * 0.1 || 10;
  const domain = [min - pad, max + pad];

  return (
    <Card style={{ marginBottom: 12 }}>
      <div style={s.chartHeader}>
        <span style={s.chartTitle}>Luck per Block</span>
      </div>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={data} margin={{ top: 8, right: 8, left: 8, bottom: 8 }}>
          <CartesianGrid strokeDasharray="1 4" stroke="#1a1b2e" vertical={false} />
          <ReferenceLine y={100} stroke="#3a3c55" strokeDasharray="4 4" />
          <XAxis
            dataKey="mine_timestamp"
            tickFormatter={(v) => new Date(Number(v) * 1000).toLocaleDateString([], { month: 'short', day: 'numeric' })}
            tick={{ fontSize: 10, fill: '#3a3c55' }}
            tickLine={false}
            axisLine={false}
            interval="preserveStartEnd"
          />
          <YAxis
            domain={domain}
            tickFormatter={(v) => `${Number(v).toFixed(0)}%`}
            tick={{ fontSize: 10, fill: '#3a3c55' }}
            tickLine={false}
            axisLine={false}
            width={52}
          />
          <Tooltip content={<CustomTooltip />} />
          <Line
            type="monotone"
            dataKey="luck"
            name="Luck"
            stroke="#6b6d8a"
            strokeWidth={1.5}
            dot={(props) => {
              const luck = Number(props.payload?.luck);
              const fill = luck >= 100 ? '#22c55e' : luck >= 80 ? '#f59e0b' : '#ef4444';
              return <circle key={props.key} cx={props.cx} cy={props.cy} r={4} fill={fill} />;
            }}
            activeDot={(props) => {
              const luck = Number(props.payload?.luck);
              const fill = luck >= 100 ? '#22c55e' : luck >= 80 ? '#f59e0b' : '#ef4444';
              return <circle key={props.key} cx={props.cx} cy={props.cy} r={6} fill={fill} />;
            }}
          />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}

function DifficultyChart({ data }) {
  return (
    <Card>
      <div style={s.chartHeader}>
        <span style={s.chartTitle}>Difficulty per Block</span>
      </div>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={data} margin={{ top: 8, right: 8, left: 8, bottom: 8 }}>
          <CartesianGrid strokeDasharray="1 4" stroke="#1a1b2e" vertical={false} />
          <XAxis
            dataKey="mine_timestamp"
            tickFormatter={(v) => new Date(Number(v) * 1000).toLocaleDateString([], { month: 'short', day: 'numeric' })}
            tick={{ fontSize: 10, fill: '#3a3c55' }}
            tickLine={false}
            axisLine={false}
            interval="preserveStartEnd"
          />
          <YAxis
            tickFormatter={(v) => Number(v).toLocaleString('en-US', { notation: 'compact', maximumFractionDigits: 2 })}
            tick={{ fontSize: 10, fill: '#3a3c55' }}
            tickLine={false}
            axisLine={false}
            width={64}
          />
          <Tooltip content={({ active, payload, label }) => {
            if (!active || !payload?.length) return null;
            const item = payload[0]?.payload;
            return (
              <div style={{ background: '#0d0e1a', border: '1px solid #2a2c45', borderRadius: 8, padding: '10px 14px', fontSize: 12, minWidth: 180 }}>
                <div style={{ color: '#6b6d8a', marginBottom: 4, fontSize: 11 }}>
                  {label ? new Date(Number(label) * 1000).toLocaleString() : ''}
                </div>
                <div style={{ color: '#3a3c55', marginBottom: 8, fontSize: 11 }}>
                  Block #{item?.block_height != null ? Number(item.block_height).toLocaleString() : '—'}
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16, marginBottom: 3 }}>
                  <span style={{ color: '#6b6d8a' }}>Pool</span>
                  <span style={{ color: '#e4e4f0', fontWeight: 600 }}>{item?.name ?? '—'}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16 }}>
                  <span style={{ color: '#6b6d8a' }}>Difficulty</span>
                  <span style={{ color: '#f59e0b', fontWeight: 600, fontVariantNumeric: 'tabular-nums' }}>
                    {item?.difficulty != null ? Number(item.difficulty).toLocaleString('en-US', { notation: 'compact', maximumFractionDigits: 2 }) : '—'}
                  </span>
                </div>
              </div>
            );
          }} />
          <Line
            type="monotone"
            dataKey="difficulty"
            name="Difficulty"
            stroke="#f59e0b"
            strokeWidth={1.5}
            dot={false}
            activeDot={{ r: 3, strokeWidth: 0 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}

const today        = new Date().toISOString().split('T')[0];
const sevenDaysAgo = new Date(Date.now() - 7 * 86400000).toISOString().split('T')[0];

export default function PoolHistoryPage({ params = {} }) {
  const [poolNames, setPoolNames] = useState([]);
  const [tags, setTags]           = useState([]);
  const [selectedPool, setPool]   = useState(params.pool ?? '');
  const [tagFilter, setTagFilter]       = useState(params.tag ?? '');
  const [statusFilter, setStatusFilter] = useState('');
  const [dateFrom, setDateFrom]         = useState(sevenDaysAgo);
  const [dateTo, setDateTo]             = useState(today);
  const [data, setData]                 = useState([]);
  const [loading, setLoading]     = useState(false);

  // Load tags on mount only
  useEffect(() => {
    api.poolTags().then(setTags);
    // If arriving from navigation with a coin+pool pre-selected, load pool names for that tag
    if (params.tag) {
      api.poolNames(params.tag).then(setPoolNames);
    }
  }, []);

  // Reload pool names when a coin is selected
  useEffect(() => {
    if (!tagFilter) { setPoolNames([]); setPool(''); return; }
    api.poolNames(tagFilter).then((names) => {
      setPoolNames(names);
      // Keep current pool if it's still valid, otherwise pick first
      if (!names.includes(selectedPool)) setPool(names[0] ?? '');
    });
  }, [tagFilter]);

  const load = useCallback(async () => {
    if (!selectedPool || !tagFilter) return;
    setLoading(true);
    try {
      const rows = await api.poolHistory(selectedPool, tagFilter || undefined, dateFrom, dateTo);
      setData(deduplicateBlocks(rows).sort((a, b) => Number(a.mine_timestamp) - Number(b.mine_timestamp)));
    } finally {
      setLoading(false);
    }
  }, [selectedPool, tagFilter, dateFrom, dateTo]);

  useEffect(() => { load(); }, [load]);

  const filteredData = useMemo(
    () => statusFilter ? data.filter((r) => r.block_status === statusFilter) : data,
    [data, statusFilter]
  );

  // Summary stats computed on full data (not filtered)
  const summary = useMemo(() => {
    if (!data.length) return null;
    const lucks    = data.map((r) => Number(r.luck)).filter((v) => !isNaN(v));
    const statuses = data.reduce((acc, r) => { acc[r.block_status] = (acc[r.block_status] ?? 0) + 1; return acc; }, {});
    return {
      blocks:    data.length,
      avgLuck:   lucks.length ? lucks.reduce((a, b) => a + b, 0) / lucks.length : null,
      candidate: statuses['candidate'] ?? 0,
      immature:  statuses['immature']  ?? 0,
      matured:   statuses['matured']   ?? 0,
    };
  }, [data]);

  const sub = !tagFilter ? 'Select a coin to begin' : selectedPool ? `${selectedPool} · ${tagFilter} · ${filteredData.length} blocks` : 'Select a pool';

  return (
    <div>
      <PageHeader
        title="Pool History"
        subtitle={sub}
        action={
          <div style={s.controls}>
            <select style={s.select} value={tagFilter} onChange={(e) => setTagFilter(e.target.value)}>
              <option value="">— Select coin —</option>
              {tags.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
            {tagFilter && poolNames.length > 0 && (
              <select style={{ ...s.select, minWidth: 160 }} value={selectedPool} onChange={(e) => setPool(e.target.value)}>
                {poolNames.map((n) => <option key={n} value={n}>{n}</option>)}
              </select>
            )}
            <select style={s.select} value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              <option value="">All status</option>
              <option value="candidate">Candidate</option>
              <option value="immature">Immature</option>
              <option value="matured">Matured</option>
            </select>
            <input type="date" style={s.dateInput} value={dateFrom} max={dateTo} onChange={(e) => setDateFrom(e.target.value)} />
            <span style={{ color: '#4a4c6a', fontSize: 11 }}>→</span>
            <input type="date" style={s.dateInput} value={dateTo} min={dateFrom} max={today} onChange={(e) => setDateTo(e.target.value)} />
            <button onClick={load} style={s.refreshBtn} disabled={loading} title="Refresh">↺</button>
          </div>
        }
      />

      {/* Summary strip */}
      {summary && (
        <div style={s.strip}>
          <div style={s.stat}>
            <span style={s.statLabel}>Blocks</span>
            <span style={s.statVal}>{summary.blocks}</span>
          </div>
          <div style={s.statDiv} />
          <div style={s.stat}>
            <span style={s.statLabel}>Avg Luck</span>
            <span style={{ ...s.statVal, color: summary.avgLuck >= 100 ? '#22c55e' : summary.avgLuck >= 80 ? '#f59e0b' : '#ef4444' }}>
              {summary.avgLuck != null ? `${summary.avgLuck.toFixed(1)}%` : '—'}
            </span>
          </div>
          <div style={s.statDiv} />
          <div style={s.stat}>
            <span style={s.statLabel}>💰 Matured</span>
            <span style={{ ...s.statVal, color: summary.matured > 0 ? '#22c55e' : '#4a4c6a' }}>{summary.matured}</span>
          </div>
          <div style={s.statDiv} />
          <div style={s.stat}>
            <span style={s.statLabel}>⏳ Immature</span>
            <span style={{ ...s.statVal, color: summary.immature > 0 ? '#6366f1' : '#4a4c6a' }}>{summary.immature}</span>
          </div>
          <div style={s.statDiv} />
          <div style={s.stat}>
            <span style={s.statLabel}>🧱 Candidate</span>
            <span style={{ ...s.statVal, color: summary.candidate > 0 ? '#f59e0b' : '#4a4c6a' }}>{summary.candidate}</span>
          </div>
        </div>
      )}

      {loading ? (
        <Spinner />
      ) : !tagFilter ? (
        <Card><p style={{ color: '#4a4c6a', fontSize: 13 }}>Select a coin to display pool history.</p></Card>
      ) : !selectedPool ? (
        <Card><p style={{ color: '#4a4c6a', fontSize: 13 }}>No pool available for this coin.</p></Card>
      ) : data.length === 0 ? (
        <Card><p style={{ color: '#4a4c6a', fontSize: 13 }}>No block data for this pool.</p></Card>
      ) : (
        <>
          <LuckChart data={filteredData} />
          <DifficultyChart data={filteredData} />
        </>
      )}
    </div>
  );
}

const s = {
  controls: { display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' },
  dateInput: {
    padding: '5px 8px', borderRadius: 7, border: '1px solid #1e2038',
    fontSize: 12, color: '#c8c8e0', background: '#111221', cursor: 'pointer', outline: 'none',
    colorScheme: 'dark',
  },
  select: {
    padding: '6px 10px', borderRadius: 7, border: '1px solid #1e2038',
    fontSize: 12, color: '#c8c8e0', background: '#111221', cursor: 'pointer', outline: 'none',
  },

  strip: {
    display: 'flex',
    alignItems: 'center',
    background: '#111221',
    border: '1px solid #1e2038',
    borderRadius: 10,
    padding: '12px 20px',
    marginBottom: 14,
    gap: 0,
  },
  stat:      { display: 'flex', flexDirection: 'column', gap: 3, padding: '0 20px' },
  statLabel: { fontSize: 10, fontWeight: 600, color: '#4a4c6a', textTransform: 'uppercase', letterSpacing: '0.6px' },
  statVal:   { fontSize: 18, fontWeight: 700, color: '#e4e4f0', fontVariantNumeric: 'tabular-nums' },
  statDiv:   { width: 1, height: 32, background: '#1e2038', flexShrink: 0 },

  chartHeader: { display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginBottom: 12 },
  chartTitle:  { fontSize: 11, fontWeight: 600, color: '#6b6d8a', textTransform: 'uppercase', letterSpacing: '0.7px' },
  chartSub:    { fontSize: 11, color: '#3a3c55' },
  refreshBtn: {
    padding: '5px 10px', borderRadius: 6,
    border: '1px solid #1e2038', background: 'transparent',
    color: '#00d4aa', fontSize: 14, cursor: 'pointer',
  },
};
