export default function DataTable({ columns, rows, keyField = 'id' }) {
  if (!rows?.length) {
    return <p style={s.empty}>No data available.</p>;
  }

  return (
    <div style={s.wrapper}>
      <table style={s.table}>
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col.key} style={{ ...s.th, textAlign: col.align || 'left' }}>
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr
              key={row[keyField] ?? i}
              style={s.row}
              onMouseEnter={(e) => (e.currentTarget.style.background = '#171829')}
              onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
            >
              {columns.map((col) => (
                <td key={col.key} style={{ ...s.td, textAlign: col.align || 'left' }}>
                  {col.render ? col.render(row[col.key], row) : (row[col.key] ?? <span style={s.nil}>—</span>)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

const s = {
  wrapper: { overflowX: 'auto' },
  table:   { width: '100%', borderCollapse: 'collapse', fontSize: 13 },
  th: {
    padding: '6px 12px',
    fontSize: 10,
    fontWeight: 600,
    color: '#4a4c6a',
    textTransform: 'uppercase',
    letterSpacing: '0.6px',
    borderBottom: '1px solid #1e2038',
    whiteSpace: 'nowrap',
  },
  row: { background: 'transparent', transition: 'background 0.1s', cursor: 'default' },
  td: {
    padding: '10px 12px',
    color: '#c8c8e0',
    borderBottom: '1px solid #161728',
    whiteSpace: 'nowrap',
    fontVariantNumeric: 'tabular-nums',
    fontFeatureSettings: '"tnum"',
  },
  nil:   { color: '#3a3c55' },
  empty: { color: '#4a4c6a', fontSize: 13, padding: '16px 0' },
};
