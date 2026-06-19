import SectionHeader from '../components/common/SectionHeader.jsx';
import LoadingSkeleton from '../components/common/LoadingSkeleton.jsx';
import ErrorState from '../components/common/ErrorState.jsx';
import HotspotMap from '../components/maps/HotspotMap.jsx';
import useHotspots from '../hooks/useHotspots.js';

export default function Hotspots() {
  const { hotspots, loading, error } = useHotspots();

  if (loading) return <LoadingSkeleton height="h-[700px]" />;
  if (error) return <ErrorState message={error} />;

  const critical = hotspots.filter(
    (h) => (h.congestion_risk_category || '').toLowerCase() === 'critical'
  ).length;
  const high = hotspots.filter(
    (h) => (h.congestion_risk_category || '').toLowerCase() === 'high'
  ).length;
  const persistent = hotspots.filter(
    (h) => (h.stability_class || '').toLowerCase() === 'persistent'
  ).length;

  return (
    <div className="space-y-6">
      <SectionHeader
        eyebrow="Spatial Intelligence"
        title="Hotspot Intelligence Map"
        subtitle="Interactive map of parking hotspot cells across Bengaluru. Markers are coloured by congestion risk."
      />

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-3">
        {[
          { label: 'Total hotspots', value: hotspots.length, color: '#00d992' },
          { label: 'Critical zones', value: critical, color: '#ef4444' },
          { label: 'Persistent cells', value: persistent, color: '#00d992' },
        ].map((stat) => (
          <div key={stat.label} className="bg-[#1a1a1a] border border-[#3d3a39] rounded-lg px-4 py-3">
            <p className="text-[11px] uppercase font-semibold" style={{ color: '#8b949e', letterSpacing: '2px' }}>
              {stat.label}
            </p>
            <p className="font-mono text-[24px] font-bold mt-1" style={{ color: stat.color }}>
              {stat.value}
            </p>
          </div>
        ))}
      </div>

      {/* Risk legend */}
      <div className="flex flex-wrap items-center gap-4">
        {[
          { label: 'Critical', color: '#ef4444' },
          { label: 'High', color: '#f97316' },
          { label: 'Moderate', color: '#eab308' },
          { label: 'Low', color: '#00d992' },
        ].map((item) => (
          <div key={item.label} className="flex items-center gap-1.5">
            <span
              className="w-3 h-3 rounded-full"
              style={{ background: item.color }}
            />
            <span className="text-[12px]" style={{ color: '#8b949e' }}>
              {item.label}
            </span>
          </div>
        ))}
      </div>

      {/* Map */}
      <div className="border border-[#3d3a39] rounded-lg overflow-hidden">
        <HotspotMap hotspots={hotspots} />
      </div>

      {/* Insight box */}
      <div
        className="bg-[#1a1a1a] rounded-lg p-5"
        style={{ border: '1px solid #3d3a39' }}
      >
        <p
          className="text-[11px] font-semibold uppercase mb-2"
          style={{ color: '#00d992', letterSpacing: '2px' }}
        >
          Spatial insight
        </p>
        <p className="text-[14px]" style={{ color: '#bdbdbd', lineHeight: 1.65 }}>
          Critical and High risk markers are clustered around the central business district. Persistent
          hotspots in these zones warrant sustained patrol coverage rather than reactive deployment.
          Use the map to visually identify dense clusters for priority resource allocation.
        </p>
      </div>
    </div>
  );
}
