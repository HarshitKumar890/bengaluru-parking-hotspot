export default function ChartContainer({
  title,
  children,
}) {
  return (
    <div className="bg-[#111827] border border-slate-800 rounded-3xl p-6">
      <h3 className="text-white text-lg font-semibold mb-6">
        {title}
      </h3>

      {children}
    </div>
  );
}