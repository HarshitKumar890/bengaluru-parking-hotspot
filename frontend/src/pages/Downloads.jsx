import SectionHeader from "../components/common/SectionHeader";
import LoadingSkeleton from "../components/common/LoadingSkeleton";
import ErrorState from "../components/common/ErrorState";

import DownloadCard from "../components/common/DownloadCard";

import useDownloads from "../hooks/useDownloads";

export default function Downloads() {
  const {
    datasets,
    loading,
    error,
  } = useDownloads();

  if (loading) {
    return (
      <LoadingSkeleton height="h-[400px]" />
    );
  }

  if (error) {
    return (
      <ErrorState message={error} />
    );
  }

  return (
    <div className="space-y-8">
      <SectionHeader
        title="Dataset Downloads"
        subtitle="Download precomputed analytics datasets."
      />

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
        {datasets.map(
          (dataset, index) => (
            <DownloadCard
              key={index}
              dataset={dataset}
            />
          )
        )}
      </div>
    </div>
  );
}