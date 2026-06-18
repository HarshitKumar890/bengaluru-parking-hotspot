export default function SectionHeader({
  title,
  subtitle,
}) {
  return (
    <div className="mb-6">
      <h2 className="text-2xl font-bold text-white">
        {title}
      </h2>

      {subtitle && (
        <p className="text-slate-400 mt-2">
          {subtitle}
        </p>
      )}
    </div>
  );
}