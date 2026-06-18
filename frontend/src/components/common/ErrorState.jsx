export default function ErrorState({
  message = "Something went wrong",
}) {
  return (
    <div className="bg-red-500/10 border border-red-500 rounded-2xl p-6">
      <p className="text-red-400">
        {message}
      </p>
    </div>
  );
}