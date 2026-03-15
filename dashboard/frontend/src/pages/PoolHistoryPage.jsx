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

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: '#0d0e1a', border: '1px solid #2a2c45', borderRadius: 8, padding: '10px 14px', fontSize: 12, minWidth: 180 }}>
      <div style={{ color: '#6b6d8a', marginBottom: 6, fontSize: 11 }}>
        {label ? new Date(Number(label) * 1000).toLocaleString() : ''}
      </div>
      {payload.map((p) => (
        <div key={p.dataKey} style={{ display: 'flex', justifyContent: 'space-between', gap: 16, marginBottom: 3 }}>
          <span style={{ color: p.color }}>{p.name}</span>
          <span style={{ color: '#e4e4f0', fontVariantNumeric: 'tabular-nums' }}>{p.value != null ? p.formattedValue : '—'}</span>
        </div>
      ))}
    </div>
  );
};

function LuckChart({ data }) {
  return (
    <Card style={{ marginBottom: 12 }}>
      <div style={s.chartHeader}>
        <span style={s.chartTitle}>Luck per Block</span>
      </div>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={data} margin={{ top: 8, right: 8, left: 8, bottom: 8 }}>
          <CartesianGrid strokeDasharray="1 4" stroke="#1a1b2e" vertical={false} />
          <ReferenceLine y={1} stroke="#3a3c55" strokeDasharray="4 4" />
          <XAxis
            dataKey="mine_timestamp"
            tickFormatter={(v) => new Date(Number(v) * 1000).toLocaleDateString([], { month: 'short', day: 'numeric' })}
            tick={{ fontSize: 10, fill: '#3a3c55' }}
            tickLine={false}
            axisLine={false}
            interval="preserveStartEnd"
          />
          <YAxis
            domain={['auto', 'auto']}
            tickFormatter={(v) => `${(Number(v) * 100).toFixed(0)}%`}
            tick={{ fontSize: 10, fill: '#3a3c55' }}
            tickLine={false}
            axisLine={false}
            width={52}
          />
          <Tooltip
            content={<CustomTooltip />}
            formatter={(v, name) => [`${(Number(v) * 100).toFixed(1)}%`, 'Luck']}
          />
          <Line
            type="monotone"
            dataKey="luck"
            name="Luck"
            stroke="#00d4aa"
            strokeWidth={1.5}
            dot={(props) => {
              const status = props.payload?.block_status?.toLowerCase();
              const fill = STATUS[status] ?? '#00d4aa';
              return <circle key={props.key} cx={props.cx} cy={props.cy} r={3} fill={fill} />;
            }}
            activeDot={{ r: 4, strokeWidth: 0 }}
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
          <Tooltip
            content={<CustomTooltip />}
            formatter={(v, name) => [Number(v).toLocaleString('en-US', { notation: 'compact', maximumFractionDigits: 2 }), 'Difficulty']}
          />
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

export default function PoolHistoryPage({ params = {} }) {
  const [poolNames, setPoolNames] = useState([]);
  const [tags, setTags]           = useState([]);
  const [selectedPool, setPool]   = useState(params.pool ?? '');
  const [tagFilter, setTagFilter] = useState(params.tag ?? '');   // '' = no coin selected
  const [data, setData]           = useState([]);
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
      const rows = await api.poolHistory(selectedPool, tagFilter || undefined);
      setData(rows);
    } finally {
      setLoading(false);
    }
  }, [selectedPool, tagFilter]);

  useEffect(() => { load(); }, [load]);
  useEffect(() => {
    if (!selectedPool || !tagFilter) return;
    const id = setInterval(load, 30_000);
    return () => clearInterval(id);
  }, [load, selectedPool, tagFilter]);

  // Summary stats
  const summary = useMemo(() => {
    if (!data.length) return null;
    const lucks   = data.map((r) => Number(r.luck)).filter((v) => !isNaN(v));
    const statuses = data.reduce((acc, r) => { acc[r.block_status] = (acc[r.block_status] ?? 0) + 1; return acc; }, {});
    return {
      blocks:    data.length,
      avgLuck:   lucks.length ? lucks.reduce((a, b) => a + b, 0) / lucks.length : null,
      confirmed: statuses['confirmed'] ?? 0,
      orphaned:  statuses['orphaned']  ?? 0,
      pending:   statuses['pending']   ?? 0,
    };
  }, [data]);

  const sub = !tagFilter ? 'Select a coin to begin' : selectedPool ? `${selectedPool} · ${tagFilter} · ${data.length} blocks · refresh 30s` : 'Select a pool';

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
            <span style={{ ...s.statVal, color: summary.avgLuck >= 1 ? '#22c55e' : summary.avgLuck >= 0.8 ? '#f59e0b' : '#ef4444' }}>
              {summary.avgLuck != null ? `${(summary.avgLuck * 100).toFixed(1)}%` : '—'}
            </span>
          </div>
          <div style={s.statDiv} />
          <div style={s.stat}>
            <span style={s.statLabel}>Confirmed</span>
            <span style={{ ...s.statVal, color: '#22c55e' }}>{summary.confirmed}</span>
          </div>
          <div style={s.statDiv} />
          <div style={s.stat}>
            <span style={s.statLabel}>Orphaned</span>
            <span style={{ ...s.statVal, color: summary.orphaned > 0 ? '#ef4444' : '#4a4c6a' }}>{summary.orphaned}</span>
          </div>
          {summary.pending > 0 && (
            <>
              <div style={s.statDiv} />
              <div style={s.stat}>
                <span style={s.statLabel}>Pending</span>
                <span style={{ ...s.statVal, color: '#f59e0b' }}>{summary.pending}</span>
              </div>
            </>
          )}
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
          <LuckChart data={data} />
          <DifficultyChart data={data} />
        </>
      )}
    </div>
  );
}

const s = {
  controls: { display: 'flex', alignItems: 'center', gap: 8 },
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
};
