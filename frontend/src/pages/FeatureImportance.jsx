import SectionHeader from "../components/common/SectionHeader";
import LoadingSkeleton from "../components/common/LoadingSkeleton";
import ErrorState from "../components/common/ErrorState";
import ChartContainer from "../components/common/ChartContainer";

import FeatureImportanceChart from "../components/charts/FeatureImportanceChart";

import useFeatureImportance from "../hooks/useFeatureImportance";

export default function FeatureImportance() {
  const {
    features,
    loading,
    error,
  } = useFeatureImportance();

  if (loading) {
    return (
      <LoadingSkeleton height="h-[600px]" />
    );
  }

  if (error) {
    return (
      <ErrorState message={error} />
    );
  }

  return (
    <div className="space-y-8">
      <SectionHeader
        title="Feature Importance"
        subtitle="LightGBM split-based feature importance rankings."
      />

      <ChartContainer title="Top Features">
        <FeatureImportanceChart
          data={features}
        />
      </ChartContainer>

      <div className="bg-[#111827] border border-slate-800 rounded-3xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-800">
                <th className="p-4 text-left text-slate-400">
                  Rank
                </th>

                <th className="p-4 text-left text-slate-400">
                  Feature
                </th>

                <th className="p-4 text-left text-slate-400">
                  Importance
                </th>

                <th className="p-4 text-left text-slate-400">
                  Importance %
                </th>
              </tr>
            </thead>

            <tbody>
              {features.map(
                (feature, index) => (
                  <tr
                    key={index}
                    className="border-b border-slate-800 hover:bg-slate-900"
                  >
                    <td className="p-4 text-yellow-400">
                      #{feature.rank}
                    </td>

                    <td className="p-4 text-white">
                      {feature.feature}
                    </td>

                    <td className="p-4 text-sky-400">
                      {feature.importance}
                    </td>

                    <td className="p-4 text-green-400">
                      {feature.importance_pct}%
                    </td>
                  </tr>
                )
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}