import { useState, useEffect, useCallback, useMemo } from 'react';

const PAGE_SIZE = 50;
import {
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell,
} from 'recharts';
import { api } from '../api';
import Card from '../components/Card';
import PageHeader from '../components/PageHeader';
import Spinner from '../components/Spinner';

const STATUS_FILTER = [
  { label: 'Tous',    value: null },
  { label: 'Succès',  value: true },
  { label: 'Échecs',  value: false },
];

const RANGE_OPTIONS = [
  { label: '1h',   value: 1 },
  { label: '6h',   value: 6 },
  { label: '24h',  value: 24 },
  { label: '7j',   value: 168 },
  { label: '30j',  value: 720 },
  { label: 'Tout', value: null },
];

function fmt(ts) {
  if (!ts) return '—';
  const d = new Date(ts);
  return d.toLocaleString('fr-FR', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
  });
}

function fmtTime(ts) {
  const d = new Date(ts);
  return d.toLocaleString('fr-FR', {
    day: '2-digit', month: '2-digit',
    hour: '2-digit', minute: '2-digit',
  });
}

const TimelineTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0]?.payload;
  if (!d) return null;
  return (
    <div style={{
      background: '#0d0e1a', border: '1px solid #2a2c45',
      borderRadius: 8, padding: '10px 14px', fontSize: 12,
    }}>
      <div style={{ color: '#6b6d8a', marginBottom: 4 }}>{fmt(d.called_at)}</div>
      <div style={{ fontFamily: 'monospace', color: '#c4c4d4', marginBottom: 4 }}>{d.api_name}</div>
      <div style={{ color: d.success ? '#22c55e' : '#ef4444', fontWeight: 600 }}>
        {d.success ? '✓ Succès' : '✗ Échec'} — {d.duration_ms} ms
      </div>
      {d.message && <div style={{ color: '#7a7c9a', marginTop: 4, maxWidth: 280, wordBreak: 'break-word' }}>{d.message}</div>}
    </div>
  );
};

