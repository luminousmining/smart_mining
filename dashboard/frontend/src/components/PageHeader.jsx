export default function PageHeader({ title, subtitle, action }) {
  return (
    <div style={s.wrap}>
      <div>
        <h1 style={s.title}>{title}</h1>
        {subtitle && <p style={s.sub}>{subtitle}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}

const s = {
  wrap: {
    display: 'flex',
    alignItems: 'flex-end',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  title: { fontSize: 22, fontWeight: 700, letterSpacing: '-0.4px', color: '#e4e4f0' },
  sub:   { fontSize: 11, color: '#4a4c6a', marginTop: 4, letterSpacing: '0.1px' },
};
