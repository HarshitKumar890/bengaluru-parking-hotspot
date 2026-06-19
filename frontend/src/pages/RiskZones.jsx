import SectionHeader from '../components/common/SectionHeader.jsx';
import LoadingSkeleton from '../components/common/LoadingSkeleton.jsx';
import ErrorState from '../components/common/ErrorState.jsx';
import ChartContainer from '../components/common/ChartContainer.jsx';
import RiskBadge from '../components/common/RiskBadge.jsx';
import RiskDistributionChart from '../components/charts/RiskDistributionChart.jsx';
import useRiskZones from '../hooks/useRiskZones.js';

const RISK_LEVELS = [
  { level: 'Critical', desc: 'Immediate response required. Persistent high-volume cells with maximum congestion impact.', color: '#ef4444' },
  { level: 'High', desc: 'Priority monitoring. Recurrent violations with significant congestion contribution.', color: '#f97316' },
  { level: 'Moderate', desc: 'Regular monitoring. Occasional violations with moderate traffic impact.', color: '#eab308' },
  { level: 'Low', desc: 'Standard patrol. Infrequent violations with minimal congestion risk.', color: '#00d992' },
];

export default function RiskZones() {
  const { riskZones, loading, error } = useRiskZones();

  if (loading) return <LoadingSkeleton height="h-96" />;
  if (error) return <ErrorState message={error} />;

  const critical = riskZones.filter((z) => (z.congestion_risk_category || '').toLowerCase() === 'critical').length;
  const high = riskZones.filter((z) => (z.congestion_risk_category || '').toLowerCase() === 'high').length;
  const moderate = riskZones.filter(
    (z) => ['moderate', 'medium'].includes((z.congestion_risk_category || '').toLowerCase())
  ).length;

  return (
    <div className="space-y-6">
      <SectionHeader
        eyebrow="Congestion Risk Engine"
        title="Congestion Risk Zones"
        subtitle="Cells ranked by parking-induced congestion risk score, derived from forecast intensity and spatial features."
      />

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-3">
        {[
          { label: 'Critical zones', value: critical, color: '#ef4444' },
          { label: 'High risk zones', value: high, color: '#f97316' },
          { label: 'Moderate zones', value: moderate, color: '#eab308' },
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

      {/* Bar chart */}
      <ChartContainer title="Risk distribution" subtitle="Count of zones by risk category">
        <RiskDistributionChart data={riskZones} />
      </ChartContainer>

      {/* Risk level legend card */}
      <div className="bg-[#1a1a1a] border border-[#3d3a39] rounded-lg p-5">
        <p
          className="text-[11px] font-semibold uppercase mb-4"
          style={{ color: '#8b949e', letterSpacing: '2px' }}
        >
          Risk level guide
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {RISK_LEVELS.map((item) => (
            <div key={item.level} className="flex items-start gap-3">
              <span
                className="w-2 h-2 rounded-full mt-1.5 shrink-0"
                style={{ background: item.color }}
              />
              <div>
                <p className="text-[13px] font-semibold" style={{ color: item.color }}>
                  {item.level}
                </p>
                <p className="text-[12px]" style={{ color: '#8b949e', lineHeight: 1.5 }}>
                  {item.desc}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="bg-[#1a1a1a] border border-[#3d3a39] rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr style={{ borderBottom: '1px solid #3d3a39' }}>
                {['Cell ID', 'Risk Score', 'Category', 'Station', 'Forecast', 'Patrol Rank'].map((h) => (
                  <th
                    key={h}
                    className="px-4 py-3 text-left text-[11px] font-semibold uppercase"
                    style={{ color: '#8b949e', letterSpacing: '1.5px' }}
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {riskZones.map((zone, index) => (
                <tr
                  key={index}
                  className="hover:bg-[rgba(255,255,255,0.02)] transition-colors"
                  style={{ borderBottom: '1px solid rgba(61,58,57,0.5)' }}
                >
                  <td className="px-4 py-3 font-mono text-[13px]" style={{ color: '#f2f2f2' }}>
                    {zone.spatial_cell_id}
                  </td>
                  <td className="px-4 py-3 font-mono text-[13px]" style={{ color: '#ef4444' }}>
                    {zone.congestion_risk_score}
                  </td>
                  <td className="px-4 py-3">
                    <RiskBadge risk={zone.congestion_risk_category} />
                  </td>
                  <td className="px-4 py-3 text-[13px]" style={{ color: '#bdbdbd' }}>
                    {zone.police_station}
                  </td>
                  <td className="px-4 py-3 font-mono text-[13px]" style={{ color: '#f2f2f2' }}>
                    {zone.forecasted_count}
                  </td>
                  <td className="px-4 py-3 font-mono text-[13px]" style={{ color: '#8b949e' }}>
                    #{zone.patrol_rank}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
