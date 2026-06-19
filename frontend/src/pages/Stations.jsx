import SectionHeader from '../components/common/SectionHeader.jsx';
import LoadingSkeleton from '../components/common/LoadingSkeleton.jsx';
import ErrorState from '../components/common/ErrorState.jsx';
import ChartContainer from '../components/common/ChartContainer.jsx';
import StationChart from '../components/charts/StationChart.jsx';
import useStations from '../hooks/useStations.js';

export default function Stations() {
  const { stations, loading, error } = useStations();

  if (loading) return <LoadingSkeleton height="h-96" />;
  if (error) return <ErrorState message={error} />;

  const topThree = stations.slice(0, 3);

  return (
    <div className="space-y-6">
      <SectionHeader
        eyebrow="Station Analytics"
        title="Police Station Analytics"
        subtitle="Case volume, approval rates, and operational scores across Bengaluru police stations."
      />

      {/* Top 3 station cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {topThree.map((station, index) => (
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
              #{index + 1} Station
            </p>
            <p className="text-[15px] font-semibold text-white mb-3">
              {station.police_station}
            </p>
            <div className="space-y-1.5">
              <div className="flex justify-between text-[12px]">
                <span style={{ color: '#8b949e' }}>Cases</span>
                <span className="font-mono" style={{ color: '#00d992' }}>{station.total_cases?.toLocaleString()}</span>
              </div>
              <div className="flex justify-between text-[12px]">
                <span style={{ color: '#8b949e' }}>Approval</span>
                <span className="font-mono" style={{ color: '#f2f2f2' }}>{station.approval_rate_pct}%</span>
              </div>
              <div className="flex justify-between text-[12px]">
                <span style={{ color: '#8b949e' }}>Ops score</span>
                <span className="font-mono" style={{ color: '#f2f2f2' }}>{station.ops_score}</span>
              </div>
              <div className="flex justify-between text-[12px]">
                <span style={{ color: '#8b949e' }}>Hotspot cells</span>
                <span className="font-mono" style={{ color: '#f2f2f2' }}>{station.n_active_hotspot_cells}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Chart */}
      <ChartContainer title="Case volume by station" subtitle="Total enforcement cases per police station">
        <StationChart data={stations} />
      </ChartContainer>

      {/* Interpretation card */}
      <div className="bg-[#1a1a1a] border border-[#3d3a39] rounded-lg p-5">
        <p
          className="text-[11px] font-semibold uppercase mb-3"
          style={{ color: '#00d992', letterSpacing: '2px' }}
        >
          Station insights
        </p>
        <p className="text-[14px]" style={{ color: '#bdbdbd', lineHeight: 1.65 }}>
          Stations with high case volumes but lower ops scores may indicate resource constraints or
          jurisdictional sprawl. High hotspot cell counts signal that enforcement coverage needs
          to be more spatially distributed. Focus resource augmentation on top 3 stations.
        </p>
      </div>

      {/* Full table */}
      <div className="bg-[#1a1a1a] border border-[#3d3a39] rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr style={{ borderBottom: '1px solid #3d3a39' }}>
                {['Station', 'Cases', 'Approval %', 'Rejection %', 'Ops Score', 'Hotspot Cells'].map((h) => (
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
              {stations.map((station, index) => (
                <tr
                  key={index}
                  className="hover:bg-[rgba(255,255,255,0.02)] transition-colors"
                  style={{ borderBottom: '1px solid rgba(61,58,57,0.5)' }}
                >
                  <td className="px-4 py-3 text-[13px]" style={{ color: '#f2f2f2' }}>
                    {station.police_station}
                  </td>
                  <td className="px-4 py-3 font-mono text-[13px]" style={{ color: '#00d992' }}>
                    {station.total_cases?.toLocaleString()}
                  </td>
                  <td className="px-4 py-3 font-mono text-[13px]" style={{ color: '#f2f2f2' }}>
                    {station.approval_rate_pct}%
                  </td>
                  <td className="px-4 py-3 font-mono text-[13px]" style={{ color: '#ef4444' }}>
                    {station.rejection_rate_pct}%
                  </td>
                  <td className="px-4 py-3 font-mono text-[13px]" style={{ color: '#bdbdbd' }}>
                    {station.ops_score}
                  </td>
                  <td className="px-4 py-3 font-mono text-[13px]" style={{ color: '#bdbdbd' }}>
                    {station.n_active_hotspot_cells}
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
