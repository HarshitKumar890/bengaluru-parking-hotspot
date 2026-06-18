import RiskBadge from "../common/RiskBadge";
import StabilityBadge from "../common/StabilityBadge";

export default function HotspotPopup({
  hotspot,
}) {
  return (
    <div className="space-y-2 min-w-62.5">

      <h3 className="font-bold">
        {hotspot.spatial_cell_id}
      </h3>

      <p>
        Station:
        {" "}
        {hotspot.police_station}
      </p>

      <p>
        Forecast:
        {" "}
        {hotspot.forecasted_count}
      </p>

      <p>
        Priority:
        {" "}
        {hotspot.priority_score}
      </p>

      <p>
        Patrol Rank:
        {" "}
        #{hotspot.patrol_rank}
      </p>

      <RiskBadge
        risk={
          hotspot.congestion_risk_category
        }
      />

      <div className="mt-2">
        <StabilityBadge
          stability={
            hotspot.stability_class
          }
        />
      </div>
    </div>
  );
}