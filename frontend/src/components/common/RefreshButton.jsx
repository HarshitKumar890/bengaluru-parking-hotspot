import { useState } from "react";

export default function RefreshButton({
  onRefresh,
}) {
  const [refreshing, setRefreshing] =
    useState(false);

  const handleRefresh = async () => {
  try {
    await Promise.all([
      fetchSummary(),
      fetchStations(),
      fetchHealth(),
    ]);
  } catch (error) {
    console.error(error);
  }
};

  return (
    <button
      onClick={handleRefresh}
      disabled={refreshing}
      className="
        px-5
        py-3
        rounded-xl
        bg-sky-500
        hover:bg-sky-600
        text-black
        font-semibold
        transition-all
        disabled:opacity-50
      "
    >
      {refreshing
        ? "Refreshing..."
        : "Refresh"}
    </button>
  );
}