import { useState, useEffect, useCallback, useMemo } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer,
} from 'recharts';
import { api } from '../api';
import Card from '../components/Card';
import PageHeader from '../components/PageHeader';
import Spinner from '../components/Spinner';

const RANGES  = ['1h', '24h', '7d', '30d', 'all'];
const METRICS = [
  { key: 'usd',              label: 'Price USD',       fmt: (v) => `$${Number(v).toLocaleString('en-US', { maximumFractionDigits: 6 })}` },
  { key: 'market_cap',       label: 'Market Cap',      fmt: (v) => `$${Number(v).toLocaleString('en-US', { notation: 'compact', maximumFractionDigits: 2 })}` },
  { key: 'difficulty',       label: 'Difficulty',      fmt: (v) => Number(v).toLocaleString('en-US', { notation: 'compact', maximumFractionDigits: 2 }) },
  { key: 'network_hashrate', label: 'Net. Hashrate',   fmt: (v) => { const n = Number(v); if (n >= 1e15) return `${(n/1e15).toFixed(2)} PH/s`; if (n >= 1e12) return `${(n/1e12).toFixed(2)} TH/s`; if (n >= 1e9) return `${(n/1e9).toFixed(2)} GH/s`; return `${(n/1e6).toFixed(2)} MH/s`; } },
  { key: 'hash_usd',         label: 'Hash USD',        fmt: (v) => `$${Number(v).toExponential(3)}` },
  { key: 'emission_usd',     label: 'Emission USD',    fmt: (v) => `$${Number(v).toLocaleString('en-US', { maximumFractionDigits: 4 })}` },
];

// Finance colors palette for multi-line
const PALETTE = ['#00d4aa', '#6366f1', '#f59e0b', '#ef4444', '#a78bfa', '#34d399', '#f472b6', '#60a5fa', '#fb923c', '#e879f9'];

// Merge rows by rounded minute, one entry per time with values keyed by coin name
function mergeData(rows, coins, metricKey, normalize) {
  const round = (ts) => { const d = new Date(ts); d.setSeconds(0, 0); return d.toISOString(); };

  const byCoin = {};
  coins.forEach((c) => { byCoin[c] = {}; });
  rows.forEach((row) => {
    if (!byCoin[row.name]) return;
    const t = round(row.created_at);
    byCoin[row.name][t] = Number(row[metricKey]);
  });

  // First value per coin for normalization
  const firstVal = {};
  if (normalize) {
    coins.forEach((c) => {
      const times = Object.keys(byCoin[c]).sort();
      firstVal[c] = byCoin[c][times[0]] ?? 1;
    });
  }

  const allTimes = [...new Set(rows.map((r) => round(r.created_at)))].sort();
  return allTimes.map((t) => {
    const item = { time: t };
    coins.forEach((coin) => {
      const raw = byCoin[coin]?.[t] ?? null;
      if (raw == null) { item[coin] = null; return; }
      item[coin] = normalize ? ((raw - firstVal[coin]) / (firstVal[coin] || 1)) * 100 : raw;
    });
    return item;
  });
}

const CustomTooltip = ({ active, payload, label, metricFmt, normalize }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: '#0d0e1a', border: '1px solid #2a2c45', borderRadius: 8, padding: '10px 14px', fontSize: 12, minWidth: 160 }}>
      <div style={{ color: '#6b6d8a', marginBottom: 8, fontSize: 11 }}>{new Date(label).toLocaleString()}</div>
      {payload.map((p) => (
        <div key={p.dataKey} style={{ display: 'flex', justifyContent: 'space-between', gap: 16, marginBottom: 3 }}>
          <span style={{ color: p.color, fontWeight: 600 }}>{p.dataKey}</span>
          <span style={{ color: '#e4e4f0', fontVariantNumeric: 'tabular-nums' }}>
            {normalize ? `${Number(p.value).toFixed(2)}%` : metricFmt(p.value)}
          </span>
        </div>
      ))}
    </div>
  );
};

