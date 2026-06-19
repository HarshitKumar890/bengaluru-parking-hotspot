import SectionHeader from '../components/common/SectionHeader.jsx';
import LoadingSkeleton from '../components/common/LoadingSkeleton.jsx';
import ErrorState from '../components/common/ErrorState.jsx';
import ChartContainer from '../components/common/ChartContainer.jsx';
import FeatureImportanceChart from '../components/charts/FeatureImportanceChart.jsx';
import useFeatureImportance from '../hooks/useFeatureImportance.js';

export default function FeatureImportance() {
  const { features, loading, error } = useFeatureImportance();

  if (loading) return <LoadingSkeleton height="h-[600px]" />;
  if (error) return <ErrorState message={error} />;

  const topFive = features.slice(0, 5);
  const totalImportance = features.reduce((sum, f) => sum + (f.importance || 0), 0);

  return (
    <div className="space-y-6">
      <SectionHeader
        eyebrow="Model Explainability"
        title="Feature Importance"
        subtitle="LightGBM split-based feature importance rankings — understanding what drives hotspot predictions."
      />

      {/* Top 5 feature pills */}
      <div className="flex flex-wrap gap-2">
        {topFive.map((feature, index) => (
          <span
            key={index}
            className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-[12px] font-medium"
            style={{
              border: '1px solid rgba(0,217,146,0.4)',
              color: '#00d992',
              background: 'rgba(0,217,146,0.06)',
            }}
          >
            <span
              className="font-mono text-[10px]"
              style={{ color: 'rgba(0,217,146,0.6)' }}
            >
              #{feature.rank}
            </span>
            {feature.feature}
          </span>
        ))}
      </div>

      {/* Chart */}
      <ChartContainer title="Feature importance — all features" subtitle="Split-based importance from LightGBM model">
        <FeatureImportanceChart data={features} />
      </ChartContainer>

      {/* Two interpretation cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-[#1a1a1a] border border-[#3d3a39] rounded-lg p-5">
          <p
            className="text-[11px] font-semibold uppercase mb-3"
            style={{ color: '#00d992', letterSpacing: '2px' }}
          >
            Top predictors
          </p>
          <p className="text-[14px]" style={{ color: '#bdbdbd', lineHeight: 1.65 }}>
            The highest-importance features dominate model decisions. Temporal features (lag values,
            rolling means) typically lead in time-series forecasting models, indicating that historical
            patterns are the strongest signals for future hotspot activity.
          </p>
        </div>
        <div className="bg-[#1a1a1a] border border-[#3d3a39] rounded-lg p-5">
          <p
            className="text-[11px] font-semibold uppercase mb-3"
            style={{ color: '#8b949e', letterSpacing: '2px' }}
          >
            Feature engineering
          </p>
          <p className="text-[14px]" style={{ color: '#bdbdbd', lineHeight: 1.65 }}>
            Spatial identifiers and station-level aggregates contribute to location-based predictions.
            Low-importance features can be candidates for pruning in future model iterations to reduce
            complexity without significant accuracy loss.
          </p>
        </div>
      </div>

      {/* Table with inline bar sparklines */}
      <div className="bg-[#1a1a1a] border border-[#3d3a39] rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr style={{ borderBottom: '1px solid #3d3a39' }}>
                {['Rank', 'Feature', 'Importance', 'Importance %', 'Relative'].map((h) => (
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
              {features.map((feature, index) => {
                const pct = totalImportance > 0 ? (feature.importance / totalImportance) * 100 : 0;
                return (
                  <tr
                    key={index}
                    className="hover:bg-[rgba(255,255,255,0.02)] transition-colors"
                    style={{ borderBottom: '1px solid rgba(61,58,57,0.5)' }}
                  >
                    <td className="px-4 py-3 font-mono text-[13px]" style={{ color: '#8b949e' }}>
                      #{feature.rank}
                    </td>
                    <td className="px-4 py-3 text-[13px]" style={{ color: '#f2f2f2' }}>
                      {feature.feature}
                    </td>
                    <td className="px-4 py-3 font-mono text-[13px]" style={{ color: '#f2f2f2' }}>
                      {feature.importance}
                    </td>
                    <td className="px-4 py-3 font-mono text-[13px]" style={{ color: '#00d992' }}>
                      {feature.importance_pct}%
                    </td>
                    <td className="px-4 py-3 w-32">
                      <div
                        className="h-1.5 rounded-full"
                        style={{ background: '#3d3a39', width: '100%' }}
                      >
                        <div
                          className="h-1.5 rounded-full"
                          style={{
                            background: index < 3 ? '#00d992' : 'rgba(0,217,146,0.4)',
                            width: `${Math.min(100, pct * 3)}%`,
                          }}
                        />
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
