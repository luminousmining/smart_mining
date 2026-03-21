import { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import CoinsPage from './pages/CoinsPage';
import CoinHistoryPage from './pages/CoinHistoryPage';
import MixedHistoryPage from './pages/MixedHistoryPage';
import HardwarePage from './pages/HardwarePage';
import PoolsPage from './pages/PoolsPage';
import PoolComparePage from './pages/PoolComparePage';
import PoolHistoryPage from './pages/PoolHistoryPage';

const PAGES = {
  coins:        CoinsPage,
  history:      CoinHistoryPage,
  mixed:        MixedHistoryPage,
  hardware:     HardwarePage,
  pools:        PoolsPage,
  poolhistory:  PoolHistoryPage,
  poolcompare:  PoolComparePage,
};

const REFRESH_OPTIONS = [
  { label: '30s', value: 30_000 },
  { label: '1m',  value: 60_000 },
  { label: '2m',  value: 120_000 },
  { label: '5m',  value: 300_000 },
];

export default function App() {
  const [page, setPage]               = useState('coins');
  const [params, setParams]           = useState({});
  const [refreshInterval, setRefresh] = useState(30_000);
  const [isMobile, setIsMobile]       = useState(window.innerWidth < 768);
  const [sidebarOpen, setSidebarOpen] = useState(window.innerWidth >= 768);

  useEffect(() => {
    const handler = () => {
      const mobile = window.innerWidth < 768;
      setIsMobile(mobile);
      if (!mobile) setSidebarOpen(true);
    };
    window.addEventListener('resize', handler);
    return () => window.removeEventListener('resize', handler);
  }, []);

  const navigate = (newPage, newParams = {}) => {
    setPage(newPage);
    setParams(newParams);
    if (isMobile) setSidebarOpen(false);
  };

  const Page = PAGES[page] ?? CoinsPage;

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      {/* Mobile backdrop */}
      {isMobile && sidebarOpen && (
        <div
          onClick={() => setSidebarOpen(false)}
          style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', zIndex: 199 }}
        />
      )}

      <Sidebar
        active={page}
        onNav={(p) => navigate(p)}
        open={sidebarOpen}
        isMobile={isMobile}
        onClose={() => setSidebarOpen(false)}
      />

      <main style={{ flex: 1, overflowY: 'auto', padding: isMobile ? '16px' : '28px 32px', background: '#0b0c14' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12, gap: 6 }}>
          {/* Hamburger button */}
          <button
            onClick={() => setSidebarOpen(o => !o)}
            style={{
              display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 4,
              padding: '6px 8px', borderRadius: 6, border: '1px solid #1e2038',
              background: 'transparent', cursor: 'pointer', flexShrink: 0,
            }}
            aria-label="Toggle sidebar"
          >
            <span style={{ width: 16, height: 2, background: '#4a4c6a', borderRadius: 1, display: 'block' }} />
            <span style={{ width: 16, height: 2, background: '#4a4c6a', borderRadius: 1, display: 'block' }} />
            <span style={{ width: 16, height: 2, background: '#4a4c6a', borderRadius: 1, display: 'block' }} />
          </button>

          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ fontSize: 11, color: '#4a4c6a', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Refresh</span>
            {REFRESH_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                onClick={() => setRefresh(opt.value)}
                style={{
                  padding: '4px 10px', borderRadius: 6, border: '1px solid #1e2038',
                  fontSize: 11, fontWeight: 500, cursor: 'pointer', transition: 'all 0.15s',
                  background: refreshInterval === opt.value ? '#1a1b2e' : 'transparent',
                  color:      refreshInterval === opt.value ? '#00d4aa' : '#4a4c6a',
                }}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
        <Page params={params} onNavigate={navigate} refreshInterval={refreshInterval} />
      </main>
    </div>
  );
}
