import { useState } from 'react';
import SectionHeader from '../components/common/SectionHeader.jsx';
import LoadingSkeleton from '../components/common/LoadingSkeleton.jsx';
import ErrorState from '../components/common/ErrorState.jsx';
import ChartContainer from '../components/common/ChartContainer.jsx';
import StabilityBadge from '../components/common/StabilityBadge.jsx';
import StabilityChart from '../components/charts/StabilityChart.jsx';
import useStability from '../hooks/useStability.js';

const ALL_FILTERS = ['All', 'Persistent', 'Seasonal', 'Sporadic', 'Volatile', 'Declining', 'Emerging'];

export default function Stability() {
  const { stabilityData, loading, error } = useStability();
  const [activeFilter, setActiveFilter] = useState('All');

  if (loading) return <LoadingSkeleton height="h-96" />;
  if (error) return <ErrorState message={error} />;

  const persistent = stabilityData.filter((d) => (d.stability_class || '').toLowerCase() === 'persistent').length;
  const volatile_ = stabilityData.filter((d) => (d.stability_class || '').toLowerCase() === 'volatile').length;
  const seasonal = stabilityData.filter((d) => (d.stability_class || '').toLowerCase() === 'seasonal').length;

  const filteredData =
    activeFilter === 'All'
      ? stabilityData
      : stabilityData.filter((d) => d.stability_class === activeFilter);

  return (
    <div className="space-y-6">
      <SectionHeader
        eyebrow="Stability Explorer"
        title="Hotspot Stability Analysis"
        subtitle="Stability classifications derived from 6-month hotspot activity patterns."
      />

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-3">
        {[
          { label: 'Persistent', value: persistent, color: '#00d992' },
          { label: 'Volatile', value: volatile_, color: '#ef4444' },
          { label: 'Seasonal', value: seasonal, color: '#eab308' },
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

      {/* Chart */}
      <ChartContainer title="Stability distribution" subtitle="Count of hotspot cells by stability class">
        <StabilityChart data={stabilityData} />
      </ChartContainer>

      {/* Interpretation card */}
      <div className="bg-[#1a1a1a] border border-[#3d3a39] rounded-lg p-5">
        <p
          className="text-[11px] font-semibold uppercase mb-3"
          style={{ color: '#00d992', letterSpacing: '2px' }}
        >
          Stability interpretation
        </p>
        <p className="text-[14px]" style={{ color: '#bdbdbd', lineHeight: 1.65 }}>
          <span style={{ color: '#00d992' }}>Persistent</span> hotspots recur consistently across months — they represent the
          core enforcement challenge and should receive permanent patrol coverage.{' '}
          <span style={{ color: '#eab308' }}>Seasonal</span> cells spike during specific periods.{' '}
          <span style={{ color: '#ef4444' }}>Volatile</span> cells show unpredictable patterns and need dynamic monitoring.
        </p>
      </div>

      {/* Filter buttons */}
      <div className="flex flex-wrap gap-2">
        {ALL_FILTERS.map((filter) => {
          const isActive = activeFilter === filter;
          return (
            <button
              key={filter}
              onClick={() => setActiveFilter(filter)}
              className="px-3 py-1.5 rounded-md text-[13px] font-medium transition-colors"
              style={
                isActive
                  ? { border: '1px solid #00d992', color: '#00d992', background: 'rgba(0,217,146,0.06)' }
                  : { border: '1px solid #3d3a39', color: '#8b949e', background: '#101010' }
              }
            >
              {filter}
            </button>
          );
        })}
      </div>

      {/* Table */}
      <div className="bg-[#1a1a1a] border border-[#3d3a39] rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr style={{ borderBottom: '1px solid #3d3a39' }}>
                {['Cell ID', 'Stability', 'Recurrence', 'Avg Monthly', 'Active Months', 'Station'].map((h) => (
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
              {filteredData.map((item, index) => (
                <tr
                  key={index}
                  className="hover:bg-[rgba(255,255,255,0.02)] transition-colors"
                  style={{ borderBottom: '1px solid rgba(61,58,57,0.5)' }}
                >
                  <td className="px-4 py-3 font-mono text-[13px]" style={{ color: '#f2f2f2' }}>
                    {item.spatial_cell_id}
                  </td>
                  <td className="px-4 py-3">
                    <StabilityBadge stability={item.stability_class} />
                  </td>
                  <td className="px-4 py-3 font-mono text-[13px]" style={{ color: '#00d992' }}>
                    {item.recurrence}
                  </td>
                  <td className="px-4 py-3 font-mono text-[13px]" style={{ color: '#f2f2f2' }}>
                    {item.mean_monthly}
                  </td>
                  <td className="px-4 py-3 font-mono text-[13px]" style={{ color: '#f2f2f2' }}>
                    {item.n_active}
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
