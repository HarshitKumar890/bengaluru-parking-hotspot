const API_BASE =
  import.meta.env.VITE_API_URL ||
  "http://localhost:8000";

export default function DownloadCard({
  dataset,
}) {
  const handleDownload = () => {
    window.open(
      `${API_BASE}/download/${dataset}`,
      "_blank"
    );
  };

  return (
    <div className="bg-[#111827] border border-slate-800 rounded-2xl p-5">
      <h3 className="text-white font-semibold break-all">
        {dataset}
      </h3>

      <button
        onClick={handleDownload}
        className="
          mt-4
          px-4
          py-2
          rounded-xl
          bg-sky-500
          hover:bg-sky-600
          text-black
          font-semibold
        "
      >
        Download CSV
      </button>
    </div>
  );
}