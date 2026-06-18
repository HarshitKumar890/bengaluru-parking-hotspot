import {
  RefreshCw,
  CheckCircle2,
  Activity,
} from "lucide-react";

export default function Navbar() {
  return (
    <header className="h-16 border-b border-slate-800 bg-[#111827] px-6 flex items-center justify-between">
      {/* Left */}
      <div>
        <h1 className="text-xl font-semibold text-white">
          Overview Dashboard
        </h1>
      </div>

      {/* Right */}
      <div className="flex items-center gap-4">
        {/* Model Status */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1 rounded-full bg-green-500/10 border border-green-500/20">
          <Activity size={14} className="text-green-400" />

          <span className="text-xs font-medium text-green-400">
            Model Loaded (LGBM)
          </span>
        </div>

        {/* API Status */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/20">
          <CheckCircle2 size={14} className="text-sky-400" />

          <span className="text-xs font-medium text-sky-400">
            API Healthy
          </span>
        </div>

        {/* Last Updated */}
        <span className="hidden lg:block text-xs text-slate-400">
          Last updated: 2 mins ago
        </span>

        {/* Refresh Button */}
        <button
          className="
            flex items-center gap-2
            bg-sky-500
            hover:bg-sky-600
            text-black
            font-semibold
            px-4 py-2
            rounded-lg
            transition
          "
        >
          <RefreshCw size={16} />

          Refresh
        </button>
      </div>
    </header>
  );
}