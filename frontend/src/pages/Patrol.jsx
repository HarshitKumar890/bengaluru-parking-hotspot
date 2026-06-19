import SectionHeader from '../components/common/SectionHeader.jsx';
import LoadingSkeleton from '../components/common/LoadingSkeleton.jsx';
import ErrorState from '../components/common/ErrorState.jsx';
import ChartContainer from '../components/common/ChartContainer.jsx';
import PatrolChart from '../components/charts/PatrolChart.jsx';
import RiskBadge from '../components/common/RiskBadge.jsx';
import StabilityBadge from '../components/common/StabilityBadge.jsx';
import usePatrol from '../hooks/usePatrol.js';

export default function Patrol() {
  const { patrols, loading, error } = usePatrol();

  if (loading) return <LoadingSkeleton height="h-[600px]" />;
  if (error) return <ErrorState message={error} />;

  const critical = patrols.filter(
    (p) => (p.congestion_risk_category || '').toLowerCase() === 'critical'
  ).length;
  const topScore = patrols.length > 0 ? patrols[0]?.priority_score : '—';

  return (
    <div className="space-y-6">
      <SectionHeader
        eyebrow="Patrol Deployment"
        title="Patrol Recommendations"
        subtitle="Top patrol deployment cells prioritized by AI composite risk scoring."
      />

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-3">
        {[
          { label: 'Total patrol cells', value: patrols.length, color: '#00d992' },
          { label: 'Critical priority', value: critical, color: '#ef4444' },
          { label: 'Top priority score', value: topScore, color: '#00d992' },
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

      {/* Top 3 highlight cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {patrols.slice(0, 3).map((item, index) => (
          <div
            key={index}
            className="bg-[#1a1a1a] rounded-lg p-5"
            style={
              index === 0
                ? { borderLeft: '2px solid #00d992', borderTop: '1px solid #3d3a39', borderRight: '1px solid #3d3a39', borderBottom: '1px solid #3d3a39' }
                : { border: '1px solid #3d3a39' }
            }
          >
            <div className="flex items-center justify-between mb-3">
              <span
                className="font-mono text-[11px] font-semibold"
                style={{ color: index === 0 ? '#00d992' : '#8b949e' }}
              >
                RANK #{item.patrol_rank}
              </span>
              <RiskBadge risk={item.congestion_risk_category} />
            </div>
            <p className="font-mono text-[13px] text-white font-semibold mb-1">
              {item.spatial_cell_id}
            </p>
            <p className="text-[12px]" style={{ color: '#8b949e' }}>
              {item.police_station}
            </p>
            {item.risk_explanation && (
              <p className="text-[12px] mt-3" style={{ color: '#bdbdbd', lineHeight: 1.6 }}>
                {item.risk_explanation}
              </p>
            )}
            <div className="mt-3 flex items-center gap-3">
              <span className="text-[12px]" style={{ color: '#8b949e' }}>
                Priority: <span className="font-mono" style={{ color: '#f2f2f2' }}>{item.priority_score}</span>
              </span>
              <StabilityBadge stability={item.stability_class} />
            </div>
          </div>
        ))}
      </div>

      {/* Chart */}
      <ChartContainer title="Priority scores by patrol rank" subtitle="Top patrol cells ordered by composite priority score">
        <PatrolChart data={patrols} />
      </ChartContainer>

      {/* Action guidance */}
      <div
        className="bg-[#1a1a1a] rounded-lg p-5"
        style={{ border: '1px solid #3d3a39' }}
      >
        <p
          className="text-[11px] font-semibold uppercase mb-3"
          style={{ color: '#00d992', letterSpacing: '2px' }}
        >
          Deployment guidance
        </p>
        <ul className="space-y-2">
          {[
            'Prioritize top 5 ranked cells for immediate deployment — highest composite risk scores.',
            'Persistent hotspots in ranks 1–10 warrant stationary patrol or fixed monitoring.',
            'Volatile and Declining stability cells should have dynamic coverage adjustments.',
            'Correlate patrol rank with junction proximity for traffic-aware routing.',
          ].map((tip, i) => (
            <li key={i} className="flex items-start gap-2">
              <span className="font-mono text-[11px] mt-0.5" style={{ color: '#00d992' }}>
                {String(i + 1).padStart(2, '0')}.
              </span>
              <p className="text-[13px]" style={{ color: '#bdbdbd', lineHeight: 1.6 }}>
                {tip}
              </p>
            </li>
          ))}
        </ul>
      </div>

      {/* Full table */}
      <div className="bg-[#1a1a1a] border border-[#3d3a39] rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr style={{ borderBottom: '1px solid #3d3a39' }}>
                {['Rank', 'Cell', 'Prediction', 'Priority', 'Risk', 'Stability', 'Station'].map((h) => (
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
              {patrols.map((item, index) => (
                <tr
                  key={index}
                  className="hover:bg-[rgba(255,255,255,0.02)] transition-colors"
                  style={{ borderBottom: '1px solid rgba(61,58,57,0.5)' }}
                >
                  <td className="px-4 py-3 font-mono text-[13px]" style={{ color: '#00d992' }}>
                    #{item.patrol_rank}
                  </td>
                  <td className="px-4 py-3 font-mono text-[13px]" style={{ color: '#f2f2f2' }}>
                    {item.spatial_cell_id}
                  </td>
                  <td className="px-4 py-3 font-mono text-[13px]" style={{ color: '#f2f2f2' }}>
                    {item.predicted_count}
                  </td>
                  <td className="px-4 py-3 font-mono text-[13px]" style={{ color: '#f2f2f2' }}>
                    {item.priority_score}
                  </td>
                  <td className="px-4 py-3">
                    <RiskBadge risk={item.congestion_risk_category} />
                  </td>
                  <td className="px-4 py-3">
                    <StabilityBadge stability={item.stability_class} />
                  </td>
                  <td className="px-4 py-3 text-[13px]" style={{ color: '#bdbdbd' }}>
                    {item.police_station}
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
