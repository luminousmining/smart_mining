import { useState, useEffect, useCallback } from 'react';
import { api } from '../api';

const STATUS_FILTER = [
  { label: 'All',     value: null },
  { label: 'Success', value: true },
  { label: 'Failed',  value: false },
];

function fmt(ts) {
  if (!ts) return '—';
  const d = new Date(ts);
  return d.toLocaleString('fr-FR', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
  });
}

export default function ApiHistoryPage({ refreshInterval }) {
  const [rows, setRows]         = useState([]);
  const [apiNames, setApiNames] = useState([]);
  const [apiName, setApiName]   = useState('');
  const [statusFilter, setStatusFilter] = useState(null);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState(null);

  useEffect(() => {
    api.apiHistoryNames().then(setApiNames).catch(() => {});
  }, []);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    api.apiHistory(apiName || undefined, statusFilter, 200)
      .then(data => { setRows(data); setLoading(false); })
      .catch(err => { setError(err.message); setLoading(false); });
  }, [apiName, statusFilter]);

  useEffect(() => { load(); }, [load]);

  useEffect(() => {
    const id = setInterval(load, refreshInterval);
    return () => clearInterval(id);
  }, [load, refreshInterval]);

  const successCount = rows.filter(r => r.success).length;
  const failCount    = rows.filter(r => !r.success).length;

  return (
    <div>
      <div style={s.header}>
        <div>
          <h2 style={s.title}>API History</h2>
          <p style={s.sub}>Historique des appels API de l'aggregator</p>
        </div>

        <div style={s.badges}>
          <span style={{ ...s.badge, background: '#16a34a22', color: '#22c55e', border: '1px solid #22c55e44' }}>
            ✓ {successCount} succès
          </span>
          <span style={{ ...s.badge, background: '#dc262622', color: '#ef4444', border: '1px solid #ef444444' }}>
            ✗ {failCount} échec{failCount !== 1 ? 's' : ''}
          </span>
        </div>
      </div>

      {/* Filters */}
      <div style={s.filters}>
        <select
          value={apiName}
          onChange={e => setApiName(e.target.value)}
          style={s.select}
        >
          <option value=''>Toutes les APIs</option>
          {apiNames.map(n => <option key={n} value={n}>{n}</option>)}
        </select>

        <div style={s.statusBtns}>
          {STATUS_FILTER.map(({ label, value }) => (
            <button
              key={label}
              onClick={() => setStatusFilter(value)}
              style={{
                ...s.statusBtn,
                ...(statusFilter === value ? s.statusBtnActive : {}),
                ...(value === true  ? { color: statusFilter === true  ? '#22c55e' : '#4a4c6a' } : {}),
                ...(value === false ? { color: statusFilter === false ? '#ef4444' : '#4a4c6a' } : {}),
              }}
            >
              {label}
            </button>
          ))}
        </div>

        <button onClick={load} style={s.refreshBtn} disabled={loading}>
          {loading ? '...' : '↺ Rafraîchir'}
        </button>
      </div>

      {error && <div style={s.error}>{error}</div>}

      <div style={s.tableWrap}>
        <table style={s.table}>
          <thead>
            <tr>
              <th style={s.th}>Heure</th>
              <th style={s.th}>API</th>
              <th style={{ ...s.th, textAlign: 'center' }}>Statut</th>
              <th style={{ ...s.th, textAlign: 'right' }}>Durée</th>
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 && !loading && (
              <tr>
                <td colSpan={4} style={{ ...s.td, textAlign: 'center', color: '#4a4c6a', padding: '40px 0' }}>
                  Aucun enregistrement
                </td>
              </tr>
            )}
            {rows.map(row => (
              <tr key={row.id} style={s.tr}>
                <td style={{ ...s.td, color: '#7a7c9a', fontSize: 12 }}>{fmt(row.called_at)}</td>
                <td style={{ ...s.td, fontFamily: 'monospace', color: '#c4c4d4' }}>{row.api_name}</td>
                <td style={{ ...s.td, textAlign: 'center' }}>
                  {row.success
                    ? <span style={s.ok}>✓ OK</span>
                    : <span style={s.ko}>✗ KO</span>
                  }
                </td>
                <td style={{ ...s.td, textAlign: 'right', color: '#7a7c9a', fontVariantNumeric: 'tabular-nums' }}>
                  {row.duration_ms} ms
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const s = {
  header: {
    display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start',
    marginBottom: 20, flexWrap: 'wrap', gap: 12,
  },
  title: { fontSize: 20, fontWeight: 700, color: '#e4e4f0', margin: 0 },
  sub:   { fontSize: 12, color: '#4a4c6a', margin: '4px 0 0' },
  badges: { display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' },
  badge: { fontSize: 12, fontWeight: 600, padding: '4px 10px', borderRadius: 6 },
  filters: {
    display: 'flex', gap: 8, alignItems: 'center', marginBottom: 16, flexWrap: 'wrap',
  },
  select: {
    background: '#0f1020', border: '1px solid #1e2038', borderRadius: 6,
    color: '#c4c4d4', padding: '6px 10px', fontSize: 12, cursor: 'pointer',
  },
  statusBtns: { display: 'flex', gap: 4 },
  statusBtn: {
    padding: '5px 12px', borderRadius: 6, border: '1px solid #1e2038',
    background: 'transparent', color: '#4a4c6a', fontSize: 12, fontWeight: 500,
    cursor: 'pointer',
  },
  statusBtnActive: { background: '#1a1b2e', borderColor: '#2e3050' },
  refreshBtn: {
    marginLeft: 'auto', padding: '5px 14px', borderRadius: 6,
    border: '1px solid #1e2038', background: 'transparent',
    color: '#00d4aa', fontSize: 12, fontWeight: 600, cursor: 'pointer',
  },
  error: {
    background: '#dc262620', border: '1px solid #ef444440', borderRadius: 8,
    color: '#ef4444', padding: '10px 14px', marginBottom: 12, fontSize: 13,
  },
  tableWrap: {
    background: '#0d0e1c', border: '1px solid #1a1b2e', borderRadius: 10, overflow: 'hidden',
  },
  table: { width: '100%', borderCollapse: 'collapse' },
  th: {
    padding: '10px 14px', fontSize: 11, fontWeight: 600, color: '#4a4c6a',
    textTransform: 'uppercase', letterSpacing: '0.6px', textAlign: 'left',
    borderBottom: '1px solid #1a1b2e', background: '#080910',
  },
  tr: { borderBottom: '1px solid #12132280' },
  td: { padding: '10px 14px', fontSize: 13, color: '#c4c4d4' },
  ok: {
    display: 'inline-block', padding: '2px 8px', borderRadius: 4,
    background: '#16a34a22', color: '#22c55e', fontSize: 12, fontWeight: 600,
  },
  ko: {
    display: 'inline-block', padding: '2px 8px', borderRadius: 4,
    background: '#dc262622', color: '#ef4444', fontSize: 12, fontWeight: 600,
  },
};
