export default function ModelStatusBadge({
  modelName,
  recall,
  loaded = true,
}) {
  return (
    <div className="bg-[#111827] border border-slate-800 rounded-xl px-4 py-3">
      <div className="flex items-center gap-2">
        <div
          className={`w-2 h-2 rounded-full ${
            loaded
              ? "bg-green-400"
              : "bg-red-400"
          }`}
        />

        <span
          className={`text-sm font-semibold ${
            loaded
              ? "text-green-400"
              : "text-red-400"
          }`}
        >
          {loaded ? "Model Loaded" : "Model Offline"}
        </span>
      </div>

      <p className="text-white mt-2 font-medium">
        {modelName || "Unknown"}
      </p>

      <p className="text-sky-400 text-sm mt-1">
        Recall@20: {recall ?? 0}
      </p>
    </div>
  );
}