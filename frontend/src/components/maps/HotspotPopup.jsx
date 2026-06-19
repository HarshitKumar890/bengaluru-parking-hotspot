import RiskBadge from '../common/RiskBadge.jsx';
import StabilityBadge from '../common/StabilityBadge.jsx';

export default function HotspotPopup({ hotspot }) {
  return (
    <div
      style={{
        background: '#1a1a1a',
        border: '1px solid #3d3a39',
        borderRadius: '8px',
        padding: '12px 14px',
        minWidth: '200px',
        color: '#f2f2f2',
        fontFamily: 'Inter, system-ui, sans-serif',
      }}
    >
      <p
        style={{
          fontFamily: 'JetBrains Mono, SF Mono, monospace',
          fontSize: '12px',
          color: '#00d992',
          fontWeight: 600,
          marginBottom: '8px',
        }}
      >
        {hotspot.spatial_cell_id}
      </p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', marginBottom: '8px' }}>
        <p style={{ fontSize: '12px', color: '#8b949e' }}>
          Station: <span style={{ color: '#f2f2f2' }}>{hotspot.police_station}</span>
        </p>
        <p style={{ fontSize: '12px', color: '#8b949e' }}>
          Forecast: <span style={{ color: '#f2f2f2', fontFamily: 'JetBrains Mono, monospace' }}>{hotspot.forecasted_count}</span>
        </p>
        <p style={{ fontSize: '12px', color: '#8b949e' }}>
          Priority: <span style={{ color: '#f2f2f2', fontFamily: 'JetBrains Mono, monospace' }}>{hotspot.priority_score}</span>
        </p>
        <p style={{ fontSize: '12px', color: '#8b949e' }}>
          Patrol Rank: <span style={{ color: '#f2f2f2' }}>#{hotspot.patrol_rank}</span>
        </p>
      </div>

      <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
        <RiskBadge risk={hotspot.congestion_risk_category} />
        <StabilityBadge stability={hotspot.stability_class} />
      </div>
    </div>
  );
}
