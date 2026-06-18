export default function LastUpdatedBadge({
  timestamp,
}) {
  if (!timestamp) return null;

  const formattedDate = new Date(
    timestamp
  ).toLocaleString();

  return (
    <div className="inline-flex items-center gap-2 px-4 py-3 rounded-xl bg-[#111827] border border-slate-800">
      <div className="w-2 h-2 rounded-full bg-green-400" />

      <span className="text-sm text-slate-300">
        Last updated: {formattedDate}
      </span>
    </div>
  );
}