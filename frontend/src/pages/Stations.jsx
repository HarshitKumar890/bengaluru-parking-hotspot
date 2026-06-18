import useStations from "../hooks/useStations";

export default function Stations() {
  const {
    stations,
    loading,
    error,
  } = useStations();

  if (loading) {
    return (
      <div className="text-white p-6">
        Loading stations...
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-500 p-6">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h1 className="text-3xl font-bold text-white">
        Police Station Analytics
      </h1>

      <div className="overflow-x-auto bg-[#111827] rounded-2xl border border-slate-800">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-800">
              <th className="p-4 text-left text-slate-400">
                Station
              </th>

              <th className="p-4 text-left text-slate-400">
                Cases
              </th>

              <th className="p-4 text-left text-slate-400">
                Approval %
              </th>

              <th className="p-4 text-left text-slate-400">
                Rejection %
              </th>

              <th className="p-4 text-left text-slate-400">
                Ops Score
              </th>

              <th className="p-4 text-left text-slate-400">
                Hotspot Cells
              </th>
            </tr>
          </thead>

          <tbody>
            {stations.map((station, index) => (
              <tr
                key={index}
                className="border-b border-slate-800"
              >
                <td className="p-4 text-white">
                  {station.police_station}
                </td>

                <td className="p-4 text-white">
                  {station.total_cases}
                </td>

                <td className="p-4 text-green-400">
                  {station.approval_rate_pct}
                </td>

                <td className="p-4 text-red-400">
                  {station.rejection_rate_pct}
                </td>

                <td className="p-4 text-sky-400">
                  {station.ops_score}
                </td>

                <td className="p-4 text-white">
                  {station.n_active_hotspot_cells}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}