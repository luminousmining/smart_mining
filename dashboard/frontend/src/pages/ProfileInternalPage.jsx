import { useState, useEffect, useCallback } from 'react';
import { api } from '../api';
import Card from '../components/Card';
import PageHeader from '../components/PageHeader';
import Spinner from '../components/Spinner';

const fmtUsd = (v) =>
  v != null ? `$${Number(v).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : '—';

const fmtCompact = (v) =>
  v != null ? `$${Number(v).toLocaleString('en-US', { notation: 'compact', maximumFractionDigits: 2 })}` : '—';

const fmtExp = (v) =>
  v != null ? `$${Number(v).toExponential(3)}` : '—';

const fmtHash = (v) => {
  if (v == null) return '—';
  const n = Number(v);
  if (n >= 1e18) return `${(n / 1e18).toFixed(2)} EH/s`;
  if (n >= 1e15) return `${(n / 1e15).toFixed(2)} PH/s`;
  if (n >= 1e12) return `${(n / 1e12).toFixed(2)} TH/s`;
  if (n >= 1e9)  return `${(n / 1e9).toFixed(2)} GH/s`;
  if (n >= 1e6)  return `${(n / 1e6).toFixed(2)} MH/s`;
  return `${n.toFixed(2)} H/s`;
};

const PROFILES = [
  { key: 'emission',         title: 'Emission USD',       valueKey: 'emission_usd',     fmt: fmtUsd },
  { key: 'hash_usd',         title: 'Hash USD',           valueKey: 'hash_usd',         fmt: fmtExp },
  { key: 'usd_sec',          title: 'USD / sec',          valueKey: 'usd_sec',          fmt: (v) => v != null ? `$${Number(v).toFixed(8)}/s` : '—' },
  { key: 'market_cap',       title: 'Market Cap',         valueKey: 'market_cap',       fmt: fmtCompact },
  { key: 'network_hashrate', title: 'Network Hashrate',   valueKey: 'network_hashrate', fmt: fmtHash },
];

export default function ProfileInternalPage() {
  const [selected, setSelected] = useState('emission');
  const [rows, setRows]         = useState([]);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState(null);

  const profile = PROFILES.find((p) => p.key === selected) ?? PROFILES[0];

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.profileData(selected);
      setRows(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [selected]);

  // Refetch on mount and every time a different profile is selected.
  useEffect(() => { load(); }, [load]);

  return (
    <div>
      <PageHeader
        title="Profile"
        subtitle="Classements de rentabilité (procédures stockées)"
        action={
          <div style={s.controls}>
            <select style={s.select} value={selected} onChange={(e) => setSelected(e.target.value)}>
              {PROFILES.map((p) => (
                <option key={p.key} value={p.key}>{p.title}</option>
              ))}
            </select>
            <button onClick={load} style={s.refreshBtn} disabled={loading} title="Refresh">↺</button>
          </div>
        }
      />

      {error && <div style={s.error}>{error}</div>}

      {loading ? (
        <Spinner />
      ) : (
        <Card title={profile.title} subtitle={`${rows.length} coins`}>
          {rows.length === 0 ? (
            <p style={{ color: '#4a4c6a', fontSize: 13 }}>No data.</p>
          ) : (
            <table style={s.table}>
              <thead>
                <tr>
                  <th style={{ ...s.th, textAlign: 'center', width: 48 }}>#</th>
                  <th style={s.th}>Coin</th>
                  <th style={s.th}>Tag</th>
                  <th style={{ ...s.th, textAlign: 'right' }}>{profile.title}</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row, i) => (
                  <tr key={`${row.name}-${i}`} style={s.tr}>
                    <td style={{ ...s.td, textAlign: 'center', color: '#4a4c6a' }}>{i + 1}</td>
                    <td style={{ ...s.td, fontWeight: 600, color: '#e4e4f0' }}>{row.name}</td>
                    <td style={s.td}><span style={s.tagBadge}>{row.tag}</span></td>
                    <td style={{ ...s.td, textAlign: 'right', color: '#00d4aa', fontVariantNumeric: 'tabular-nums', fontWeight: 500 }}>
                      {profile.fmt(row[profile.valueKey])}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </Card>
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
  refreshBtn: {
    padding: '5px 10px', borderRadius: 6, border: '1px solid #1e2038',
    background: 'transparent', color: '#00d4aa', fontSize: 14, cursor: 'pointer',
  },
  table: { width: '100%', borderCollapse: 'collapse' },
  th: {
    padding: '8px 12px', fontSize: 10, fontWeight: 600, color: '#4a4c6a',
    textTransform: 'uppercase', letterSpacing: '0.6px', textAlign: 'left',
    borderBottom: '1px solid #1a1b2e',
  },
  tr: { borderBottom: '1px solid #12132240' },
  td: { padding: '9px 12px', fontSize: 13, color: '#c4c4d4' },
  tagBadge: {
    padding: '2px 7px', borderRadius: 4, fontSize: 11, fontWeight: 600,
    background: '#0d2030', color: '#00d4aa', letterSpacing: '0.3px',
  },
  error: {
    background: '#dc262620', border: '1px solid #ef444440', borderRadius: 8,
    color: '#ef4444', padding: '10px 14px', marginBottom: 12, fontSize: 13,
  },
};
