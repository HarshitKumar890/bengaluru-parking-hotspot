export default function KPICard({
  title,
  value,
  subtitle,
  color = "text-sky-400",
}) {
  return (
    <div
      className="
        bg-[#111827]
        border
        border-slate-800
        rounded-2xl
        p-5
        hover:border-sky-500/30
        transition-all
        duration-300
      "
    >
      <p className="text-xs uppercase tracking-wider text-slate-500 font-semibold">
        {title}
      </p>

      <h2 className={`text-3xl font-bold mt-3 ${color}`}>
        {value}
      </h2>

      {subtitle && (
        <p className="text-sm text-slate-400 mt-2">
          {subtitle}
        </p>
      )}
    </div>
  );
}