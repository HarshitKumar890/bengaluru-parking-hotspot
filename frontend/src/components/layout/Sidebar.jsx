import { NavLink } from "react-router-dom";
import { BarChart3 } from "lucide-react";
import { sidebarItems } from "../../constants/sidebarItems";

export default function Sidebar() {
  return (
    <aside className="w-70 bg-[#111827] border-r border-slate-800 flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <BarChart3 className="w-7 h-7 text-sky-400" />

          <div>
            <h1 className="text-white font-bold text-xl">
              ParkIntel AI
            </h1>

            <p className="text-slate-400 text-sm">
              Traffic Intelligence
            </p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {sidebarItems.map((item) => {
          const Icon = item.icon;

          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `
                flex items-center gap-3
                px-4 py-3
                rounded-xl
                transition-all
                ${
                  isActive
                    ? "bg-sky-500/10 text-sky-400 border border-sky-500/20"
                    : "text-slate-400 hover:bg-slate-800 hover:text-white"
                }
              `
              }
            >
              <Icon size={18} />

              <span className="text-sm font-medium">
                {item.title}
              </span>
            </NavLink>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-slate-800">
        <div className="bg-slate-900 rounded-xl p-3">
          <p className="text-white text-sm font-semibold">
            System Status
          </p>

          <p className="text-green-400 text-xs mt-1">
            ● Active
          </p>
        </div>
      </div>
    </aside>
  );
}