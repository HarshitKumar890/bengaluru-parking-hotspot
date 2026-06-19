import KPICard from '../components/common/KPICard.jsx';
import ChartContainer from '../components/common/ChartContainer.jsx';
import StationChart from '../components/charts/StationChart.jsx';
import LoadingSkeleton from '../components/common/LoadingSkeleton.jsx';
import ErrorState from '../components/common/ErrorState.jsx';
import useHealth from '../hooks/useHealth.js';
import useSummary from '../hooks/useSummary.js';
import useStations from '../hooks/useStations.js';
import { AlertTriangle, MapPin, Database, CheckCircle2 } from 'lucide-react';

export default function Dashboard() {
  const { summary, loading: sl, error: se } = useSummary();
  const { stations, loading: stl } = useStations();
  const { health } = useHealth();

  if (sl) {
    return (
      <div className="space-y-5">
        <LoadingSkeleton height="h-28" />
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[0, 1, 2, 3].map((i) => (
            <LoadingSkeleton key={i} height="h-24" />
          ))}
        </div>
        <LoadingSkeleton height="h-72" />
      </div>
    );
  }

  if (se) return <ErrorState message={se} />;

  return (
    <div className="space-y-6 w-full">

      {/* ── Hero band ── */}
      <section className="bg-[#101010]">
        <p
          className="font-mono text-[12px] font-semibold uppercase mb-2"
          style={{ color: '#00d992', letterSpacing: '2.52px' }}
        >
          Parking Hotspot Intelligence
        </p>
        <h1
          className="text-[32px] font-light tracking-tight text-white"
        >
          Bengaluru enforcement intelligence
        </h1>
        <p className="text-[15px] mt-2 max-w-2xl" style={{ color: '#8b949e', lineHeight: 1.65 }}>
          Identifying illegal parking clusters, estimating congestion risk, and
          prioritizing patrol deployment using spatial and temporal machine learning.
        </p>
      </section>

      {/* ── Primary KPIs ── */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <KPICard
          title="Total violations"
          value={summary?.total_violations?.toLocaleString()}
          accent
        />
        <KPICard
          title="Critical risk zones"
          value={summary?.critical_risk_zones}
          subtitle="Highest severity"
        />
        <KPICard
          title="Recall@20"
          value={summary?.best_recall_at_20}
          subtitle="Model performance"
          accent
        />
        <KPICard
          title="Top station"
          value={summary?.top_police_station}
          subtitle="Highest workload"
        />
      </div>

      {/* ── Secondary KPIs ── */}
      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-3">
        <KPICard title="Spatial cells" value={summary?.total_spatial_cells} />
        <KPICard title="Persistent hotspots" value={summary?.persistent_hotspots} accent />
        <KPICard title="High risk zones" value={summary?.high_risk_zones} />
        <KPICard title="Patrol cells" value={summary?.total_patrol_cells} />
        <KPICard title="Top 20 patrol" value={summary?.top20_patrol_cells} />
        <KPICard title="April factor" value={summary?.april_normalization_factor} />
      </div>

      {/* ── Operational takeaway + Chart side by side ── */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">

        {/* Takeaway card */}
        <div
          className="bg-[#1a1a1a] rounded-lg p-5 flex flex-col gap-4"
          style={{ borderLeft: '2px solid #00d992', borderTop: '1px solid #3d3a39', borderRight: '1px solid #3d3a39', borderBottom: '1px solid #3d3a39' }}
        >
          <div>
            <p
              className="text-[11px] font-semibold uppercase mb-3"
              style={{ color: '#8b949e', letterSpacing: '2px' }}
            >
              Operational summary
            </p>
            <ul className="space-y-3">
              {[
                {
                  icon: AlertTriangle,
                  color: '#ef4444',
                  text: 'UPPARPET and CITY MARKET are highest-priority zones — critical with persistent recurrence.',
                },
                {
                  icon: MapPin,
                  color: '#f97316',
                  text: 'Persistent hotspots matter more than isolated spikes. Focus sustained coverage on recurring cells.',
                },
                {
                  icon: AlertTriangle,
                  color: '#eab308',
                  text: 'SHIVAJINAGAR is high volume but comparatively more stable. Monitor but not first priority.',
                },
                {
                  icon: MapPin,
                  color: '#00d992',
                  text: 'Deploy patrol units to top-ranked cells first. Top 20 cells deliver highest ROI.',
                },
              ].map((item, i) => {
                const Icon = item.icon;
                return (
                  <li key={i} className="flex items-start gap-2.5">
                    <Icon size={13} style={{ color: item.color, marginTop: '2px', flexShrink: 0 }} />
                    <p className="text-[12px] leading-relaxed" style={{ color: '#8b949e' }}>
                      {item.text}
                    </p>
                  </li>
                );
              })}
            </ul>
          </div>

          {/* System health */}
          <div
            className="pt-4 mt-auto"
            style={{ borderTop: '1px solid #3d3a39' }}
          >
            <p
              className="text-[11px] font-semibold uppercase mb-3"
              style={{ color: '#8b949e', letterSpacing: '2px' }}
            >
              System health
            </p>
            <div className="space-y-2">
              {[
                {
                  label: 'Model',
                  value: health?.model_loaded ? 'Loaded' : 'Unavailable',
                  color: health?.model_loaded ? '#00d992' : '#ef4444',
                },
                { label: 'API', value: 'Healthy', color: '#00d992' },
                { label: 'Best model', value: summary?.best_model_name ?? 'LightGBM', color: '#8b949e' },
                { label: 'Inference', value: 'Precomputed snapshot', color: '#8b949e' },
              ].map((row) => (
                <div key={row.label} className="flex justify-between items-center">
                  <span className="text-[12px]" style={{ color: '#8b949e' }}>
                    {row.label}
                  </span>
                  <span
                    className="text-[12px] font-medium font-mono"
                    style={{ color: row.color }}
                  >
                    {row.value}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Chart */}
        <div className="xl:col-span-2">
          <ChartContainer
            title="Top stations by case volume"
            subtitle="Stations with highest enforcement workload"
          >
            {stl ? <LoadingSkeleton height="h-64" /> : <StationChart data={stations} />}
          </ChartContainer>
        </div>
      </div>

      {/* ── Station table ── */}
      {stations.length > 0 && (
        <div className="bg-[#1a1a1a] border border-[#3d3a39] rounded-lg overflow-hidden">
          <div
            className="px-5 py-3 flex items-center justify-between"
            style={{ borderBottom: '1px solid #3d3a39' }}
          >
            <p className="text-[13px] font-semibold text-white">Station summary</p>
            <div className="flex items-center gap-1.5">
              <Database size={12} style={{ color: '#8b949e' }} />
              <span className="text-[12px]" style={{ color: '#8b949e' }}>
                {stations.length} stations
              </span>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr style={{ borderBottom: '1px solid #3d3a39' }}>
                  {['Station', 'Cases', 'Approval %', 'Ops score', 'Hotspot cells'].map((h) => (
                    <th
                      key={h}
                      className="px-4 py-2.5 text-left text-[11px] font-semibold uppercase"
                      style={{ color: '#8b949e', letterSpacing: '1.5px' }}
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {stations.slice(0, 6).map((s, i) => (
                  <tr
                    key={i}
                    style={{ borderBottom: '1px solid rgba(61,58,57,0.5)' }}
                    className="hover:bg-[rgba(255,255,255,0.02)] transition-colors"
                  >
                    <td className="px-4 py-2.5 text-[13px]" style={{ color: '#f2f2f2' }}>
                      {s.police_station}
                    </td>
                    <td
                      className="px-4 py-2.5 text-[13px] font-mono font-medium"
                      style={{ color: '#00d992' }}
                    >
                      {s.total_cases?.toLocaleString()}
                    </td>
                    <td className="px-4 py-2.5 text-[13px] font-mono" style={{ color: '#f2f2f2' }}>
                      {s.approval_rate_pct}%
                    </td>
                    <td className="px-4 py-2.5 text-[13px] font-mono" style={{ color: '#bdbdbd' }}>
                      {s.ops_score}
                    </td>
                    <td className="px-4 py-2.5 text-[13px] font-mono" style={{ color: '#bdbdbd' }}>
                      {s.n_active_hotspot_cells}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
