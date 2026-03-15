import { useState } from 'react';
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

export default function App() {
  const [page, setPage]     = useState('coins');
  const [params, setParams] = useState({});

  const navigate = (newPage, newParams = {}) => {
    setPage(newPage);
    setParams(newParams);
  };

  const Page = PAGES[page] ?? CoinsPage;

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      <Sidebar active={page} onNav={(p) => navigate(p)} />
      <main style={{ flex: 1, overflowY: 'auto', padding: '28px 32px', background: '#0b0c14' }}>
        <Page params={params} onNavigate={navigate} />
      </main>
    </div>
  );
}
