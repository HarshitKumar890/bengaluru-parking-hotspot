import SectionHeader from "../components/common/SectionHeader";
import LoadingSkeleton from "../components/common/LoadingSkeleton";
import ErrorState from "../components/common/ErrorState";

import ChartContainer from "../components/common/ChartContainer";
import StabilityBadge from "../components/common/StabilityBadge";

import StabilityChart from "../components/charts/StabilityChart";

import useStability from "../hooks/useStability";

export default function Stability() {
  const {
    stabilityData,
    loading,
    error,
  } = useStability();

  if (loading) {
    return (
      <LoadingSkeleton height="h-96" />
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
        title="Hotspot Stability Analysis"
        subtitle="Stability classifications derived from 6-month hotspot activity."
      />

      <ChartContainer title="Stability Distribution">
        <StabilityChart
          data={stabilityData}
        />
      </ChartContainer>

      <div className="bg-[#111827] border border-slate-800 rounded-3xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-800">
                <th className="p-4 text-left text-slate-400">
                  Cell ID
                </th>

                <th className="p-4 text-left text-slate-400">
                  Stability
                </th>

                <th className="p-4 text-left text-slate-400">
                  Recurrence
                </th>

                <th className="p-4 text-left text-slate-400">
                  Avg Monthly
                </th>

                <th className="p-4 text-left text-slate-400">
                  Active Months
                </th>

                <th className="p-4 text-left text-slate-400">
                  Station
                </th>
              </tr>
            </thead>

            <tbody>
              {stabilityData.map(
                (item, index) => (
                  <tr
                    key={index}
                    className="border-b border-slate-800 hover:bg-slate-900"
                  >
                    <td className="p-4 text-white">
                      {
                        item.spatial_cell_id
                      }
                    </td>

                    <td className="p-4">
                      <StabilityBadge
                        stability={
                          item.stability_class
                        }
                      />
                    </td>

                    <td className="p-4 text-sky-400">
                      {item.recurrence}
                    </td>

                    <td className="p-4 text-white">
                      {item.mean_monthly}
                    </td>

                    <td className="p-4 text-green-400">
                      {item.n_active}
                    </td>

                    <td className="p-4 text-white">
                      {
                        item.police_station
                      }
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