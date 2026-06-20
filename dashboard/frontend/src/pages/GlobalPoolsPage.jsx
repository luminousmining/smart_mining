import { useState, useEffect, useCallback, useMemo } from 'react';
import { api } from '../api';
import Card from '../components/Card';
import PageHeader from '../components/PageHeader';
import Spinner from '../components/Spinner';

const THRESHOLD_MINUTES = 15;

function timeSince(epochSec) {
  const diff = Math.floor(Date.now() / 1000 - Number(epochSec));
  if (diff < 60)    return `${diff}s`;
  if (diff < 3600)  return `${Math.floor(diff / 60)}m`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ${Math.floor((diff % 3600) / 60)}m`;
  return `${Math.floor(diff / 86400)}d`;
}

function fmtTs(epochSec) {
  if (!epochSec) return 'Never';
  return new Date(Number(epochSec) * 1000).toLocaleString();
}

export default function GlobalPoolsPage({ refreshInterval = 30_000 }) {
  const [data, setData]       = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);

  const load = useCallback(async () => {
    try {
      const rows = await api.poolStatus();
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

  // Pivot: rows = coins (tags), columns = pools, cell = last_seen
  const { coins, pools, matrix } = useMemo(() => {
    const coinSet = [...new Set(data.map((r) => r.tag))].sort();
    const poolSet = [...new Set(data.map((r) => r.name))].sort();
    const m = {};
    for (const r of data) {
      m[`${r.tag}|${r.name}`] = r.last_seen;
    }
    return { coins: coinSet, pools: poolSet, matrix: m };
  }, [data]);

  const onCount = data.filter((r) => (Date.now() / 1000 - Number(r.last_seen)) / 60 < THRESHOLD_MINUTES).length;
  const sub = lastUpdate
    ? `${coins.length} coins · ${pools.length} pools · ${onCount} active · Updated ${lastUpdate.toLocaleTimeString()}`
    : 'Loading…';

  return (
    <div>
      <PageHeader
        title="Pool Status"
        subtitle={sub}
        action={
          <div style={s.legend}>
            <span style={s.legendItem}><span style={{ ...s.ldot, background: '#22c55e' }} /> ON (&lt;{THRESHOLD_MINUTES}m)</span>
            <span style={s.legendItem}><span style={{ ...s.ldot, background: '#6b6d8a' }} /> OFF</span>
          </div>
        }
      />

      {loading ? (
        <Spinner />
      ) : coins.length === 0 ? (
        <Card><p style={{ color: '#4a4c6a', fontSize: 13 }}>No pool data available.</p></Card>
      ) : (
        <div style={s.tableWrap}>
          <table style={s.table}>
            <thead>
              <tr>
                <th style={{ ...s.th, ...s.stickyCol, textAlign: 'left', zIndex: 3 }}>Coin</th>
                {pools.map((p) => (
                  <th key={p} style={{ ...s.th, textAlign: 'center' }}>{p}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {coins.map((coin) => (
                <tr key={coin} style={s.tr}>
                  <td style={{ ...s.td, ...s.stickyCol }}>
                    <span style={s.tagBadge}>{coin}</span>
                  </td>
                  {pools.map((pool) => {
                    const lastSeen = matrix[`${coin}|${pool}`];
                    if (lastSeen == null) {
                      return <td key={pool} style={{ ...s.td, textAlign: 'center', color: '#2e3050' }}>—</td>;
                    }
                    const minutesAgo = (Date.now() / 1000 - Number(lastSeen)) / 60;
                    const isOn = minutesAgo < THRESHOLD_MINUTES;
                    return (
                      <td key={pool} style={{ ...s.td, textAlign: 'center' }} title={fmtTs(lastSeen)}>
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5 }}>
                          <span style={{
                            width: 8, height: 8, borderRadius: '50%', flexShrink: 0,
                            background: isOn ? '#22c55e' : '#6b6d8a',
                            boxShadow: isOn ? '0 0 6px #22c55e88' : 'none',
                          }} />
                          <span style={{ fontSize: 11, color: isOn ? '#22c55e' : '#6b6d8a', fontWeight: 600 }}>
                            {isOn ? 'ON' : timeSince(lastSeen)}
                          </span>
                        </span>
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

const s = {
  legend: { display: 'flex', gap: 14, alignItems: 'center' },
  legendItem: { display: 'flex', alignItems: 'center', gap: 5, fontSize: 11, color: '#6b6d8a' },
  ldot: { width: 8, height: 8, borderRadius: '50%', display: 'inline-block' },
  tableWrap: {
    background: '#0d0e1c', border: '1px solid #1a1b2e', borderRadius: 10, overflow: 'auto',
    maxHeight: 'calc(100vh - 180px)',
  },
  table: { borderCollapse: 'collapse', width: '100%' },
  th: {
    padding: '10px 14px', fontSize: 11, fontWeight: 600, color: '#7a7c9a',
    letterSpacing: '0.4px', textAlign: 'center', whiteSpace: 'nowrap',
    borderBottom: '1px solid #1a1b2e', background: '#080910',
    position: 'sticky', top: 0, zIndex: 2,
  },
  stickyCol: {
    position: 'sticky', left: 0, zIndex: 1, background: '#0b0c14', textAlign: 'left',
  },
  tr: { borderBottom: '1px solid #12132280' },
  td: { padding: '8px 14px', fontSize: 12, color: '#c4c4d4', whiteSpace: 'nowrap' },
  tagBadge: {
    padding: '2px 7px', borderRadius: 4, fontSize: 11, fontWeight: 600,
    background: '#0d2030', color: '#00d4aa', letterSpacing: '0.3px',
  },
};
