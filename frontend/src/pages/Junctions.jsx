import SectionHeader from "../components/common/SectionHeader";
import LoadingSkeleton from "../components/common/LoadingSkeleton";
import ErrorState from "../components/common/ErrorState";

import ChartContainer from "../components/common/ChartContainer";
import JunctionChart from "../components/charts/JunctionChart";

import useJunctions from "../hooks/useJunctions";

export default function Junctions() {
  const {
    junctions,
    loading,
    error,
  } = useJunctions();

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
        title="Junction Analytics"
        subtitle="Case volume and operational analytics across Bengaluru junctions."
      />

      <ChartContainer title="Top Junctions by Case Volume">
        <JunctionChart
          data={junctions}
        />
      </ChartContainer>

      <div className="bg-[#111827] border border-slate-800 rounded-3xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-800">
                <th className="p-4 text-left text-slate-400">
                  Junction
                </th>

                <th className="p-4 text-left text-slate-400">
                  Cases
                </th>

                <th className="p-4 text-left text-slate-400">
                  Vehicles
                </th>

                <th className="p-4 text-left text-slate-400">
                  Approved
                </th>

                <th className="p-4 text-left text-slate-400">
                  Rejected
                </th>

                <th className="p-4 text-left text-slate-400">
                  Approval %
                </th>

                <th className="p-4 text-left text-slate-400">
                  Peak Hour
                </th>

                <th className="p-4 text-left text-slate-400">
                  Rank
                </th>
              </tr>
            </thead>

            <tbody>
              {junctions.map(
                (junction, index) => (
                  <tr
                    key={index}
                    className="border-b border-slate-800 hover:bg-slate-900"
                  >
                    <td className="p-4 text-white">
                      {
                        junction.junction_name
                      }
                    </td>

                    <td className="p-4 text-sky-400 font-semibold">
                      {
                        junction.total_cases
                      }
                    </td>

                    <td className="p-4 text-white">
                      {
                        junction.unique_vehicles
                      }
                    </td>

                    <td className="p-4 text-green-400">
                      {
                        junction.n_approved
                      }
                    </td>

                    <td className="p-4 text-red-400">
                      {
                        junction.n_rejected
                      }
                    </td>

                    <td className="p-4 text-white">
                      {
                        junction.approval_rate_pct
                      }
                      %
                    </td>

                    <td className="p-4 text-white">
                      {
                        junction.peak_hour_violations
                      }
                    </td>

                    <td className="p-4 text-yellow-400">
                      #
                      {
                        junction.volume_rank
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