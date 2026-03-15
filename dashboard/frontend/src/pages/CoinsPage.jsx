import { useState, useEffect, useCallback, useMemo } from 'react';
import { api } from '../api';
import Card from '../components/Card';
import DataTable from '../components/DataTable';
import PageHeader from '../components/PageHeader';
import Spinner from '../components/Spinner';

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

function buildColumns(onNavigate) {
  return [
    {
      key: '_actions',
      label: '',
      render: (_, row) => (
        <button
          style={s.histBtn}
          title="View History"
          onClick={() => onNavigate('history', { coin: row.name })}
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
      render: (v) => <strong style={{ color: '#e4e4f0', fontWeight: 600 }}>{v}</strong>,
    },
    {
      key: 'tag',
      label: 'Tag',
      render: (v) => v ? (
        <span style={{ padding: '2px 7px', borderRadius: 4, fontSize: 11, fontWeight: 600, background: '#0d2030', color: '#00d4aa', letterSpacing: '0.3px' }}>
          {v}
        </span>
      ) : null,
    },
    {
      key: 'algorithm',
      label: 'Algorithm',
      render: (v) => v ? (
        <span style={{ padding: '2px 7px', borderRadius: 4, fontSize: 11, background: '#181828', color: '#7070a0' }}>
          {v}
        </span>
      ) : null,
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
    {
      key: 'hash_usd',
      label: 'Hash USD',
      align: 'right',
      render: (v) => v != null ? <span style={{ color: '#00d4aa' }}>${Number(v).toExponential(3)}</span> : null,
    },
    { key: 'emission_usd', label: 'Emission USD', align: 'right', render: fmtUsd },
  ];
}

export default function CoinsPage({ onNavigate }) {
  const [data, setData]       = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [filter, setFilter]   = useState('');

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
    const id = setInterval(load, 30_000);
    return () => clearInterval(id);
  }, [load]);

  const filtered = useMemo(() => {
    if (!filter.trim()) return data;
    const q = filter.toLowerCase();
    return data.filter(
      (r) =>
        r.name?.toLowerCase().includes(q) ||
        r.tag?.toLowerCase().includes(q) ||
        r.algorithm?.toLowerCase().includes(q)
    );
  }, [data, filter]);

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
            {filter && (
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
