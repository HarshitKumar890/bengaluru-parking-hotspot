export default function StabilityBadge({
  stability,
}) {
  const colors = {
    Persistent:
      "bg-green-500/20 text-green-400",

    Seasonal:
      "bg-yellow-500/20 text-yellow-400",

    Sporadic:
      "bg-red-500/20 text-red-400",
  };

  return (
    <span
      className={`
        px-3
        py-1
        rounded-full
        text-xs
        font-semibold
        ${colors[stability] || colors.Sporadic}
      `}
    >
      {stability}
    </span>
  );
}