export default function MixedHistoryPage() {
  const [allCoins, setAllCoins]   = useState([]);
  const [selected, setSelected]   = useState([]);
  const [range, setRange]         = useState('24h');
  const [metric, setMetric]       = useState('usd');
  const [normalize, setNormalize] = useState(false);
  const [rawData, setRawData]     = useState([]);
  const [loading, setLoading]     = useState(false);
  const [filter, setFilter]       = useState('');

  useEffect(() => {
    api.coinNames().then((rows) => setAllCoins(rows));
  }, []);

  const load = useCallback(async () => {
    if (!selected.length) { setRawData([]); return; }
    setLoading(true);
    try {
      const rows = await api.coinHistoryMulti(selected, range);
      setRawData(rows);
    } finally {
      setLoading(false);
    }
  }, [selected, range]);

  useEffect(() => { load(); }, [load]);
  useEffect(() => {
    if (!selected.length) return;
    const id = setInterval(load, 30_000);
    return () => clearInterval(id);
  }, [load, selected]);

  const metricDef = METRICS.find((m) => m.key === metric) ?? METRICS[0];
  const chartData = useMemo(
    () => mergeData(rawData, selected, metric, normalize),
    [rawData, selected, metric, normalize]
  );

  const toggleCoin = (name) =>
    setSelected((prev) =>
      prev.includes(name) ? prev.filter((c) => c !== name) : [...prev, name]
    );

  const filteredCoins = useMemo(() => {
    const q = filter.toLowerCase();
    return allCoins.filter((c) => !q || c.name.toLowerCase().includes(q) || c.tag.toLowerCase().includes(q));
  }, [allCoins, filter]);

  return (
    <div>
      <PageHeader title="Compare Coins" subtitle="Multi-coin overlay · refresh 30s" />

      <div style={s.layout}>
        {/* ── Left: coin selector ── */}
        <div style={s.panel}>
          <div style={s.panelHead}>
            <span style={s.panelTitle}>Coins</span>
            <span style={s.panelCount}>{selected.length} selected</span>
          </div>
          <input
            style={s.searchInput}
            placeholder="Search…"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          />
          <div style={s.coinList}>
            {filteredCoins.map(({ name, tag }, i) => {
              const on = selected.includes(name);
              const color = PALETTE[selected.indexOf(name) % PALETTE.length];
              return (
                <button
                  key={name}
                  style={{ ...s.coinBtn, ...(on ? { ...s.coinBtnOn, borderColor: color } : {}) }}
                  onClick={() => toggleCoin(name)}
                >
                  {on && <span style={{ ...s.coinDot, background: color }} />}
                  <span style={s.coinName}>{name}</span>
                  <span style={s.coinTag}>{tag}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* ── Right: chart ── */}
        <div style={{ flex: 1, minWidth: 0 }}>
          {/* Controls */}
          <div style={s.controls}>
            <select style={s.select} value={metric} onChange={(e) => setMetric(e.target.value)}>
              {METRICS.map((m) => (
                <option key={m.key} value={m.key}>{m.label}</option>
              ))}
            </select>
            <div style={s.seg}>
              {RANGES.map((r) => (
                <button key={r} style={{ ...s.segBtn, ...(range === r ? s.segActive : {}) }} onClick={() => setRange(r)}>{r}</button>
              ))}
            </div>
            <button
              style={{ ...s.normBtn, ...(normalize ? s.normBtnOn : {}) }}
              onClick={() => setNormalize((v) => !v)}
              title="Normalize to % change from start"
            >
              % Change
            </button>
          </div>

          {/* Chart card */}
          <Card style={{ marginTop: 12 }}>
            {!selected.length ? (
              <div style={s.empty}>Select coins on the left to compare them.</div>
            ) : loading ? (
              <Spinner />
            ) : chartData.length === 0 ? (
              <div style={s.empty}>No data for selected range.</div>
            ) : (
              <ResponsiveContainer width="100%" height={420}>
                <LineChart data={chartData} margin={{ top: 8, right: 8, left: 8, bottom: 8 }}>
                  <CartesianGrid strokeDasharray="1 4" stroke="#1a1b2e" vertical={false} />
                  <XAxis
                    dataKey="time"
                    tickFormatter={(v) => new Date(v).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    tick={{ fontSize: 10, fill: '#3a3c55' }}
                    tickLine={false}
                    axisLine={false}
                    interval="preserveStartEnd"
                  />
                  <YAxis
                    tickFormatter={(v) => normalize ? `${v.toFixed(1)}%` : metricDef.fmt(v)}
                    tick={{ fontSize: 10, fill: '#3a3c55' }}
                    tickLine={false}
                    axisLine={false}
                    width={90}
                  />
                  <Tooltip content={<CustomTooltip metricFmt={metricDef.fmt} normalize={normalize} />} />
                  <Legend
                    wrapperStyle={{ fontSize: 11, paddingTop: 12 }}
                    formatter={(v) => <span style={{ color: '#c8c8e0' }}>{v}</span>}
                  />
                  {selected.map((coin, i) => (
                    <Line
                      key={coin}
                      type="monotone"
                      dataKey={coin}
                      stroke={PALETTE[i % PALETTE.length]}
                      strokeWidth={1.5}
                      dot={false}
                      activeDot={{ r: 3, strokeWidth: 0 }}
                      connectNulls={false}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}

const s = {
  layout: { display: 'flex', gap: 16, alignItems: 'flex-start' },

  panel: {
    width: 200,
    flexShrink: 0,
    background: '#111221',
    borderRadius: 12,
    border: '1px solid #1e2038',
    padding: '14px 12px',
    display: 'flex',
    flexDirection: 'column',
    gap: 10,
  },
  panelHead: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
  panelTitle: { fontSize: 11, fontWeight: 600, color: '#6b6d8a', textTransform: 'uppercase', letterSpacing: '0.7px' },
  panelCount:  { fontSize: 11, color: '#00d4aa' },

  searchInput: {
    padding: '6px 10px',
    borderRadius: 7,
    border: '1px solid #1e2038',
    fontSize: 12,
    color: '#c8c8e0',
    background: '#0d0e1a',
    outline: 'none',
    width: '100%',
  },

  coinList: { display: 'flex', flexDirection: 'column', gap: 4, maxHeight: 520, overflowY: 'auto' },
  coinBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: 6,
    padding: '6px 8px',
    borderRadius: 7,
    border: '1px solid #1e2038',
    background: 'transparent',
    cursor: 'pointer',
    transition: 'all 0.15s',
    textAlign: 'left',
  },
  coinBtnOn: { background: '#131425' },
  coinDot:   { width: 6, height: 6, borderRadius: '50%', flexShrink: 0 },
  coinName:  { fontSize: 12, fontWeight: 500, color: '#c8c8e0', flex: 1 },
  coinTag:   { fontSize: 10, color: '#4a4c6a' },

  controls: { display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' },
  select: {
    padding: '6px 10px', borderRadius: 7, border: '1px solid #1e2038',
    fontSize: 12, color: '#c8c8e0', background: '#111221', cursor: 'pointer', outline: 'none',
  },
  seg: { display: 'flex', background: '#0d0e1a', borderRadius: 7, padding: 2, gap: 2, border: '1px solid #1e2038' },
  segBtn: {
    padding: '4px 9px', borderRadius: 5, border: 'none', background: 'transparent',
    fontSize: 11, fontWeight: 500, color: '#4a4c6a', cursor: 'pointer', transition: 'all 0.15s',
  },
  segActive: { background: '#1a1b2e', color: '#00d4aa' },

  normBtn: {
    padding: '5px 10px', borderRadius: 7, border: '1px solid #1e2038',
    fontSize: 11, fontWeight: 500, color: '#4a4c6a', background: 'transparent', cursor: 'pointer', transition: 'all 0.15s',
  },
  normBtnOn: { background: '#1a1b2e', color: '#00d4aa', borderColor: '#00d4aa44' },

  empty: { color: '#4a4c6a', fontSize: 13, padding: '48px 0', textAlign: 'center' },
};
