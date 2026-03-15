import { useState, useEffect, useCallback } from 'react';
import { api } from '../api';
import Card from '../components/Card';
import DataTable from '../components/DataTable';
import PageHeader from '../components/PageHeader';
import Spinner from '../components/Spinner';

const fmtHash = (v) => {
  if (v == null) return null;
  const n = Number(v);
  if (n >= 1e12) return `${(n / 1e12).toFixed(2)} TH/s`;
  if (n >= 1e9)  return `${(n / 1e9).toFixed(2)} GH/s`;
  if (n >= 1e6)  return `${(n / 1e6).toFixed(2)} MH/s`;
  if (n >= 1e3)  return `${(n / 1e3).toFixed(2)} KH/s`;
  return `${n.toFixed(2)} H/s`;
};

const COLUMNS = [
  {
    key: 'hardware',
    label: 'Hardware',
    render: (v) => <strong style={{ color: '#e4e4f0' }}>{v}</strong>,
  },
  {
    key: 'algo',
    label: 'Algorithm',
    render: (v) => v ? (
      <span style={{ padding: '2px 7px', borderRadius: 4, fontSize: 11, background: '#181828', color: '#7070a0' }}>
        {v}
      </span>
    ) : null,
  },
  {
    key: 'hashrate',
    label: 'Hashrate',
    align: 'right',
    render: (v) => {
      const s = fmtHash(v);
      return s ? <span style={{ color: '#00d4aa', fontWeight: 500 }}>{s}</span> : null;
    },
  },
  {
    key: 'power',
    label: 'Power',
    align: 'right',
    render: (v) => v != null ? (
      <span style={{ color: '#f59e0b' }}>{Number(v).toLocaleString()} W</span>
    ) : null,
  },
  {
    key: '_eff',
    label: 'Efficiency',
    align: 'right',
    render: (_, row) => {
      if (!row.hashrate || !row.power || Number(row.power) === 0) return null;
      const s = fmtHash(Number(row.hashrate) / Number(row.power));
      return s ? <span style={{ color: '#6366f1' }}>{s.replace('/s', '/W')}</span> : null;
    },
  },
];

export default function HardwarePage() {
  const [data, setData]       = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);

  const load = useCallback(async () => {
    try {
      const rows = await api.hardware();
      setData(rows);
      setLastUpdate(new Date());
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    const id = setInterval(load, 30_000);
    return () => clearInterval(id);
  }, [load]);

  const sub = lastUpdate ? `Updated ${lastUpdate.toLocaleTimeString()} · refresh 30s` : 'Loading…';

  return (
    <div>
      <PageHeader title="Hardware" subtitle={sub} />
      <Card>
        {loading ? <Spinner /> : <DataTable columns={COLUMNS} rows={data} keyField="id" />}
      </Card>
    </div>
  );
}