export default function ApiHistoryPage() {
  const [rows, setRows]         = useState([]);
  const [apiNames, setApiNames] = useState([]);
  const [apiName, setApiName]   = useState('');
  const [statusFilter, setStatusFilter] = useState(null);
  const [rangeHours, setRangeHours]     = useState(168);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState(null);
  const [view, setView]         = useState('timeline'); // 'timeline' | 'table'
  const [tablePage, setTablePage] = useState(0);

  useEffect(() => {
    api.apiHistoryNames().then(setApiNames).catch(() => {});
  }, []);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    setTablePage(0);
    const from = rangeHours != null ? new Date(Date.now() - rangeHours * 3600_000).toISOString() : undefined;
    api.apiHistory(apiName || undefined, statusFilter, 5000, from)
      .then(data => { setRows(data); setLoading(false); })
      .catch(err => { setError(err.message); setLoading(false); });
  }, [apiName, statusFilter, rangeHours]);

  useEffect(() => { load(); }, [load]);

  const successCount = rows.filter(r => r.success).length;
  const failCount    = rows.filter(r => !r.success).length;
  const totalPages   = Math.max(1, Math.ceil(rows.length / PAGE_SIZE));
  const pagedRows    = useMemo(
    () => rows.slice(tablePage * PAGE_SIZE, (tablePage + 1) * PAGE_SIZE),
    [rows, tablePage]
  );

  // Prepare timeline data: map api_name to a Y index
  const { chartData, apiIndex } = useMemo(() => {
    const names = [...new Set(rows.map(r => r.api_name))].sort();
    const idx = Object.fromEntries(names.map((n, i) => [n, i]));
    const data = rows.map(r => ({
      ...r,
      ts: new Date(r.called_at).getTime(),
      y: idx[r.api_name],
    }));
    return { chartData: data, apiIndex: idx };
  }, [rows]);

  const apiLabels = Object.keys(apiIndex);

  return (
    <div>
      <PageHeader
        title="API History"
        subtitle="Historique des appels API de l'aggregator"
        action={
          <div style={s.badges}>
            <span style={{ ...s.badge, background: '#16a34a22', color: '#22c55e', border: '1px solid #22c55e44' }}>
              ✓ {successCount}
            </span>
            <span style={{ ...s.badge, background: '#dc262622', color: '#ef4444', border: '1px solid #ef444444' }}>
              ✗ {failCount}
            </span>
          </div>
        }
      />

      {/* Filters */}
      <div style={s.filters}>
        <select value={apiName} onChange={e => setApiName(e.target.value)} style={s.select}>
          <option value=''>Toutes les APIs</option>
          {apiNames.map(n => <option key={n} value={n}>{n}</option>)}
        </select>

        <div style={s.btnGroup}>
          {STATUS_FILTER.map(({ label, value }) => (
            <button
              key={label}
              onMouseDown={(e) => e.preventDefault()}
              onClick={() => setStatusFilter(value)}
              style={{
                ...s.btn,
                ...(statusFilter === value ? s.btnActive : {}),
                ...(value === true  ? { color: statusFilter === true  ? '#22c55e' : '#4a4c6a' } : {}),
                ...(value === false ? { color: statusFilter === false ? '#ef4444' : '#4a4c6a' } : {}),
              }}
            >
              {label}
            </button>
          ))}
        </div>

        <div style={s.btnGroup}>
          {RANGE_OPTIONS.map(({ label, value }) => (
            <button
              key={label}
              onMouseDown={(e) => e.preventDefault()}
              onClick={() => setRangeHours(value)}
              style={{
                ...s.btn,
                ...(rangeHours === value ? s.btnActive : {}),
              }}
            >
              {label}
            </button>
          ))}
        </div>

        <div style={{ ...s.btnGroup, marginLeft: 'auto' }}>
          <button
            onMouseDown={(e) => e.preventDefault()}
            onClick={() => setView('timeline')}
            style={{ ...s.btn, ...(view === 'timeline' ? s.btnActive : {}) }}
          >
            Timeline
          </button>
          <button
            onMouseDown={(e) => e.preventDefault()}
            onClick={() => setView('table')}
            style={{ ...s.btn, ...(view === 'table' ? s.btnActive : {}) }}
          >
            Table
          </button>
        </div>

        <button onMouseDown={(e) => e.preventDefault()} onClick={load} style={s.refreshBtn} disabled={loading}>
          {loading ? '...' : '↺'}
        </button>
      </div>

      {error && <div style={s.error}>{error}</div>}
      {loading && rows.length === 0 && <Spinner />}

      {/* Timeline View */}
      {view === 'timeline' && rows.length > 0 && (
        <Card title="Timeline" subtitle={`${rows.length} appels`}>
          <ResponsiveContainer width="100%" height={Math.max(200, apiLabels.length * 40 + 60)}>
            <ScatterChart margin={{ top: 10, right: 20, bottom: 20, left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1a1b2e" />
              <XAxis
                dataKey="ts"
                type="number"
                domain={['dataMin', 'dataMax']}
                tickFormatter={fmtTime}
                stroke="#2a2c45"
                tick={{ fill: '#4a4c6a', fontSize: 10 }}
                scale="time"
              />
              <YAxis
                dataKey="y"
                type="number"
                domain={[-0.5, apiLabels.length - 0.5]}
                ticks={apiLabels.map((_, i) => i)}
                tickFormatter={i => apiLabels[i] || ''}
                stroke="#2a2c45"
                tick={{ fill: '#7a7c9a', fontSize: 11, fontFamily: 'monospace' }}
                width={100}
              />
              <Tooltip content={<TimelineTooltip />} cursor={false} />
              <Scatter data={chartData} shape="circle">
                {chartData.map((entry, i) => (
                  <Cell
                    key={i}
                    fill={entry.success ? '#22c55e' : '#ef4444'}
                    fillOpacity={0.8}
                    r={4}
                  />
                ))}
              </Scatter>
            </ScatterChart>
          </ResponsiveContainer>
        </Card>
      )}

      {/* Table View */}
      {view === 'table' && (
        <div style={s.tableWrap}>
          <table style={s.table}>
            <thead>
              <tr>
                <th style={s.th}>Heure</th>
                <th style={s.th}>API</th>
                <th style={{ ...s.th, textAlign: 'center' }}>Statut</th>
                <th style={{ ...s.th, textAlign: 'right' }}>Durée</th>
                <th style={s.th}>Message</th>
              </tr>
            </thead>
            <tbody>
              {rows.length === 0 && !loading && (
                <tr>
                  <td colSpan={5} style={{ ...s.td, textAlign: 'center', color: '#4a4c6a', padding: '40px 0' }}>
                    Aucun enregistrement
                  </td>
                </tr>
              )}
              {pagedRows.map(row => (
                <tr key={row.id} style={s.tr}>
                  <td style={{ ...s.td, color: '#7a7c9a', fontSize: 12, whiteSpace: 'nowrap' }}>{fmt(row.called_at)}</td>
                  <td style={{ ...s.td, fontFamily: 'monospace', color: '#c4c4d4' }}>{row.api_name}</td>
                  <td style={{ ...s.td, textAlign: 'center' }}>
                    {row.success
                      ? <span style={s.ok}>✓ OK</span>
                      : <span style={s.ko}>✗ KO</span>
                    }
                  </td>
                  <td style={{ ...s.td, textAlign: 'right', color: '#7a7c9a', fontVariantNumeric: 'tabular-nums', whiteSpace: 'nowrap' }}>
                    {row.duration_ms} ms
                  </td>
                  <td style={{ ...s.td, color: '#4a4c6a', fontSize: 12, maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {row.message || '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {rows.length > PAGE_SIZE && (
            <div style={s.pagination}>
              <button style={s.pageBtn} onClick={() => setTablePage(0)} disabled={tablePage === 0}>«</button>
              <button style={s.pageBtn} onClick={() => setTablePage(p => p - 1)} disabled={tablePage === 0}>‹</button>
              <span style={s.pageInfo}>{tablePage + 1} / {totalPages} · {rows.length} lignes</span>
              <button style={s.pageBtn} onClick={() => setTablePage(p => p + 1)} disabled={tablePage >= totalPages - 1}>›</button>
              <button style={s.pageBtn} onClick={() => setTablePage(totalPages - 1)} disabled={tablePage >= totalPages - 1}>»</button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

const s = {
  badges: { display: 'flex', gap: 8, alignItems: 'center' },
  badge: { fontSize: 12, fontWeight: 600, padding: '4px 10px', borderRadius: 6 },
  filters: {
    display: 'flex', gap: 8, alignItems: 'center', marginBottom: 16, flexWrap: 'wrap',
  },
  select: {
    background: '#0f1020', border: '1px solid #1e2038', borderRadius: 6,
    color: '#c4c4d4', padding: '6px 10px', fontSize: 12, cursor: 'pointer',
  },
  btnGroup: { display: 'flex', gap: 2 },
  btn: {
    padding: '5px 12px', borderRadius: 6, border: '1px solid #1e2038',
    background: 'transparent', color: '#4a4c6a', fontSize: 12, fontWeight: 500,
    cursor: 'pointer', outline: 'none',
  },
  btnActive: { background: '#1a1b2e', borderColor: '#2e3050', color: '#00d4aa' },
  refreshBtn: {
    padding: '5px 10px', borderRadius: 6,
    border: '1px solid #1e2038', background: 'transparent',
    color: '#00d4aa', fontSize: 14, cursor: 'pointer',
  },
  error: {
    background: '#dc262620', border: '1px solid #ef444440', borderRadius: 8,
    color: '#ef4444', padding: '10px 14px', marginBottom: 12, fontSize: 13,
  },
  tableWrap: {
    background: '#0d0e1c', border: '1px solid #1a1b2e', borderRadius: 10, overflow: 'auto',
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
  pagination: {
    display: 'flex', alignItems: 'center', gap: 6, padding: '10px 14px',
    borderTop: '1px solid #1a1b2e', justifyContent: 'center',
  },
  pageBtn: {
    padding: '4px 10px', borderRadius: 6, border: '1px solid #1e2038',
    background: 'transparent', color: '#c4c4d4', fontSize: 12, cursor: 'pointer',
    disabled: { opacity: 0.4 },
  },
  pageInfo: { fontSize: 12, color: '#4a4c6a', padding: '0 8px' },
};
