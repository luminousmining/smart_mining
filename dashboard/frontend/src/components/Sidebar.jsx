const NAV = [
  { id: 'coins',       label: 'Coins',          icon: CoinIcon,    group: 'Market' },
  { id: 'history',     label: 'History',        icon: ChartIcon,   group: 'Market' },
  { id: 'mixed',       label: 'Compare Coins',  icon: CompareIcon, group: 'Market' },
  { id: 'hardware',    label: 'Hardware',        icon: HardwareIcon,group: 'Mining' },
  { id: 'pools',       label: 'Pools',           icon: PoolIcon,    group: 'Mining' },
  { id: 'poolhistory', label: 'Pool History',    icon: ChartIcon,   group: 'Mining' },
  { id: 'poolcompare', label: 'Compare Pools',   icon: CompareIcon, group: 'Mining' },
];

export default function Sidebar({ active, onNav }) {
  return (
    <nav style={s.nav}>
      <div style={s.logo}>
        <div style={s.logoMark}>M</div>
        <div>
          <div style={s.logoTitle}>Mining</div>
          <div style={s.logoSub}>Dashboard</div>
        </div>
      </div>

      <ul style={s.list}>
        {['Market', 'Mining'].map((group) => (
          <li key={group}>
            <div style={s.group}>{group}</div>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 2 }}>
              {NAV.filter(n => n.group === group).map(({ id, label, icon: Icon }) => {
                const isActive = active === id;
                return (
                  <li key={id}>
                    <button
                      style={{ ...s.item, ...(isActive ? s.itemActive : {}) }}
                      onClick={() => onNav(id)}
                    >
                      <span style={{ ...s.iconWrap, ...(isActive ? s.iconActive : {}) }}>
                        <Icon />
                      </span>
                      <span style={isActive ? s.labelActive : s.label}>{label}</span>
                      {isActive && <span style={s.dot} />}
                    </button>
                  </li>
                );
              })}
            </ul>
          </li>
        ))}
      </ul>

      <div style={s.footer}>
        <div style={s.pulse} />
        <span style={s.footerText}>Live</span>
      </div>
    </nav>
  );
}

function CoinIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" /><path d="M12 6v12M9 9h4.5a1.5 1.5 0 0 1 0 3H9m0 0h4.5a1.5 1.5 0 0 1 0 3H9" />
    </svg>
  );
}

function ChartIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
    </svg>
  );
}

function HardwareIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="2" y="6" width="20" height="12" rx="2" /><path d="M6 12h.01M10 12h.01M14 12h.01M18 12h.01M8 6V4M16 6V4M8 18v2M16 18v2" />
    </svg>
  );
}

function PoolIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <ellipse cx="12" cy="5" rx="9" ry="3" /><path d="M3 5v14a9 3 0 0 0 18 0V5M3 12a9 3 0 0 0 18 0" />
    </svg>
  );
}

function CompareIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M18 20V10M12 20V4M6 20v-6" />
    </svg>
  );
}

const s = {
  nav: {
    width: 210,
    background: '#080910',
    borderRight: '1px solid #1a1b2e',
    display: 'flex',
    flexDirection: 'column',
    padding: '20px 10px',
    flexShrink: 0,
  },
  logo: { display: 'flex', alignItems: 'center', gap: 10, padding: '4px 10px 28px' },
  logoMark: {
    width: 32, height: 32, borderRadius: 8,
    background: 'linear-gradient(135deg, #00d4aa, #0080ff)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    fontSize: 16, fontWeight: 800, color: '#fff', flexShrink: 0,
  },
  logoTitle: { fontSize: 14, fontWeight: 700, color: '#e4e4f0', letterSpacing: '-0.2px' },
  logoSub:   { fontSize: 10, color: '#4a4c6a', letterSpacing: '0.5px', textTransform: 'uppercase', marginTop: 1 },
  list: { listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 8, flex: 1 },
  group: { fontSize: 10, fontWeight: 600, color: '#2e3050', textTransform: 'uppercase', letterSpacing: '0.8px', padding: '6px 10px 4px' },
  item: {
    width: '100%', display: 'flex', alignItems: 'center', gap: 10,
    padding: '9px 10px', borderRadius: 8, border: 'none',
    background: 'transparent', cursor: 'pointer', textAlign: 'left',
    transition: 'background 0.15s', position: 'relative',
  },
  itemActive:  { background: '#1a1b2e' },
  iconWrap:    { color: '#4a4c6a', display: 'flex', flexShrink: 0 },
  iconActive:  { color: '#00d4aa' },
  label:       { fontSize: 13, fontWeight: 500, color: '#5a5c7a' },
  labelActive: { fontSize: 13, fontWeight: 600, color: '#e4e4f0' },
  dot: { width: 5, height: 5, borderRadius: '50%', background: '#00d4aa', marginLeft: 'auto', flexShrink: 0 },
  footer: { display: 'flex', alignItems: 'center', gap: 7, padding: '12px 10px 4px', borderTop: '1px solid #1a1b2e' },
  pulse: { width: 7, height: 7, borderRadius: '50%', background: '#22c55e', boxShadow: '0 0 8px #22c55e88', animation: 'pulse 2s ease infinite' },
  footerText: { fontSize: 11, color: '#4a4c6a', letterSpacing: '0.5px', textTransform: 'uppercase' },
};

if (typeof document !== 'undefined' && !document.getElementById('pulse-kf')) {
  const st = document.createElement('style');
  st.id = 'pulse-kf';
  st.textContent = '@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.3}}';
  document.head.appendChild(st);
}
