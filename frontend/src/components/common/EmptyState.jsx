export default function EmptyState({
  message = "No data available",
}) {
  return (
    <div className="bg-[#111827] border border-slate-800 rounded-2xl p-10 text-center">
      <p className="text-slate-400">
        {message}
      </p>
    </div>
  );
}