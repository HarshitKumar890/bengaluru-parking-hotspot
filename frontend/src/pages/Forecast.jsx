import SectionHeader from '../components/common/SectionHeader.jsx';
import LoadingSkeleton from '../components/common/LoadingSkeleton.jsx';
import ErrorState from '../components/common/ErrorState.jsx';
import ChartContainer from '../components/common/ChartContainer.jsx';
import ForecastChart from '../components/charts/ForecastChart.jsx';
import RiskBadge from '../components/common/RiskBadge.jsx';
import StabilityBadge from '../components/common/StabilityBadge.jsx';
import useForecast from '../hooks/useForecast.js';

export default function Forecast() {
  const { forecasts, metadata, loading, error } = useForecast();

  if (loading) return <LoadingSkeleton height="h-[600px]" />;
  if (error) return <ErrorState message={error} />;

  return (
    <div className="space-y-6">
      <SectionHeader
        eyebrow="Predictive Analytics"
        title="Forecast Snapshot"
        subtitle="Latest LightGBM hotspot forecast output — precomputed from spatial-temporal features."
      />

      {/* Status chips */}
      <div className="flex flex-wrap gap-3">
        <div
          className="flex items-center gap-2 px-3 py-1.5 rounded-full text-[12px] font-semibold"
          style={{
            background: metadata?.model_loaded ? 'rgba(0,217,146,0.1)' : 'rgba(239,68,68,0.1)',
            border: `1px solid ${metadata?.model_loaded ? 'rgba(0,217,146,0.3)' : 'rgba(239,68,68,0.3)'}`,
            color: metadata?.model_loaded ? '#00d992' : '#ef4444',
          }}
        >
          <span
            className="w-1.5 h-1.5 rounded-full"
            style={{ background: metadata?.model_loaded ? '#00d992' : '#ef4444' }}
          />
          Model {metadata?.model_loaded ? 'Loaded' : 'Unavailable'}
        </div>

        <div
          className="flex items-center gap-2 px-3 py-1.5 rounded-full text-[12px] font-semibold"
          style={{
            background: 'rgba(0,217,146,0.06)',
            border: '1px solid rgba(0,217,146,0.2)',
            color: '#00d992',
          }}
        >
          <span className="font-mono">{metadata?.returned}</span> records
        </div>

        <div
          className="px-3 py-1.5 rounded-full text-[12px] font-semibold"
          style={{
            background: 'rgba(255,255,255,0.04)',
            border: '1px solid #3d3a39',
            color: '#8b949e',
          }}
        >
          {metadata?.total} total cells
        </div>
      </div>

      {/* Snapshot note */}
      {metadata?.snapshot_note && (
        <div
          className="rounded-lg px-4 py-3 font-mono text-[13px]"
          style={{
            background: '#1a1a1a',
            border: '1px solid #3d3a39',
            color: '#8b949e',
          }}
        >
          <span style={{ color: '#00d992' }}># </span>
          {metadata.snapshot_note}
        </div>
      )}

      {/* Chart */}
      <ChartContainer title="Forecasted hotspots — top 20 cells" subtitle="Ranked by predicted violation count">
        <ForecastChart data={forecasts.slice(0, 20)} />
      </ChartContainer>

      {/* Interpretation panel */}
      <div
        className="bg-[#1a1a1a] rounded-lg p-5"
        style={{ border: '1px solid #3d3a39' }}
      >
        <p
          className="text-[11px] font-semibold uppercase mb-3"
          style={{ color: '#00d992', letterSpacing: '2px' }}
        >
          Forecast interpretation
        </p>
        <p className="text-[14px]" style={{ color: '#bdbdbd', lineHeight: 1.65 }}>
          The LightGBM model generates per-cell forecasted violation counts for the next period.
          Bars in green represent the top 3 highest-predicted cells. Use these predictions alongside
          congestion risk and stability class when allocating patrol resources.
        </p>
      </div>

      {/* Table */}
      <div className="bg-[#1a1a1a] border border-[#3d3a39] rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr style={{ borderBottom: '1px solid #3d3a39' }}>
                {['Rank', 'Cell', 'Forecast', 'Risk', 'Stability', 'Station'].map((h) => (
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
              {forecasts.map((item, index) => (
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
                    {item.forecasted_count}
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
