import { useState, useEffect, useCallback } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine,
} from 'recharts';
import { api } from '../api';
import Card from '../components/Card';
import PageHeader from '../components/PageHeader';
import Spinner from '../components/Spinner';

const RANGES = ['1h', '24h', '7d', '30d', 'all'];

const METRICS = [
  { key: 'usd',              label: 'Price',          unit: 'USD',   color: '#00d4aa', fmt: (v) => `$${Number(v).toLocaleString('en-US', { maximumFractionDigits: 6 })}` },
  { key: 'market_cap',       label: 'Market Cap',     unit: 'USD',   color: '#6366f1', fmt: (v) => `$${Number(v).toLocaleString('en-US', { notation: 'compact', maximumFractionDigits: 2 })}` },
  { key: 'difficulty',       label: 'Difficulty',     unit: '',      color: '#f59e0b', fmt: (v) => Number(v).toLocaleString('en-US', { notation: 'compact', maximumFractionDigits: 2 }) },
  { key: 'network_hashrate', label: 'Net. Hashrate',  unit: 'H/s',   color: '#a78bfa', fmt: (v) => { const n = Number(v); if (n >= 1e15) return `${(n/1e15).toFixed(2)} PH/s`; if (n >= 1e12) return `${(n/1e12).toFixed(2)} TH/s`; if (n >= 1e9) return `${(n/1e9).toFixed(2)} GH/s`; return `${(n/1e6).toFixed(2)} MH/s`; } },
  { key: 'hash_usd',         label: 'Hash USD',       unit: '$/H',   color: '#f472b6', fmt: (v) => `$${Number(v).toExponential(3)}` },
  { key: 'emission_usd',     label: 'Emission USD',   unit: 'USD',   color: '#34d399', fmt: (v) => `$${Number(v).toLocaleString('en-US', { maximumFractionDigits: 4 })}` },
];

const CustomTooltip = ({ active, payload, label, metric }) => {
  if (!active || !payload?.length) return null;
  const val = payload[0]?.value;
  return (
    <div style={{
      background: '#0d0e1a',
      border: '1px solid #2a2c45',
      borderRadius: 8,
      padding: '10px 14px',
      fontSize: 12,
    }}>
      <div style={{ color: '#6b6d8a', marginBottom: 4 }}>
        {new Date(label).toLocaleString()}
      </div>
      <div style={{ color: metric.color, fontWeight: 600, fontVariantNumeric: 'tabular-nums' }}>
        {metric.fmt(val)}
      </div>
    </div>
  );
};

