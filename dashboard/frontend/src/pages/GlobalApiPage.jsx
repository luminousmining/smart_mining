import { useState, useEffect, useCallback } from 'react';
import { api } from '../api';
import Card from '../components/Card';
import PageHeader from '../components/PageHeader';
import Spinner from '../components/Spinner';

function fmt(ts) {
  if (!ts) return '—';
  return new Date(ts).toLocaleString('en-US', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
  });
}

export default function GlobalApiPage({ refreshInterval = 30_000 }) {
  const [data, setData]       = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);

  const load = useCallback(async () => {
    try {
      const rows = await api.apiStatus();
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
  }, [load, refreshInterval]);

  const healthy  = data.filter((r) => !r.last_failure || (r.last_success && r.last_success >= r.last_failure)).length;
  const failing  = data.length - healthy;
  const sub = lastUpdate ? `${data.length} APIs · Updated ${lastUpdate.toLocaleTimeString()}` : 'Loading…';

  return (
    <div>
      <PageHeader
        title="API Status"
        subtitle={sub}
        action={
          <div style={s.badges}>
            <span style={{ ...s.badge, background: '#16a34a22', color: '#22c55e', border: '1px solid #22c55e44' }}>
              ✓ {healthy} OK
            </span>
            {failing > 0 && (
              <span style={{ ...s.badge, background: '#dc262622', color: '#ef4444', border: '1px solid #ef444444' }}>
                ✗ {failing} KO
              </span>
            )}
          </div>
        }
      />

      {loading ? (
        <Spinner />
      ) : data.length === 0 ? (
        <Card><p style={{ color: '#4a4c6a', fontSize: 13 }}>No API history available.</p></Card>
      ) : (
        <div style={s.tableWrap}>
          <table style={s.table}>
            <thead>
              <tr>
                <th style={s.th}>API</th>
                <th style={{ ...s.th, textAlign: 'center' }}>Status</th>
                <th style={s.th}>Last success</th>
                <th style={s.th}>Last failure</th>
                <th style={{ ...s.th, textAlign: 'right' }}>✓ 24h</th>
                <th style={{ ...s.th, textAlign: 'right' }}>✗ 24h</th>
              </tr>
            </thead>
            <tbody>
              {data.map((row) => {
                const isOk = !row.last_failure || (row.last_success && row.last_success >= row.last_failure);
                const fail24 = Number(row.fail_24h ?? 0);
                return (
                  <tr key={row.api_name} style={s.tr}>
                    <td style={{ ...s.td, fontFamily: 'monospace', color: '#c4c4d4', fontWeight: 600 }}>
                      {row.api_name}
                    </td>
                    <td style={{ ...s.td, textAlign: 'center' }}>
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5 }}>
                        <span style={{ width: 8, height: 8, borderRadius: '50%', background: isOk ? '#22c55e' : '#ef4444', boxShadow: isOk ? '0 0 6px #22c55e88' : '0 0 6px #ef444488', display: 'inline-block' }} />
                        <span style={{ fontSize: 11, color: isOk ? '#22c55e' : '#ef4444', fontWeight: 600 }}>
                          {isOk ? 'OK' : 'KO'}
                        </span>
                      </span>
                    </td>
                    <td style={{ ...s.td, color: '#22c55e', fontSize: 12, whiteSpace: 'nowrap' }}>
                      {fmt(row.last_success)}
                    </td>
                    <td style={{ ...s.td, color: row.last_failure ? '#ef4444' : '#4a4c6a', fontSize: 12, whiteSpace: 'nowrap' }}>
                      {fmt(row.last_failure)}
                    </td>
                    <td style={{ ...s.td, textAlign: 'right', color: '#22c55e', fontVariantNumeric: 'tabular-nums' }}>
                      {Number(row.success_24h ?? 0).toLocaleString()}
                    </td>
                    <td style={{ ...s.td, textAlign: 'right', color: fail24 > 0 ? '#ef4444' : '#4a4c6a', fontVariantNumeric: 'tabular-nums', fontWeight: fail24 > 0 ? 700 : 400 }}>
                      {fail24.toLocaleString()}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

const s = {
  badges: { display: 'flex', gap: 8, alignItems: 'center' },
  badge:  { fontSize: 12, fontWeight: 600, padding: '4px 10px', borderRadius: 6 },
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
};
