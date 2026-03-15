export default function Card({ title, subtitle, children, style }) {
  return (
    <div style={{ ...s.card, ...style }}>
      {(title || subtitle) && (
        <div style={s.header}>
          {title && <h2 style={s.title}>{title}</h2>}
          {subtitle && <span style={s.subtitle}>{subtitle}</span>}
        </div>
      )}
      {children}
    </div>
  );
}

const s = {
  card: {
    background: '#111221',
    borderRadius: 12,
    padding: '18px 20px',
    border: '1px solid #1e2038',
  },
  header: {
    display: 'flex',
    alignItems: 'baseline',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  title: {
    fontSize: 11,
    fontWeight: 600,
    color: '#6b6d8a',
    textTransform: 'uppercase',
    letterSpacing: '0.7px',
  },
  subtitle: { fontSize: 11, color: '#3a3c55' },
};
