import { useLocation } from 'react-router-dom';
import { RefreshCw } from 'lucide-react';
import { sidebarItems } from '../../constants/sidebarItems.js';

export default function Navbar() {
  const location = useLocation();

  const currentItem = sidebarItems.find((item) => {
    if (item.path === '/') return location.pathname === '/';
    return location.pathname.startsWith(item.path);
  });

  const pageTitle = currentItem?.title ?? 'Dashboard';

  return (
    <header
      className="flex items-center justify-between px-6"
      style={{
        height: '56px',
        background: '#101010',
        borderBottom: '1px solid #3d3a39',
      }}
    >
      {/* Left: page title */}
      <p className="text-[15px] font-medium text-white">{pageTitle}</p>

      {/* Right: chips + refresh */}
      <div className="flex items-center gap-3">
        {/* Status chip */}
        <div
          className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold"
          style={{
            background: 'rgba(0,217,146,0.1)',
            border: '1px solid rgba(0,217,146,0.3)',
            color: '#00d992',
          }}
        >
          <span
            className="w-1.5 h-1.5 rounded-full"
            style={{ background: '#00d992' }}
          />
          Live
        </div>

        {/* API chip */}
        <div
          className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold"
          style={{
            background: 'rgba(0,217,146,0.06)',
            border: '1px solid rgba(0,217,146,0.2)',
            color: '#00d992',
          }}
        >
          API Healthy
        </div>

        {/* Refresh */}
        <button
          onClick={() => window.location.reload()}
          className="flex items-center gap-1.5 text-[13px] font-semibold rounded-md px-3 py-1.5 transition-colors"
          style={{
            background: '#101010',
            color: '#f2f2f2',
            border: '1px solid #3d3a39',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'rgba(255,255,255,0.04)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = '#101010';
          }}
        >
          <RefreshCw size={13} />
          <span className="hidden sm:inline">Refresh</span>
        </button>
      </div>
    </header>
  );
}