function MetricChart({ data, metric }) {
  if (!data?.length) return null;

  const vals  = data.map(d => Number(d[metric.key]) || 0);
  const min   = Math.min(...vals);
  const max   = Math.max(...vals);
  const pad   = (max - min) * 0.08 || 1;
  const first = vals[0];
  const last  = vals[vals.length - 1];
  const delta = last - first;
  const pct   = first !== 0 ? ((delta / first) * 100).toFixed(2) : null;
  const up    = delta >= 0;

  return (
    <Card style={{ marginBottom: 12 }}>
      <div style={s.chartHeader}>
        <div style={s.metricLabel}>{metric.label}</div>
        <div style={s.metricRight}>
          <span style={s.metricVal}>{metric.fmt(last)}</span>
          {pct !== null && (
            <span style={{ ...s.pct, color: up ? '#22c55e' : '#ef4444' }}>
              {up ? '+' : ''}{pct}%
            </span>
          )}
        </div>
      </div>
      <ResponsiveContainer width="100%" height={160}>
        <LineChart data={data} margin={{ top: 4, right: 4, left: 4, bottom: 4 }}>
          <CartesianGrid strokeDasharray="1 4" stroke="#1a1b2e" vertical={false} />
          <XAxis
            dataKey="created_at"
            tickFormatter={(v) => new Date(v).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            tick={{ fontSize: 10, fill: '#3a3c55' }}
            tickLine={false}
            axisLine={false}
            interval="preserveStartEnd"
          />
          <YAxis
            domain={[min - pad, max + pad]}
            tickFormatter={metric.fmt}
            tick={{ fontSize: 10, fill: '#3a3c55' }}
            tickLine={false}
            axisLine={false}
            width={88}
          />
          <Tooltip content={<CustomTooltip metric={metric} />} />
          <Line
            type="monotone"
            dataKey={metric.key}
            stroke={metric.color}
            strokeWidth={1.5}
            dot={false}
            activeDot={{ r: 3, fill: metric.color, strokeWidth: 0 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}

export default function CoinHistoryPage({ params = {} }) {
  const [coinNames, setCoinNames] = useState([]);
  const [selected, setSelected]   = useState(params.coin ?? '');
  const [range, setRange]         = useState('24h');
  const [data, setData]           = useState([]);
  const [loading, setLoading]     = useState(false);

  useEffect(() => {
    api.coinNames().then((rows) => {
      setCoinNames(rows);
      if (!params.coin && rows.length) setSelected(rows[0].name);
    });
  }, []);

  const load = useCallback(async () => {
    if (!selected) return;
    setLoading(true);
    try {
      const rows = await api.coinHistory(selected, range);
      setData(rows);
    } finally {
      setLoading(false);
    }
  }, [selected, range]);

  useEffect(() => { load(); }, [load]);
  useEffect(() => {
    if (!selected) return;
    const id = setInterval(load, 30_000);
    return () => clearInterval(id);
  }, [load, selected]);

  return (
    <div>
      <PageHeader
        title="Coin History"
        subtitle="Time series · refresh 30s"
        action={
          <div style={s.controls}>
            <select style={s.select} value={selected} onChange={(e) => setSelected(e.target.value)}>
              {coinNames.map(({ name, tag }) => (
                <option key={name} value={name}>{name} ({tag})</option>
              ))}
            </select>
            <div style={s.seg}>
              {RANGES.map((r) => (
                <button
                  key={r}
                  style={{ ...s.segBtn, ...(range === r ? s.segActive : {}) }}
                  onClick={() => setRange(r)}
                >
                  {r}
                </button>
              ))}
            </div>
          </div>
        }
      />

      {loading && <Spinner />}

      {!loading && data.length === 0 && (
        <Card><p style={{ color: '#4a4c6a', fontSize: 13 }}>No history data for this coin / range.</p></Card>
      )}

      {!loading && METRICS.map((metric) => (
        <MetricChart key={metric.key} data={data} metric={metric} />
      ))}
    </div>
  );
}

const s = {
  chartHeader: {
    display: 'flex',
    alignItems: 'baseline',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  metricLabel: { fontSize: 11, fontWeight: 600, color: '#6b6d8a', textTransform: 'uppercase', letterSpacing: '0.7px' },
  metricRight: { display: 'flex', alignItems: 'baseline', gap: 8 },
  metricVal:   { fontSize: 16, fontWeight: 700, color: '#e4e4f0', fontVariantNumeric: 'tabular-nums' },
  pct:         { fontSize: 12, fontWeight: 600 },

  controls: { display: 'flex', alignItems: 'center', gap: 10 },
  select: {
    padding: '6px 10px',
    borderRadius: 7,
    border: '1px solid #1e2038',
    fontSize: 12,
    color: '#c8c8e0',
    background: '#111221',
    cursor: 'pointer',
    outline: 'none',
  },
  seg: {
    display: 'flex',
    background: '#0d0e1a',
    borderRadius: 7,
    padding: 2,
    gap: 2,
    border: '1px solid #1e2038',
  },
  segBtn: {
    padding: '4px 9px',
    borderRadius: 5,
    border: 'none',
    background: 'transparent',
    fontSize: 11,
    fontWeight: 500,
    color: '#4a4c6a',
    cursor: 'pointer',
    transition: 'all 0.15s',
  },
  segActive: {
    background: '#1a1b2e',
    color: '#00d4aa',
  },
};
