import SectionHeader from "../components/common/SectionHeader";
import LoadingSkeleton from "../components/common/LoadingSkeleton";
import ErrorState from "../components/common/ErrorState";

import HotspotMap from "../components/maps/HotspotMap";

import useHotspots from "../hooks/useHotspots";

export default function Hotspots() {
  const {
    hotspots,
    loading,
    error,
  } = useHotspots();

  if (loading) {
    return (
      <LoadingSkeleton height="h-[700px]" />
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
        title="Hotspot Intelligence Map"
        subtitle="Interactive map of parking hotspot cells across Bengaluru."
      />

      <div className="bg-[#111827] border border-slate-800 rounded-3xl overflow-hidden">
        <HotspotMap
          hotspots={hotspots}
        />
      </div>

    </div>
  );
}