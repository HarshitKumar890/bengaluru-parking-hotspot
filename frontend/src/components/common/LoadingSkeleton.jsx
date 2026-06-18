export default function LoadingSkeleton({
  height = "h-32",
}) {
  return (
    <div
      className={`
        bg-[#111827]
        border
        border-slate-800
        rounded-2xl
        animate-pulse
        ${height}
      `}
    />
  );
}