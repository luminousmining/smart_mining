export default function Spinner() {
  return (
    <div style={s.wrap}>
      <div style={s.ring} />
    </div>
  );
}

const s = {
  wrap: { display: 'flex', justifyContent: 'center', padding: '48px 0' },
  ring: {
    width: 24,
    height: 24,
    border: '2px solid #1e2038',
    borderTopColor: '#00d4aa',
    borderRadius: '50%',
    animation: 'spin 0.7s linear infinite',
  },
};

if (typeof document !== 'undefined' && !document.getElementById('spinner-kf')) {
  const el = document.createElement('style');
  el.id = 'spinner-kf';
  el.textContent = '@keyframes spin { to { transform: rotate(360deg); } }';
  document.head.appendChild(el);
}
