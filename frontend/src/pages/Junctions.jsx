import SectionHeader from '../components/common/SectionHeader.jsx';
import LoadingSkeleton from '../components/common/LoadingSkeleton.jsx';
import ErrorState from '../components/common/ErrorState.jsx';
import ChartContainer from '../components/common/ChartContainer.jsx';
import JunctionChart from '../components/charts/JunctionChart.jsx';
import useJunctions from '../hooks/useJunctions.js';

export default function Junctions() {
  const { junctions, loading, error } = useJunctions();

  if (loading) return <LoadingSkeleton height="h-96" />;
  if (error) return <ErrorState message={error} />;

  const topThree = junctions.slice(0, 3);

  return (
    <div className="space-y-6">
      <SectionHeader
        eyebrow="Junction Analytics"
        title="Junction Analytics"
        subtitle="Case volume and operational analytics across Bengaluru junctions."
      />

      {/* Top 3 cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {topThree.map((junction, index) => (
          <div
            key={index}
            className="bg-[#1a1a1a] rounded-lg p-5"
            style={
              index === 0
                ? { borderLeft: '2px solid #00d992', borderTop: '1px solid #3d3a39', borderRight: '1px solid #3d3a39', borderBottom: '1px solid #3d3a39' }
                : { border: '1px solid #3d3a39' }
            }
          >
            <p
              className="font-mono text-[11px] font-semibold uppercase mb-2"
              style={{ color: index === 0 ? '#00d992' : '#8b949e', letterSpacing: '2px' }}
            >
              Rank #{junction.volume_rank}
            </p>
            <p className="text-[14px] font-semibold text-white mb-3 leading-tight">
              {junction.junction_name}
            </p>
            <div className="space-y-1.5">
              <div className="flex justify-between text-[12px]">
                <span style={{ color: '#8b949e' }}>Cases</span>
                <span className="font-mono" style={{ color: '#00d992' }}>{junction.total_cases?.toLocaleString()}</span>
              </div>
              <div className="flex justify-between text-[12px]">
                <span style={{ color: '#8b949e' }}>Vehicles</span>
                <span className="font-mono" style={{ color: '#f2f2f2' }}>{junction.unique_vehicles}</span>
              </div>
              <div className="flex justify-between text-[12px]">
                <span style={{ color: '#8b949e' }}>Approval</span>
                <span className="font-mono" style={{ color: '#f2f2f2' }}>{junction.approval_rate_pct}%</span>
              </div>
              <div className="flex justify-between text-[12px]">
                <span style={{ color: '#8b949e' }}>Peak hour</span>
                <span className="font-mono" style={{ color: '#f2f2f2' }}>{junction.peak_hour_violations}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Chart */}
      <ChartContainer title="Top junctions by case volume" subtitle="Total enforcement cases per junction">
        <JunctionChart data={junctions} />
      </ChartContainer>

      {/* Insight card */}
      <div className="bg-[#1a1a1a] border border-[#3d3a39] rounded-lg p-5">
        <p
          className="text-[11px] font-semibold uppercase mb-3"
          style={{ color: '#00d992', letterSpacing: '2px' }}
        >
          Junction insights
        </p>
        <p className="text-[14px]" style={{ color: '#bdbdbd', lineHeight: 1.65 }}>
          High-volume junctions with peak-hour concentration indicate congestion hotspots requiring
          time-sensitive patrol deployment. Junctions with high unique vehicle counts but lower
          approval rates may indicate enforcement bottlenecks or contested parking zones.
        </p>
      </div>

      {/* Full table */}
      <div className="bg-[#1a1a1a] border border-[#3d3a39] rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr style={{ borderBottom: '1px solid #3d3a39' }}>
                {['Junction', 'Cases', 'Vehicles', 'Approved', 'Rejected', 'Approval %', 'Peak Hour', 'Rank'].map((h) => (
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
              {junctions.map((junction, index) => (
                <tr
                  key={index}
                  className="hover:bg-[rgba(255,255,255,0.02)] transition-colors"
                  style={{ borderBottom: '1px solid rgba(61,58,57,0.5)' }}
                >
                  <td className="px-4 py-3 text-[13px]" style={{ color: '#f2f2f2' }}>
                    {junction.junction_name}
                  </td>
                  <td className="px-4 py-3 font-mono text-[13px]" style={{ color: '#00d992' }}>
                    {junction.total_cases?.toLocaleString()}
                  </td>
                  <td className="px-4 py-3 font-mono text-[13px]" style={{ color: '#f2f2f2' }}>
                    {junction.unique_vehicles}
                  </td>
                  <td className="px-4 py-3 font-mono text-[13px]" style={{ color: '#00d992' }}>
                    {junction.n_approved}
                  </td>
                  <td className="px-4 py-3 font-mono text-[13px]" style={{ color: '#ef4444' }}>
                    {junction.n_rejected}
                  </td>
                  <td className="px-4 py-3 font-mono text-[13px]" style={{ color: '#f2f2f2' }}>
                    {junction.approval_rate_pct}%
                  </td>
                  <td className="px-4 py-3 font-mono text-[13px]" style={{ color: '#bdbdbd' }}>
                    {junction.peak_hour_violations}
                  </td>
                  <td className="px-4 py-3 font-mono text-[13px]" style={{ color: '#8b949e' }}>
                    #{junction.volume_rank}
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
