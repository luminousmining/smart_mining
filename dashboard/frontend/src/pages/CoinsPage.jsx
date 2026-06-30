import { useState, useEffect, useCallback, useMemo } from 'react';
import { api } from '../api';
import Card from '../components/Card';
import DataTable from '../components/DataTable';
import PageHeader from '../components/PageHeader';
import Spinner from '../components/Spinner';
import Tooltip from '../components/Tooltip';

const fmtUsd = (v) =>
  v != null ? `$${Number(v).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 6 })}` : null;

const fmtHash = (v) => {
  if (v == null) return null;
  const n = Number(v);
  if (n >= 1e18) return `${(n / 1e18).toFixed(2)} EH/s`;
  if (n >= 1e15) return `${(n / 1e15).toFixed(2)} PH/s`;
  if (n >= 1e12) return `${(n / 1e12).toFixed(2)} TH/s`;
  if (n >= 1e9)  return `${(n / 1e9).toFixed(2)} GH/s`;
  if (n >= 1e6)  return `${(n / 1e6).toFixed(2)} MH/s`;
  if (n >= 1e3)  return `${(n / 1e3).toFixed(2)} KH/s`;
  return `${n.toFixed(2)} H/s`;
};

// Data-availability filters. Missing values are stored as 0 (the aggregator
// converts None -> 0) and NUMERIC columns come back as strings, so `hasData`
// normalises with Number() to handle 0, "0", null and undefined uniformly.
const DATA_FILTERS = [
  { key: 'usd',              label: 'USD' },
  { key: 'market_cap',       label: 'Market Cap' },
  { key: 'difficulty',       label: 'Difficulty' },
  { key: 'network_hashrate', label: 'Network' },
  { key: 'emission_usd',     label: 'Emission' },
];

const hasData = (v) => Number(v) > 0;

function buildColumns(onNavigate) {
  return [
    {
      key: '_actions',
      label: '',
      render: (_, row) => (
        <button
          style={s.histBtn}
          title="View History"
          onClick={() => onNavigate('history-coin', { coin: row.name })}
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
          </svg>
        </button>
      ),
    },
    {
      key: 'name',
      label: 'Coin',
      render: (v, row) => {
        const hasInfo = row.tag || row.algorithm;
        const popup = hasInfo ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {row.tag && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <span style={{ fontSize: 10, color: '#6b6d8a', textTransform: 'uppercase', letterSpacing: '0.4px' }}>Tag</span>
                <span style={{ padding: '2px 7px', borderRadius: 4, fontSize: 11, fontWeight: 600, background: '#0d2030', color: '#00d4aa', letterSpacing: '0.3px' }}>
                  {row.tag}
                </span>
              </div>
            )}
            {row.algorithm && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <span style={{ fontSize: 10, color: '#6b6d8a', textTransform: 'uppercase', letterSpacing: '0.4px' }}>Algo</span>
                <span style={{ padding: '2px 7px', borderRadius: 4, fontSize: 11, background: '#181828', color: '#7070a0' }}>
                  {row.algorithm}
                </span>
              </div>
            )}
          </div>
        ) : null;
        return (
          <Tooltip content={popup}>
            <strong style={{ color: '#e4e4f0', fontWeight: 600, cursor: hasInfo ? 'help' : 'default' }}>{v}</strong>
          </Tooltip>
        );
      },
    },
    {
      key: 'usd',
      label: 'Price USD',
      align: 'right',
      render: (v) => v != null ? <span style={{ color: '#e4e4f0', fontWeight: 500 }}>{fmtUsd(v)}</span> : null,
    },
    { key: 'market_cap',       label: 'Market Cap',    align: 'right', render: fmtUsd },
    { key: 'difficulty',       label: 'Difficulty',    align: 'right', render: (v) => v != null ? Number(v).toLocaleString('en-US', { notation: 'compact', maximumFractionDigits: 2 }) : null },
    { key: 'network_hashrate', label: 'Net. Hashrate', align: 'right', render: fmtHash },
    { key: 'emission_usd', label: 'Emission USD', align: 'right', render: fmtUsd },
  ];
}

