import KPICard from "../components/common/KPICard";
import ChartContainer from "../components/common/ChartContainer";
import StationChart from "../components/charts/StationChart";

import useSummary from "../hooks/useSummary";
import useStations from "../hooks/useStations";

export default function Dashboard() {
  const {
    summary,
    loading: summaryLoading,
    error: summaryError,
  } = useSummary();

  const {
    stations,
    loading: stationsLoading,
    error: stationsError,
  } = useStations();

  if (summaryLoading) {
    return (
      <div className="flex items-center justify-center h-[70vh]">
        <p className="text-white text-lg">
          Loading dashboard...
        </p>
      </div>
    );
  }

  if (summaryError) {
    return (
      <div className="flex items-center justify-center h-[70vh]">
        <p className="text-red-500 text-lg">
          {summaryError}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Hero Section */}

      <section className="bg-[#111827] border border-slate-800 rounded-3xl p-8">
        <h1 className="text-4xl font-bold text-sky-400">
          AI Powered Parking Hotspot Intelligence
        </h1>

        <p className="text-slate-400 mt-4 max-w-4xl">
          Forecast illegal parking hotspots, estimate
          parking-induced congestion risk, and prioritize
          enforcement using machine learning powered
          hotspot intelligence.
        </p>
      </section>

      {/* Primary KPI Grid */}

      <section className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-6 gap-4">
        <KPICard
          title="Total Violations"
          value={summary?.total_violations ?? 0}
        />

        <KPICard
          title="Spatial Cells"
          value={summary?.total_spatial_cells ?? 0}
        />

        <KPICard
          title="Persistent Hotspots"
          value={summary?.persistent_hotspots ?? 0}
          color="text-green-400"
        />

        <KPICard
          title="Critical Risk Zones"
          value={summary?.critical_risk_zones ?? 0}
          color="text-red-400"
        />

        <KPICard
          title="Best Model"
          value={summary?.best_model_name ?? "-"}
          color="text-purple-400"
        />

        <KPICard
          title="Top Police Station"
          value={summary?.top_police_station ?? "-"}
        />
      </section>

      {/* Secondary KPI Grid */}

      <section className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-6 gap-4">
        <KPICard
          title="High Risk Zones"
          value={summary?.high_risk_zones ?? 0}
          color="text-orange-400"
        />

        <KPICard
          title="Top Junction"
          value={summary?.top_junction ?? "-"}
        />

        <KPICard
          title="Recall@20"
          value={summary?.best_recall_at_20 ?? 0}
          color="text-green-400"
        />

        <KPICard
          title="April Factor"
          value={summary?.april_normalization_factor ?? 0}
        />

        <KPICard
          title="Patrol Cells"
          value={summary?.total_patrol_cells ?? 0}
        />

        <KPICard
          title="Top 20 Patrol"
          value={summary?.top20_patrol_cells ?? 0}
        />
      </section>

      {/* Charts Section */}

      <section className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <ChartContainer title="Top Police Stations">
          {stationsLoading ? (
            <div className="text-white">
              Loading station analytics...
            </div>
          ) : stationsError ? (
            <div className="text-red-500">
              {stationsError}
            </div>
          ) : (
            <StationChart data={stations} />
          )}
        </ChartContainer>

        <ChartContainer title="System Status">
          <div className="space-y-4">
            <div className="flex justify-between">
              <span className="text-slate-400">
                Model
              </span>

              <span className="text-green-400 font-medium">
                Loaded
              </span>
            </div>

            <div className="flex justify-between">
              <span className="text-slate-400">
                API
              </span>

              <span className="text-green-400 font-medium">
                Healthy
              </span>
            </div>

            <div className="flex justify-between">
              <span className="text-slate-400">
                Best Model
              </span>

              <span className="text-white font-medium">
                {summary?.best_model_name ?? "-"}
              </span>
            </div>

            <div className="flex justify-between">
              <span className="text-slate-400">
                Recall@20
              </span>

              <span className="text-sky-400 font-medium">
                {summary?.best_recall_at_20 ?? 0}
              </span>
            </div>
          </div>
        </ChartContainer>
      </section>
    </div>
  );
}