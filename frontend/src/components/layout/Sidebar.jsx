import { NavLink } from 'react-router-dom';
import { Zap } from 'lucide-react';
import { sidebarItems } from '../../constants/sidebarItems.js';

export default function Sidebar() {
  return (
    <aside
      className="flex flex-col h-screen shrink-0"
      style={{
        width: '256px',
        background: '#101010',
        borderRight: '1px solid #3d3a39',
      }}
    >
      {/* Logo */}
      <div
        className="flex items-center gap-3 px-5 py-4"
        style={{ borderBottom: '1px solid #3d3a39' }}
      >
        <Zap size={20} style={{ color: '#00d992' }} />
        <div>
          <p className="text-white font-bold text-[15px] leading-tight">ParkIntel</p>
          <p className="text-[11px]" style={{ color: '#8b949e' }}>Bengaluru</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-3 overflow-y-auto space-y-0.5">
        {sidebarItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              className="flex items-center gap-3 py-2.5 pr-3 rounded-md text-sm font-medium transition-colors group"
              style={({ isActive }) =>
                isActive
                  ? {
                      borderLeft: '2px solid #00d992',
                      paddingLeft: '14px',
                      color: '#00d992',
                      background: 'transparent',
                      borderRadius: '0 6px 6px 0',
                    }
                  : {
                      paddingLeft: '16px',
                      color: '#8b949e',
                    }
              }
            >
              {({ isActive }) => (
                <>
                  <Icon
                    size={16}
                    style={{ color: isActive ? '#00d992' : 'inherit', transition: 'color 0.15s' }}
                  />
                  <span style={{ transition: 'color 0.15s' }}>{item.title}</span>
                </>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Footer */}
      <div
        className="px-5 py-3"
        style={{ borderTop: '1px solid #3d3a39' }}
      >
        <div className="flex items-center gap-2">
          <span
            className="w-1.5 h-1.5 rounded-full"
            style={{ background: '#00d992' }}
          />
          <span className="text-[12px]" style={{ color: '#8b949e' }}>
            System operational
          </span>
        </div>
      </div>
    </aside>
  );
}