export default function CoinsPage({ onNavigate, refreshInterval = 30_000 }) {
  const [data, setData]       = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [filter, setFilter]   = useState('');
  const [active, setActive]   = useState([]); // keys of enabled data filters

  const toggle = (key) =>
    setActive((prev) => prev.includes(key) ? prev.filter((k) => k !== key) : [...prev, key]);

  const load = useCallback(async () => {
    try {
      const rows = await api.coins();
      setData(rows);
      setLastUpdate(new Date());
    } catch { /* keep previous */ } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    const id = setInterval(load, refreshInterval ?? 30_000);
    return () => clearInterval(id);
  }, [load]);

  const filtered = useMemo(() => {
    const q = filter.trim().toLowerCase();
    return data.filter((r) => {
      if (q && !(
        r.name?.toLowerCase().includes(q) ||
        r.tag?.toLowerCase().includes(q) ||
        r.algorithm?.toLowerCase().includes(q)
      )) return false;
      // every enabled filter requires that field to hold data (> 0)
      return active.every((key) => hasData(r[key]));
    });
  }, [data, filter, active]);

  const columns = useMemo(() => buildColumns(onNavigate), [onNavigate]);

  const sub = lastUpdate ? `Updated ${lastUpdate.toLocaleTimeString()} · ${data.length} coins · refresh 30s` : 'Loading…';

  return (
    <div>
      <PageHeader
        title="Coins"
        subtitle={sub}
        action={
          <input
            style={s.search}
            placeholder="Filter coins…"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          />
        }
      />
      <Card>
        {loading ? <Spinner /> : (
          <>
            <div style={s.filterBar}>
              <span style={s.filterBarLabel}>Require data</span>
              {DATA_FILTERS.map((f) => {
                const on = active.includes(f.key);
                return (
                  <button
                    key={f.key}
                    style={{ ...s.toggleBtn, ...(on ? s.toggleBtnOn : {}) }}
                    onClick={() => toggle(f.key)}
                  >
                    {on && <span style={{ marginRight: 4 }}>✓</span>}{f.label}
                  </button>
                );
              })}
              <Tooltip content={
                <div style={{ maxWidth: 240, lineHeight: 1.5, color: '#c8c8e0' }}>
                  Filters by data availability. When a field is enabled, a coin is shown
                  only if it has a value for that field (greater than 0). Coins missing
                  that data (e.g. BTC has no difficulty) are hidden. Enabling several
                  fields requires all of them. With nothing enabled, all coins are shown.
                </div>
              }>
                <span style={s.infoIcon}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="10" />
                    <path d="M12 16v-4M12 8h.01" />
                  </svg>
                </span>
              </Tooltip>
            </div>
            {(filter || active.length > 0) && (
              <div style={s.filterInfo}>
                {filtered.length} / {data.length} coins
              </div>
            )}
            <DataTable columns={columns} rows={filtered} />
          </>
        )}
      </Card>
    </div>
  );
}

const s = {
  search: {
    padding: '7px 12px',
    borderRadius: 8,
    border: '1px solid #1e2038',
    fontSize: 12,
    color: '#c8c8e0',
    background: '#111221',
    outline: 'none',
    width: 180,
  },
  filterInfo: {
    fontSize: 11,
    color: '#4a4c6a',
    marginBottom: 10,
  },
  filterBar: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    flexWrap: 'wrap',
    marginBottom: 14,
  },
  filterBarLabel: {
    fontSize: 11,
    fontWeight: 600,
    color: '#6b6d8a',
    textTransform: 'uppercase',
    letterSpacing: '0.7px',
    marginRight: 2,
  },
  toggleBtn: {
    display: 'flex',
    alignItems: 'center',
    padding: '6px 12px',
    borderRadius: 7,
    border: '1px solid #1e2038',
    fontSize: 12,
    fontWeight: 500,
    color: '#4a4c6a',
    background: 'transparent',
    cursor: 'pointer',
    transition: 'all 0.15s',
  },
  toggleBtnOn: {
    background: '#1a1b2e',
    color: '#00d4aa',
    borderColor: '#00d4aa44',
  },
  infoIcon: {
    display: 'flex',
    alignItems: 'center',
    color: '#4a4c6a',
    cursor: 'help',
  },
  histBtn: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: 24,
    height: 24,
    borderRadius: 6,
    border: '1px solid #1e2038',
    background: 'transparent',
    color: '#4a4c6a',
    cursor: 'pointer',
    transition: 'all 0.15s',
  },
};
