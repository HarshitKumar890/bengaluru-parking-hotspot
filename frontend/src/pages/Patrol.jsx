import SectionHeader from "../components/common/SectionHeader";
import LoadingSkeleton from "../components/common/LoadingSkeleton";
import ErrorState from "../components/common/ErrorState";

import ChartContainer from "../components/common/ChartContainer";

import PatrolChart from "../components/charts/PatrolChart";

import RiskBadge from "../components/common/RiskBadge";
import StabilityBadge from "../components/common/StabilityBadge";

import usePatrol from "../hooks/usePatrol";

export default function Patrol() {
  const {
    patrols,
    loading,
    error,
  } = usePatrol();

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
        title="Patrol Recommendations"
        subtitle="Top patrol deployment cells prioritized by AI risk scoring."
      />

      <ChartContainer title="Priority Scores">
        <PatrolChart
          data={patrols}
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
                  Cell
                </th>

                <th className="p-4 text-left text-slate-400">
                  Prediction
                </th>

                <th className="p-4 text-left text-slate-400">
                  Priority
                </th>

                <th className="p-4 text-left text-slate-400">
                  Risk
                </th>

                <th className="p-4 text-left text-slate-400">
                  Stability
                </th>

                <th className="p-4 text-left text-slate-400">
                  Station
                </th>

              </tr>
            </thead>

            <tbody>
              {patrols.map(
                (item, index) => (
                  <tr
                    key={index}
                    className="border-b border-slate-800 hover:bg-slate-900"
                  >
                    <td className="p-4 text-yellow-400 font-semibold">
                      #{item.patrol_rank}
                    </td>

                    <td className="p-4 text-white">
                      {
                        item.spatial_cell_id
                      }
                    </td>

                    <td className="p-4 text-sky-400">
                      {
                        item.predicted_count
                      }
                    </td>

                    <td className="p-4 text-orange-400">
                      {
                        item.priority_score
                      }
                    </td>

                    <td className="p-4">
                      <RiskBadge
                        risk={
                          item.congestion_risk_category
                        }
                      />
                    </td>

                    <td className="p-4">
                      <StabilityBadge
                        stability={
                          item.stability_class
                        }
                      />
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

      <div className="grid gap-4">
        {patrols.slice(0, 5).map(
          (item, index) => (
            <div
              key={index}
              className="bg-[#111827] border border-slate-800 rounded-2xl p-5"
            >
              <h3 className="text-white font-semibold">
                Rank #{item.patrol_rank}
              </h3>

              <p className="text-slate-400 mt-2">
                {
                  item.risk_explanation
                }
              </p>
            </div>
          )
        )}
      </div>
    </div>
  );
}